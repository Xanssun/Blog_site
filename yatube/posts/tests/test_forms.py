import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Comment, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='User')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Описание группы'
        )
        cls.gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='gif',
            content=cls.gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовая запись',
            group=cls.group,
            image=cls.uploaded
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        post_count = Post.objects.count()
        form_data = {
            "text": "Тестовая запись",
            "group": self.group.id,
            'image': self.uploaded
        }
        self.authorized_client.post(
            reverse("posts:post_create"), data=form_data)
        self.assertEqual(
            Post.objects.latest('pub_date').text, form_data['text']
        )
        Post.objects.latest('pub_date').text
        self.assertEqual(Post.objects.count(), post_count)

    def test_edit_form(self):
        """Проверка измения поста"""
        self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
        post_new_data = {
            'text': 'Другой текст поста',
            'group': self.group.id,
        }
        self.authorized_client.post(
            reverse(
                'posts:post_edit', kwargs={'post_id': self.post.id}
            ), data=post_new_data
        )
        self.assertTrue(Post.objects.filter(
            text=post_new_data['text'],
            group=post_new_data['group'],
        ).exists()
        )

    def test_comment_can_authorized_user_show(self):
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Новый комментарий',
        }
        response = self.authorized_client.post(
            reverse((
                'posts:add_comment'), kwargs={'post_id': f'{self.post.id}'}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse((
            'posts:post_detail'), kwargs={'post_id': f'{self.post.id}'}))
        self.assertTrue(
            Comment.objects.filter(text='Новый комментарий').exists()
        )
        self.assertEqual(Comment.objects.count(), comments_count + 1)
