from http import HTTPStatus

from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User


class PostURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

    def setUp(self):
        self.user = User.objects.create_user(username='User')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()
        self.post = Post.objects.create(
            author=self.user,
            group=self.group,
            text='Тестовый пост',
        )

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = (
            ('/', 'posts/index.html'),
            (f'/group/{self.group.slug}/', 'posts/group_list.html'),
            (f'/profile/{self.user.username}/', 'posts/profile.html'),
            (f'/posts/{self.post.id}/', 'posts/post_detail.html'),
            (f'/posts/{self.post.id}/edit/', 'posts/create_post.html'),
            ('/create/', 'posts/create_post.html'),
            ('/follow/', 'posts/follow.html'),
        )
        for address, template in templates_url_names:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_guest_url_code_200(self):
        """Страницы доступны любому пользователю."""
        guest_url = (
            '/',
            f'/group/{self.group.slug}/',
            f'/profile/{self.user.username}/',
            f'/posts/{self.post.id}/'
        )
        for address in guest_url:
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK,
                                 f'статус код страницы {address} не 200')

    def test_unexisting_page_url_code_404(self):
        """Страница /unexisting_page/ не доступна."""
        response = self.authorized_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND,
                         'статус код страницы /unexisting_page/ не 404')
        self.assertTemplateUsed(response, 'core/404.html')

    def test_authorized_url_code_200(self):
        """Страницы доступны авторизованному пользователю."""
        authorized_url = (
            '/create/',
            f'/posts/{self.post.id}/edit/',
            '/follow/'
        )
        for address in authorized_url:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK,
                                 f'статус код страницы {address} не 200')

    def test_authorized_url_redirect_anonymous_on_admin_login(self):
        """Страницы перенаправит анонимного
        пользователя на страницу логина.
        """
        authorized_url = (
            '/create/',
            '/follow/'
        )
        url_2 = reverse('users:login')
        for address in authorized_url:
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertRedirects(response, f'{url_2}?next={address}')

    def test_edit_url_redirect_not_author_on_post_detail(self):
        """Страница по адресу f'/posts/{self.post.id перенаправит не автора
        на страницу просмотра поста.
        """
        self.user_2 = User.objects.create_user(username='Вася')
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(self.user_2)
        cache.clear()
        response = self.authorized_client_2.get(
            f'/posts/{self.post.id}/edit/', follow=True)
        self.assertRedirects(response, f'/posts/{self.post.id}/')
