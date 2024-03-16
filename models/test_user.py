from unittest import TestCase

from models import CreateUserRequest

mock_email = 'test@test.com'


class TestCreateUserRequest(TestCase):
    def test_should_fail_when_no_name_is_provided(self):
        with self.assertRaises(ValueError) as context:
            CreateUserRequest(
                username='username',
                email=mock_email,
                password='password'
            )

    def test_should_fail_when_name_is_empty(self):
        with self.assertRaises(ValueError) as context:
            CreateUserRequest(
                name='',
                username='username',
                email=mock_email,
                password='password'
            )

    def test_should_fail_when_no_username_is_provided(self):
        with self.assertRaises(ValueError) as context:
            CreateUserRequest(
                name='name',
                email=mock_email,
                password='password'
            )

    def test_should_fail_when_username_is_empty(self):
        with self.assertRaises(ValueError) as context:
            CreateUserRequest(
                name='name',
                username='',
                email=mock_email,
                password='password'
            )

    def test_should_fail_when_username_is_not_lower_cased(self):
        with self.assertRaises(ValueError) as context:
            CreateUserRequest(
                name='name',
                username='Username',
                email=mock_email,
                password='password'
            )

    def test_should_fail_when_username_has_less_than_4_characters(self):
        with self.assertRaises(ValueError) as context:
            CreateUserRequest(
                name='name',
                username='use',
                email=mock_email,
                password='password'
            )

    def test_should_fail_when_no_email_is_provided(self):
        with self.assertRaises(ValueError) as context:
            CreateUserRequest(
                name='name',
                username='username',
                password='password'
            )

    def test_should_fail_when_email_is_empty(self):
        with self.assertRaises(ValueError) as context:
            CreateUserRequest(
                name='name',
                username='username',
                email='',
                password='password'
            )

    def test_should_fail_when_email_is_not_valid(self):
        with self.assertRaises(ValueError) as context:
            CreateUserRequest(
                name='name',
                username='username',
                email='invalid_email',
                password='password'
            )

    def test_should_fail_when_no_password_is_provided(self):
        with self.assertRaises(ValueError) as context:
            CreateUserRequest(
                name='name',
                username='username',
                email=mock_email
            )

    def test_should_fail_when_password_is_empty(self):
        with self.assertRaises(ValueError) as context:
            CreateUserRequest(
                name='name',
                username='username',
                email=mock_email,
                password=''
            )

    def test_should_fail_when_password_has_less_than_8_characters(self):
        with self.assertRaises(ValueError) as context:
            CreateUserRequest(
                name='name',
                username='username',
                email=mock_email,
                password='pass'
            )
