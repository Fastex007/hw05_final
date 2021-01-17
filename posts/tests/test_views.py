import time

from django import forms
from django.core.cache import cache
from django.urls import reverse

from posts.lib.MyTestCase import MyTestCase
from posts.models import Comment, Follow, Post
from posts.views import POSTS_PER_PAGE


class PostsPagesTests(MyTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.templates_pages_names = {
            'index.html': reverse('index'),
            'group.html': (
                reverse('group', kwargs={'slug': 'test_group'})
            ),
            'new_post.html': reverse('new_post'),
        }

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for template, reverse_name in (
                PostsPagesTests.templates_pages_names.items()
        ):
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def check_index_context(self, response):
        """Проверяем контекст index.

        Вынесено в отдельную функцию чтобы не дублировать код
        """
        post_text_0 = response.context.get('page')[0].text
        post_author_0 = response.context.get('page')[0].author
        post_group_0 = response.context.get('page')[0].group
        # post_image_0 = response.context.get('page')[0].image

        self.assertEqual(post_text_0, PostsPagesTests.test_post.text)
        self.assertEqual(post_author_0, PostsPagesTests.test_user)
        self.assertEqual(post_group_0, PostsPagesTests.test_group)
        # Тут post_image_0 = 'posts/small.gif'
        # а PostsPagesTests.uploaded.name = 'small.gif'
        # а settings.MEDIA_ROOT = рандомное название временных папок
        # Как быть ?
        # self.assertEqual(
        # post_image_0, 'posts/'+PostsPagesTests.uploaded.name)
        self.assertContains(response, '<img')

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('index'))
        self.check_index_context(response)

    def test_group_pages_show_correct_context(self):
        """Шаблон group сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': 'test_group'})
        )
        group = response.context.get('group')
        self.assertEqual(group.title, 'Тестовая группа')
        self.assertEqual(group.slug, 'test_group')
        # Провряем на месте ли оказался новый пост
        self.check_index_context(response)
        self.assertContains(response, '<img')

    def test_new_post_page_show_correct_context(self):
        """Шаблон new_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('new_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)


class PaginatorViewsTest(MyTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        for i in range(12):
            Post.objects.create(
                group=cls.test_group,
                text=f'Тестовый текст {i}',
                author=cls.test_user,
            )

    def test_first_page_contains_ten_records(self):
        """Проверяем работу пагинации на главной страницу.

        Должно быть 10 записей
        """
        response = self.client.get(reverse('index'))
        self.assertEqual(len(response.context.get('page').object_list),
                         POSTS_PER_PAGE)

    def test_first_page_posts_contains(self):
        """Проверяем правильные ли записи выводятся на главную страницу.

        На первой странице пагинации
        """
        response = self.client.get(reverse('index'))
        for i in range(POSTS_PER_PAGE-1, 0):
            self.assertEqual(response.context.get('page').object_list[i].text,
                             f'Тестовый текст {i}')

    def test_second_page_contains_three_records(self):
        """Проверяем количество записей на второй странице пагинации.

        Должно быть 3 записи
        """
        response = self.client.get(reverse('index') + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list), 3)


class ProfileTests(MyTestCase):
    def test_edit_correct_form_fields(self):
        """Шаблон /edit/ сформирован с правильными полями."""
        response = self.authorized_client.get(
            reverse('post_edit',
                    kwargs={'username': ProfileTests.test_user.username,
                            'post_id': ProfileTests.test_post.id})
        )

        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
            'image': forms.fields.ImageField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_correct_context(self):
        """Шаблон /edit/ сформирован с правильными контекстом."""
        response = self.authorized_client.get(
            reverse('post_edit',
                    kwargs={'username': ProfileTests.test_user.username,
                            'post_id': ProfileTests.test_post.id})
        )

        form = response.context['form']
        from_data = form.initial

        self.assertEqual(from_data['text'], ProfileTests.test_post.text)
        self.assertEqual(from_data['group'], ProfileTests.test_group.id)

    def test_profile_correct_context(self):
        """Шаблон /<username>/ сформирован с правильными контекстом."""
        response = self.authorized_client.get(
            reverse('profile',
                    kwargs={'username': ProfileTests.test_user.username})
        )

        post_text_0 = response.context.get('page')[0].text
        post_author_0 = response.context.get('page')[0].author
        post_group_0 = response.context.get('page')[0].group
        post_image_0 = response.context.get('page')[0].image

        self.assertEqual(post_text_0, ProfileTests.test_post.text)
        self.assertEqual(post_author_0, ProfileTests.test_user)
        self.assertEqual(post_group_0, ProfileTests.test_group)
        self.assertEqual(post_image_0, ProfileTests.test_post.image)
        self.assertContains(response, '<img')

    def test_one_post_correct_context(self):
        """Шаблон /<username>/<post_id>/.

        Сформирован с правильным контекстом
        """
        response = self.authorized_client.get(
            reverse('post',
                    kwargs={'username': ProfileTests.test_user.username,
                            'post_id': ProfileTests.test_post.id})
        )

        self.assertEqual(response.context.get('post').group,
                         ProfileTests.test_group)
        self.assertEqual(response.context.get('post').author.username,
                         ProfileTests.test_user.username)
        self.assertEqual(response.context.get('post').text,
                         ProfileTests.test_post.text)
        self.assertContains(response, '<img')


class CacheTests(MyTestCase):
    def test_index_cache_works_correct(self):
        """Кэш главной страницы работает корректно."""
        response = self.authorized_client.get(reverse('index'))

        self.assertNotContains(response, 'Второй пост')
        self.assertContains(response, CacheTests.test_post.text)

        response = self.authorized_client.post(
            reverse('post_edit',
                    kwargs={
                        'username': CacheTests.test_user.username,
                        'post_id': CacheTests.test_post.id
                    }),
            {'text': 'Второй пост'},
            follow=True
        )
        self.assertEqual(response.status_code, 200)

        response = self.authorized_client.get(reverse('index'))
        self.assertNotContains(response, 'Второй пост')
        self.assertContains(response, self.test_post.text)

        time.sleep(21)

        response_url_index = self.authorized_client.get(reverse('index'))
        self.assertContains(response_url_index, 'Второй пост')

    def test_cache_key(self):
        """Проверка ключа кэша"""
        response = self.client.get(reverse('index'))
        cache_content = response.context.get('page').object_list[0].text
        cache.set('index_page', cache_content, 1)
        self.assertEqual(cache.get('index_page'), CacheTests.test_post.text)


class FollowingTests(MyTestCase):
    def test_authorized_user_can_follow(self):
        """Авторизованный пользователь может подписываться на автора."""
        response = self.authorized_client.get(
            reverse(
                'profile_follow',
                kwargs={'username': FollowingTests.test_author}),
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            Follow.objects.filter(user=FollowingTests.test_user,
                                  author=FollowingTests.test_author).exists()
        )

    def test_authorized_user_can_unfollow(self):
        """Авторизованный пользователь может отписываться от автора."""
        Follow.objects.create(user=FollowingTests.test_user,
                              author=FollowingTests.test_author)
        response = self.authorized_client.get(
            reverse('profile_unfollow',
                    kwargs={'username': FollowingTests.test_author}),
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            Follow.objects.filter(user=FollowingTests.test_user,
                                  author=FollowingTests.test_author).exists()
        )

    def test_follow_index_for_follower(self):
        """Новая запись появляется в ленте подписчика."""
        Follow.objects.create(user=FollowingTests.test_author,
                              author=FollowingTests.test_user)
        response = self.author_client.get(reverse('follow_index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, FollowingTests.test_post.text)

    def test_follow_index_for_non_follower(self):
        """Новая запись НЕ появляется в ленте НЕ подписчика."""
        response = self.author_client.get(reverse('follow_index'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, FollowingTests.test_post.text)


class CommentTests(MyTestCase):
    def test_authorized_user_can_comment(self):
        """Авторизованный пользователь может комментировать посты."""
        response = self.authorized_client.post(
            reverse(
                'add_comment',
                kwargs={'username': CommentTests.test_user,
                        'post_id': CommentTests.test_post.id}
            ),
            {'text': 'Тестовый комментарий',
             'author': CommentTests.test_user},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.comment = Comment.objects.last()
        self.assertEqual(self.comment.text, 'Тестовый комментарий')

    def test_non_authorized_user_cant_comment(self):
        """Неавторизованный пользователь не может комментировать посты."""
        self.guest_client.post(
            reverse(
                'add_comment',
                kwargs={'username': CommentTests.test_user,
                        'post_id': CommentTests.test_post.id}
            ),
            {'text': 'Тестовый комментарий',
             'author': CommentTests.test_user},
            follow=True,
        )
        self.assertEqual(Comment.objects.count(), 0)
