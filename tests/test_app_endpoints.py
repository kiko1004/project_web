import unittest

from app import *
from flask_testing import TestCase
from functools import wraps


class TestUserInfoRoute(TestCase):
    def create_app(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        return app

    def test_user_info(self):
        # Create a test client
        with self.client as client:
            # Create a test request context
            with client.session_transaction() as session:
                # Mock the request headers with a valid token
                session['Authorization'] = 'Bearer valid_token'

            # Test the user_info function
            with client.session_transaction() as session:
                session['Authorization'] = 'Bearer valid_token'

            response = client.post('/get_user_info')
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertEqual(data['username'], 'test_user')

    def test_user_info_invalid_request(self):
        # Create a test client
        with self.client as client:
            # Create a test request context
            with client.session_transaction() as session:
                # Mock the request headers with an invalid token
                session['Authorization'] = 'Bearer invalid_token'

            # Mock the token_required decorator to return an error
            def mock_token_required(f):
                @wraps(f)
                def decorated(*args, **kwargs):
                    return jsonify({"message": "Token is missing!"}), 403
                return decorated

            # Apply the mock decorator to the user_info function
            global user_info
            user_info = mock_token_required(user_info)

            # Test the user_info function with an invalid request
            with client.session_transaction() as session:
                session['Authorization'] = 'Bearer invalid_token'

            response = client.post('/get_user_info')
            self.assertEqual(response.status_code, 403)
            data = response.get_json()
            self.assertEqual(data['message'], 'Token is missing!')

class TestSumRoute(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()

    def test_sum_page_invalid_request(self):
        # Test the sum_page function with an invalid request
        response = self.app.post('/sum')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertDictEqual({'response': 0}, data)
