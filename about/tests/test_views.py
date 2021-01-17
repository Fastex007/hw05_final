from django.urls import reverse

from posts.lib.MyTestCase import MyTestCase


class StaticURLTests(MyTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.templates_pages_names = {
            'author.html': reverse('about:author'),
            'tech.html': (reverse('about:tech')),
        }

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for template, reverse_name in (
                StaticURLTests.templates_pages_names.items()
        ):
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_page_technologies(self):
        """Страница tech/ доступна по about:tech всем"""
        response = self.guest_client.get(reverse('about:tech'))
        self.assertEqual(response.status_code, 200)

    def test_page_about_author(self):
        """Страница author/ доступна по about:author всем"""
        response = self.guest_client.get(reverse('about:author'))
        self.assertEqual(response.status_code, 200)
