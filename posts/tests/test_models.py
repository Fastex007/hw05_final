from posts.lib.MyTestCase import MyTestCase


class PostModelTest(MyTestCase):
    def test_verbose_name_post(self):
        """verbose_name в полях совпадает с ожидаемым.

        Модель Post
        """
        self.assertEqual(
            PostModelTest.test_post._meta.get_field('text').verbose_name,
            'Текст'
        )

    def test_verbose_name_group(self):
        """verbose_name в полях совпадает с ожидаемым.

        Модель Group
        """
        self.assertEqual(
            PostModelTest.test_group._meta.get_field('title').verbose_name,
            'Название'
        )

    def test_verbose_name_comment(self):
        """verbose_name в полях совпадает с ожидаемым.

        Модель Comment
        """
        field_verboses = {
            'text': 'Текст комментария',
            'created': 'Дата комментария',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    PostModelTest.test_comment._meta.get_field(
                        value
                    ).verbose_name,
                    expected
                )

    def test_help_text_post(self):
        """help_text в полях совпадает с ожидаемым.

        Модель Post
        """
        self.assertEqual(
            PostModelTest.test_post._meta.get_field('text').help_text,
            'Текст публикации'
        )

    def test_help_text_group(self):
        """help_text в полях совпадает с ожидаемым.

        Модель Group
        """
        self.assertEqual(
            PostModelTest.test_group._meta.get_field('title').help_text,
            'Группа, в которой может быть опубликован текст'
        )

    def test_help_text_comment(self):
        """help_text в полях совпадает с ожидаемым.

        Модель Comment
        """
        self.assertEqual(
            PostModelTest.test_comment._meta.get_field('text').help_text,
            'Введите текст комментария'
        )

    def test_str_post(self):
        """Проверяем, правильно ли работает метод __str__ модели Post."""
        self.assertEquals(PostModelTest.test_post.__str__(),
                          'Тестовый текст,')

    def test_str_group(self):
        """Проверяем, правильно ли работает метод __str__ модели Group."""
        self.assertEquals(PostModelTest.test_group.__str__(),
                          'Тестовая группа')

    def test_str_comment(self):
        """Проверяем, правильно ли работает метод __str__ модели Comment."""
        self.assertEquals(
            PostModelTest.test_comment.__str__(),
            f'{PostModelTest.test_user.username} '
            f'{PostModelTest.test_comment.text[:15]}'
        )

    def test_str_follow(self):
        """Проверяем, правильно ли работает метод __str__ модели Follow."""
        self.assertEquals(
            PostModelTest.test_following.__str__(),
            f'{PostModelTest.test_user.username} -> '
            f'{PostModelTest.test_author.username}'
        )
