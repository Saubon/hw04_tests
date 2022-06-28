from django import forms
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostViewTests(TestCase):
    """Создаем тестовые посты и группы"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='SomeGuy')
        cls.group = Group.objects.create(
            title='Группа ненавистников графа',
            slug='tolstoisucks',
            description='Задолбал за курс'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост не обязан быть интересным. Sorry',
            group=cls.group,
        )

    def setUp(self):
        """Создаем клиент зарегистрированного пользователя"""
        self.authorized_client = Client()
        self.authorized_client.force_login(PostViewTests.user)
        cache.clear()

    def test_paginator_correct_context(self):
        """Шаблоны index, group_list и profile с корректным пагинатором"""
        paginator_objects = []
        for i in range(1, 18):
            new_post = Post(
                author=PostViewTests.user,
                text='Тестовый пост ' + str(i),
                group=PostViewTests.group
            )
            paginator_objects.append(new_post)
        Post.objects.bulk_create(paginator_objects)
        paginator_data = {
            'index': reverse('posts:index'),
            'group': reverse(
                'posts:group_list',
                kwargs={'slug': PostViewTests.group.slug}
            ),
            'profile': reverse(
                'posts:profile',
                kwargs={'username': PostViewTests.user.username}
            )
        }
        for paginator_place, paginator_page in paginator_data.items():
            with self.subTest(paginator_place=paginator_place):
                response_page_1 = self.authorized_client.get(paginator_page)
                response_page_2 = self.authorized_client.get(
                    paginator_page + '?page=2'
                )
                self.assertEqual(len(
                    response_page_1.context['page_obj']),
                    10
                )
                self.assertEqual(len(
                    response_page_2.context['page_obj']),
                    8
                )

    def test_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом"""
        response_index = self.authorized_client.get(reverse('posts:index'))
        page_index_context = response_index.context
        self.assertEqual(page_index_context)

    def test_group_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом"""
        response_group = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': PostViewTests.group.slug}
            )
        )
        task_group = response_group.context['group']
        self.assertEqual(task_group, PostViewTests.group)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response_post_detail = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostViewTests.post.pk}
            )
        )
        page_post_detail_context = response_post_detail.context
        self.assertEqual(page_post_detail_context,PostViewTests.post)

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом"""
        response_profile = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': PostViewTests.user.username}
            )
        )
        task_profile = response_profile.context['author']
        self.assertEqual(task_profile, PostViewTests.user)

    def test_create_post_page_show_correct_context(self):
        """Шаблон create_post (create) сформирован с правильным контекстом"""
        response = self.authorized_client.get(reverse('posts:create_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон create_post (edit) сформирован с правильным контекстом"""
        response = self.authorized_client.get(
            reverse('posts:update_post',
                    kwargs={'post_id': PostViewTests.post.pk})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)
