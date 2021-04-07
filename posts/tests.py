from django.test import TestCase, Client, override_settings
from django.contrib.auth import get_user_model
from .models import Post, Group, User, Follow
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.images import ImageFile
from django.core.cache import cache


User = get_user_model()


class ProfileTest(TestCase):

    def setUp(self):
        """
        Регистрация пользователя и создание новой записи
        """
        self.client = Client()
        self.user = User.objects.create_user(username='sarah')
        self.post = Post.objects.create(text="test1", author=self.user)

    def test_profile(self):
        """
        Проверка - после регистрации пользователя
        создается его персональная страница (profile)
        """
        self.client.force_login(self.user)
        response = self.client.get('/sarah/')
        self.assertEqual(response.status_code, 200)

    def test_new(self):
        """
        Проверка - авторизованный пользователь
        может опубликовать пост (new)
        """
        self.client.force_login(self.user)
        response = self.client.post(
            "/new/",
            {"text": self.post.text}, follow=True
        )
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        """
        Проверка - неавторизованный посетитель не может
        опубликовать пост и его редиректит на страницу входа
        """
        response = self.client.get('/new/')
        self.assertRedirects(response, '/auth/login/?next=/new/')

    def test_new_entry(self):
        """
        Проверка - после публикации поста новая запись
        появляется на главной странице сайта (index),
        на персональной странице пользователя (profile),
        и на отдельной странице поста (post)
        """
        self.client.force_login(self.user)
        response = self.client.get('/')
        self.assertContains(response, 'test1')
        response = self.client.get('/sarah/')
        self.assertContains(response, 'test1')
        response = self.client.get('/sarah/1/')
        self.assertContains(response, 'test1')

    @override_settings(CACHES=settings.TEST_CACHES)
    def test_user_edit_post(self):
        """
        Проверка - авторизованный пользователь может
        отредактировать свой пост и его содержимое
        изменится на всех связанных страницах
        """
        self.client.force_login(self.user)
        new_text = 'Test'
        self.client.post('/sarah/1/edit', {'text': new_text})
        response = self.client.get('/')
        self.assertContains(response, new_text)
        response = self.client.get('/sarah/')
        self.assertContains(response, new_text)
        response = self.client.get('/sarah/1/')
        self.assertContains(response, new_text)

    def test_not_found(self):
        """
        Проверка - возвращает сервер код 404,
        если страница не найдена
        """
        response = self.client.get("/user/1/")
        self.assertEqual(response.status_code, 404)
        response = self.client.get("/user/")
        self.assertEqual(response.status_code, 404)


class ImageTest(TestCase):

    def setUp(self):
        """
        Регистрация пользователя, создание новой группы
        и создание новой записи с картинкой
        """
        self.client = Client()
        self.user = User.objects.create_user(username='sarah')
        self.group = Group.objects.create(
            title='foo',
            slug='foo',
            description='foo'
        )
        self.post = Post.objects.create(text="test1", author=self.user)
        small_gif = (
                b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
                b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
                b'\x02\x4c\x01\x00\x3b'
        )
        image = SimpleUploadedFile(
            'small.gif',
            small_gif,
            content_type='image/gif'
        )
        self.client.force_login(self.user)
        with ImageFile(image) as fp:
            self.client.post(
                '/sarah/1/edit',
                {'text': self.post.text, 'group': self.group.id, 'image': fp}
            )

    def test_image1(self):
        """
        Проверяем страницу конкретной записи с картинкой:
        на странице есть тег <img>
        """
        self.client.force_login(self.user)
        response = self.client.get('/sarah/1/')
        self.assertContains(response, 'img')

    def test_image2(self):
        """
        Проверяем, что на главной странице, на странице профайла
        и на странице группы пост с картинкой отображается
        корректно, с тегом <img>
        """
        response = self.client.get('/')
        self.assertContains(response, 'img')
        response = self.client.get('/sarah/')
        self.assertContains(response, 'img')
        response = self.client.get('/group/foo/')
        self.assertContains(response, 'img')

    def test_image3(self):
        """
        Проверяем, что срабатывает защита от загрузки файлов
        не-графических форматов
        """
        self.post = Post.objects.create(text="test2", author=self.user)
        self.client.force_login(self.user)
        with open('manage.py', 'rb') as fp:
            self.client.post(
                '/sarah/2/edit',
                {'text': self.post.text, 'image': fp}
            )
        response = self.client.get('/sarah/2/')
        self.assertNotContains(response, 'img')

    def test_cache(self):
        """
        Проверяем работу кэша
        """
        response = self.client.get('/')
        self.post = Post.objects.create(text="test2", author=self.user)
        response = self.client.get('/')
        self.assertNotContains(response, "test2")
        cache.clear()
        response = self.client.get('/')
        self.assertContains(response, "test2")


class FollowTest(TestCase):

    def setUp(self):
        """
        Регистрация пользователей и создание новых записей
        """
        self.client = Client()
        self.user = User.objects.create_user(username='sarah')
        self.user2 = User.objects.create_user(username='conor')
        self.user3 = User.objects.create_user(username='arni')
        self.post = Post.objects.create(text="test1", author=self.user)
        self.post = Post.objects.create(text="test2", author=self.user2)
        self.post = Post.objects.create(text="test3", author=self.user3)

    def test_follow1(self):
        """
        Авторизованный пользователь может подписываться
        на других пользователей и удалять их из подписок
        """
        self.client.force_login(self.user)
        follow = Follow.objects.create(user=self.user, author=self.user2)
        response = self.client.get('/follow/')
        self.assertContains(response, "test2")
        follow.delete()
        response = self.client.get('/follow/')
        self.assertNotContains(response, "test2")

    def test_follow2(self):
        """
        Новая запись пользователя появляется в ленте тех,
        кто на него подписан и не появляется в ленте тех,
        кто не подписан на него
        """
        self.client.force_login(self.user)
        follow = Follow.objects.create(user=self.user, author=self.user2)
        self.client.force_login(self.user2)
        self.post = Post.objects.create(text="test4", author=self.user2)
        self.client.force_login(self.user)
        response = self.client.get('/follow/')
        self.assertContains(response, "test4")
        self.client.force_login(self.user3)
        response = self.client.get('/follow/')
        self.assertNotContains(response, "test4")

    def test_follow3(self):
        """
        Неавторизированный пользователь не может комментировать посты
        и его редиректит на страницу входа
        """
        response = self.client.get('/sarah/1/comment/')
        self.assertRedirects(response, '/auth/login/?next=/sarah/1/comment/')
