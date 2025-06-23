#!/usr/bin/env python3
"""
Test script for authentication and post creation
"""
import requests
import json

# Base URL for the API
BASE_URL = "http://127.0.0.1:8000"

def test_authentication_and_posts():
    """Test the complete flow: login -> create post -> get posts"""
    
    print("🔐 Testing Authentication and Post Creation")
    print("=" * 50)
    
    # Step 1: Login to get JWT token
    print("\n1️⃣ Logging in...")
    login_data = {
        "username": "markcole256",
        "password": "12345678"  # Replace with your actual password
    }
    
    try:
        login_response = requests.post(f"{BASE_URL}/api/auth/token/", json=login_data)
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data.get('access')
            refresh_token = token_data.get('refresh')
            
            print(f"✅ Login successful!")
            print(f"   Access Token: {access_token[:50]}...")
            print(f"   Refresh Token: {refresh_token[:50]}...")
            
            # Set up headers for authenticated requests
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Step 2: Create a post
            print("\n2️⃣ Creating a post...")
            post_data = {
                "content": "Hello World! This is my first post from the API! 🚀",
                "post_type": "text",
                "visibility": "public",
                "hashtags": ["#firstpost", "#api", "#django"]
            }
            
            create_response = requests.post(
                f"{BASE_URL}/api/social/posts/", 
                json=post_data, 
                headers=headers
            )
            
            if create_response.status_code == 201:
                post = create_response.json()
                print(f"✅ Post created successfully!")
                print(f"   Post ID: {post.get('id')}")
                print(f"   Content: {post.get('content')}")
                print(f"   Author: {post.get('author', {}).get('username')}")
                print(f"   Created: {post.get('created_at')}")
                
                # Step 3: Get all posts
                print("\n3️⃣ Fetching all posts...")
                posts_response = requests.get(f"{BASE_URL}/api/social/posts/", headers=headers)
                
                if posts_response.status_code == 200:
                    posts = posts_response.json()
                    print(f"✅ Retrieved {len(posts.get('results', []))} posts")
                    
                    for i, post in enumerate(posts.get('results', []), 1):
                        print(f"   {i}. {post.get('content', '')[:50]}...")
                        print(f"      By: {post.get('author', {}).get('username')}")
                        print(f"      Likes: {post.get('like_count', 0)}")
                        print()
                else:
                    print(f"❌ Failed to get posts: {posts_response.status_code}")
                    print(f"   Response: {posts_response.text}")
            else:
                print(f"❌ Failed to create post: {create_response.status_code}")
                print(f"   Response: {create_response.text}")
                
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"   Response: {login_response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error: Make sure the Django server is running on http://127.0.0.1:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_user_registration():
    """Test user registration"""
    print("\n👤 Testing User Registration")
    print("=" * 30)
    
    register_data = {
        "username": "testuser123",
        "email": "testuser123@example.com",
        "password": "testpass123",
        "first_name": "Test",
        "last_name": "User"
    }
    
    try:
        register_response = requests.post(f"{BASE_URL}/api/auth/register/register/", json=register_data)
        
        if register_response.status_code == 201:
            user_data = register_response.json()
            print(f"✅ User registered successfully!")
            print(f"   Username: {user_data.get('username')}")
            print(f"   Email: {user_data.get('email')}")
        else:
            print(f"❌ Registration failed: {register_response.status_code}")
            print(f"   Response: {register_response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error: Make sure the Django server is running")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting API Tests...")
    
    # Test user registration first
    test_user_registration()
    
    # Test authentication and post creation
    test_authentication_and_posts()
    
    print("\n✨ Test completed!")
    print("\n📝 Note: If login fails, make sure to:")
    print("   1. Use the correct password you set during superuser creation")
    print("   2. Or register a new user using the registration endpoint")
    print("   3. Check that the Django server is running on http://127.0.0.1:8000") 