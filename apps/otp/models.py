from django.db import models

class FarmOTP(models.Model):
    """Model to store OTPs for various actions"""
    farmotp_email = models.EmailField(max_length=255)
    farmotp_value = models.CharField(max_length=10)
    farmotp_type = models.CharField(max_length=50)  # e.g., 'forgotPwd', 'bypassPwd'
    farmotp_usage = models.BooleanField(default=False)  # True = used, False = active
    farmotp_create_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.farmotp_type} - {self.farmotp_email}"

    class Meta:
        verbose_name = "Farm OTP"
        verbose_name_plural = "Farm OTPs"

