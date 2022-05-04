from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class UserUrlTests(TestCase):
    """Проверка пользовательских страниц авторизации и
    регистрации.
    """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='urls_user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.clients = {
            'guest_client': self.guest_client,
            'authorized_client': self.authorized_client,
        }

    def test_urls_available_to_any_client(self):
        """Проверка по статусу кода URLs доступных любому
        пользователю.
        """
        guest_client_status_codes = {
            '/auth/logout/': 200,
            '/auth/login/': 200,
            '/auth/password_change/done/': 302,
            '/auth/password_change/': 302,
            '/auth/password_reset/complete/': 200,
            '/auth/password_reset/done/': 200,
            '/auth/password_reset/': 200,
            '/auth/signup/': 200,
        }

        auth_client_status_codes = {
            '/auth/logout/': 200,
            '/auth/login/': 200,
            '/auth/password_change/done/': 302,
            '/auth/password_change/': 302,
            '/auth/password_reset/complete/': 200,
            '/auth/password_reset/done/': 200,
            '/auth/password_reset/': 200,
            '/auth/signup/': 200,
        }

        clients_status_codes = {
            'guest_client': guest_client_status_codes,
            'authorized_client': auth_client_status_codes,
        }

        for client, status_codes in clients_status_codes.items():
            for url, status_code in status_codes.items():
                with self.subTest(client=client, url=url):
                    response = self.clients[client].get(url)
                    self.assertEqual(response.status_code, status_code)
        print('Страницы доступны любому пользователю, коды верные.')

    def test_static_url_uses_correct_template(self):
        """Проверка соответствия шаблонов к их URL'ам."""
        templates_urls = {
            '/auth/logout/': 'users/logged_out.html',
            '/auth/login/': 'users/login.html',
            '/auth/password_reset/complete/':
                'users/password_reset_complete.html',
            '/auth/password_reset/done/':
                'users/password_reset_done.html',
            '/auth/password_reset/':
                'users/password_reset_form.html',
            '/auth/signup/': 'users/signup.html',
        }

        for url_address, template in templates_urls.items():
            with self.subTest(address=url_address):
                response = self.guest_client.get(url_address)
                self.assertTemplateUsed(response, template)
        print('Шаблоны страниц авторизации и URLs совпадают с ожидаемыми.')
