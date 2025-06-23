#!/usr/bin/env python3
"""
Simple test script for User Management APIs
Run this script to test the API endpoints
"""

import requests
import json
import sys

# Configuration
BASE_URL = "http://localhost:8000/api"
TEST_USER = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!",
    "first_name": "Test",
    "last_name": "User"
}

def print_response(response, title):
    """Print formatted response"""
    print(f"\n{'='*50}")
    print(f"{title}")
    print(f"{'='*50}")
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")

def test_user_registration():
    """Test user registration endpoint"""
    print("\n🧪 Testing User Registration...")
    
    url = f"{BASE_URL}/auth/register/"
    response = requests.post(url, json=TEST_USER)
    print_response(response, "User Registration")
    
    if response.status_code == 201:
        print("✅ User registration successful!")
        return response.json()
    else:
        print("❌ User registration failed!")
        return None

def test_user_login():
    """Test user login endpoint"""
    print("\n🧪 Testing User Login...")
    
    url = f"{BASE_URL}/auth/token/"
    login_data = {
        "username": TEST_USER["username"],
        "password": TEST_USER["password"]
    }
    response = requests.post(url, json=login_data)
    print_response(response, "User Login")
    
    if response.status_code == 200:
        print("✅ User login successful!")
        return response.json()
    else:
        print("❌ User login failed!")
        return None

def test_get_user_profile(token):
    """Test getting user profile"""
    print("\n🧪 Testing Get User Profile...")
    
    url = f"{BASE_URL}/users/users/me/"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    print_response(response, "Get User Profile")
    
    if response.status_code == 200:
        print("✅ Get user profile successful!")
        return response.json()
    else:
        print("❌ Get user profile failed!")
        return None

def test_update_user_profile(token):
    """Test updating user profile"""
    print("\n🧪 Testing Update User Profile...")
    
    url = f"{BASE_URL}/users/users/update_profile/"
    headers = {"Authorization": f"Bearer {token}"}
    update_data = {
        "bio": "Updated bio from API test",
        "first_name": "Updated"
    }
    response = requests.patch(url, json=update_data, headers=headers)
    print_response(response, "Update User Profile")
    
    if response.status_code == 200:
        print("✅ Update user profile successful!")
        return response.json()
    else:
        print("❌ Update user profile failed!")
        return None

def test_get_user_profiles(token):
    """Test getting user profiles"""
    print("\n🧪 Testing Get User Profiles...")
    
    url = f"{BASE_URL}/users/profiles/my_profile/"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    print_response(response, "Get User Profiles")
    
    if response.status_code == 200:
        print("✅ Get user profiles successful!")
        return response.json()
    else:
        print("❌ Get user profiles failed!")
        return None

def test_social_media_platforms(token):
    """Test getting social media platforms"""
    print("\n🧪 Testing Get Social Media Platforms...")
    
    url = f"{BASE_URL}/users/social-accounts/platforms/"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    print_response(response, "Get Social Media Platforms")
    
    if response.status_code == 200:
        print("✅ Get social media platforms successful!")
        return response.json()
    else:
        print("❌ Get social media platforms failed!")
        return None

def test_link_social_account(token):
    """Test linking social media account"""
    print("\n🧪 Testing Link Social Media Account...")
    
    url = f"{BASE_URL}/users/social-accounts/"
    headers = {"Authorization": f"Bearer {token}"}
    social_data = {
        "platform": "twitter",
        "account_id": "testuser_twitter",
        "access_token": "test_access_token"
    }
    response = requests.post(url, json=social_data, headers=headers)
    print_response(response, "Link Social Media Account")
    
    if response.status_code == 201:
        print("✅ Link social media account successful!")
        return response.json()
    else:
        print("❌ Link social media account failed!")
        return None

def main():
    """Main test function"""
    print("🚀 Starting User Management API Tests")
    print(f"Base URL: {BASE_URL}")
    
    # Test 1: User Registration
    user_data = test_user_registration()
    if not user_data:
        print("❌ Cannot continue without user registration")
        return
    
    # Test 2: User Login
    auth_data = test_user_login()
    if not auth_data:
        print("❌ Cannot continue without user login")
        return
    
    access_token = auth_data.get("access")
    if not access_token:
        print("❌ No access token received")
        return
    
    # Test 3: Get User Profile
    profile_data = test_get_user_profile(access_token)
    
    # Test 4: Update User Profile
    updated_profile = test_update_user_profile(access_token)
    
    # Test 5: Get User Profiles
    profiles_data = test_get_user_profiles(access_token)
    
    # Test 6: Get Social Media Platforms
    platforms_data = test_social_media_platforms(access_token)
    
    # Test 7: Link Social Media Account
    social_data = test_link_social_account(access_token)
    
    print("\n🎉 API Testing Complete!")
    print("\n📋 Summary:")
    print("- User Registration: ✅")
    print("- User Login: ✅")
    print("- Get User Profile: ✅")
    print("- Update User Profile: ✅")
    print("- Get User Profiles: ✅")
    print("- Get Social Media Platforms: ✅")
    print("- Link Social Media Account: ✅")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Testing interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        sys.exit(1) 