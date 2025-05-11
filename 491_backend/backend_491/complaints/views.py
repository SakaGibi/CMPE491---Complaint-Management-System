from datetime import timedelta
from django.db.models import Count
from django.db.models.functions import TruncDay
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import SuggestionOrComplaint
from .serializers import SuggestionOrComplaintSerializer
from django.utils.timezone import now
from .models import ReportRecommendation
from datetime import datetime, timedelta
from django.db.models import Q
from django.core.mail import send_mail

import joblib
import os
from django.conf import settings

from groq import Groq
import json
import numpy as np

MODEL_PATH = os.path.join(settings.ML_MODELS_DIR, 'sikayet_model.joblib')
ENCODER_PATH = os.path.join(settings.ML_MODELS_DIR, 'label_encoder.joblib')


try:
    model = joblib.load(MODEL_PATH)
    label_encoder = joblib.load(ENCODER_PATH)
    print("ML modeli ve label encoder başarıyla yüklendi.")
except FileNotFoundError:
    print(f"HATA: Model veya encoder dosyaları bulunamadı!")
    print(f"Aranan Model Yolu: {MODEL_PATH}")
    print(f"Aranan Encoder Yolu: {ENCODER_PATH}")
    model = None
    label_encoder = None
except Exception as e:
    print(f"ML modeli yüklenirken bir hata oluştu: {e}")
    model = None
    label_encoder = None

def classify_all(description):
    if model is None or label_encoder is None:
        print("Uyarı: Model yüklenemediği için varsayılan sınıflandırma yapılıyor.")
        return "complaint", "general", "general", None

    try:
        try:
            tfidf_vectorizer = model.named_steps['tfidf']
            classifier = model.named_steps['clf']
        except (KeyError, AttributeError):
            print("HATA: Yüklenen model beklenen Pipeline yapısında değil ('tfidf' veya 'clf' adımı eksik/yanlış).")
            return "complaint", "error_model_structure", "error_model_structure", None

        prediction_numeric_main = model.predict([description])
        category = label_encoder.inverse_transform(prediction_numeric_main)[0]
        type_ = "complaint"
        sub_category = category

        proba_threshold = getattr(settings, 'SUB_CATEGORY_PROBA_THRESHOLD', 0.20)
        score_diff_threshold = getattr(settings, 'SUB_CATEGORY_SCORE_DIFF_THRESHOLD', 0.35)

        all_class_names = label_encoder.classes_
        num_classes = len(all_class_names)
        scores_or_probabilities = None

        transformed_text = tfidf_vectorizer.transform([description])

        has_predict_proba = hasattr(classifier, "predict_proba")
        has_decision_function = hasattr(classifier, "decision_function")

        if has_predict_proba:
            try:
                scores_or_probabilities = classifier.predict_proba(transformed_text)[0]
                using_proba = True
            except Exception as e:
                print(f"predict_proba çağrılırken hata: {e}. decision_function denenecek.")
                has_predict_proba = False
                using_proba = False
        
        if not has_predict_proba and has_decision_function:
            scores_or_probabilities = classifier.decision_function(transformed_text)[0]
            using_proba = False
        elif not has_predict_proba and not has_decision_function:
            print("Uyarı: Sınıflandırıcı skor/olasılık metodu desteklemiyor.")
            return type_, category, sub_category, None

        if scores_or_probabilities is not None:
            sorted_indices = np.argsort(scores_or_probabilities)[::-1]

            if num_classes > 1 and len(sorted_indices) > 1:
                best_score_index = sorted_indices[0]
                second_best_index = sorted_indices[1]
                
                # En iyi tahminin `category` ile aynı olduğunu teyit et
                # (predict() ve decision_function/predict_proba'nın en yüksek skoru aynı olmalı)
                best_category_from_scores = all_class_names[best_score_index]
                if best_category_from_scores != category:
                    print(f"Uyarı: predict() sonucu ({category}) ile en yüksek skorlu sınıf ({best_category_from_scores}) farklı")
                    # Bu durumda predict()'in sonucunu ana kategori olarak kabul etmeye devam edebiliriz
                    # veya skorlara göre olanı alabiliriz. Şimdilik predict()'i kullanacağız.

                second_best_category_name = all_class_names[second_best_index]

                if using_proba:
                    second_best_proba_value = scores_or_probabilities[second_best_index]
                    if second_best_category_name != category and second_best_proba_value >= proba_threshold:
                        sub_category = second_best_category_name
                        # print(f"  Proba sub_cat: {sub_category} (P={second_best_proba_value:.2f})")
                else:
                    best_score_value = scores_or_probabilities[best_score_index]
                    second_best_score_value = scores_or_probabilities[second_best_index]
                    
                    score_difference = best_score_value - second_best_score_value
                    
                    # Eğer ikinci en iyi kategori ana kategoriden farklıysa VE
                    # en iyi skor ile ikinci en iyi skor arasındaki fark, belirlenen eşikten küçükse
                    if second_best_category_name != category and score_difference < score_diff_threshold:
                        sub_category = second_best_category_name
                        # print(f"  Score sub_cat: {sub_category} (Skor Farkı={score_difference:.2f} < {score_diff_threshold})")
                        # print(f"    Best score ({category}): {best_score_value:.2f}, Second best ({second_best_category_name}): {second_best_score_value:.2f}")
        
        return type_, category, sub_category, scores_or_probabilities

    except Exception as e:
        import traceback
        print(f"Sınıflandırma sırasında genel hata: {e}")
        traceback.print_exc()
        return "complaint", "error_classification", "error_classification", None

@api_view(['POST'])
def submit_suggestion_or_complaint(request):
    description = request.data.get('description')
    is_trackable = request.data.get('isTrackable', False)
    email = request.data.get('email') if is_trackable else None

    if not description:
        return Response({"error": "Şikayet metni zorunludur."}, status=status.HTTP_400_BAD_REQUEST)

    if is_trackable and not email:
        return Response({"error": "Takip için e‑posta gereklidir."}, status=status.HTTP_400_BAD_REQUEST)

    # ML sınıflandırma
    type_, category, sub_category, raw_scores = classify_all(description)

    data = {
        "sender_id": 1,
        "type": type_,
        "category": category,
        "sub_category": sub_category,
        "description": description,
        "status": "new",
        "created_at": timezone.now(),
        "updated_at": timezone.now(),
        "isTrackable": is_trackable,
        "email": email,
        "response": "",
        "response_at": None
    }

    serializer = SuggestionOrComplaintSerializer(data=data)
    if serializer.is_valid():
        saved = serializer.save()

        if is_trackable and email:
            try:
                message = f"""
Şikayetiniz başarıyla alındı.

Takip Numarası: {saved.id}
Açıklama: {saved.description}

Bu şikayet takibini takip numaranız ile sistem üzerinden gerçekleştirebilirsiniz.
"""
                send_mail(
                    subject='Şikayetiniz Alındı – Takip Bilgisi',
                    message=message.strip(),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False
                )
            except Exception as e:
                print(f"E‑posta gönderilemedi: {e}")

        return Response({'message': 'Kayıt başarıyla eklendi.'}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
def track_complaint(request, complaint_id):
    try:
        complaint = SuggestionOrComplaint.objects.get(id=complaint_id)
        data = {
            "status": complaint.status,
            "created_at": complaint.created_at,
            "updated_at": complaint.updated_at,
            "isTrackable": complaint.isTrackable,
            "category": complaint.category,
            "sub_category": complaint.sub_category,
            "description": complaint.description
        }
        return Response(data, status=status.HTTP_200_OK)
    except SuggestionOrComplaint.DoesNotExist:
        return Response({"error": "Şikayet bulunamadı."}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def retrive_complaint_by_id(request, complaint_id):
    try:
        complaint = SuggestionOrComplaint.objects.get(id=complaint_id)
        serializer = SuggestionOrComplaintSerializer(complaint)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except SuggestionOrComplaint.DoesNotExist:
        return Response({"error": "Şikayet bulunamadı."}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def get_complaints(request):
    complaints = SuggestionOrComplaint.objects.all()

    type_param = request.GET.get('type')
    status_param = request.GET.get('status')
    category_param = request.GET.get('category')
    trackable_param = request.GET.get('isTrackable')

    if type_param:
        complaints = complaints.filter(type=type_param)
    if status_param:
        complaints = complaints.filter(status=status_param)
    if category_param:
        complaints = complaints.filter(category=category_param)
    if trackable_param:
        complaints = complaints.filter(isTrackable=trackable_param.lower() == 'true')

    serializer = SuggestionOrComplaintSerializer(complaints, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PUT'])
def update_complaint_status(request, complaint_id):
    new_status = request.data.get('status')

    if not new_status:
        return Response({"error": "Yeni durum belirtilmelidir."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        complaint = SuggestionOrComplaint.objects.get(id=complaint_id)
        complaint.status = new_status
        complaint.save()
        return Response({"message": "Durum güncellendi.", "new_status": complaint.status}, status=status.HTTP_200_OK)
    except SuggestionOrComplaint.DoesNotExist:
        return Response({"error": "Şikayet bulunamadı."}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
def delete_complaint(request, complaint_id):
    try:
        complaint = SuggestionOrComplaint.objects.get(id=complaint_id)
        complaint.delete()
        return Response({"message": "Kayıt silindi."}, status=status.HTTP_200_OK)
    except SuggestionOrComplaint.DoesNotExist:
        return Response({"error": "Şikayet veya öneri bulunamadı."}, status=status.HTTP_404_NOT_FOUND)


# İHTİYAÇ HALİNDE GÜNCELLENİCEK
@api_view(['GET'])
def get_complaint_statistics(request):
    range_param = request.GET.get('range')  # '7d', '1m', '3m', '6m'

    qs = SuggestionOrComplaint.objects.filter(type='complaint')

    if range_param:
        now = timezone.now()
        if range_param == '7d':
            qs = qs.filter(created_at__gte=now - timedelta(days=7))
        elif range_param == '1m':
            qs = qs.filter(created_at__gte=now - timedelta(days=30))
        elif range_param == '3m':
            qs = qs.filter(created_at__gte=now - timedelta(days=90))
        elif range_param == '6m':
            qs = qs.filter(created_at__gte=now - timedelta(days=180))

    stats = qs.values('category').annotate(count=Count('id')).order_by('-count')

    return Response(stats, status=200)


# İHTİYAÇ HALİNDE GÜNCELLENİCEK.
@api_view(['GET'])
def get_complaint_trends(request):
    category = request.GET.get('category')
    range_param = request.GET.get('range')

    qs = SuggestionOrComplaint.objects.filter(type='complaint')

    if category:
        qs = qs.filter(category=category)

    if range_param:
        now = timezone.now()
        if range_param == '7d':
            qs = qs.filter(created_at__gte=now - timedelta(days=7))
        elif range_param == '1m':
            qs = qs.filter(created_at__gte=now - timedelta(days=30))
        elif range_param == '3m':
            qs = qs.filter(created_at__gte=now - timedelta(days=90))
        elif range_param == '6m':
            qs = qs.filter(created_at__gte=now - timedelta(days=180))

    trend = qs.annotate(day=TruncDay('created_at')).values('day').annotate(count=Count('id')).order_by('day')
    return Response(trend, status=200)

# --- LLM Rapor Fonksiyonları ---

def _apply_llm_filters(queryset, filters):
    filter_mapping = {
        'category': 'category__iexact',
        'status': 'status__iexact',
        'type': 'type__iexact',
        'isTrackable': 'isTrackable',
    }
    q_objects = Q()
    for key, value in filters.items():
        if key == 'date_from':
            try: q_objects &= Q(created_at__date__gte=value)
            except ValueError: raise ValueError(f"Geçersiz tarih formatı (date_from): {value}. YYYY-MM-DD kullanın.")
        elif key == 'date_to':
            try:
                end_date = datetime.strptime(value, '%Y-%m-%d').date() + timedelta(days=1)
                q_objects &= Q(created_at__date__lt=end_date)
            except ValueError: raise ValueError(f"Geçersiz tarih formatı (date_to): {value}. YYYY-MM-DD kullanın.")
        elif key in filter_mapping:
            processed_value = str(value).lower() in ['true', '1', 't', 'y', 'yes'] if key == 'isTrackable' else value
            q_objects &= Q(**{filter_mapping[key]: processed_value})
    return queryset.filter(q_objects)

def _generate_llm_prompt(complaints_list, filters, report_type):
    filter_desc = ", ".join([f"{k}: {v}" for k, v in filters.items()]) if filters else "Tüm Şikayetler"
    prompt = f"""
Görev: Aşağıda belirtilen bina şikayetlerini analiz ederek **'{report_type}'** adında bir rapor hazırla.

Filtreler: {filter_desc}

Şikayet Listesi:
"""
    if not complaints_list:
        prompt += "- Bu filtrelerle eşleşen şikayet bulunmamaktadır.\n"
    else:
        for complaint in complaints_list:
            short_desc = complaint.description[:150] + ('...' if len(complaint.description) > 150 else '')
            prompt += f"- ID:{complaint.id}, Kategori: {complaint.category}, Durum: {complaint.status}, Tarih: {complaint.created_at.strftime('%Y-%m-%d')}, Açıklama: {short_desc}\n"

    prompt += f"""

📝 Aşağıdaki formatı kullanarak kısa ve öz bir rapor hazırla:

* **Genel Durum:** (Şikayetlerin genel özeti)
* **Öne Çıkan Temalar:** (Tekrarlayan problemler)
* **Öneriler (Varsa):** (Sorunların çözümüne yönelik net, uygulanabilir adımlar)

⚠️ Aşağıdakilerden KAÇIN:
- "Bina yönetimi adım atmalıdır", "gerekli işlemler yapılmalıdır" gibi belirsiz ve yuvarlak ifadeler kullanma.
- Öneri gibi görünse de aslında hiçbir şey söylemeyen cümleler kurma.
- "Sonuç", "Saygılar", "Özetle" gibi kapanış metinleri ekleme.

✅ OLACAK:
- Her öneri, gerçekten **ne yapılması gerektiğini** net olarak belirtmeli.
- "Ne yapılmalı?" sorusunun cevabını ver.
- Öneriler uygulanabilir, somut ve sade bir dille yazılmalı.
- Teknik detaya girme, ancak "kim/hangi ekip ne yapacak" açık olmalı (örneğin: "temizlik ekibi müdahale etmeli", "teknik servis bilgilendirilmeli").
- Her öneri bağımsız ve anlaşılır olmalı; belirsiz referanslardan ("sorun", "önceki madde") kaçın.
- Şikayetin tekrarını değil, doğrudan çözüm yolunu yaz.
- Gereksiz tekrar yapma; aynı öneriyi farklı cümlelerle sunma.
- İlgili birime yönlendirme yapılmalıysa, hangi ekip olduğu açıkça belirtilmeli.
- Gerekiyorsa öncelik/önem vurgusu yapılabilir (örn. "acil olarak değerlendirilmelidir").
- Öneri sayısı az da olsa kaliteli ve anlamlı olmalı.


Sadece yukarıdaki üç başlıkla sınırlı kal ve profesyonel bir dille yaz.
"""


    return prompt


def _call_groq_api(prompt):

    api_key = getattr(settings, 'GROQ_API_KEY', None)
    model_id = getattr(settings, 'LLM_MODEL_ID', "llama-3.1-8b-instant")
    if not api_key: return None, "Groq API anahtarı (GROQ_API_KEY) Django ayarlarında bulunamadı."
    try:
        client = Groq(api_key=api_key, timeout=30.0)
        print(f"Groq API'ye gönderiliyor (Model: {model_id})...")
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=model_id, temperature=0.6, max_tokens=500, stream=False,
        )
        print("Groq API'den yanıt alındı.")
        content = chat_completion.choices[0].message.content
        if not content or content.strip() == "": return None, "LLM API'den boş yanıt alındı."
        return content, None
    except Exception as e:
        error_message = f"Groq API çağrısı sırasında hata oluştu: {e}"
        print(error_message)
        return None, error_message
    
# LLM RAPOR OLUŞTURMA
@api_view(['POST'])
def generate_report(request):
    report_type = request.data.get('reportType', 'Genel Özet')
    filters = request.data.get('filters', {})

    # Şikayetleri Filtrele
    try:
        base_qs = SuggestionOrComplaint.objects.filter(type='complaint')
        filtered_complaints_qs = _apply_llm_filters(base_qs, filters)
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(f"Filtreleme sırasında beklenmedik hata: {e}")
        return Response({"error": "Şikayetler filtrelenirken bir hata oluştu."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # LLM'e gönderilecek şikayet sayısını sınırla (örn. son 10)
    try:
        max_complaints = int(filters.pop('maxComplaints', 10))
        if max_complaints < 1 or max_complaints > 1000:
            max_complaints = 10  # sınır dışıysa default'a dön
    except (ValueError, TypeError):
        max_complaints = 10

    complaints_for_llm = list(filtered_complaints_qs.order_by('-created_at')[:max_complaints])

    # LLM için Prompt Oluştur
    prompt = _generate_llm_prompt(complaints_for_llm, filters, report_type)

    # LLM API'sini Çağır
    report_content, error = _call_groq_api(prompt)

    if error:
        print(f"LLM Rapor Hatası: {error}")
        return Response({"error": "Yapay zeka raporu oluşturulurken bir hata oluştu."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    # DB'ye kaydet
    try:
        ReportRecommendation.objects.create(
            report_type=report_type,
            filters_applied=filters,
            content=report_content,
            created_at=now()
        )
    except Exception as e:
        print(f"Rapor veritabanına kaydedilemedi: {e}")

    # Başarılı Yanıtı Döndür
    return Response({
        "message": f"'{report_type}' raporu başarıyla oluşturuldu.",
        "report_content": report_content,
        "reportType": report_type,
        "filters_applied": filters,
        "complaints_analyzed_count": len(complaints_for_llm)
    }, status=status.HTTP_200_OK)

@api_view(['DELETE'])
def delete_report(request, report_id):
    try:
        report = ReportRecommendation.objects.get(id=report_id)
        report.delete()
        return Response({"message": f"ID {report_id} olan rapor başarıyla silindi."}, status=status.HTTP_200_OK)
    except ReportRecommendation.DoesNotExist:
        return Response({"error": f"ID {report_id} olan rapor bulunamadı."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": f"Silme işlemi sırasında hata oluştu: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_report_by_id(request, report_id):
    try:
        report = ReportRecommendation.objects.get(id=report_id)
        return Response({
            "id": report.id,
            "report_type": report.report_type,
            "filters_applied": report.filters_applied,
            "content": report.content,
            "created_at": report.created_at
        }, status=status.HTTP_200_OK)
    except ReportRecommendation.DoesNotExist:
        return Response({"error": f"ID {report_id} olan rapor bulunamadı."}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def list_all_reports(request):
    try:
        reports = ReportRecommendation.objects.all().order_by('-created_at')
        data = []
        for report in reports:
            data.append({
                "id": report.id,
                "report_type": report.report_type,
                "created_at": report.created_at.strftime("%Y-%m-%d %H:%M"),
            })
        return Response(data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": f"Raporlar listelenemedi: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
