from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from django.core.cache import cache

from yatube.settings import LIMIT_POSTS
from posts.models import Group, Post, Comment

User = get_user_model()


class PaginatorViewsTest(TestCase):
    """Тестирование паджинатора."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        RANGE_SIZE = 21
        cls.posts = []
        cls.author = User.objects.create_user(
            username='paginator_author'
        )
        cls.group = Group.objects.create(
            title='Заголовок для паджинатора',
            slug='paginator_views',
            description='Описание для паджинатора',
        )

        for paginator_post in range(RANGE_SIZE):
            cls.posts.append(
                Post(
                    author=cls.author,
                    group=cls.group,
                    text=f'{paginator_post}',
                )
            )
        Post.objects.bulk_create(cls.posts)

    def setUp(self):
        self.user = User.objects.create_user(
            username='paginator_user'
        )
        self.authorized_client = self.client
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_page_has_ten_posts(self):
        """Паджинатор отображает не более 10 постов."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), LIMIT_POSTS)
