from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import SuggestionOrComplaint
from .serializers import SuggestionOrComplaintSerializer


def classify_all(description): #PLACEHOLDER FOR ML ALGORITHM. CHANGE WHEN READY
    desc = description.lower()
    if "öneri" in desc or "olsun" in desc or "eklenebilir" in desc:
        return "suggestion", "app", "features"
    elif "geç" in desc or "kargo" in desc:
        return "complaint", "delivery", "late"
    elif "bozuk" in desc or "çalışmıyor" in desc:
        return "complaint", "product", "defective"
    elif "donuyor" in desc:
        return "complaint", "app", "performance"
    else:
        return "complaint", "general", "unspecified"

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
        "sender_id": 1,  # sabit, login ile dinamik hale getirilebilir
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

