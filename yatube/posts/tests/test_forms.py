from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post
from ..forms import PostForm

User = get_user_model()


class PostsFormsTests(TestCase):
    """Тестирование формы поста."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.form = PostForm()
        cls.user = User.objects.create_user(
            username='forms_user'
        )
        cls.group = Group.objects.create(
            title='Заголовок формы',
            slug='forms_group',
            description='Описание формы',
        )
        cls.post = Post.objects.create(
            group=cls.group,
            author=cls.user,
            text='Текст формы',
        )
        cls.group_check = Group.objects.create(
            title='Тестирование формы',
            slug='forms_slug',
            description='Формы, повсюду формы',
        )
        cls.form_data = {
            'group': cls.group.id,
            'text': cls.post.text,
        }

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_new_post(self):
        """Тестирование создания новой записи."""
        count_posts = Post.objects.count()
        context = {
            'group': self.group.id,
            'text': 'Какой-то текст 1',
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=context,
            follow=False
        )
        self.assertEqual(
            Post.objects.latest('id').text, context['text']
        )
        self.assertEqual(
            Post.objects.latest('id').group_id, context['group']
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', args=[self.user])
        )
        self.assertEqual(
            Post.objects.count(), count_posts + 1
        )

    def test_editing_post(self):
        """Тестирование редактирования записи."""
        count_posts = Post.objects.count()
        latest_post_id = Post.objects.latest('id').id
        context = {
            'group': self.group_check.id,
            'text': 'Какой-то текст 2',
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': latest_post_id}
            ),
            data=context,
            follow=True
        )
        self.assertRedirects(
            response, reverse(
                'posts:post_detail',
                kwargs={'post_id': latest_post_id}
            )
        )
        self.assertEqual(
            Post.objects.count(), count_posts
        )
        self.assertTrue(Post.objects.filter(
            id=latest_post_id, text=context['text'],
            group=context['group']).exists()
                        )

    def test_guest_client_cannot_create_post(self):
        """Тестирование невозможности создания записи без
        регистрации.
        """
        post_count = Post.objects.count()

        response = self.client.post(
            reverse('posts:post_create'),
            data={
                'group': 1,
                'text': "Guest post",
            },
            follow=False
        )

        self.assertRedirects(
            response, '%s?next=/create/' % reverse('login')
        )

        self.assertEqual(Post.objects.count(), post_count)

    def test_fail_to_edit_other_person_post(self):
        """Тестирование невозможности редактировать чужие записи."""
        user = User.objects.create(
            username='forms_some_other_user'
        )
        auth_other_user = Client()
        auth_other_user.force_login(user)

        response = auth_other_user.post(
            reverse('posts:post_edit', args=[self.post.pk]),
            data=self.form_data,
            follow=False
        )

        self.assertTrue(HTTPStatus.FORBIDDEN, response.status_code)

    def test_post_help_text(self):
        """Coverage-зависимость. Тестирование text_field и
        group_field.
        """
        response = PostsFormsTests.post
        fields_help_texts = {
            'group': 'Выберите группу для новой записи',
            'text': 'Добавьте текст для новой записи',
        }

        for field, fields in fields_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    response._meta.get_field(field).help_text, fields
                )
