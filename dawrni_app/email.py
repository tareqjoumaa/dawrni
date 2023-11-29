from django.core.mail import send_mail
import random
from django.conf import settings
from django.contrib.auth.models import User



def send_otp(email):
    subject = "Your Verification Code for Dawrni app Registration"
    code_name = random.randint(1000,8888)
    message = f"""Thank you for registering with Dawrni app.
    To complete your registration, please enter the following verification code:
    Verification Code: {code_name} 
    Welcome to Dawrni App """
    email_from = settings.EMAIL_HOST_USER
    send_mail(subject, message, email_from, [email])
    user_obj = User.objects.get(email=email)
    user_obj.first_name = str(code_name)
    user_obj.save()