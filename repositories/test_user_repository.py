from datetime import datetime
from select import select
from unittest import TestCase
from unittest.mock import Mock

from sqlalchemy.sql import operators, select

import orm
from models import CreateUserRequest
from repositories.user_repository import get_user_by_email_or_username, get_user_by_id, create_user

mock_user = orm.User(
    id=1,
    name='test',
    username='test',
    email='test@test.com',
    hashed_password='hashed_password',
    is_active=True,
    created_at=datetime.utcnow(),
)


def _create_user_mock_add(user_orm):
    user_orm.id = mock_user.id
    user_orm.created_at = mock_user.created_at
    return user_orm


class TestUserRepository(TestCase):
    def test_get_user_by_email_or_username(self):
        mock_session = Mock()
        mock_session.execute.return_value.scalar.return_value = mock_user

        user = get_user_by_email_or_username(mock_session, mock_user.email)

        self.assertEqual(user.id, mock_user.id)
        self.assertEqual(user.name, mock_user.name)
        self.assertEqual(user.username, mock_user.username)
        self.assertEqual(user.email, mock_user.email)
        self.assertEqual(user.hashed_password, mock_user.hashed_password)
        self.assertEqual(user.is_active, mock_user.is_active)
        self.assertEqual(user.created_at, int(mock_user.created_at.timestamp()))
        mock_session.execute.assert_called_once()
        mock_session.execute.return_value.scalar.assert_called_once()
        self.assertTrue(
            mock_session.execute.call_args[0][0].compare(
                select(orm.User).filter(
                    operators.and_(
                        operators.eq(orm.User.is_active, True),
                        operators.or_(
                            orm.User.email == mock_user.email,
                            orm.User.username == mock_user.email
                        ),
                    ),
                ),
            ),
        )

    def test_get_user_by_email_or_username_with_invalid_user(self):
        mock_session = Mock()
        mock_session.execute.return_value.scalar.return_value = None

        user = get_user_by_email_or_username(mock_session, mock_user.email)

        self.assertIsNone(user)
        mock_session.execute.assert_called_once()
        mock_session.execute.return_value.scalar.assert_called_once()

    def test_get_user_by_id(self):
        mock_session = Mock()
        mock_session.execute.return_value.scalar.return_value = mock_user

        user = get_user_by_id(mock_session, mock_user.id)

        self.assertEqual(user.id, mock_user.id)
        self.assertEqual(user.name, mock_user.name)
        self.assertEqual(user.username, mock_user.username)
        self.assertEqual(user.email, mock_user.email)
        self.assertEqual(user.hashed_password, mock_user.hashed_password)
        self.assertEqual(user.is_active, mock_user.is_active)
        self.assertEqual(user.created_at, int(mock_user.created_at.timestamp()))
        mock_session.execute.assert_called_once()
        mock_session.execute.return_value.scalar.assert_called_once()
        self.assertTrue(
            mock_session.execute.call_args[0][0].compare(
                select(orm.User).filter(orm.User.id == mock_user.id),
            ),
        )

    def test_get_user_by_id_with_invalid_user(self):
        mock_session = Mock()
        mock_session.execute.return_value.scalar.return_value = None

        user = get_user_by_id(mock_session, mock_user.id)

        self.assertIsNone(user)
        mock_session.execute.assert_called_once()
        mock_session.execute.return_value.scalar.assert_called_once()

    def test_create_user(self):
        mock_session = Mock()
        mock_session.add = Mock()
        mock_session.commit = Mock()
        mock_session.add.side_effect = _create_user_mock_add

        user = create_user(mock_session, CreateUserRequest(
            name=mock_user.name,
            username=mock_user.username,
            email=mock_user.email,
            password=mock_user.hashed_password,
        ))

        self.assertEqual(user.id, mock_user.id)
        self.assertEqual(user.name, mock_user.name)
        self.assertEqual(user.username, mock_user.username)
        self.assertEqual(user.email, mock_user.email)
        self.assertEqual(user.hashed_password, mock_user.hashed_password)
        self.assertEqual(user.is_active, mock_user.is_active)
        self.assertEqual(user.created_at, int(mock_user.created_at.timestamp()))
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.commit.assert_called_once()

    def test_create_user_fails(self):
        mock_session = Mock()
        mock_session.add = Mock()
        mock_session.commit = Mock()
        mock_session.add.side_effect = _create_user_mock_add

        user = create_user(mock_session, CreateUserRequest(
            name=mock_user.name,
            username=mock_user.username,
            email=mock_user.email,
            password=mock_user.hashed_password,
        ))

        self.assertEqual(user.id, mock_user.id)
        self.assertEqual(user.name, mock_user.name)
        self.assertEqual(user.username, mock_user.username)
        self.assertEqual(user.email, mock_user.email)
        self.assertEqual(user.hashed_password, mock_user.hashed_password)
        self.assertEqual(user.is_active, mock_user.is_active)
        self.assertEqual(user.created_at, int(mock_user.created_at.timestamp()))
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.add.side_effect = Exception('Error')
        self.assertRaises(Exception, create_user, mock_session, CreateUserRequest(
            name=mock_user.name,
            username=mock_user.username,
            email=mock_user.email,
            password=mock_user.hashed_password,
        ))
