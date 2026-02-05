from django.db import models

class PermitRequest(models.Model):
    full_name = models.CharField(max_length=100)
    id_number = models.CharField(max_length=20)
    phone = models.CharField(max_length=20)
    subcounty = models.CharField(max_length=50)
    ward = models.CharField(max_length=50)
    location = models.CharField(max_length=100)
    purpose = models.TextField()
    source = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.full_name} - {'Approved' if self.approved else 'Pending'}"

class ClientMessage(models.Model):
    client_name = models.CharField(max_length=100, blank=True)
    client_email = models.EmailField()
    client_message = models.TextField()
    filled_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.client_email