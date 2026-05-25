import random
from django.core.mail import send_mail


def generate_otp():
    return str(random.randint(100000, 999999))


def send_otp_email(email, otp):
    send_mail(
        subject='Your OTP Verification Code',
        message=f'Your OTP is: {otp}\nValid for 10 minutes.',
        from_email='noreply@aiengr.io',
        recipient_list=[email],
        fail_silently=False,
    )