from django.test import Client, TestCase


class StaticPagesURLTests(TestCase):
    """Проверка статических страниц."""
    def setUp(self):
        self.guest_client = Client()

    def test_statics_pages(self):
        templates_static_urls = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }

        for address, template in templates_static_urls.items():
            with self.subTest(address=template):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)
        print('Статические шаблоны страниц и URLs совпадают с ожидаемыми.')
