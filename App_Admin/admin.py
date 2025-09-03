from django.contrib import admin

# Register your models here.
from .models import Provider

# Admin_Superuser_Id: 123
# Admin_Superuser_pass: 123
# Admin_Superuser_email: 123@gmail.com

# @admin.register(Provider)
# class ProviderAdmin(admin.ModelAdmin):
#     list_display = ('name','email', 'unique_url')