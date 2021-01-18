from django.urls import reverse

from posts.lib.MyTestCase import MyTestCase


class PostsURLTests(MyTestCase):
    def test_home_url_exists_at_desired_location(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_group_posts_url_exists_at_desired_location(self):
        """Страница /group/test_group/ доступна любому пользователю."""
        response = self.guest_client.get(
            reverse('group',
                    kwargs={'slug': PostsURLTests.test_group.slug})
        )
        self.assertEqual(response.status_code, 200)

    def test_new_post_url_exists_at_desired_location_authorized(self):
        """Страница /new/ доступна только авторизованному пользователю."""
        response = self.authorized_client.get(reverse('new_post'))
        self.assertEqual(response.status_code, 200)

    def test_group_posts_url_redirect_anonymous(self):
        """Страница /new/ перенаправляет анонимного пользователя."""
        response = self.guest_client.get(reverse('new_post'))
        self.assertEqual(response.status_code, 302)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'index.html': '/',
            'group.html': '/group/test_group/',
            'new_post.html': '/new/',
        }
        for template, reverse_name in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)


class ProfileURLTests(MyTestCase):
    def test_profile_exists_at_desired_location(self):
        """Страница /<username>/ доступна любому пользователю."""
        response = self.guest_client.get(
            reverse('profile',
                    kwargs={'username': PostsURLTests.test_user.username})
        )
        self.assertEqual(response.status_code, 200)

    def test_current_post_exists_at_desired_location(self):
        """Страница /<username>/<post_id>/ доступна любому пользователю."""
        response = self.guest_client.get(
            reverse('post',
                    kwargs={'username': PostsURLTests.test_user.username,
                            'post_id': PostsURLTests.test_post.id})
        )
        self.assertEqual(response.status_code, 200)

    def test_edit_post_url_redirect_anonymous(self):
        """Страница /<username>/<post_id>/edit/.

        Перенаправляет анонимного пользователя.
        """
        response = self.guest_client.get(
            reverse('post_edit',
                    kwargs={'username': PostsURLTests.test_user.username,
                            'post_id': PostsURLTests.test_post.id})
        )
        self.assertEqual(response.status_code, 302)

    def test_edit_post_url_redirect_non_author(self):
        """Страница /<username>/<post_id>/edit/ перенаправляет НЕ автора."""
        response = self.non_author_client.get(
            reverse('post_edit',
                    kwargs={'username': PostsURLTests.test_user.username,
                            'post_id': PostsURLTests.test_post.id})
        )
        self.assertEqual(response.status_code, 302)

    def test_edit_post_exists_at_desired_location_authorized(self):
        """Страница /<username>/<post_id>/edit/ доступна для автора."""
        response = self.authorized_client.get(
            reverse('post_edit',
                    kwargs={'username': PostsURLTests.test_user.username,
                            'post_id': PostsURLTests.test_post.id})
        )
        self.assertEqual(response.status_code, 200)

    def test_edit_post_page_uses_correct_template(self):
        """URL-адрес использует шаблон new_post.html."""
        response = self.authorized_client.get(
            reverse('post_edit',
                    kwargs={'username': PostsURLTests.test_user.username,
                            'post_id': PostsURLTests.test_post.id})
        )
        self.assertTemplateUsed(response, 'new_post.html')

    def test_edit_post_page_non_author_redirect(self):
        """Правильный редирект НЕ автора при попытке отредактировать."""
        response = self.non_author_client.get(
            reverse('post_edit',
                    kwargs={'username': PostsURLTests.test_user.username,
                            'post_id': PostsURLTests.test_post.id}),
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'post',
                kwargs={
                    'username': PostsURLTests.test_user.username,
                    'post_id': PostsURLTests.test_post.id
                }
            )
        )

    def test_page_not_found_works_correct(self):
        """Запрос к неизвестной странице возвращает статус 404."""
        response = self.guest_client.get('/unknown_ulr/')
        self.assertEqual(response.status_code, 404)
