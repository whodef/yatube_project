import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django import forms
from django.urls import reverse
from django.test import Client, TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from yatube import settings
from yatube.settings import LIMIT_POSTS
from posts.forms import PostForm
from posts.models import Group, Post, Comment

User = get_user_model()


class PostsViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=tempfile.gettempdir())

        cls.author = User.objects.create_user(
            username='views_author',
        )
        cls.group = Group.objects.create(
            title='Тесты',
            slug='views_group',
            description='Тестовое описание',
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text='Тестовый пост',
            image=cls.uploaded,
        )
        cls.group_check = Group.objects.create(
            title='Тестовое название группы',
            slug='views_slug',
            description='Повсюду тесты',
        )
        cls.post_id = cls.post.id

    def setUp(self):
        self.user = User.objects.create_user(username='views_user')
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def service_asserts(self, test_object):
        """Служебные asserts."""
        self.assertEqual(test_object.pk, self.post.pk)
        self.assertEqual(
            test_object.author.username, self.post.author.username)
        self.assertEqual(test_object.group.title, self.group.title)
        self.assertEqual(test_object.text, self.post.text)

    def service_asserts_group(self, test_object):
        """Служебные asserts для тестирования групп."""
        self.assertEqual(test_object.pk, self.group.id)
        self.assertEqual(test_object.slug, self.group.slug)
        self.assertEqual(test_object.title, self.group.title)
        self.assertEqual(
            test_object.description, self.group.description)

    def test_homepage_and_profile_show_correct_contexts(self):
        """View: index и profile получают соответствующий контекст."""
        cache.clear()
        response_types = [
            self.authorized_client.get(reverse('posts:index')),
            self.authorized_client.get(
                reverse(
                    'posts:profile',
                    kwargs={'username': self.author.username}
                )
            )
        ]

        for response in response_types:
            post_object = response.context['page_obj'].object_list[0]
            self.service_asserts(post_object)

    def test_group_list_context(self):
        """View: group_posts имеет соответствующий контекст."""
        response = self.authorized_client.get(
            reverse(
                'posts:group_posts',
                kwargs={'slug': self.group.slug}
            )
        )
        self.service_asserts_group(response.context['group'])

    def test_post_detail_show_correct_context(self):
        """View: post_detail имеет соответствующий контекст."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            )
        )
        self.assertEqual(
            response.context.get('post').id, self.post.id
        )

    def test_create_post_correct_context(self):
        """View: post_create и post_edit имеют соответствующий
        контекст.
        """
        response = self.authorized_client.get(
            reverse('posts:post_create')
        )
        self.assertIsInstance(
            response.context.get('form'), PostForm
        )

        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }

        for value, values in form_fields.items():
            with self.subTest(value=value):
                f_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(f_field, values)

    def test_new_post_appearance(self):
        """Проверка появления новой записи на всех страницах."""
        # На главной
        response = self.authorized_client.get(
            reverse('posts:index')
        )
        self.assertEqual(
            response.context['page_obj'][0], self.post
        )

        # В группе
        response = self.authorized_client.get(
            reverse(
                'posts:group_posts',
                kwargs={'slug': 'views_group'}
            )
        )

        # В профиле пользователя
        post_in_profile = response.context['page_obj'][0]
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.author.username}
            )
        )
        self.assertEqual(post_in_profile, self.post)

        context = {
            response.context['page_obj'][0]: self.post,
            post_in_profile.group: self.group,
        }

        for entity, entities in context.items():
            with self.subTest(element=entity):
                self.assertEqual(entity, entities)

    def test_comment_show_correct_context_on_post_page(self):
        """Комменты правильно отображаются на странице поста."""
        text = 'Текст комментария'

        Comment.objects.create(
            post=self.post,
            author=self.author,
            text=text,
        )

        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        context = response.context['comments'].first()
        context_detail = {
            context.post.id: self.post.id,
            context.text: text,
            context.author.username: self.author.username,
        }

        for context, expected in context_detail.items():
            with self.subTest(context=context):
                self.assertEqual(context, expected)

    def test_post_not_found(self):
        """Проверка отсутствия записи не в той группе."""
        response = self.authorized_client.get(
            reverse(
                'posts:group_posts',
                kwargs={'slug': self.group_check.slug}
            )
        )
        context = response.context['page_obj'].object_list
        self.assertNotIn(self.post, [context])

    def test_pages_uses_correct_template(self):
        """Проверка, что URL-адрес использует нужный шаблон."""
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

        template_pages = {
            '/': 'posts/index.html',
            '/group/views_group/': 'posts/group_list.html',
            '/create/': 'posts/post_create.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            f'/posts/{self.post.id}/edit/': 'posts/post_edit.html',
            '/profile/views_user/': 'posts/profile.html',
        }

        for url_address, templates in template_pages.items():
            with self.subTest(address=url_address):
                response = self.authorized_client.get(
                    url_address,
                    follow=True
                )
                self.assertTemplateUsed(response, templates)


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
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_page_has_ten_posts(self):
        """Паджинатор отображает не более 10 постов."""
        cache.clear()
        response = self.authorized_client.get(
            reverse('posts:index')
        )

        self.assertEqual(len(response.context['page_obj']), LIMIT_POSTS)
