from typing import List

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.http.response import HttpResponse
from django.test import TestCase, Client

from posts.models import Comment, Follow, Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.another_user = User.objects.create_user(username='AnotherUser')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.unauthorized_client = Client()
        cls.clients = [
            cls.authorized_client,
            cls.unauthorized_client
        ]

        cls.group = Group.objects.create(title='Title', slug='test-group')
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9'
            b'\x04\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00'
            b'\x00\x02\x02\x4c\x01\x00\x3b'
        )
        cls.post = Post.objects.create(
            text='posts text',
            author=cls.user,
            group=cls.group,
            image=SimpleUploadedFile(
                'small.gif', cls.small_gif, content_type='image/gif'
            )
        )

        cls.index_url = 'index'
        cls.follow_index_url = 'follow_index'
        cls.add_comment_url = 'add_comment'
        cls.group_url = 'group'
        cls.post_url = 'post'
        cls.post_delete_url = 'post_delete'
        cls.profile_url = 'profile'
        cls.profile_follow_url = 'profile_follow'
        cls.profile_unfollow_url = 'profile_unfollow'
        cls.new_post_url = 'new_post'
        cls.new_group_url = 'new_group'
        cls.post_edit_url = 'post_edit'

    def check_content_contains(
        self, responses: list, *expected_items
    ) -> None:
        """Check responses contain expected_items."""
        for response in responses:
            for item in expected_items:
                self.assertContains(response, item)

    def check_content_not_contains(
        self, responses: list, *expected_items
    ) -> None:
        """Check responses don't contain expected_items."""
        for response in responses:
            for item in expected_items:
                self.assertNotContains(response, item)

    def get_linked_pages(
        self,
        profile_kwargs,
        post_kwargs,
        group_kwargs
    ) -> List[HttpResponse]:
        """Return list of post's linked pages."""
        cache.clear()

        index_responses = self.do_get_requests(
            clients=self.clients,
            url=self.index_url,
        )
        profile_responses = self.do_get_requests(
            clients=self.clients,
            url=self.profile_url,
            url_kwargs=profile_kwargs
        )
        post_responses = self.do_get_requests(
            clients=self.clients,
            url=self.post_url,
            url_kwargs=post_kwargs
        )
        group_responses = self.do_get_requests(
            clients=self.clients,
            url=self.group_url,
            url_kwargs=group_kwargs
        )

        return (
            index_responses +
            profile_responses +
            post_responses +
            group_responses
        )

    def do_post_requests(
        self, clients, url, url_kwargs=None, context=None
    ) -> None:
        """Do POST requests."""
        for client in clients:
            client.post(
                reverse(url, kwargs=url_kwargs),
                context
            )

    def do_get_requests(
        self, clients, url, url_kwargs=None
    ) -> List[HttpResponse]:
        """Return list of GET responses."""
        return [
            client.get(reverse(url, kwargs=url_kwargs)) for client in clients
        ]

    def test_profile_follow_view_yourself(self) -> None:
        """Test authorized user is not able to follow yourself."""
        current_follow_count: int = Follow.objects.count()
        self.do_post_requests(
            clients=[self.authorized_client],
            url=self.profile_follow_url,
            url_kwargs={'username': self.user.username}
        )
        self.assertEqual(current_follow_count, Follow.objects.count())

        self.assertFalse(
            Follow.objects.filter(
                user=self.user, author=self.user
            ).exists()
        )

    def test_profile_follow_view(self) -> None:
        """Test authorized user is able to follow other users."""
        current_follow_count: int = Follow.objects.count()
        self.do_post_requests(
            clients=[self.authorized_client],
            url=self.profile_follow_url,
            url_kwargs={'username': self.another_user.username}
        )
        self.assertEqual(current_follow_count + 1, Follow.objects.count())

        self.assertTrue(
            Follow.objects.filter(
                user=self.user, author=self.another_user
            ).exists()
        )

    def test_profile_unfollow_view(self) -> None:
        """Test authorized user is able to unfollow followed users."""
        Follow.objects.create(
            user=self.user, author=self.another_user
        )
        current_follow_count: int = Follow.objects.count()
        self.do_post_requests(
            clients=[self.authorized_client],
            url=self.profile_unfollow_url,
            url_kwargs={'username': self.another_user.username}
        )
        self.assertEqual(current_follow_count - 1, Follow.objects.count())

        self.assertFalse(
            Follow.objects.filter(
                user=self.user, author=self.another_user
            ).exists()
        )

    def test_follow_index_view_following(self) -> None:
        """Test follow_index page
        Assert that follow_index page contains
        users messages, that are followed up.
        """
        new_post_text = 'new post'
        new_post_author = self.another_user
        Post.objects.create(
            text=new_post_text, author=new_post_author
        )
        Follow.objects.create(
            user=self.user, author=new_post_author
        )

        follow_index = self.do_get_requests(
            clients=[self.authorized_client],
            url=self.follow_index_url
        )

        self.check_content_contains(
            follow_index,
            new_post_text,
            new_post_author.username
        )

    def test_follow_index_view_not_following(self) -> None:
        """Test follow_index page
        Assert follow_index doesn't contain
        users messages, that are not followed up.
        """
        new_post_text = 'new post'
        new_post_author = self.another_user
        Post.objects.create(
            text=new_post_text, author=new_post_author
        )

        follow_index = self.do_get_requests(
            clients=[self.authorized_client],
            url=self.follow_index_url,
        )

        self.check_content_not_contains(
            follow_index,
            new_post_text,
            new_post_author.username
        )

    def test_index_view(self) -> None:
        """Test index page contains posts."""
        new_post_text = 'testing new post index page'
        new_post_author = self.user
        new_post_group = self.group
        self.do_post_requests(
            clients=[self.authorized_client],
            url=self.new_post_url,
            context={
                'text': new_post_text,
                'group':  new_post_group.id
            }
        )

        cache.clear()
        index_page = self.do_get_requests(
            clients=self.clients,
            url=self.index_url,
        )

        self.check_content_contains(
            index_page,
            new_post_text,
            new_post_author,
            new_post_group.title
        )

    def test_index_view_cache(self) -> None:
        """Test index page caching."""
        new_post_text = 'checking cache'
        self.do_post_requests(
            clients=[self.authorized_client],
            url=self.new_post_url,
            context={
                'text': new_post_text,
                'group': self.group.id
            }
        )

        index_before_cache_clear = self.do_get_requests(
            clients=self.clients,
            url=self.index_url
        )
        self.check_content_not_contains(
            index_before_cache_clear,
            new_post_text
        )

        cache.clear()
        index_after_cache_clear = self.do_get_requests(
            clients=self.clients,
            url=self.index_url
        )
        self.check_content_contains(
            index_after_cache_clear,
            new_post_text
        )

    def test_group_posts_view(self) -> None:
        """Test group page contains posts, that belong to the group."""
        group_page = self.do_get_requests(
            clients=self.clients,
            url=self.group_url,
            url_kwargs={
                'slug': self.group.slug
            }
        )
        self.check_content_contains(
            group_page,
            self.user.get_full_name(),
            self.post.text,
            self.group.title
        )

    def test_profile_view(self) -> None:
        """Test profile page
        Assert profile page contains
        username, user's full name, user's posts.
        """
        profile_page = self.do_get_requests(
            clients=self.clients,
            url=self.profile_url,
            url_kwargs={
                'username': self.user.username
            }
        )
        self.check_content_contains(
            profile_page,
            self.user.get_full_name(),
            self.user.username,
            self.group.title,
            '<img'
        )

    def test_post_view(self) -> None:
        """Test post page contains post."""
        post_page = self.do_get_requests(
            clients=self.clients,
            url=self.post_url,
            url_kwargs={
                'username': self.user.username,
                'post_id': self.post.id
            }
        )
        self.check_content_contains(
            post_page,
            self.user.username,
            self.user.get_full_name(),
            self.post.text,
            self.group.title
        )

    def test_new_post_view(self) -> None:
        """Test authorized user is able to create new post."""
        new_post_text: str = 'its new post text'
        current_posts_count: int = Post.objects.count()
        self.do_post_requests(
            clients=[self.authorized_client],
            url=self.new_post_url,
            context={
                'text': new_post_text,
                'group': self.group.id
            }
        )
        self.assertEqual(Post.objects.count(), current_posts_count + 1)

        self.assertTrue(
            Post.objects.filter(
                text=new_post_text,
                author=self.user,
                group=self.group.id
            ).exists()
        )

        new_post = Post.objects.get(
            text=new_post_text,
            author=self.user,
            group=self.group.id
        )
        linked_pages = self.get_linked_pages(
            profile_kwargs={
                'username': new_post.author
            },
            post_kwargs={
                'username': new_post.author,
                'post_id': new_post.pk
            },
            group_kwargs={
                'slug': new_post.group.slug
            }
        )
        self.check_content_contains(
            linked_pages,
            new_post_text,
            self.group.title
        )

    def test_new_post_view_not_image(self) -> None:
        """Test new post view with non-graphical file uploaded."""
        post_text: str = 'post with non-graphical image attr'
        current_posts_count = Post.objects.count()
        post_response = self.authorized_client.post(
            reverse(self.new_post_url),
            {
                'author': self.user,
                'text': post_text,
                'group': self.group.id,
                'image': SimpleUploadedFile(
                    name='txt_file.txt',
                    content=b'content',
                    content_type='text/txt'
                )
            }
        )

        error_msg = ('Загрузите правильное изображение. '
                     'Файл, который вы загрузили, поврежден '
                     'или не является изображением.')
        self.assertFormError(post_response, 'form', 'image', error_msg)
        self.assertEqual(current_posts_count, Post.objects.count())

        self.assertFalse(
            Post.objects.filter(
                author=self.user,
                text=post_text,
                group=self.group.id
            ).exists()
        )

    def test_new_post_view_image(self) -> None:
        """Test new post view with graphical file uploaded."""
        post_text: str = 'post with graphical image attr'
        current_posts_count = Post.objects.count()
        self.do_post_requests(
            clients=[self.authorized_client],
            url=self.new_post_url,
            context={
                'author': self.user,
                'text': post_text,
                'group': self.group.id,
                'image': SimpleUploadedFile(
                    name='test_gif.gif',
                    content=self.small_gif,
                    content_type='image/gif'
                )
            }
        )
        self.assertEqual(current_posts_count + 1, Post.objects.count())

        self.assertTrue(
            Post.objects.filter(
                author=self.user,
                text=post_text,
                group=self.group.id
            ).exists()
        )

        new_post = Post.objects.get(
            author=self.user,
            text=post_text,
            group=self.group.id
        )
        linked_pages = self.get_linked_pages(
            profile_kwargs={
                'username': new_post.author
            },
            post_kwargs={
                'username': new_post.author,
                'post_id': new_post.pk
            },
            group_kwargs={
                'slug': new_post.group.slug
            }
        )
        self.check_content_contains(
            linked_pages,
            '<img'
        )

    def test_new_group_view(self) -> None:
        """Test authorized user is able to create new group."""
        current_groups_count: int = Group.objects.count()
        new_group_title: str = 'new group'
        new_group_slug: str = 'new-group'
        new_group_description: str = 'desc'

        self.do_post_requests(
            clients=[self.authorized_client],
            url=self.new_group_url,
            context={
                'title': new_group_title,
                'slug': new_group_slug,
                'description': new_group_description
            }
        )
        self.assertEqual(current_groups_count + 1, Group.objects.count())

        self.assertTrue(
            Group.objects.filter(slug=new_group_slug).exists()
        )

        group_page = self.do_get_requests(
            clients=self.clients,
            url=self.group_url,
            url_kwargs={
                'slug': new_group_slug
            }
        )
        self.check_content_contains(
            group_page,
            self.user.get_full_name(),
            new_group_title,
            new_group_description
        )

    def test_unauthorized_user_add_comment_view(self) -> None:
        """Test unauthorized user is not able to add comments."""
        current_comments_count: int = Comment.objects.count()
        comment_text: str = 'force login me pls'
        self.do_post_requests(
            clients=[self.unauthorized_client],
            url=self.add_comment_url,
            url_kwargs={
                'username': self.user,
                'post_id': self.post.id
            },
            context={
                'text': comment_text
            }
        )
        self.assertEqual(current_comments_count, Comment.objects.count())

        self.assertFalse(
            Comment.objects.filter(text=comment_text).exists()
        )

        post_pages = self.do_get_requests(
            clients=self.clients,
            url=self.post_url,
            url_kwargs={
                'username': self.user,
                'post_id': self.post.id
            }
        )
        self.check_content_not_contains(
            post_pages,
            comment_text
        )

    def test_authorized_user_add_comment_view(self) -> None:
        """Test authorized user is able to add comments."""
        current_comments_count: int = Comment.objects.count()
        comment_text = 'auth user comment'
        self.do_post_requests(
            clients=[self.authorized_client],
            url=self.add_comment_url,
            url_kwargs={
                'username': self.user,
                'post_id': self.post.id
            },
            context={
                'text': comment_text
            }
        )
        self.assertEqual(current_comments_count + 1, Comment.objects.count())

        self.assertTrue(
            Comment.objects.filter(text=comment_text).exists()
        )

        post_page = self.do_get_requests(
            clients=[self.authorized_client, self.unauthorized_client],
            url=self.post_url,
            url_kwargs={
                'username': self.user,
                'post_id': self.post.id
            }
        )
        self.check_content_contains(
            post_page,
            comment_text
        )

    def test_unauthorized_user_post_delete_view(self) -> None:
        """Test unauthorized user is not able to delete posts."""
        new_post: Post = Post.objects.create(
            text='test unauth post delete',
            author=self.another_user,
            group=self.group
        )
        current_posts_count: int = Post.objects.count()

        self.do_post_requests(
            clients=[self.unauthorized_client],
            url=self.post_delete_url,
            url_kwargs={
                'username': new_post.author,
                'post_id': new_post.id
            }
        )
        self.assertEqual(current_posts_count, Post.objects.count())

        self.assertTrue(
            Post.objects.filter(
                text=new_post.text,
                author=new_post.author,
                group=new_post.group
            ).exists()
        )

        linked_pages = self.get_linked_pages(
            profile_kwargs={
                'username': new_post.author
            },
            post_kwargs={
                'username': new_post.author,
                'post_id': new_post.pk
            },
            group_kwargs={
                'slug': new_post.group.slug
            }
        )
        self.check_content_contains(
            linked_pages,
            new_post.text
        )

    def test_authorized_user_post_delete_view(self) -> None:
        """Test authorized user is able to delete his posts."""
        new_post: Post = Post.objects.create(
            text='test post delete',
            author=self.user,
            group=self.group
        )
        current_posts_count: int = Post.objects.count()

        self.do_post_requests(
            clients=[self.authorized_client],
            url=self.post_delete_url,
            url_kwargs={
                'username': new_post.author,
                'post_id': new_post.id
            }
        )
        self.assertEqual(current_posts_count - 1, Post.objects.count())

        self.assertFalse(
            Post.objects.filter(
                text=new_post.text,
                author=new_post.author,
                group=new_post.group
            ).exists()
        )

        linked_pages = self.get_linked_pages(
            profile_kwargs={
                'username': self.user.username
            },
            post_kwargs={
                'username': self.user.username,
                'post_id': self.post.id
            },
            group_kwargs={
                'slug': self.group.slug
            }
        )
        self.check_content_not_contains(
            linked_pages,
            new_post.text
        )

    def test_post_edit_view_get(self) -> None:
        """Test post edit page contains post."""
        post_edit_page = self.do_get_requests(
            clients=[self.authorized_client],
            url=self.post_edit_url,
            url_kwargs={
                'username': self.user.username,
                'post_id': self.post.id
            }
        )
        self.check_content_contains(
            post_edit_page,
            self.post.text,
            self.group.title
        )

    def test_post_edit_view(self) -> None:
        """Test authorized user is able to edit his post."""
        new_post_text: str = 'new text'
        new_post_group: Group = Group.objects.create(
            title='new group',
            slug='new-group'
        )
        self.do_post_requests(
            clients=[self.authorized_client],
            url=self.post_edit_url,
            url_kwargs={
                'username': self.user.username,
                'post_id': self.post.id
            },
            context={
                'text': new_post_text,
                'group': new_post_group.pk,
                'image': SimpleUploadedFile(
                    name='gif.gif',
                    content=self.small_gif,
                    content_type='text/gif'
                )
            }
        )

        linked_pages = self.get_linked_pages(
            profile_kwargs={
                'username': self.user.username
            },
            post_kwargs={
                'username': self.user.username,
                'post_id': self.post.id
            },
            group_kwargs={
                'slug': new_post_group.slug
            }
        )
        self.check_content_contains(
            linked_pages,
            new_post_text,
            new_post_group.title
        )

    def test_post_edit_view_old_group(self):
        """Test old post's group page doesn't contain edited post."""
        new_post_text: str = 'new text'
        new_post_group: Group = Group.objects.create(
            title='new group',
            slug='new-group'
        )
        self.do_post_requests(
            clients=[self.authorized_client],
            url=self.post_edit_url,
            url_kwargs={
                'username': self.user.username,
                'post_id': self.post.id
            },
            context={
                'text': new_post_text,
                'group': new_post_group.pk,
                'image': SimpleUploadedFile(
                    name='gif.gif',
                    content=self.small_gif,
                    content_type='text/gif'
                )
            }
        )

        old_group_page = self.do_get_requests(
            clients=self.clients,
            url=self.group_url,
            url_kwargs={
                'slug': self.group.slug
            }
        )
        self.check_content_not_contains(
            old_group_page,
            self.post.text
        )
