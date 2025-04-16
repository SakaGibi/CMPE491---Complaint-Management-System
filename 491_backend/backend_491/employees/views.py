from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Employee
from .serializers import EmployeeLoginSerializer

@api_view(['POST'])
def employee_login(request):
    serializer = EmployeeLoginSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        try:
            employee = Employee.objects.get(username=username, password=password)
            return Response({
                "message": "Giriş başarılı.",
                "employee_id": employee.employee_id,
                "role": employee.role
            }, status=status.HTTP_200_OK)
        except Employee.DoesNotExist:
            return Response({"error": "Kullanıcı adı veya şifre hatalı."}, status=status.HTTP_401_UNAUTHORIZED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
