from datetime import timedelta
from django.db.models import Count
from django.db.models.functions import TruncDay
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import SuggestionOrComplaint
from .serializers import SuggestionOrComplaintSerializer


import joblib
import os
from django.conf import settings

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


# LLM RAPOR OLUŞTURMA İÇİN PLACEHOLDER
@api_view(['POST'])
def generate_report(request):
    report_type = request.data.get('reportType')
    filters = request.data.get('filters', {})

    return Response({
        "message": "Bu endpoint gelecekte yapay zeka destekli bir rapor oluşturacaktır.",
        "reportType": report_type,
        "filters": filters
    }, status=200)