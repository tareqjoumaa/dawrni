from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext as _


class custom_user(User):
    TYPE_CHOICES = (
        ('company', 'Company'),
        ('user', 'User'),
    )
    full_name = models.CharField(max_length=255, null=True, blank=True)
    image = models.ImageField(upload_to='user_images/', null=True, blank=True)
    user_type = models.CharField(max_length=8, choices=TYPE_CHOICES, default='user')
    is_verified = models.BooleanField(null=True, blank=True, default=False)

    
class Category(models.Model):
    name = models.CharField(max_length=255)
    
    def __str__(self):
        return self.name


class Company(models.Model):
    user = models.ForeignKey(custom_user, on_delete=models.CASCADE)
    name_ar = models.CharField(max_length=255, verbose_name=_("Name (Arabic)"), null=True, blank=True)
    name_en = models.CharField(max_length=255, verbose_name=_("Name (English)"), null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name=_("Category"), null=True, blank=True)
    address_ar = models.TextField(verbose_name=_("Address (Arabic)"), null=True, blank=True)
    address_en = models.TextField(verbose_name=_("Address (English)"), null=True, blank=True)
    is_certified = models.BooleanField(default=False, verbose_name=_("Is Certified"))
    about_ar = models.TextField(verbose_name=_("About (Arabic)"), null=True, blank=True)
    about_en = models.TextField(verbose_name=_("About (English)"), null=True, blank=True)
    image = models.ImageField(upload_to='user_images/', null=True, blank=True)
    lat = models.FloatField(null=True, blank=True, verbose_name=_("Latitude"))
    lng = models.FloatField(null=True, blank=True, verbose_name=_("Longitude"))
    is_favorite = models.BooleanField(default=False, verbose_name=_("Is Favorite"))


    # def __str__(self):
    #     return self.name_en


class Client(models.Model):
    user = models.ForeignKey(custom_user, on_delete=models.CASCADE)
    name_en = models.CharField(max_length=255, null=True, blank=True)
    name_ar = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(max_length=255) 
    photo = models.ImageField(upload_to='client_photos/', null=True, blank=True)
    favorites = models.ManyToManyField(Company, through='Favorite', related_name='favorited_by')

    # def __str__(self):
    #     return self.name_en  

class Favorite(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('client', 'company')


class Appointment(models.Model):
    APPOINTMENT_STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('confirmed', _('Confirmed')),
        ('canceled', _('Canceled')),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    date = models.DateField(verbose_name=_("Appointment Date"))
    time = models.TimeField(verbose_name=_("Appointment Time"))
    status = models.CharField(max_length=20, choices=APPOINTMENT_STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Appointment #{self.id} - {self.client.name_en} with {self.company.name_en}"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)  
    body = models.TextField()
    
    def __str__(self):
        return self.name    


class CompanyPhoto(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='company_photos/')
