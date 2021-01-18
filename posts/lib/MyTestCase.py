import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase

from posts.models import Comment, Follow, Group, Post, User


class MyTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

        cls.test_user = User.objects.create_user(
            username='test_user',
            password='123456'
        )

        cls.test_author = User.objects.create_user(
            username='test_author',
            password='123456'
        )

        cls.test_following = Follow.objects.create(
            user=cls.test_user,
            author=cls.test_author,
        )

        cls.non_author = User.objects.create_user(
            username='non_author',
            password='123456'
        )

        cls.non_follower = User.objects.create_user(
            username='non_follower',
            password='123456'
        )

        cls.test_group = Group.objects.create(
            id=1,
            title='Тестовая группа',
            slug='test_group',
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

        cls.test_post = Post.objects.create(
            id=1,
            group=cls.test_group,
            text='Тестовый текст, который надо чтобы был длиннее пятнадцати '
                 'символов, а то ничего не получится. '
                 'один два три четрые пять',
            author=cls.test_user,
            image=cls.uploaded,
        )

        cls.test_comment = Comment.objects.create(
            id=1,
            post=cls.test_post,
            author=cls.test_user,
            text='Тестовый комментарий',
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()

        self.authorized_client = Client()
        self.authorized_client.force_login(self.test_user)

        self.author_client = Client()
        self.author_client.force_login(self.test_author)

        self.non_author_client = Client()
        self.non_author_client.force_login(self.non_author)

        self.non_follower_client = Client()
        self.non_follower_client.force_login(self.non_follower)
