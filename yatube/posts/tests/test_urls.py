from http import HTTPStatus

from django.test import Client, TestCase

from ..models import Group, Post, User


class PostsURLsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(
            username='any_author',
            email='any@user.com',
            password='anypassword',

        )
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='urls_group_slug',
            description='Тестовое описание для URL',
        )
        cls.post = Post.objects.create(
            group=cls.group,
            author=cls.author,
            text='Какой-то текст',
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='urls_user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_home_url_exists(self):
        """Проверка главной страницы."""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_group_url_exists(self):
        """Проверка /group/urls_group_slug/."""
        response = self.guest_client.get('/group/urls_group_slug/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_profile_url_for_non_authorized(self):
        """Проверка доступности страницы пользователя."""
        response = self.guest_client.get('/profile/urls_user/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_url_exists(self):
        """Проверка доступности страницы записи."""
        response = self.guest_client.get('/posts/1/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_url_redirect_anonymous(self):
        """Редирект /create/ для анонимного пользователя."""
        response = self.guest_client.get('/create/', follow=True)
        # Без статус-кода
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_create_url_for_authorized(self):
        """Проверка создания записи для авторизованных."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        """Проверка соответствия шаблонов к их URL'ам."""
        templates_urls = {
            '/': 'posts/index.html',
            '/group/urls_group_slug/': 'posts/group_list.html',
            '/create/': 'posts/post_create.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
            f'/profile/{self.author.username}/': 'posts/profile.html',
        }

        for address, template in templates_urls.items():
            with self.subTest(address=template):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_404_url_exists(self):
        """Проверка страницы Not Found."""
        response = self.guest_client.get('/group/urls_test/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
