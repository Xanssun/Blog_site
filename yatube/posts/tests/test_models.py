from django.test import TestCase

from posts.models import Group, Post, User

from ..constants import TESTS_NUMBER


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='User')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_post_have_correct_object_names(self):
        """Проверяем, что у модели post корректно работает __str__."""
        post = PostModelTest.post
        correct_object_name = post.text[:TESTS_NUMBER]
        self.assertEqual(correct_object_name, str(post))

    def test_model_group_have_correct_object_names(self):
        """Проверяем, что у модели group корректно работает __str__."""
        group = PostModelTest.group
        correct_object_name = group.title
        self.assertEqual(correct_object_name, str(group))

    def test_model_comment_have_correct_object_names(self):
        """Проверяем, что у модели comment корректно работает __str__."""
        comment = PostModelTest.group
        correct_object_name = comment.title
        self.assertEqual(correct_object_name, str(comment))

    def test_text_label(self):
        """verbose_name поля совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
            'image': 'Картинка',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)

    def test_text_help_text(self):
        """help_text поля text совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост',
            'image': 'Загрузите картинку',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value)
