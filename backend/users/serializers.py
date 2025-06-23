from rest_framework import serializers
from .models import User, UserProfile, SocialMediaAccount
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
import re

class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile model"""
    class Meta:
        model = UserProfile
        fields = ['id', 'phone_number', 'address', 'social_links', 'preferences', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_phone_number(self, value):
        """Validate phone number format"""
        if value:
            # Basic phone number validation (can be enhanced based on requirements)
            phone_pattern = re.compile(r'^\+?1?\d{9,15}$')
            if not phone_pattern.match(value):
                raise ValidationError("Please enter a valid phone number")
        return value

class SocialMediaAccountSerializer(serializers.ModelSerializer):
    """
    Serializer for the SocialMediaAccount model
    """
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = SocialMediaAccount
        fields = [
            'id', 'user', 'platform', 'username', 
            'api_key', 'api_secret', 'access_token', 'access_token_secret',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']

    def validate(self, data):
        """
        Ensure that the same user cannot link the same platform twice.
        """
        user = self.context['request'].user
        platform = data.get('platform')
        account_id = data.get('account_id')
        
        # Check for existing account with same platform and account_id
        existing = SocialMediaAccount.objects.filter(
            user=user, 
            platform=platform, 
            account_id=account_id
        )
        
        if self.instance:
            existing = existing.exclude(pk=self.instance.pk)
            
        if existing.exists():
            raise ValidationError(f"You already have a {platform} account with this ID")
        
        return data

class UserSerializer(serializers.ModelSerializer):
    """Main User serializer with nested profile and social accounts"""
    profile = UserProfileSerializer(read_only=True)
    social_accounts = SocialMediaAccountSerializer(many=True, read_only=True)
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'bio', 'profile_picture', 'profile', 'social_accounts',
            'date_joined', 'last_login', 'is_active'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']

    def get_full_name(self, obj):
        """Get user's full name"""
        if obj.first_name and obj.last_name:
            return f"{obj.first_name} {obj.last_name}"
        return obj.username

class UserDetailSerializer(UserSerializer):
    """Detailed user serializer for profile management"""
    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ['is_staff', 'is_superuser']

class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user information"""
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'bio', 'profile_picture']
        
    def validate_username(self, value):
        """Validate username uniqueness"""
        user = self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(username=value).exists():
            raise ValidationError("A user with this username already exists.")
        return value

class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'password', 'password_confirm')

    def validate_email(self, value):
        """Validate email uniqueness"""
        if User.objects.filter(email=value).exists():
            raise ValidationError("A user with this email already exists.")
        return value

    def validate_username(self, value):
        """Validate username format and uniqueness"""
        if User.objects.filter(username=value).exists():
            raise ValidationError("A user with this username already exists.")
        
        # Username validation
        if len(value) < 3:
            raise ValidationError("Username must be at least 3 characters long")
        
        if not re.match(r'^[a-zA-Z0-9_]+$', value):
            raise ValidationError("Username can only contain letters, numbers, and underscores")
        
        return value

    def validate(self, data):
        """Validate password confirmation"""
        if data['password'] != data['password_confirm']:
            raise ValidationError("Passwords don't match")
        return data

    def create(self, validated_data):
        """Create user and associated profile"""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(
            username=validated_data.get('username'),
            email=validated_data.get('email'),
            password=password,
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            bio=validated_data.get('bio', '')
        )
        
        # Create user profile
        UserProfile.objects.create(user=user)
        
        return user

class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for password change"""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)

    def validate_old_password(self, value):
        """Validate old password"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise ValidationError("Current password is incorrect")
        return value

    def validate(self, data):
        """Validate new password confirmation"""
        if data['new_password'] != data['new_password_confirm']:
            raise ValidationError("New passwords don't match")
        return data

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile"""
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'address', 'social_links', 'preferences']

    def validate_social_links(self, value):
        """Validate social links format"""
        if value:
            for platform, link in value.items():
                if not isinstance(link, str) or not link.startswith(('http://', 'https://')):
                    raise ValidationError(f"Invalid social link format for {platform}")
        return value 