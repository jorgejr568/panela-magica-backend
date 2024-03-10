from unittest import TestCase
from unittest.mock import Mock, patch

from clients import s3_client

base_mock_settings = Mock()
base_mock_settings.s3_region = 'us-east-1'
base_mock_settings.s3_endpoint = 'http://localhost:9000'
base_mock_settings.s3_access_key = 's3-access-key'
base_mock_settings.s3_secret_key = 's3-secret-key'
base_mock_settings.s3_bucket = 's3-bucket'


class TestS3Client(TestCase):
    def tearDown(self):
        s3_client.S3Client.__destroy__()

    @patch('boto3.session.Session')
    @patch('settings.settings', return_value=base_mock_settings)
    def test_get_instance(self, mock_settings, mock_session):
        mock_client = Mock()
        mock_session.return_value.client = mock_client

        s3_client.S3Client.get_instance()

        mock_session.assert_called_once()
        mock_client.assert_called_once_with('s3',
                                            region_name=base_mock_settings.s3_region,
                                            endpoint_url=base_mock_settings.s3_endpoint,
                                            aws_access_key_id=base_mock_settings.s3_access_key,
                                            aws_secret_access_key=base_mock_settings.s3_secret_key)

    @patch('boto3.session.Session')
    @patch('settings.settings', return_value=base_mock_settings)
    def test_new_instance_should_fail(self, mock_settings, mock_session):
        with self.assertRaises(Exception) as context:
            s3_client.S3Client.get_instance()
            s3_client.S3Client()

        self.assertEqual(str(context.exception), 'This class is a singleton!')

    @patch('boto3.session.Session')
    @patch('settings.settings', return_value=base_mock_settings)
    def test_upload_fileobj(self, mock_settings, mock_session):
        mock_client = Mock()
        mock_session.return_value.client.return_value = mock_client

        s3 = s3_client.S3Client.get_instance()
        s3.upload_fileobj(b'conteudo', 'bucket', 'key', foo='bar', baz='qux')

        mock_client.upload_fileobj.assert_called_once_with(b'conteudo', 'bucket', 'key', foo='bar', baz='qux')

    @patch('clients.s3_client.S3Client.get_instance')
    @patch('settings.settings', return_value=base_mock_settings)
    def test_upload_file(self, mock_settings, mock_get_instance):
        mock_upload_fileobj = Mock()
        mock_upload_fileobj.return_value = None
        mock_get_instance.return_value.upload_fileobj = mock_upload_fileobj
        s3_client.upload_file(b'conteudo', 'key')

        mock_upload_fileobj.assert_called_once()
        mock_upload_fileobj.assert_called_once_with(
            b'conteudo',
            base_mock_settings.s3_bucket,
            'key',
            ExtraArgs={'ACL': 'public-read', 'ContentType': 'application/octet-stream'}
        )

    @patch('clients.s3_client.S3Client.get_instance')
    @patch('settings.settings', return_value=base_mock_settings)
    def test_upload_file_private(self, mock_settings, mock_get_instance):
        mock_upload_fileobj = Mock()
        mock_upload_fileobj.return_value = None
        mock_get_instance.return_value.upload_fileobj = mock_upload_fileobj
        s3_client.upload_file(b'conteudo', 'key', public=False)

        mock_upload_fileobj.assert_called_once()
        mock_upload_fileobj.assert_called_once_with(
            b'conteudo',
            base_mock_settings.s3_bucket,
            'key',
            ExtraArgs={'ACL': 'private', 'ContentType': 'application/octet-stream'}
        )

    @patch('clients.s3_client.S3Client.get_instance')
    @patch('settings.settings', return_value=base_mock_settings)
    def test_upload_file_mime_type(self, mock_settings, mock_get_instance):
        mock_upload_fileobj = Mock()
        mock_upload_fileobj.return_value = None
        mock_get_instance.return_value.upload_fileobj = mock_upload_fileobj
        s3_client.upload_file(b'conteudo', 'key', mime_type='image/png')

        mock_upload_fileobj.assert_called_once()
        mock_upload_fileobj.assert_called_once_with(
            b'conteudo',
            base_mock_settings.s3_bucket,
            'key',
            ExtraArgs={'ACL': 'public-read', 'ContentType': 'image/png'}
        )

    @patch('clients.s3_client.S3Client.get_instance')
    @patch('settings.settings', return_value=base_mock_settings)
    def test_upload_file_throw_exception(self, mock_settings, mock_get_instance):
        mock_upload_fileobj = Mock()
        mock_upload_fileobj.side_effect = Exception('Erro ao fazer upload')
        mock_get_instance.return_value.upload_fileobj = mock_upload_fileobj

        with self.assertRaises(Exception) as context:
            s3_client.upload_file(b'conteudo', 'key')

        self.assertEqual(str(context.exception), 'Erro ao fazer upload')
