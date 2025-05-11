from django.db import models


class SuggestionOrComplaint(models.Model):
    SENDER_TYPE = [
        ('complaint', 'Complaint'),
        ('suggestion', 'Suggestion')
    ]

    STATUS_TYPE = [
        ('new', 'New'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed')
    ]

    sender_id = models.IntegerField()
    type = models.CharField(max_length=20, choices=SENDER_TYPE)
    category = models.CharField(max_length=255)
    sub_category = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_TYPE)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    isTrackable = models.BooleanField()
    email = models.CharField(max_length=255, null=True, blank=True)
    response = models.TextField(null=True, blank=True)
    response_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'complaints_suggestions'


class ReportRecommendation(models.Model):
    report_type = models.CharField(max_length=100)
    filters_applied = models.JSONField()
    content = models.TextField()
    created_at = models.DateTimeField()

    class Meta:
        db_table = 'report_recommendation'
        managed = False
