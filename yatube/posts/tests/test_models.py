from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post
from yatube.settings import POST_SYMBOLS

User = get_user_model()


class PostModelTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей Post и Group корректно
        работает __str__.
        """
        post = PostModelTests.post
        expected_post_str = post.text[:POST_SYMBOLS]
        self.assertEqual(expected_post_str, str(post))

        group = PostModelTests.group
        expected_group_str = group.title
        self.assertEqual(expected_group_str, str(group))

        print('У моделей Post и Group корректно работает __str__.')

    def test_post_verbose_name(self):
        """verbose_name в полях модели Post совпадает с ожидаемым."""
        post = PostModelTests.post
        field_verbose = {
            'text': 'Текст',
            'group': 'Группа',
            'pub_date': 'pub date',
            'author': 'author',
        }
        for field, expected_value in field_verbose.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)
        print('verbose_name в полях модели Post совпадает с ожидаемым.')

    def test_post_help_text(self):
        """help_text в полях модели Post совпадает с ожидаемым."""
        post = PostModelTests.post
        field_help_texts = {
            'text': 'Добавьте текст для новой записи',
            'group': 'Выберите группу для новой записи',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value)
        print('help_text в полях модели Post совпадает с ожидаемым.')
