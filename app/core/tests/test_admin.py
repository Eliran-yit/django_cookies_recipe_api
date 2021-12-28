from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse 


class AdminSiteTests(TestCase):
    
    def setUp(self):
        # set the object a client variable so it will be reachable from
        # other tests
        self.client = Client() 
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@gmail.com',
            password='password123'
        )
        # log user in using helper function of the Client module
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email='test@gmail.com',
            password='password123',
            name='Test user full name'
        )
        
        
    def test_users_listed(self):
        """Test that users are listed on user page"""
        # generate the url for the list user page
        url = reverse('admin:core_user_changelist')
        # response object
        res = self.client.get(url)
        
        # the assert contains check that the response is 200, 
        # and check in the rendered response object the 
        # name and email of the user
        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)
        
    def test_user_change_page(self):
        """Test that the user edit page works"""
        # grab the url changed and add to the end of the user id
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)
        
        # make sure that the response is 200 ok
        self.assertEqual(res.status_code, 200)
        
    def test_create_user_page(self):
        """Test that create user page works"""
        url = reverse('admin:core_user_add')
        res = self.client.get(url)
        
        self.assertEqual(res.status_code, 200)