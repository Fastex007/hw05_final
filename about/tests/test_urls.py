from posts.lib.MyTestCase import MyTestCase


class StaticURLTests(MyTestCase):
    def test_page_technologies(self):
        """Страница /about/tech/ доступна всем"""
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, 200)

    def test_page_about_author(self):
        """Страница /about/author/ доступна"""
        response = self.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, 200)
