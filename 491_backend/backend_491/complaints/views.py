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


import joblib
import os
from django.conf import settings

from groq import Groq
import json

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
        return "complaint", "general", "unspecified_model_error"

    try:
        prediction_numeric = model.predict([description])
        predicted_category_name = label_encoder.inverse_transform(prediction_numeric)

        type_ = "complaint"
        category = predicted_category_name[0]
        sub_category = category

        return type_, category, sub_category

    except Exception as e:
        print(f"Sınıflandırma sırasında hata: {e}")
        return "complaint", "general", "unspecified_prediction_error"

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
    type_, category, sub_category = classify_all(description)

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
        serializer.save()
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
