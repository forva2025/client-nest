from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import User

# Create your tests here.

class UserRegistrationTests(APITestCase):
    def setUp(self):
        self.url = reverse('user_registration')
        self.valid_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'TestPass123!',
        }

    def test_registration_success(self):
        response = self.client.post(self.url, self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='testuser@example.com').exists())

    def test_registration_missing_fields(self):
        data = {
            'username': '',
            'email': '',
            'password': '',
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_duplicate_email(self):
        User.objects.create_user(username='existing', email='dupe@example.com', password='TestPass123!')
        data = {
            'username': 'newuser',
            'email': 'dupe@example.com',
            'password': 'TestPass123!',
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        data = self.valid_data.copy()
        data['password'] = 'Short1!'
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_no_uppercase(self):
        data = self.valid_data.copy()
        data['password'] = 'testpass123!'
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_no_lowercase(self):
        data = self.valid_data.copy()
        data['password'] = 'TESTPASS123!'
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_no_number(self):
        data = self.valid_data.copy()
        data['password'] = 'TestPassWord!'
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_no_special_char(self):
        data = self.valid_data.copy()
        data['password'] = 'TestPass123'
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
