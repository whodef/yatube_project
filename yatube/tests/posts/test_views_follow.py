from pprint import pprint

from django.test import Client, TestCase
from django.urls import reverse
from django.core.cache import cache

from posts.models import User, Follow, Post


class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.author = User.objects.create_user(username='author')

        cls.post0 = Post.objects.create(
            text='Какой-то текст.',
            author=cls.author,
        )
        cls.post1 = Post.objects.create(
            text='Снова какой-то текст.',
            author=cls.author,
        )

    def setUp(self):
        self.user = User.objects.create_user(username='user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_authorized_user_cannot_subscribe_on_himself(self):
        """Пользователь имеет возможность подписаться."""
        self.assertFalse(self.user.follower.exists())

        self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.author.username}
            )
        )
        self.assertEqual(self.user.follower.first().author, self.author)

    def test_forbidden_user_subscribe_to_himself(self):
        """Пользователь не может подписаться на себя."""
        author_client = Client()
        author_client.force_login(self.author)

        response = author_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.author.username})
        )
        expected_redirect_url = reverse(
            'posts:profile', kwargs={'username': self.author.username}
        )
        self.assertRedirects(response, expected_redirect_url)

    def test_authorized_user_unsubscribe(self):
        """Пользователь имеет возможность отписаться."""
        Follow.objects.create(user=self.user, author=self.author)
        self.authorized_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.author.username}
            )
        )
        self.assertFalse(self.user.follower.exists())

    def test_new_post_shown_in_feed_subscriber(self):
        """Пост появляется в ленте подписанного пользователя."""
        Follow.objects.create(user=self.user, author=self.author)
        response = self.authorized_client.get(reverse('posts:follow_index'))
        context = response.context.get('page_obj').object_list
        self.assertIn(self.post0, context)

    def test_new_post_doesnt_show_in_feed_unsubscribed(self):
        """Пост не появляется в ленте у неподписанного пользователя."""
        cache.clear()
        unsubscribe = User.objects.create_user(username='unsubscribe_user')
        unsubscribed_client = Client()
        unsubscribed_client.force_login(unsubscribe)

        response = unsubscribed_client.get(reverse('posts:follow_index'))
        context = response.context.get('page_obj').object_list
        self.assertNotIn(self.post1, context)

