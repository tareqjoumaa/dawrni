from django.urls import path, include
from knox import views as knox_views
from . import views
from rest_framework.routers import DefaultRouter
from .views import CompanyViewSet , ClientViewSet, FavoriteViewSet, AppointmentViewSet, AppointmentCompanyViewSet


router = DefaultRouter()
router.register(r'companies', CompanyViewSet, basename='company')
router.register(r'clients', ClientViewSet, basename='client')
router.register(r'favorite_list', FavoriteViewSet, basename='favorite_list')
router.register(r'client_appointments', AppointmentViewSet, basename='clien_app')
router.register(r'company_appointments', AppointmentCompanyViewSet, basename='company_app')


urlpatterns = [
    path('user/', views.get_user),
    path('login/', views.login),
    path('register/', views.register),
    path('verify/', views.verify),
    path('logout/', knox_views.LogoutView.as_view(), name='knox_logout'),
   
    path('update_company/', views.update_company),
    path('company_photos/', views.Companyphotos),
    path('company_photos/<int:photo_id>', views.Companyphotos),
    path('client_image/', views.add_client_image),
    
    path('favorite/<int:company_id>', views.favorite_company),
    
    path('company_profile/', views.Companyprofile),

    path('book_appointment/<int:company_id>', views.book_an_appointment),
    path('delete_appointment/<int:appointment_id>', views.book_an_appointment),
    path('status_appointment/<int:appointment_id>', views.change_appointment_status),
    
    path('', include(router.urls)),
]
