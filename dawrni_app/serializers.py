from django.contrib.auth.models import User
from rest_framework import serializers, validators
from django.core.validators import MinLengthValidator
from django.utils.translation import gettext as _
from .models import Category, Company, Client, Notification, CompanyPhoto, custom_user, Favorite, Appointment

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = custom_user
        fields = ('id', 'email','user_type', 'is_verified')

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class CompanyPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyPhoto
        fields = '__all__'


class CompanyProfileSerializer(serializers.ModelSerializer):
    photos = CompanyPhotoSerializer(many=True, read_only=True)
    class Meta:
        model = Company
        fields = '__all__'
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        photos_data = representation.pop('photos', None)
        representation['photos'] = photos_data
        return representation

class ClientProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        exclude = ('favorites',)  # Exclude the user field from serialization


class ClientSerializer(serializers.ModelSerializer):
    favorites = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = '__all__'
        read_only_fields = ('user', 'email')

    def to_representation(self, obj):
        request = self.context.get('request')
        language = request.META.get('HTTP_ACCEPT_LANGUAGE', 'en')

        if language == 'ar':
            name = obj.name_ar
        else: 
            name = obj.name_en
        return {
            'id': obj.id,
            'name': name,
            'email': obj.email,
            'photo': obj.photo.url,
            }
    
    def update(self, instance, validated_data):
        instance.name_en = validated_data.get('name_en', instance.name_en)
        instance.name_ar = validated_data.get('name_ar', instance.name_ar)
        image_file = validated_data.get('photo', None)
        if image_file:
            instance.photo = image_file
        instance.save()
        ClientSerializer(instance)
        return instance
    
    def get_favorites(self, obj):
        favorites = Favorite.objects.filter(client=obj)
        return [fav.company.id for fav in favorites]


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = custom_user
        fields = ("password", "email", "full_name", "image", "user_type", "is_verified")
        extra_kwargs = {
            "email": {
                "required": True,
                "allow_blank": False,
                "validators": [
                    validators.UniqueValidator(
                        custom_user.objects.all(), _("A user with that Email already exists.")
                    )
                ],
            },
        }

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError(_("Password must be at least 8 characters long."))
        return value    

    def create(self, validated_data):
        user_type = validated_data.get("user_type")
        user = custom_user.objects.create_user(
            username=validated_data["email"],
            email=validated_data["email"],
            password=validated_data["password"],
            user_type=validated_data["user_type"],
        )
        if user_type == "company" :
            Company.objects.create(
                user=user,
                )
        elif user_type == "user" :
            Client.objects.create(
                user=user,
                email=validated_data["email"],
                )
        return user
    

class CompanySerializer(serializers.ModelSerializer):
    photos = CompanyPhotoSerializer(many=True, read_only=True)
    category = serializers.IntegerField(required=False)  # Change to IntegerField for category ID
    image = serializers.ImageField(use_url=True, allow_null=True, required=False)

    class Meta:
        model = Company
        exclude = ('user',)  # Exclude the user field from serialization

    def to_representation(self, obj):
        request = self.context.get('request')
        language = request.META.get('HTTP_ACCEPT_LANGUAGE', 'en')
        
        # for the localization 
        if language == 'ar':
            name = obj.name_ar
            address = obj.address_ar
            about = obj.about_ar
        else:
            name = obj.name_en
            address = obj.address_en
            about = obj.about_en
        category_id = obj.category.id if obj.category else None
        image_url = request.build_absolute_uri(obj.image.url) if obj.image else None
        # photos_data = [photo['image'] for photo in CompanyPhotoSerializer(obj.photos.all(), many=True).data] just get the images without id
        
        return {
            'id': obj.id,
            'category': category_id,
            'name': name,
            'address': address,
            'about': about,
            'is_certified': obj.is_certified,
            'user': obj.user.username,
            'image': image_url,
            'photos': CompanyPhotoSerializer(obj.photos.all(), many=True).data,
            'lat': obj.lat,
            'lng': obj.lng,
        }
    
    def update(self, instance, validated_data):
        # Update only the category if present in the validated data
        category_id = validated_data.pop('category', None)
        if category_id is not None:
            category_instance = Category.objects.get(pk=category_id)
            instance.category = category_instance

        # Update other fields if present in the validated data
        instance.name_en = validated_data.get('name_en', instance.name_en)
        instance.address_en = validated_data.get('address_en', instance.address_en)
        instance.about_en = validated_data.get('about_en', instance.about_en)
        instance.name_ar = validated_data.get('name_ar', instance.name_ar)
        instance.address_ar = validated_data.get('address_ar', instance.address_ar)
        instance.about_ar = validated_data.get('about_ar', instance.about_ar)
        instance.is_certified = validated_data.get('is_certified', instance.is_certified)
        instance.lat = validated_data.get('lat', instance.lat)
        instance.lng = validated_data.get('lng', instance.lng)
        image_file = validated_data.get('image', None)
        if image_file:
            instance.image = image_file
        instance.save()
        CompanySerializer(instance)
        return instance
        

class AppointmentSerializer(serializers.ModelSerializer):
    company = CompanySerializer()
    client = ClientSerializer()  # Adjust with your actual ClientSerializer

    class Meta:
        model = Appointment
        fields = ['id', 'client', 'company', 'date', 'time', 'status']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        company_data = representation['company']
        client_data = representation['client']

        representation['company'] = {
            'id': company_data['id'],
            'name': company_data['name'],
            'category_id': company_data['category'],
            'image': company_data['image'],
            'address': company_data['address'],
            'about': company_data['about'],
            'is_certified': company_data['is_certified'],
            'lat': company_data['lat'],
            'lng': company_data['lng'],
        }
        representation['client'] = {
            'id': client_data['id'],
            'name': client_data['name'],
            'email': client_data['email'],
            'photo': client_data['photo'],
        }
        return representation

class FavoriteSerializer(serializers.ModelSerializer):
    company = CompanySerializer()
    photos = CompanyPhotoSerializer(many=True, read_only=True)

    class Meta:
        model = Favorite
        exclude = ['id', 'client']
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        company_data = representation['company']
        
        return {
            'id': company_data['id'],
            'name': company_data['name'],
            'category_id': company_data['category'],
            'image': company_data['image'],
            'address': company_data['address'],
            'about': company_data['about'],
            'is_certified': company_data['is_certified'],
            'lat': company_data['lat'],
            'lng': company_data['lng'],
            'photos': company_data['photos'],
            }


class VerifyAccountSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code_name = serializers.CharField() 