from django.db import models

class Employee(models.Model):
    ROLE_CHOICES = [
        ('employee', 'Employee'),
        ('admin', 'Admin'),
    ]

    employee_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        db_table = 'employees'