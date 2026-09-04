from django.test import TestCase, override_settings

from movies.models import Movie
from users.models import PasswordResetToken, User, UserToken

from .auth_service import AuthService


class AuthenticationFlowTests(TestCase):
    def create_user(self, username='testuser', email='user@example.com'):
        return AuthService.register_user(
            email=email, phone=None, username=username, password='SecurePass123'
        )

    def login(self, email='user@example.com'):
        response = self.client.post(
            '/auth/login',
            {'identifier': email, 'password': 'SecurePass123'},
            content_type='application/json',
        )
        self.client.cookies.update(response.cookies)
        return response

    def test_same_passwords_use_different_salts_and_hashes(self):
        first = self.create_user()
        second = self.create_user('seconduser', 'second@example.com')
        self.assertNotEqual(first.password_salt, second.password_salt)
        self.assertNotEqual(first.password_hash, second.password_hash)

    def test_login_cookies_and_whoami(self):
        self.create_user()
        response = self.login()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.cookies['access_token']['httponly'])
        self.assertTrue(response.cookies['refresh_token']['httponly'])
        self.assertEqual(self.client.get('/auth/whoami').status_code, 200)

    def test_protected_movies_require_authentication(self):
        self.assertEqual(self.client.get('/api/movies/').status_code, 401)

    def test_logout_revokes_current_tokens(self):
        self.create_user()
        self.login()
        self.assertEqual(UserToken.objects.filter(is_revoked=False).count(), 2)
        self.assertEqual(self.client.post('/auth/logout').status_code, 200)
        self.assertEqual(UserToken.objects.filter(is_revoked=False).count(), 0)

    def test_user_cannot_access_another_users_movie(self):
        self.create_user()
        other = self.create_user('otheruser', 'other@example.com')
        movie = Movie.objects.create(user=other, title='Private movie', director='Director', year=2020)
        self.login()
        self.assertEqual(self.client.get(f'/api/movies/{movie.id}/').status_code, 403)

    def test_oauth_callback_rejects_invalid_state(self):
        response = self.client.get('/auth/oauth/yandex/callback?code=code&state=wrong')
        self.assertEqual(response.status_code, 400)
        self.assertIn('state', response.json()['error'])

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_password_reset_token_is_hashed_and_can_be_used(self):
        user = self.create_user()
        raw_token = AuthService.request_password_reset(user.email)
        stored_token = PasswordResetToken.objects.get(user=user)
        self.assertNotEqual(stored_token.token, raw_token)
        self.assertTrue(stored_token.token_salt)
        AuthService.reset_password(raw_token, 'AnotherPass123')
        user.refresh_from_db()
        self.assertTrue(user.check_password('AnotherPass123'))
