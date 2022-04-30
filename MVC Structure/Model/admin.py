from django.contrib import admin
from .models import User, Profile, Category, Doctor,Appointment, Order, BillingAddress
# Register your models here.

admin.site.register(User)
admin.site.register(Profile)
admin.site.register(Category)
admin.site.register(Doctor)
admin.site.register(Appointment)
admin.site.register(Order)
admin.site.register(BillingAddress)
