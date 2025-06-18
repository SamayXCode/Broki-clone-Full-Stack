from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.mail import send_mail
import random
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.core.cache import cache
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Service,Property, Category, City
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
import django_filters



from .serializers import (
    SendOTPSerializer,
    VerifyOTPSerializer,
    RegisterUserSerializer,
    OutletFormSerializer, 
    ServiceSerializer,
    PropertySerializer,
    CategorySerializer,
    CitySerializer,

)

OTP_EXPIRY_SECONDS = 300

User = get_user_model()

@api_view(['POST'])
def submit_form(request):
    serializer = OutletFormSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Data saved successfully!'})
    return Response(serializer.errors, status=400)

class RegisterUserView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterUserSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated = serializer.validated_data
        user = User.objects.create_user(
            username=validated['email'], 
            email=validated['email'],
            first_name=validated['first_name'],
            last_name=validated['last_name']
        )

        return Response({
            'detail': 'User registered successfully. Please verify OTP to login.',
        }, status=status.HTTP_201_CREATED)
 
class SendOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']

        if cache.get(f"otp_cooldown:{email}"):
            return Response({'detail': 'Please wait before requesting another OTP.'}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        otp = str(random.randint(100000, 999999))
        cache.set(f"otp:{email}", otp, timeout=OTP_EXPIRY_SECONDS)
        cache.set(f"otp_cooldown:{email}", True, timeout=60)

        try:
            send_mail(
                'Your OTP Code',
                f'Your OTP is {otp}. It expires in 5 minutes.',
                'trialofproject@gmail.com',
                [email],
                fail_silently=False,
            )
        except Exception as e:
            return Response({'detail': f'Failed to send OTP: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'detail': 'OTP sent to your email'}, status=status.HTTP_200_OK)

class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')

        if not email or not otp:
            return Response({'detail': 'Email and OTP required.'}, status=status.HTTP_400_BAD_REQUEST)

        cached_otp = cache.get(f"otp:{email}")
        if cached_otp != otp:
            return Response({'detail': 'Invalid or expired OTP.'}, status=status.HTTP_400_BAD_REQUEST)

        user, _ = User.objects.get_or_create(username=email, email=email)

        cache.delete(f"otp:{email}")

        refresh = RefreshToken.for_user(user)

        return Response({
            'detail': f'Logged in as {email}',
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'email': user.email,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
            }
        }, status=status.HTTP_200_OK)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Logged out successfully"}, status=200)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class AuthStatusView(APIView):
    authentication_classes = []  # Disable authentication for this view
    permission_classes = [AllowAny]  # Allow any user (authenticated or not) to access

    def get(self, request):
        user = request.user
        if user and user.is_authenticated:
            return Response({
                "is_authenticated": True,
                "email": user.email,
                "username": user.username
            })
        else:
            return Response({"is_authenticated": False})

#Servive page
class ServiceListAPIView(ListAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

class ServiceDetailAPIView(RetrieveAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    lookup_field = 'slug'

# ✅ Inline PropertyFilter (no extra file)
class PropertyFilter(FilterSet):
    city = django_filters.NumberFilter(field_name='city')
    category = django_filters.NumberFilter(field_name='category')
    price_min = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    sqft_min = django_filters.NumberFilter(field_name='sqft', lookup_expr='gte')
    sqft_max = django_filters.NumberFilter(field_name='sqft', lookup_expr='lte')
    property_for = django_filters.NumberFilter(field_name='property_for')
    listing_status = django_filters.NumberFilter(field_name='property_for')

    class Meta:
        model = Property
        fields = ['city', 'category', 'property_for', 'listing_status']


# ✅ API view with all filters + pagination
class PropertyListAPIView(ListAPIView):
    queryset = Property.objects.filter(status=True)
    serializer_class = PropertySerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PropertyFilter
    search_fields = ['name', 'address', 'city__name']
    ordering_fields = ['price', 'sqft', 'premium_property']
    ordering = ['-premium_property']



class PropertyBulkUploadView(APIView):
    def post(self, request):
        properties = request.data.get("property", [])
        saved = []
        errors = []

        for index, item in enumerate(properties):
            serializer = PropertySerializer(data=item)
            if serializer.is_valid():
                serializer.save()
                saved.append(serializer.data)
            else:
                errors.append({"index": index, "errors": serializer.errors})

        if errors:
            return Response({
                "message": "Some properties could not be uploaded.",
                "saved": saved,
                "errors": errors
            }, status=status.HTTP_207_MULTI_STATUS)  # 207 = partial success
        else:
            return Response({
                "message": "All properties uploaded successfully.",
                "data": saved
            }, status=status.HTTP_201_CREATED)

class CityListAPIView(ListAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer

class CategoryListAPIView(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer





