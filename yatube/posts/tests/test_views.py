from django.contrib.auth import get_user_model
from django import forms
from django.urls import reverse
from django.test import Client, TestCase

from ..forms import PostForm
from ..models import Group, Post

from yatube.settings import LIMIT_POSTS

User = get_user_model()


class PostsViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.author = User.objects.create_user(
            username='views_author',
        )
        cls.group = Group.objects.create(
            title='Тесты',
            slug='views_group',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.author,
            group=cls.group,
        )
        cls.group_check = Group.objects.create(
            title='Тестовое название группы',
            slug='views_slug',
            description='Повсюду тесты',
        )

    def setUp(self):
        self.user = User.objects.create_user(
            username='views_user'
        )
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def asserts_for_tests(self, test_object):
        """Служебные asserts."""
        self.assertEqual(
            test_object.pk,
            self.post.pk
        )
        self.assertEqual(
            test_object.author.username,
            self.post.author.username
        )
        self.assertEqual(
            test_object.text,
            self.post.text
        )
        self.assertEqual(
            test_object.group.title,
            self.group.title
        )

    def test_homepage_shows_correct_context(self):
        """View: index имеет соответствующий
        контекст.
        """
        response = self.authorized_client.get(
            reverse('posts:index')
        )
        self.asserts_for_tests(response.context['page_obj'][0])
        print('Корректный контекст index.')

    def test_group_list_context(self):
        """View: group_posts имеет соответствующий
        контекст.
        """
        response = self.authorized_client.get(
            reverse(
                'posts:group_posts',
                kwargs={'slug': self.group.slug}
            )
        )

        self.assertEqual(
            response.context.get('group').slug, self.group.slug
        )
        self.assertEqual(
            response.context.get('group').pk, self.group.id
        )
        self.assertEqual(
            response.context.get('group').title,
            self.group.title
        )
        self.assertEqual(
            response.context.get('group').description,
            self.group.description
        )
        print('Корректный контекст group_posts.')

    def test_profile_show_correct_context(self):
        """View: profile  имеет соответствующий
        контекст.
        """
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.author.username}
            )
        )
        self.asserts_for_tests(response.context['page_obj'][0])
        print('Корректный контекст profile.')

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
        print('Корректный контекст post_detail.')

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
                f_field = response.context.get('form')\
                    .fields.get(value)
                self.assertIsInstance(f_field, values)
        print('Корректные контексты post_create и post_edit.')

    def test_new_post_appearance(self):
        """Проверка появления новой записи на всех
        страницах.
        """
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
        print('Везде правильно отображается новая запись.')

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
        print('Новая запись в чужих группах отсутствует.')

    def test_pages_uses_correct_template(self):
        """Проверка, что URL-адрес использует нужный шаблон."""
        template_pages = {
            '/': 'posts/index.html',
            '/group/views_group/': 'posts/group_list.html',
            '/create/': 'posts/post_create.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            f'/posts/{self.post.id}/edit/':
                'posts/post_detail.html',
            '/profile/views_user/': 'posts/profile.html',
        }

        for url_address, templates in template_pages.items():
            with self.subTest(address=url_address):
                response = self.authorized_client.get(
                    url_address,
                    follow=True
                )
                self.assertTemplateUsed(response, templates)
        print('URLs соответствуют своим шаблонам.')


class PaginatorViewsTest(TestCase):
    """Тестирование паджинатора."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.posts = []
        cls.author = User.objects.create_user(
            username='paginator_author'
        )
        cls.group = Group.objects.create(
            title='Заголовок для паджинатора',
            slug='paginator_views',
            description='Описание для паджинатора',
        )

        for paginator_post in range(21):
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
        response = self.authorized_client.get(
            reverse('posts:index')
        )
        self.assertEqual(
            len(response.context['page_obj']), LIMIT_POSTS
        )
        print('Паджинатор отображает не более 10 постов.')
