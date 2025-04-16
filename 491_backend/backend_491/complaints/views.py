from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import SuggestionOrComplaint
from .serializers import SuggestionOrComplaintSerializer

@api_view(['POST'])
def submit_suggestion_or_complaint(request):
    serializer = SuggestionOrComplaintSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Kayıt başarıyla eklendi!'}, status=status.HTTP_201_CREATED)
    else:
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)