from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from unittest import TestCase

import jwt

import services
from services.user_service import _hash_password, _verify_password, _generate_token, sign_in, CredentialsNotMatchError, \
    _validate_token


class TestUserService(TestCase):

    @patch('backports.pbkdf2.pbkdf2_hmac')
    @patch('settings.settings')
    def test_hash_password(self, mock_settings, mock_pbkdf2_hmac):
        mock_settings.return_value.pdkdf2_salt_bytes.return_value = b'salt'
        mock_settings.return_value.pdkdf2_rounds = 50000
        mock_pbkdf2_hmac.return_value = b'hashed_password'
        mock_password = 'password'
        password = 'password'
        hashed_password = _hash_password(password)

        self.assertEqual(hashed_password, b'hashed_password'.hex())
        mock_pbkdf2_hmac.assert_called_once_with(
            "sha256",
            mock_password.encode('utf-8'),
            b'salt',
            50000,
        )

        self.assertTrue(_verify_password(password, hashed_password))

    @patch('backports.pbkdf2.pbkdf2_hmac')
    @patch('settings.settings')
    def test_hash_password_throws_error(self, mock_settings, mock_pbkdf2_hmac):
        mock_settings.return_value.pdkdf2_salt_bytes.return_value = b'salt'
        mock_settings.return_value.pdkdf2_rounds = 50000
        mock_pbkdf2_hmac.side_effect = Exception('error')
        mock_password = 'password'
        password = 'password'

        with self.assertRaises(Exception) as context:
            _hash_password(password)
        self.assertTrue('error' in str(context.exception))

    @patch('services.user_service._hash_password')
    def test_verify_password(self, mock_hash_password):
        mock_hash_password.return_value = 'hashed_password'
        hashed_password = 'hashed_password'
        password = 'password'
        self.assertTrue(_verify_password(password, hashed_password))

    @patch('services.user_service._hash_password')
    def test_verify_password_false(self, mock_hash_password):
        mock_hash_password.return_value = 'hashed_password'
        password = 'password'

        self.assertFalse(_verify_password(password, 'wrong_password'))

    @patch('services.user_service._hash_password')
    def test_verify_password_throws_error(self, mock_hash_password):
        mock_hash_password.side_effect = Exception('error')
        hashed_password = 'hashed_password'
        password = 'password'

        with self.assertRaises(Exception) as context:
            _verify_password(password, hashed_password)
        self.assertTrue('error' in str(context.exception))

    @patch('jwt.encode')
    @patch('settings.settings')
    @patch('datetime.datetime')
    def test_generate_token(self, mock_datetime, mock_settings, mock_jwt_encode):
        mock_settings.return_value.jwt_secret = 'mock_secret'
        mock_settings.return_value.jwt_expire_seconds = 3600
        mock_jwt_encode.return_value = 'mock_token'
        now = datetime(2021, 1, 1, 0, 0, 0)
        mock_datetime.utcnow.return_value = now
        mock_user = Mock()
        mock_user.id = 1
        mock_user.name = 'test'

        token = _generate_token(mock_user)
        self.assertEqual(token, 'mock_token')
        mock_jwt_encode.assert_called_once_with(
            {
                'id': 1,
                'name': 'test',
                'iat': now,
                'exp': now + timedelta(seconds=3600),
                'iss': 'panela-magica',
                'aud': ['urn:panela-magica-api'],
            },
            'mock_secret',
            algorithm='HS256',
        )

    @patch('jwt.encode')
    @patch('settings.settings')
    def test_generate_token_throws_error(self, mock_settings, mock_jwt_encode):
        mock_settings.return_value.jwt_secret = 'mock_secret'
        mock_settings.return_value.jwt_expire_seconds = 3600
        mock_jwt_encode.side_effect = Exception('error')
        mock_user = Mock()
        mock_user.id = 1
        mock_user.name = 'test'
        with self.assertRaises(Exception) as context:
            _generate_token(mock_user)
        self.assertTrue('error' in str(context.exception))

    @patch('services.user_service.user_repository')
    @patch('services.user_service._generate_token')
    @patch('services.user_service._verify_password')
    def test_sign_in(self, mock_verify_password, mock_generate_token, mock_user_repository):
        mock_session = Mock()
        mock_user = Mock()
        mock_user.id = 1
        mock_user.name = 'test'
        mock_user.username = 'test'
        mock_user.email = 'test@test.com'
        mock_user.hashed_password = 'hashed_password'
        mock_user.is_active = True
        mock_user.created_at = int(datetime.utcnow().timestamp())

        mock_user_repository.get_user_by_email_or_username.return_value = mock_user
        mock_verify_password.return_value = True
        mock_generate_token.return_value = 'mock_token'

        response = sign_in('test', 'password', session=mock_session)
        self.assertEqual(response.id, 1)
        self.assertEqual(response.name, 'test')
        self.assertEqual(response.token, 'mock_token')
        self.assertEqual(response.username, 'test')
        self.assertEqual(response.email, 'test@test.com')
        self.assertEqual(response.created_at, mock_user.created_at)

        mock_user_repository.get_user_by_email_or_username.assert_called_once_with(mock_session, 'test')
        mock_verify_password.assert_called_once_with('password', 'hashed_password')
        mock_generate_token.assert_called_once_with(mock_user)

    @patch('services.user_service.user_repository')
    def test_sign_in_user_not_found(self, mock_user_repository):
        mock_user_repository.get_user_by_email_or_username.return_value = None
        with self.assertRaises(CredentialsNotMatchError) as context:
            sign_in('test', 'password')
        self.assertTrue('Credentials not match' in str(context.exception))

    @patch('services.user_service.user_repository')
    @patch('services.user_service._verify_password')
    def test_sign_in_password_not_match(self, mock_verify_password, mock_user_repository):
        mock_session = Mock()
        mock_user = Mock()
        mock_user.id = 1
        mock_user.username = 'test'
        mock_user.email = 'test@test.com'
        mock_user.hashed_password = 'hashed_password'
        mock_user.is_active = True
        mock_user.created_at = int(datetime.utcnow().timestamp())

        mock_user_repository.get_user_by_email_or_username.return_value = mock_user
        mock_verify_password.return_value = False
        with self.assertRaises(CredentialsNotMatchError) as context:
            sign_in('test', 'password', session=mock_session)
        self.assertTrue('Credentials not match' in str(context.exception))
        mock_user_repository.get_user_by_email_or_username.assert_called_once_with(mock_session, 'test')
        mock_verify_password.assert_called_once_with('password', 'hashed_password')

    @patch('jwt.decode')
    @patch('repositories.user_repository.get_user_by_id')
    @patch('settings.settings')
    def test_validate_token(self, mock_settings, mock_get_user_by_id, mock_jwt_decode):
        mock_jwt_decode.return_value = {
            'id': 1,
            'name': 'test',
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(seconds=3600),
            'iss': 'panela-magica',
            'aud': ['urn:panela-magica-api'],
        }
        mock_session = Mock()
        mock_user = Mock()
        mock_user.id = 1
        mock_user.name = 'test'
        mock_get_user_by_id.return_value = mock_user
        token = 'mock_token'
        mock_settings.return_value.jwt_secret = 'mock_secret'
        response = _validate_token(token, session=mock_session)
        self.assertEqual(response.id, 1)
        self.assertEqual(response.name, 'test')
        mock_get_user_by_id.assert_called_once_with(mock_session, 1)
        mock_jwt_decode.assert_called_once_with(token, 'mock_secret', algorithms=['HS256'])

    @patch('jwt.decode')
    @patch('settings.settings')
    def test_validate_token_expired(self, mock_settings, mock_jwt_decode):
        mock_settings.return_value.jwt_secret = 'mock_secret'
        mock_jwt_decode.side_effect = jwt.ExpiredSignatureError()
        with self.assertRaises(services.user_service.TokenExpiredError) as context:
            _validate_token('mock_token')
        self.assertTrue('Token expired' in str(context.exception))

    @patch('jwt.decode')
    @patch('settings.settings')
    def test_validate_token_invalid(self, mock_settings, mock_jwt_decode):
        mock_settings.return_value.jwt_secret = 'mock_secret'
        mock_jwt_decode.side_effect = jwt.InvalidTokenError()
        with self.assertRaises(services.user_service.InvalidTokenError) as context:
            _validate_token('mock_token')
        self.assertTrue('Invalid token' in str(context.exception))

    @patch('jwt.decode')
    @patch('settings.settings')
    def test_validate_token_throws_error(self, mock_settings, mock_jwt_decode):
        mock_settings.return_value.jwt_secret = 'mock_secret'
        mock_jwt_decode.side_effect = Exception('mock_error')
        with self.assertRaises(Exception) as context:
            _validate_token('mock')
        self.assertTrue('mock_error' in str(context.exception))

    @patch('jwt.decode')
    @patch('repositories.user_repository.get_user_by_id')
    @patch('settings.settings')
    def test_validate_token_user_not_found(self, mock_settings, mock_get_user_by_id, mock_jwt_decode):
        mock_jwt_decode.return_value = {
            'id': 1,
            'name': 'test',
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(seconds=3600),
            'iss': 'panela-magica',
            'aud': ['urn:panela-magica-api'],
        }
        mock_get_user_by_id.return_value = None

        with self.assertRaises(services.user_service.InvalidTokenError) as context:
            _validate_token('mock_token')
        self.assertTrue('Invalid token' in str(context.exception))

        mock_get_user_by_id.assert_called_once()
        mock_jwt_decode.assert_called_once()

    @patch('jwt.decode')
    @patch('repositories.user_repository.get_user_by_id')
    @patch('settings.settings')
    def test_validate_token_user_throws_error(self, mock_settings, mock_get_user_by_id, mock_jwt_decode):
        mock_jwt_decode.return_value = {
            'id': 1,
            'name': 'test',
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(seconds=3600),
            'iss': 'panela-magica',
            'aud': ['urn:panela-magica-api'],
        }
        mock_get_user_by_id.side_effect = Exception('mock_error')

        with self.assertRaises(Exception) as context:
            _validate_token('mock_token')
        self.assertTrue('mock_error' in str(context.exception))

        mock_get_user_by_id.assert_called_once()
        mock_jwt_decode.assert_called_once()

    @patch('services.user_service._validate_token')
    def test_me(self, mock_validate_token):
        mock_session = Mock()
        mock_user = Mock()
        mock_user.id = 1
        mock_user.name = 'test'
        mock_user.username = 'test'
        mock_user.email = 'test@test.com'
        mock_user.created_at = int(datetime.utcnow().timestamp())

        mock_validate_token.return_value = mock_user
        response = services.me('mock_token', session=mock_session)

        self.assertEqual(response.id, 1)
        self.assertEqual(response.name, 'test')
        self.assertEqual(response.username, 'test')
        self.assertEqual(response.email, 'test@test.com')
        self.assertEqual(response.created_at, mock_user.created_at)
        mock_validate_token.assert_called_once_with('mock_token', mock_session)

    @patch('services.user_service._validate_token')
    def test_me_throws_invalid_token_error(self, mock_validate_token):
        mock_validate_token.side_effect = services.user_service.InvalidTokenError()
        with self.assertRaises(services.user_service.InvalidTokenError):
            services.me('mock_token')
        mock_validate_token.assert_called_once_with('mock_token', None)

    @patch('services.user_service._validate_token')
    def test_me_throws_token_expired_error(self, mock_validate_token):
        mock_validate_token.side_effect = services.user_service.TokenExpiredError()
        with self.assertRaises(services.user_service.TokenExpiredError):
            services.me('mock_token')
        mock_validate_token.assert_called_once_with('mock_token', None)

    @patch('services.user_service._validate_token')
    def test_me_throws_error(self, mock_validate_token):
        mock_validate_token.side_effect = Exception('mock_error')
        with self.assertRaises(Exception):
            services.me('mock_token')
        mock_validate_token.assert_called_once_with('mock_token', None)