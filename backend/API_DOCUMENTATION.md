# User Management API Documentation

## Overview

This document provides comprehensive documentation for the User Management APIs in the Client-Nest platform. The APIs handle user registration, authentication, profile management, and social media account linking.

## Base URL

```
http://localhost:8000/api/
```

## Authentication

Most endpoints require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

## Endpoints

### 1. Authentication Endpoints

#### 1.1 User Registration
**POST** `/auth/register/`

Register a new user account.

**Request Body:**
```json
{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!",
    "first_name": "John",
    "last_name": "Doe"
}
```

**Response (201 Created):**
```json
{
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "bio": "",
    "profile_picture": null,
    "profile": {
        "id": 1,
        "phone_number": "",
        "address": "",
        "social_links": {},
        "preferences": {},
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    },
    "social_accounts": [],
    "date_joined": "2024-01-01T00:00:00Z",
    "last_login": null,
    "is_active": true
}
```

**Validation Rules:**
- Username: 3+ characters, alphanumeric + underscore only
- Email: Must be unique and valid format
- Password: 8+ characters, uppercase, lowercase, digit, special character
- Passwords must match

#### 1.2 JWT Token Authentication
**POST** `/auth/token/`

Obtain JWT access and refresh tokens.

**Request Body:**
```json
{
    "username": "john_doe",
    "password": "SecurePass123!"
}
```

**Response (200 OK):**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### 1.3 Token Refresh
**POST** `/auth/token/refresh/`

Refresh JWT access token using refresh token.

**Request Body:**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (200 OK):**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### 2. User Management Endpoints

#### 2.1 Get Current User Profile
**GET** `/users/users/me/`

Get the current authenticated user's profile.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response (200 OK):**
```json
{
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "bio": "Software Developer",
    "profile_picture": "/media/profile_pictures/john.jpg",
    "profile": {
        "id": 1,
        "phone_number": "+1234567890",
        "address": "123 Main St, City, Country",
        "social_links": {
            "linkedin": "https://linkedin.com/in/johndoe",
            "github": "https://github.com/johndoe"
        },
        "preferences": {
            "theme": "dark",
            "notifications": true
        },
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    },
    "social_accounts": [
        {
            "id": 1,
            "platform": "twitter",
            "platform_display": "Twitter",
            "account_id": "johndoe_twitter",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
    ],
    "date_joined": "2024-01-01T00:00:00Z",
    "last_login": "2024-01-01T12:00:00Z",
    "is_active": true,
    "is_staff": false,
    "is_superuser": false
}
```

#### 2.2 Update User Profile
**PUT/PATCH** `/users/users/update_profile/`

Update the current user's profile information.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Request Body:**
```json
{
    "username": "john_doe_updated",
    "first_name": "John",
    "last_name": "Smith",
    "bio": "Updated bio information"
}
```

**Response (200 OK):**
```json
{
    "id": 1,
    "username": "john_doe_updated",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Smith",
    "full_name": "John Smith",
    "bio": "Updated bio information",
    "profile_picture": "/media/profile_pictures/john.jpg",
    "profile": {...},
    "social_accounts": [...],
    "date_joined": "2024-01-01T00:00:00Z",
    "last_login": "2024-01-01T12:00:00Z",
    "is_active": true
}
```

#### 2.3 Change Password
**POST** `/users/users/change_password/`

Change the current user's password.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Request Body:**
```json
{
    "old_password": "SecurePass123!",
    "new_password": "NewSecurePass456!",
    "new_password_confirm": "NewSecurePass456!"
}
```

**Response (200 OK):**
```json
{
    "message": "Password changed successfully"
}
```

#### 2.4 Deactivate Account
**POST** `/users/users/deactivate_account/`

Deactivate the current user's account.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response (200 OK):**
```json
{
    "message": "Account deactivated successfully"
}
```

### 3. User Profile Management Endpoints

#### 3.1 Get My Profile
**GET** `/users/profiles/my_profile/`

Get the current user's detailed profile information.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response (200 OK):**
```json
{
    "id": 1,
    "phone_number": "+1234567890",
    "address": "123 Main St, City, Country",
    "social_links": {
        "linkedin": "https://linkedin.com/in/johndoe",
        "github": "https://github.com/johndoe",
        "twitter": "https://twitter.com/johndoe"
    },
    "preferences": {
        "theme": "dark",
        "notifications": true,
        "language": "en"
    },
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
}
```

#### 3.2 Update My Profile
**PUT/PATCH** `/users/profiles/update_my_profile/`

Update the current user's profile information.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Request Body:**
```json
{
    "phone_number": "+1234567890",
    "address": "456 New St, City, Country",
    "social_links": {
        "linkedin": "https://linkedin.com/in/johndoe",
        "github": "https://github.com/johndoe"
    },
    "preferences": {
        "theme": "light",
        "notifications": false,
        "language": "en"
    }
}
```

**Response (200 OK):**
```json
{
    "id": 1,
    "phone_number": "+1234567890",
    "address": "456 New St, City, Country",
    "social_links": {
        "linkedin": "https://linkedin.com/in/johndoe",
        "github": "https://github.com/johndoe"
    },
    "preferences": {
        "theme": "light",
        "notifications": false,
        "language": "en"
    },
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z"
}
```

### 4. Social Media Account Management Endpoints

#### 4.1 Get My Social Accounts
**GET** `/users/social-accounts/my_accounts/`

Get all social media accounts linked to the current user.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "platform": "twitter",
        "platform_display": "Twitter",
        "account_id": "johndoe_twitter",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    },
    {
        "id": 2,
        "platform": "linkedin",
        "platform_display": "LinkedIn",
        "account_id": "johndoe_linkedin",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }
]
```

#### 4.2 Get Available Platforms
**GET** `/users/social-accounts/platforms/`

Get list of available social media platforms.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response (200 OK):**
```json
[
    {
        "value": "facebook",
        "label": "Facebook"
    },
    {
        "value": "twitter",
        "label": "Twitter"
    },
    {
        "value": "instagram",
        "label": "Instagram"
    },
    {
        "value": "linkedin",
        "label": "LinkedIn"
    }
]
```

#### 4.3 Link Social Media Account
**POST** `/users/social-accounts/`

Link a new social media account to the current user.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Request Body:**
```json
{
    "platform": "twitter",
    "account_id": "johndoe_twitter",
    "access_token": "twitter_access_token_here"
}
```

**Response (201 Created):**
```json
{
    "id": 1,
    "platform": "twitter",
    "platform_display": "Twitter",
    "account_id": "johndoe_twitter",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
}
```

#### 4.4 Update Social Media Account
**PUT/PATCH** `/users/social-accounts/{id}/`

Update a specific social media account.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Request Body:**
```json
{
    "account_id": "johndoe_twitter_updated",
    "access_token": "new_twitter_access_token"
}
```

**Response (200 OK):**
```json
{
    "id": 1,
    "platform": "twitter",
    "platform_display": "Twitter",
    "account_id": "johndoe_twitter_updated",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z"
}
```

#### 4.5 Unlink Social Media Account
**DELETE** `/users/social-accounts/{id}/`

Unlink a social media account from the current user.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response (204 No Content):**
No content returned.

### 5. Admin Endpoints (Admin Users Only)

#### 5.1 List All Users
**GET** `/users/users/`

Get all users in the system (admin only).

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Query Parameters:**
- `search`: Search by username, email, first_name, last_name
- `is_active`: Filter by active status
- `is_staff`: Filter by staff status
- `date_joined`: Filter by join date
- `ordering`: Sort by username, email, date_joined, last_login
- `page`: Page number for pagination

**Response (200 OK):**
```json
{
    "count": 100,
    "next": "http://localhost:8000/api/users/users/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "username": "john_doe",
            "email": "john@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "full_name": "John Doe",
            "bio": "Software Developer",
            "profile_picture": null,
            "profile": {...},
            "social_accounts": [...],
            "date_joined": "2024-01-01T00:00:00Z",
            "last_login": "2024-01-01T12:00:00Z",
            "is_active": true
        }
    ]
}
```

#### 5.2 Get User Details
**GET** `/users/users/{id}/`

Get detailed information about a specific user (admin only).

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response (200 OK):**
```json
{
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "bio": "Software Developer",
    "profile_picture": null,
    "profile": {...},
    "social_accounts": [...],
    "date_joined": "2024-01-01T00:00:00Z",
    "last_login": "2024-01-01T12:00:00Z",
    "is_active": true,
    "is_staff": false,
    "is_superuser": false
}
```

## Error Responses

### 400 Bad Request
```json
{
    "field_name": [
        "Error message describing the validation issue."
    ]
}
```

### 401 Unauthorized
```json
{
    "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
    "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
    "detail": "Not found."
}
```

### 429 Too Many Requests
```json
{
    "detail": "Request was throttled. Expected available in 60 seconds."
}
```

## Rate Limiting

- **Registration**: 3 requests per hour per IP
- **General API**: 100 requests per hour per user
- **Admin endpoints**: 1000 requests per hour per user

## Pagination

All list endpoints support pagination with the following parameters:
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)

## Filtering and Search

### User Endpoints
- **Search**: username, email, first_name, last_name
- **Filter**: is_active, is_staff, date_joined
- **Order**: username, email, date_joined, last_login

### Profile Endpoints
- **Search**: user__username, user__email, phone_number

### Social Media Account Endpoints
- **Search**: account_id, platform
- **Filter**: platform

## File Upload

For profile picture uploads, use `multipart/form-data` content type:

```
Content-Type: multipart/form-data

{
    "profile_picture": <file>
}
```

## Security Considerations

1. **JWT Tokens**: Access tokens expire after 30 minutes, refresh tokens after 1 day
2. **Password Requirements**: Minimum 8 characters with uppercase, lowercase, digit, and special character
3. **Rate Limiting**: Prevents abuse and brute force attacks
4. **Input Validation**: All inputs are validated and sanitized
5. **Access Control**: Users can only access their own data unless they're admin users

## Testing

You can test the APIs using tools like:
- **Postman**
- **cURL**
- **Insomnia**
- **Django REST Framework's browsable API**

Example cURL command for user registration:
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!",
    "first_name": "Test",
    "last_name": "User"
  }'
``` 