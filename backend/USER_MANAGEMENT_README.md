# User Management APIs - Implementation Guide

## 🎯 Overview

This document provides a comprehensive guide to the User Management APIs implementation in the Client-Nest platform. The APIs provide complete CRUD operations for user management, profile management, and social media account linking.

## 🏗️ Architecture

### Models
- **User**: Custom user model extending Django's AbstractUser
- **UserProfile**: Extended profile information for users
- **SocialMediaAccount**: Social media platform account linking

### Key Features
- ✅ JWT Authentication with SimpleJWT
- ✅ Custom User Model with email as username
- ✅ Comprehensive validation and security
- ✅ Rate limiting and throttling
- ✅ Search, filter, and pagination
- ✅ File upload support for profile pictures
- ✅ Social media account management
- ✅ Admin-only endpoints for user management

## 📁 File Structure

```
backend/
├── users/
│   ├── models.py              # User, UserProfile, SocialMediaAccount models
│   ├── serializers.py         # All serializers for user management
│   ├── views.py               # ViewSets and API endpoints
│   ├── urls.py                # URL routing for users app
│   ├── utils.py               # Utility functions (email sending, etc.)
│   └── tests.py               # Unit tests
├── config/
│   ├── settings.py            # Django settings with API configuration
│   └── urls.py                # Main URL configuration
├── requirements.txt           # Dependencies including django-filter
├── API_DOCUMENTATION.md       # Comprehensive API documentation
├── test_api.py               # API testing script
└── USER_MANAGEMENT_README.md  # This file
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Setup
Copy the environment example and configure your settings:
```bash
cp env.example .env
# Edit .env with your database and email settings
```

### 3. Database Setup
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Create Superuser
```bash
python manage.py createsuperuser
```

### 5. Run Development Server
```bash
python manage.py runserver
```

### 6. Test APIs
```bash
python test_api.py
```

## 📋 API Endpoints Summary

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/token/` - JWT token authentication
- `POST /api/auth/token/refresh/` - Token refresh

### User Management
- `GET /api/users/users/me/` - Get current user profile
- `PUT/PATCH /api/users/users/update_profile/` - Update user profile
- `POST /api/users/users/change_password/` - Change password
- `POST /api/users/users/deactivate_account/` - Deactivate account

### Profile Management
- `GET /api/users/profiles/my_profile/` - Get user profile details
- `PUT/PATCH /api/users/profiles/update_my_profile/` - Update profile details

### Social Media Accounts
- `GET /api/users/social-accounts/my_accounts/` - Get linked accounts
- `GET /api/users/social-accounts/platforms/` - Get available platforms
- `POST /api/users/social-accounts/` - Link new account
- `PUT/PATCH /api/users/social-accounts/{id}/` - Update account
- `DELETE /api/users/social-accounts/{id}/` - Unlink account

### Admin Endpoints
- `GET /api/users/users/` - List all users (admin only)
- `GET /api/users/users/{id}/` - Get user details (admin only)

## 🔧 Configuration

### Django Settings
The following settings are configured in `config/settings.py`:

```python
# Custom user model
AUTH_USER_MODEL = 'users.User'

# REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
    },
}

# JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
}
```

## 🔒 Security Features

### Authentication & Authorization
- JWT-based authentication with configurable token lifetimes
- Custom permission classes for object-level access control
- Rate limiting to prevent abuse
- Password validation with strong requirements

### Data Protection
- Input validation and sanitization
- Secure password hashing
- Access token protection (write-only fields)
- User data isolation (users can only access their own data)

### Rate Limiting
- Registration: 3 requests per hour per IP
- General API: 100 requests per hour per user
- Admin endpoints: 1000 requests per hour per user

## 📊 Data Models

### User Model
```python
class User(AbstractUser):
    email = models.EmailField(unique=True)
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
```

### UserProfile Model
```python
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    social_links = models.JSONField(default=dict, blank=True)
    preferences = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### SocialMediaAccount Model
```python
class SocialMediaAccount(models.Model):
    PLATFORM_CHOICES = (
        ('facebook', 'Facebook'),
        ('twitter', 'Twitter'),
        ('instagram', 'Instagram'),
        ('linkedin', 'LinkedIn'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='social_accounts')
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    account_id = models.CharField(max_length=100)
    access_token = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

## 🧪 Testing

### Automated Testing
Run the test suite:
```bash
python manage.py test users
```

### Manual Testing
Use the provided test script:
```bash
python test_api.py
```

### API Testing Tools
- **Postman**: Import the API collection
- **cURL**: Use the examples in the documentation
- **Django REST Framework Browsable API**: Visit `/api/` in your browser

## 📈 Performance Considerations

### Database Optimization
- Indexed fields for search and filtering
- Efficient query patterns with select_related and prefetch_related
- Pagination to limit result sets

### Caching Strategy
- Redis cache configuration for session storage
- Query result caching for frequently accessed data
- JWT token caching

### Rate Limiting
- Prevents API abuse
- Configurable limits per user and IP
- Graceful degradation under load

## 🔧 Customization

### Adding New Social Media Platforms
1. Update `PLATFORM_CHOICES` in `SocialMediaAccount` model
2. Add platform-specific validation in serializer
3. Update API documentation

### Custom User Fields
1. Add fields to `User` model
2. Update serializers to include new fields
3. Add validation rules
4. Update API documentation

### Custom Permissions
1. Create custom permission classes
2. Apply to ViewSets as needed
3. Test thoroughly

## 🐛 Troubleshooting

### Common Issues

#### 1. Database Migration Errors
```bash
# Reset migrations if needed
python manage.py migrate users zero
python manage.py makemigrations users
python manage.py migrate
```

#### 2. JWT Token Issues
- Check token expiration settings
- Verify JWT secret key configuration
- Ensure proper token format in requests

#### 3. Permission Errors
- Verify user authentication
- Check object-level permissions
- Ensure proper serializer context

#### 4. Rate Limiting Issues
- Check throttle settings
- Verify IP address detection
- Monitor rate limit headers

### Debug Mode
Enable debug mode in settings for detailed error messages:
```python
DEBUG = True
```

## 📚 Additional Resources

- [Django REST Framework Documentation](https://www.django-rest-framework.org/)
- [SimpleJWT Documentation](https://django-rest-framework-simplejwt.readthedocs.io/)
- [Django Filter Documentation](https://django-filter.readthedocs.io/)
- [API Documentation](./API_DOCUMENTATION.md)

## 🤝 Contributing

1. Follow the existing code style
2. Add tests for new features
3. Update documentation
4. Test thoroughly before submitting

## 📄 License

This implementation is part of the Client-Nest platform.

---

**Next Steps:**
- [ ] Implement frontend integration
- [ ] Add email verification
- [ ] Implement password reset functionality
- [ ] Add two-factor authentication
- [ ] Implement user activity logging
- [ ] Add user analytics and reporting 