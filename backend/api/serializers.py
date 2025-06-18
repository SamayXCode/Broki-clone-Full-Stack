from rest_framework import serializers
from .models import OutletForm, Service, Property, Category, City #Favorite
from django.contrib.auth import get_user_model
import re

User = get_user_model()

def camel_to_snake(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

class OutletFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = OutletForm
        fields = '__all__'

class SendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email__iexact=value.strip()).exists():
            raise serializers.ValidationError("Email not registered. Please register first.")
        return value.strip()

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(min_length=6, max_length=6)

class RegisterUserSerializer(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()

    def to_internal_value(self, data):
        new_data = {}
        for key, value in data.items():
            new_key = camel_to_snake(key)
            new_data[new_key] = value
        return super().to_internal_value(new_data)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered.")
        return value

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'image']

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name']

class PropertySerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    city = CitySerializer()

    class Meta:
        model = Property
        fields = [
            'id',                      # ❗ Extra field not in your model
            'name',
            'category',
            'price',
            'price_format',
            'address',
            'status',
            'premium_property',
            'price_duration',
            'property_image',
            'property_for',
            'advertisement_property',
            'advertisement_property_date',
            'city',
            'sqft',
            ]









