from rest_framework.decorators import api_view
from rest_framework import viewsets, filters
from rest_framework.response import Response
from knox.auth import AuthToken, TokenAuthentication
from .serializers import *
from .email import *
from .models import Company, custom_user, Category
from rest_framework import status
from django.utils.translation import gettext as _
from rest_framework import exceptions
from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework.pagination import LimitOffsetPagination
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import parser_classes
from django.shortcuts import render, redirect


class AuthTokenSerializer(serializers.Serializer):
    email = serializers.CharField(
        label=_("Email"),
        write_only=True
    )
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )
    token = serializers.CharField(
        label=_("Token"),
        read_only=True
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'),
                                username=email, password=password)

            # The authenticate call simply returns None for is_active=False
            # users. (Assuming the default ModelBackend authentication
            # backend.)
            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "username" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs

@api_view(['GET'])
def profile(request):
    user = request.user
    if user.is_authenticated:
        try:
            company = Company.objects.get(user=user)
            serializer = CompanyProfileSerializer(company, context={'request': request})
            return Response(serializer.data)
        except Company.DoesNotExist:
            pass
        try:
            client = Client.objects.get(user=user)
            serializer = ClientProfileSerializer(client, context={'request': request})
            return Response(serializer.data)
        except Client.DoesNotExist:
            return Response({"error": "User is neither a company nor a client"}, status=400)
    else:
        return Response({"error": "User is not authenticated"}, status=401)
    

@api_view(['POST','DELETE'])
@parser_classes([MultiPartParser, FormParser])
def Companyphotos(request, photo_id=None):
    user = request.user
    if user.is_authenticated:
        try:
            company = Company.objects.get(user=user)
        except Company.DoesNotExist:
            return Response({"error": "User is not associated with any company"}, status=400)

        if request.method == 'POST':
            data = request.data.copy()
            data['company'] = company.id 

            serializer = CompanyPhotoSerializer(data=data)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=201)
            return Response(serializer.errors, status=400)

        elif request.method == 'DELETE':
            if photo_id is not None:
                try:
                    # Ensure the photo belongs to the user's company
                    photo = CompanyPhoto.objects.get(id=photo_id, company=company)
                    photo.delete()
                    return Response({"message": "Photo deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
                except CompanyPhoto.DoesNotExist:
                    return Response({"error": "Photo not found or does not belong to the user's company"}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({"error": "Missing photo_id for DELETE request"}, status=status.HTTP_400_BAD_REQUEST)

    return Response({"error": "Invalid HTTP method"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        user = self.request.user
        client = Client.objects.get(user=user)
        return Appointment.objects.filter(client=client)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["status", ]


class AppointmentCompanyViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        user = self.request.user
        company = Company.objects.get(user=user)
        return Appointment.objects.filter(company=company)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["status", ]


@api_view(['POST'])
def change_appointment_status(request, appointment_id=None):
    try:
        user = request.user
        company = Company.objects.get(user=user)    
        if request.method == 'POST':
            try:
                appointment = Appointment.objects.get(id=appointment_id, company=company)
            except Appointment.DoesNotExist:
                return Response({'error': 'Appointment not found for the company'}, status=status.HTTP_404_NOT_FOUND)

            new_status = request.data.get('status')
            if new_status in ['pending', 'confirmed', 'canceled']:
                appointment.status = new_status
                appointment.save()
                serializer = AppointmentSerializer(appointment, context={'request': request})
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid appointment status'}, status=status.HTTP_400_BAD_REQUEST)
    
    except Client.DoesNotExist:
        return Response({'error': 'Client not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST', 'DELETE'])
def book_an_appointment(request, company_id=None, appointment_id=None):
    try:
        user = request.user
        client = Client.objects.get(user=user)    

        if request.method == 'POST':
            try:
                company = Company.objects.get(pk=company_id)
            except Company.DoesNotExist:
                return Response({'error': 'Company not found'}, status=status.HTTP_404_NOT_FOUND)
            appointment_data = {
                'client': client,
                'company': company,
                'date': request.data.get('date'), 
                'time': request.data.get('time'),  
            }
            appointment = Appointment.objects.create(**appointment_data)
            serializer = AppointmentSerializer(appointment, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            try:
                appointment = Appointment.objects.get(id=appointment_id, client=client)
                appointment.delete()
                return Response({'message': 'Appointment deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
            except Appointment.DoesNotExist:
                return Response({'error': 'Appointment not found'}, status=status.HTTP_404_NOT_FOUND)

    except Client.DoesNotExist:
        return Response({'error': 'Client not found'}, status=status.HTTP_404_NOT_FOUND)
    

class ClientViewSet(viewsets.ModelViewSet):
    serializer_class = ClientSerializer
    queryset = Client.objects.all() 
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name_ar", "name_en"]


class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        user = self.request.user
        client = Client.objects.get(user=user)
        return Favorite.objects.filter(client=client)


@api_view(['GET', 'POST', 'DELETE'])
def favorite_company(request, company_id=None):
    try:
        user = request.user
        client = Client.objects.get(user=user) 
        if request.method == 'GET':
            try:
                favorites = Favorite.objects.filter(client=client)
                serializer = FavoriteSerializer(favorites,  context={'request': request}, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Client.DoesNotExist:
                return Response({'error': 'Client not found'}, status=status.HTTP_404_NOT_FOUND)
   
        if request.method == 'DELETE':
            try:
                company = Company.objects.get(pk=company_id)
            except Company.DoesNotExist:
                return Response({'error': 'Company not found'}, status=status.HTTP_404_NOT_FOUND)
            Favorite.objects.filter(client=client, company=company).delete()
            company.is_favorite = False
            company.save()
            
            return Response({'message': 'Company removed from favorites'}, status=status.HTTP_204_NO_CONTENT)
        
        elif request.method == 'POST':
            try:
                company = Company.objects.get(pk=company_id)
            except Company.DoesNotExist:
                return Response({'error': 'Company not found'}, status=status.HTTP_404_NOT_FOUND)
            favorite, created = Favorite.objects.get_or_create(client=client, company=company)
            
            # Set is_favorite to True when adding to favorites
            if created:
                company.is_favorite = True
                company.save()

            serializer = FavoriteSerializer(favorite, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


    except Client.DoesNotExist:
        return Response({'error': 'Client not found'}, status=status.HTTP_404_NOT_FOUND)
    


@api_view(['PUT'])
@parser_classes([MultiPartParser, FormParser])    
def add_client_image(request):
    try:
        user = request.user
        if user.is_authenticated:
            client = Client.objects.get(user=user)
        else:
            return Response({'message':_("this client doesn't exiest")}, status=401)    
    except Client.DoesNotExist:
        return Response({'error': 'Client not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = ClientSerializer(client, data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@parser_classes([MultiPartParser, FormParser])    
def Companyprofile(request):
    try:
        user = request.user
        if user.is_authenticated:
            company = Company.objects.get(user=user)
        else:
            return Response({'message':_("this company doesn't exiest")}, status=401)    
    except Company.DoesNotExist:
        return Response({'error': 'Company not found'}, status=status.HTTP_404_NOT_FOUND)
   
    # Delete the main image
    company.image.delete()

    # Optionally, update the company serializer to exclude the deleted main image from the response
    serializer = CompanySerializer(company, context={'request': request})
    return Response(serializer.data)


@api_view(['PUT'])
@parser_classes([MultiPartParser, FormParser])
def update_company(request):
    try:
        user = request.user
        if user.is_authenticated:
            company = Company.objects.get(user=user)
        else:
            return Response({'message':_("this company doesn't exiest")}, status=401)    
    except Company.DoesNotExist:
        return Response({'error': 'Company not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = CompanySerializer(company, data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

 
class CompanyViewSet(viewsets.ModelViewSet):
    serializer_class = CompanySerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return Company.objects.filter(
            name_en__isnull=False,
            category__isnull=False,
            address_en__gt='',
            about_en__gt='',
        )

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset)

        search_query = self.request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(
                Q(name_ar__icontains=search_query) |
                Q(name_en__icontains=search_query)
            )

        # Apply pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.serializer_class(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = self.serializer_class(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["category", ]
    search_fields = ["name_ar", "name_en",]


def serialize_user(user):
    return {
        "email": user.email,
        "user_type": user.user_type
    }


@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password: 
        return Response({'message': _('Please provide both email and password.')})
    serializer = AuthTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data['user']
    s, token = AuthToken.objects.create(user)
    c_user = custom_user.objects.get(email=user.email)
    user_serializer = CustomUserSerializer(c_user)

    return Response({
        "user": user_serializer.data,
        'token': token
    })
        

@api_view(['POST'])
def register(request):
    password = request.data.get('password')
    email = request.data.get('email')
    user_type = request.data.get('user_type')

    if not user_type or not password or not email :
        return Response({'message': _('Please provide your email, and password and type')})

    serializer = RegisterSerializer(data=request.data)

    if serializer.is_valid(raise_exception=True):
        user = serializer.save()
        send_otp(serializer.data['email'])
        s, token = AuthToken.objects.create(user)

        return Response({   
            "user_info": serialize_user(user),
            "token": token,
        })


@api_view(['GET'])
def get_user(request):
    try:
        user = request.user
        if user.is_authenticated:
            c_user = custom_user.objects.get(email=user.email)
            company = Company.objects.filter(user=user).first()
            client = Client.objects.filter(user=user).first()

            if company:
                image_url = str(company.image)
            elif client:
                image_url = str(client.photo)
            else:
                image_url = None

            return Response({
                "id": c_user.id,
                "email": c_user.email,
                "image": image_url,
                "user_type": c_user.user_type,
                "is_verified": c_user.is_verified,
                'status': 200,
            })
        else:
            return Response({'message':_('this user is not authenticated')}, status=401)
    except exceptions.AuthenticationFailed as e:
        return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def verify(request):
    email = request.data.get('email')
    code_name = request.data.get('code_name')

    if not email or not code_name:
        return Response({'message': _('Please provide both email and code.')})
    try:
        data = request.data
        serializer = VerifyAccountSerializer(data = data)
        if serializer.is_valid():
            email = serializer.data['email']
            code_name = serializer.data['code_name']

            user = User.objects.filter(email=email)
            if not user.exists():
                return Response({
                    'message': _('User with this email does not exist.'),
                },status=404)
            
            if user[0].first_name != code_name:
                return Response({
                    'message': _('Invalid verification code.'),
                },status=400)
            user = user.first() 
            user.save()
            user_obj = custom_user.objects.get(email=email)
            user_obj.is_verified = True
            user_obj.save()
            return Response({
                'message': _('Verification successful.'),
                'is_verified' : True,
                'status': 200,
            })

    except:
        return Response({
            'message': _('An error occurred.'),
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)   
    

def privacy_policy(request):
    return render(request, 'privacy_policy.html')

