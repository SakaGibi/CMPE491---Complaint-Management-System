from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import SupportMessage
from .serializers import SupportMessageSerializer

@api_view(['POST'])
def submit_support_message(request):
    data = request.data.copy()

    if 'type' not in data:
        data['type'] = 'support'

    if 'status' not in data:
        data['status'] = 'new'

    serializer = SupportMessageSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Mesaj alındı.", "type": data['type']}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def answer_faq(request, message_id):
    try:
        message = SupportMessage.objects.get(message_id=message_id, type='question')
    except SupportMessage.DoesNotExist:
        return Response({"error": "SSS bulunamadı."}, status=404)

    response_text = request.data.get('response', '')
    if not response_text.strip():
        return Response({"error": "Cevap boş olamaz."}, status=400)

    message.response = response_text
    message.response_at = timezone.now()
    message.save()

    return Response({"message": "SSS cevabı eklendi."}, status=200)

@api_view(['GET'])
def get_faq(request):
    faqs = SupportMessage.objects.filter(type='question')
    serializer = SupportMessageSerializer(faqs, many=True)
    return Response(serializer.data, status=200)


@api_view(['DELETE'])
def delete_support_message(request, message_id):
    try:
        message = SupportMessage.objects.get(message_id=message_id)
        message.delete()
        return Response({"message": "Mesaj silindi."}, status=200)
    except SupportMessage.DoesNotExist:
        return Response({"error": "Mesaj bulunamadı."}, status=404)


