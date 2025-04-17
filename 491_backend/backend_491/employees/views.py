from django.utils import timezone
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


@api_view(['POST'])
def add_user(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email')
    role = request.data.get('role', 'employee')  # default: employee

    if not username or not password:
        return Response({"error": "Kullanıcı adı ve şifre zorunludur."}, status=400)

    if role not in ['employee', 'admin']:
        return Response({"error": "Geçersiz rol."}, status=400)

    if Employee.objects.filter(username=username).exists():
        return Response({"error": "Bu kullanıcı adı zaten var."}, status=400)

    Employee.objects.create(
        username=username,
        password=password,
        email=email,
        role=role,
        created_at=timezone.now(),
        updated_at=timezone.now()
    )

    return Response({"message": "Kullanıcı başarıyla eklendi."}, status=201)


@api_view(['DELETE'])
def delete_user(request):
    username = request.data.get('username')

    if not username:
        return Response({"error": "Kullanıcı adı zorunludur."}, status=400)

    try:
        user = Employee.objects.get(username=username)
        user.delete()
        return Response({"message": "Kullanıcı silindi."}, status=200)
    except Employee.DoesNotExist:
        return Response({"error": "Kullanıcı bulunamadı."}, status=404)


@api_view(['GET'])
def get_user_list(request):
    employees = Employee.objects.all().values('employee_id', 'username', 'email', 'role', 'created_at')
    return Response(list(employees), status=200)


@api_view(['PUT'])
def change_user_role(request):
    username = request.data.get('username')
    new_role = request.data.get('role')

    if not username or not new_role:
        return Response({"error": "Kullanıcı adı ve yeni rol zorunludur."}, status=400)

    if new_role not in ['employee', 'admin']:
        return Response({"error": "Geçersiz rol."}, status=400)

    try:
        user = Employee.objects.get(username=username)
        user.role = new_role
        user.updated_at = timezone.now()
        user.save()

        return Response({
            "message": f"Kullanıcının rolü '{new_role}' olarak güncellendi."
        }, status=200)

    except Employee.DoesNotExist:
        return Response({"error": "Kullanıcı bulunamadı."}, status=404)
