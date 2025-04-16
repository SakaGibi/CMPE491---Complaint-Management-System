from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import SuggestionOrComplaint
from .serializers import SuggestionOrComplaintSerializer


@api_view(['POST'])
def submit_suggestion_or_complaint(request):
    serializer = SuggestionOrComplaintSerializer(data=request.data)
    if serializer.is_valid():
        is_trackable = serializer.validated_data.get('isTrackable')
        email = serializer.validated_data.get('email')

        if is_trackable and not email:
            return Response({"error": "Takip etmek için e‑posta girilmelidir."}, status=status.HTTP_400_BAD_REQUEST)

        complaint = serializer.save()

        return Response({'message': 'Kayıt başarıyla eklendi!'}, status=status.HTTP_201_CREATED)
    else:
        print(serializer.errors)
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
