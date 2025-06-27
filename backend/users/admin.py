from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# Custom admin class to set ordering
class CustomUserAdmin(UserAdmin):
    ordering = ['id']
    # Optionally, customize list_display, search_fields, etc.

# Register the User model with custom admin
admin.site.register(User, CustomUserAdmin)
