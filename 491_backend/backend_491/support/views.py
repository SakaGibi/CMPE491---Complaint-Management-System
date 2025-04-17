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


