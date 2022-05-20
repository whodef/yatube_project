from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.core.cache import cache

from posts.models import Post

User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.authorized_client = Client()
        cls.user = User.objects.create(username='cache_test')

    def test_cache_index_page(self):
        """Тест работы кэша."""
        post = Post.objects.create(author=self.user, text="Тестим кэш")

        url = reverse("posts:index")

        response = self.authorized_client.get(url)
        post.delete()
        old_response = self.authorized_client.get(url)
        self.assertEqual(response.content, old_response.content)

        cache.clear()
        new_response = self.authorized_client.get(url)
        self.assertNotEqual(old_response.content, new_response.content)
