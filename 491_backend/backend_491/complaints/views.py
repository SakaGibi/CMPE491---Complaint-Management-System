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