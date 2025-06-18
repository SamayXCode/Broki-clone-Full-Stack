from django.db import models
from django.utils.text import slugify
import json

class OutletForm(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=50)
    email = models.EmailField()
    outlet_type = models.CharField(max_length=50)
    location = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)
    max_budget = models.BigIntegerField()
    min_size = models.IntegerField()
 
    def __str__(self):
        return f"{self.name} - {self.email}"

class Service(models.Model):
    title = models.CharField(max_length=200)
    photographer = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    per_item_price = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=100)
    image = models.ImageField(upload_to='services/')
    description = models.TextField()
    featured = models.BooleanField(default=False)
    is_onsite = models.BooleanField(default=True)
    photos_covered = models.IntegerField(default=0)  # "15 items covered"
    slug = models.SlugField(unique=True, blank=True)
    # any additional fields like props, add-ons, etc.

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

# from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)
    image = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.name

class City(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Property(models.Model):
    SALE_CHOICES = (
        (1, 'Sale'),
        (2, 'Lease'),
    )

    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='properties')
    price = models.BigIntegerField()
    price_format = models.CharField(max_length=100)
    address = models.TextField()
    status = models.BooleanField(default=True)
    premium_property = models.BooleanField(default=False)
    price_duration = models.CharField(max_length=100, null=True, blank=True)
    property_image = models.URLField()
    property_for = models.IntegerField(choices=SALE_CHOICES, default=1)
    advertisement_property = models.BooleanField(null=True, blank=True)
    advertisement_property_date = models.DateTimeField(null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='properties')
    sqft = models.IntegerField()

    def __str__(self):
        return self.name

# class Favorite(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     property = models.ForeignKey(Property, on_delete=models.CASCADE)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.user.username} - {self.property.name}"







# class Listing(models.Model):
#     title = models.CharField(max_length=255)
#     city = models.CharField(max_length=100)
#     state = models.CharField(max_length=100)
#     country = models.CharField(max_length=100, default='India')
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#     area_sqft = models.PositiveIntegerField()
#     property_type = models.CharField(max_length=100)
#     year_built = models.IntegerField()
#     monthly_sales = models.DecimalField(max_digits=10, decimal_places=2)
#     current_rental = models.DecimalField(max_digits=10, decimal_places=2)
#     age_of_property = models.CharField(max_length=100)
#     features = models.TextField(blank=True)
#     slug = models.SlugField(unique=True, blank=True)
#     location = models.CharField(max_length=100) 
#     thumbnail = models.ImageField(upload_to='listing_thumbs/')

#     def __str__(self):
#         return self.title

#     # Optional: helper to get features as list
#     def get_features(self):
#         try:
#             return json.loads(self.features)
#         except json.JSONDecodeError:
#             return []
    
#     def save(self, *args, **kwargs):
#         if not self.slug:
#             self.slug = slugify(self.title)
#         super().save(*args, **kwargs)

#     def get_lat_lng(self):
#         try:
#             lat, lng = self.location.split(",")
#             return float(lat.strip()), float(lng.strip())
#         except ValueError:
#             return None, None