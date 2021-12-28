# write test case
from django.test import TestCase
# use the user model
from django.contrib.auth import get_user_model
# genarate api url
from django.urls import reverse 

# make request to our api and check what is the response 
from rest_framework.test import APIClient
# module that contains status code - easier to write and read status code 
from rest_framework import status

# const url variable of the create user var
CREATE_USER_URL = reverse('user:create')
# const url variable of the token var
TOKEN_URL = reverse('user:token')
# const user url var - help to test if user is authenticated
ME_URL = reverse('user:me')


# create a helper function to create user for our test
def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """"Tests the users API (public)"""
    
    # create one client that will be useful for all the tests
    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating user with valid payload is successful"""
        payload = {
            'email': 'test@gmail.com',
            'password': 'testpass',
            'name': 'test name'
        }
        
        # do http post request to our client url
        res = self.client.post(CREATE_USER_URL, payload)
        # check that the response returned 201
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        # test that the user created
        user = get_user_model().objects.get(**res.data)
        # test the password is match
        self.assertTrue(user.check_password(payload['password']))
        # test that the password is not returned in the request
        self.assertNotIn('password', res.data)
        
        
    def test_user_exists(self):
        """Test creating a user already exists fails"""
        payload = {'email': 'test@gmail.com', 'password': 'testpass'}
        create_user(**payload)
        
        res = self.client.post(CREATE_USER_URL, payload)
        
        # return 400 because user already exist
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        
        
    def test_password_too_short(self):
        """Test that the password must be more than 5 charecters"""
        payload = {
                    'email': 'test@gmail.com',
                    'password': 'pw',
                    'name': 'Test',
                }
        res = self.client.post(CREATE_USER_URL, payload)
        
        # return 400 because password is too short
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        
        # if the user already exist return true else return false
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        # we want that the user exist return false
        self.assertFalse(user_exists)
        
        
    def test_create_token_for_user(self):
        """Test that a token is created for the user"""
        payload = {
                    'email': 'test@gmail.com',
                    'password': 'testpass',
                }
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)
        
        # tests that the response contains a token key var
        self.assertIn('token', res.data)
        
        # check that the response status code is 200
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        
    def test_create_token_invalid_credentials(self):
        """Test that token is invalid credentials are given"""
        create_user(email='test@gmail.com', password='testpass')
        payload = {'email': 'test@gmail.com', 'password': 'wrong'}
        res = self.client.post(TOKEN_URL, payload)
        
        # if the token is invalid it would not be exist in the request
        self.assertNotIn('token', res.data)            
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_create_token_no_user(self):
        """Test that token is not created if user does not exist"""
        payload = {'email': 'test@gmail.com', 'password': 'testpass'}
        res = self.client.post(TOKEN_URL, payload)
        
        # if the user does not exist the token wont exist in the request
        self.assertNotIn('token', res.data)            
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        
        
    def test_create_token_missing_field(self):
        """Test that email and password are required"""
        payload = {'email': 'one', 'password': ''}
        res = self.client.post(TOKEN_URL, payload)            
        
        # if some data is missing, the token wont exist in the request
        self.assertNotIn('token', res.data)            
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        
        
    def test_retrieve_user_unauthorized(self):
        """Test that authentication is required for users"""
        res = self.client.get(ME_URL)
        
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        
        
        
class PrivateUserApiTests(TestCase):
    """Test API requests that require authentication"""
    
    def setUp(self):
        self.user = create_user(
            email='test@gmail.com',
            password='testpass',
            name='name',
        )
        self.client = APIClient()    
        self.client.force_authenticate(user=self.user)
        
    def test_retreive_profile_success(self):
        """Test retreving profile for logged in user"""
        res = self.client.get(ME_URL)
        profile_data = {
            'name': self.user.name,
            'email': self.user.email,
        }
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, profile_data)
        
    def test_post_me_not_allowed(self):
        """Test that POST is not allowed on the me url"""
        res = self.client.post(ME_URL, {})
        
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        
        
    def test_update_user_profile(self):
        """Test updating the user profile for authenticated user"""
        payload = {'name': 'new name', 'password': 'newpassword123'}
        
        res = self.client.patch(ME_URL, payload)
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        
        
        
        
        
        