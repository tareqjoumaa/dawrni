from django.contrib import admin
from .models import Company, Client, Notification, Category, CompanyPhoto, custom_user, Favorite, Appointment

# Register your models here.
admin.site.register(Company)
admin.site.register(Client)
admin.site.register(Notification)
admin.site.register(Category)
admin.site.register(CompanyPhoto)
admin.site.register(custom_user)
admin.site.register(Favorite)
admin.site.register(Appointment)
