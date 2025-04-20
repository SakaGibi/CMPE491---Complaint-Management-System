from django.db import models

class SupportMessage(models.Model):
    TYPE_CHOICES = [
        ('support', 'Support'),
        ('question', 'Question'),
    ]

    message_id = models.AutoField(primary_key=True)
    sender_id = models.IntegerField()
    message = models.TextField()
    email = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=[('new', 'New'), ('resolved', 'Resolved')])
    created_at = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='support')
    response = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'support_question_messages'