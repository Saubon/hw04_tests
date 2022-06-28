from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    """Создаем тестовый пост и группу"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='SomeGuy')
        cls.group = Group.objects.create(
            title='Ненавистники Толстого',
            slug='tolstoisucks',
            description='Задолбал за курс'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Новый пост для проверки'
        )

    def setUp(self):
        """Создаем клиент гостя и зарегистрированного пользователя"""
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostURLTests.user)

    def test_urls_response_auth(self):
        """Проверяем статус страниц для авторизованного пользователя"""
        url_status = {
            reverse('posts:index'): HTTPStatus.OK,
            reverse(
                'posts:group_list',
                kwargs={'slug': PostURLTests.group.slug}
            ): HTTPStatus.OK,
            reverse(
                'posts:profile',
                kwargs={'username': PostURLTests.user.username}
            ): HTTPStatus.OK,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostURLTests.post.pk}
            ): HTTPStatus.OK,
            reverse(
                'posts:update_post',
                kwargs={'post_id': PostURLTests.post.pk}
            ): HTTPStatus.OK,
            reverse('posts:create_post'): HTTPStatus.FOUND,
            '/unexpecting_page/': HTTPStatus.NOT_FOUND,
        }
        for url, status_code in url_status.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_urls_response_guest(self):
        """Проверяем статус страниц для гостя"""
        url_status = {
            reverse('posts:index'): HTTPStatus.OK,
            reverse(
                'posts:group_list',
                kwargs={'slug': PostURLTests.group.slug}
            ): HTTPStatus.OK,
            reverse(
                'posts:profile',
                kwargs={'username': PostURLTests.user.username}
            ): HTTPStatus.OK,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostURLTests.post.pk}
            ): HTTPStatus.OK,
            reverse(
                'posts:update_post',
                kwargs={'post_id': PostURLTests.post.pk}
            ): HTTPStatus.FOUND,
            reverse(
                'posts:create_post',
                kwargs={'/': PostURLTests.post.pk}
            ): HTTPStatus.FOUND,
        }
        for url, status_code in url_status.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_urls_uses_correct_template(self):
        """Проверяем запрашиваемые шаблоны страниц через имена."""
        cache.clear()
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': PostURLTests.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': PostURLTests.user.username}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostURLTests.post.pk}
            ): 'posts/post_detail.html',
            reverse(
                'posts:update_post',
                kwargs={'post_id': PostURLTests.post.pk}
            ): 'posts/create_post.html',
            reverse(
                'posts:create_post',
                kwargs={'/': PostURLTests.post.pk}
            ): 'posts/create_post.html'
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
