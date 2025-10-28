from django.db import models

class Feedback(models.Model):
    user_type = models.CharField(max_length=50)
    category = models.CharField(max_length=50)
    description = models.TextField()
    location = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.category} - {self.status}"
