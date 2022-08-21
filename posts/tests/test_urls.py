from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase, Client
from django.http.response import HttpResponse

from posts.models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.unauthorized_client = Client()

        cls.group = Group.objects.create(title='Title', slug='test-group')
        cls.post = Post.objects.create(
            text='posts text',
            author=cls.user,
            group=cls.group
        )

        cls.follow_index_url_name = 'follow_index'
        cls.profile_url_name = 'profile'
        cls.profile_follow_url_name = 'profile_follow'
        cls.profile_unfollow_url_name = 'profile_unfollow'
        cls.post_url_name = 'post'
        cls.post_edit_url_name = 'post_edit'
        cls.post_delete_url_name = 'post_delete'
        cls.post_delete_confirm_url_name = 'post_delete_confirm'
        cls.add_comment_url_name = 'add_comment'
        cls.group_url_name = 'group'

        cls.index_url = reverse('index')
        cls.follow_index_url = reverse('follow_index')
        cls.new_post_url = reverse('new_post')
        cls.new_group_url = reverse('new_group')
        cls.login_url = reverse('login')

    def test_homepage(self) -> None:
        """Test homepage GET response."""
        get_response: HttpResponse = self.unauthorized_client.get(
            self.index_url
        )
        self.assertEqual(get_response.status_code, 200)

    def test_group_page(self) -> None:
        """Test group page GET response."""
        get_response: HttpResponse = self.unauthorized_client.get(
            reverse(
                self.group_url_name,
                kwargs={'slug': self.group.slug}
            )
        )
        self.assertEqual(get_response.status_code, 200)

    def tets_new_post_get(self) -> None:
        """Test new post GET response."""
        get_response: HttpResponse = self.authorized_client.get(
            self.new_post_url
        )
        self.assertEqual(get_response.status_code, 200)

    def test_new_post_post(self) -> None:
        """Test new post page POST response."""
        post_response: HttpResponse = self.authorized_client.post(
            self.new_post_url,
            {
                'text': 'its posts text',
                'group': self.group.id
            }
        )
        self.assertRedirects(
            post_response,
            self.index_url,
            302,
            200
        )

    def test_unauthorized_user_new_post(self) -> None:
        """Test unauthorized user new post page POST response."""
        get_response: HttpResponse = self.unauthorized_client.get(
            self.new_post_url
        )
        self.assertRedirects(
            get_response,
            f'{self.login_url}?next={self.new_post_url}',
            302,
            200
        )

    def test_new_group_get(self) -> None:
        """Test new group page GET response."""
        get_response: HttpResponse = self.authorized_client.get(
            self.new_group_url
        )
        self.assertEqual(get_response.status_code, 200)

    def test_new_group_post(self) -> None:
        """Test new group page POST response."""
        new_group_slug = 'its-slug'
        post_response: HttpResponse = self.authorized_client.post(
            self.new_group_url,
            {
                'title': 'Its title',
                'slug': new_group_slug,
                'description': 'its desc'
            }
        )
        self.assertRedirects(
            post_response,
            reverse(self.group_url_name, kwargs={'slug': new_group_slug}),
            302,
            200
        )

    def test_unauthorized_user_new_group(self) -> None:
        """Test unauthorized user new group page GET response."""
        get_response: HttpResponse = self.unauthorized_client.get(
            self.new_group_url
        )
        self.assertRedirects(
            get_response,
            f'{self.login_url}?next={self.new_group_url}',
            302,
            200
        )

    def test_follow_index(self) -> None:
        """Test follow index page GET response."""
        get_response: HttpResponse = self.authorized_client.get(
            self.follow_index_url
        )
        self.assertEqual(get_response.status_code, 200)

    def test_unauthorized_user_follow_index(self) -> None:
        """Test unauthorized user follow index page GET response."""
        get_response: HttpResponse = self.unauthorized_client.get(
            reverse(self.follow_index_url_name)
        )
        self.assertRedirects(
            get_response,
            f'{self.login_url}?next={self.follow_index_url}',
            302,
            200
        )

    def test_profile_follow(self) -> None:
        """Test profile follow page GET response."""
        get_response: HttpResponse = self.authorized_client.get(
            reverse(
                self.profile_follow_url_name,
                kwargs={'username': self.user.username}
            )
        )
        self.assertRedirects(
            get_response,
            reverse(
                self.profile_url_name,
                kwargs={'username': self.user.username}
            ),
            302,
            200
        )

    def test_unauthorized_user_profile_follow(self) -> None:
        """Test unauthorized user profile follow page GET response."""
        profile_follow_url = reverse(
            self.profile_follow_url_name,
            kwargs={'username': self.user.username}
        )

        get_response: HttpResponse = self.unauthorized_client.get(
            profile_follow_url
        )
        self.assertRedirects(
            get_response,
            f'{self.login_url}?next={profile_follow_url}',
            302,
            200
        )

    def test_profile_unfollow(self) -> None:
        """Test profile unfollow page GET response."""
        get_response: HttpResponse = self.authorized_client.get(
            reverse(
                self.profile_unfollow_url_name,
                kwargs={'username': self.user.username}
            )
        )
        self.assertRedirects(
            get_response,
            reverse(
                self.profile_url_name,
                kwargs={'username': self.user.username}
            ),
            302,
            200
        )

    def test_unauthorized_user_profile_unfollow(self) -> None:
        """Test unauthorized user profile unfollow page GET response."""
        profile_unfollow_url = reverse(
            self.profile_unfollow_url_name,
            kwargs={
                'username': self.user.username
            }
        )

        get_response: HttpResponse = self.unauthorized_client.get(
            profile_unfollow_url
        )
        self.assertRedirects(
            get_response,
            f'{self.login_url}?next={profile_unfollow_url}',
            302,
            200
        )

    def test_authorized_user_add_comment(self) -> None:
        """Test add comment page GET response."""
        get_response: HttpResponse = self.authorized_client.get(
            reverse(
                self.add_comment_url_name,
                kwargs={
                    'username': self.user.username,
                    'post_id': self.post.id
                }
            )
        )
        self.assertEqual(get_response.status_code, 200)

    def test_unauthorized_user_add_comment(self) -> None:
        """Test unauthorized user add comment page GET response."""
        get_response: HttpResponse = self.unauthorized_client.get(
            reverse(
                self.add_comment_url_name,
                kwargs={
                    'username': self.user.username,
                    'post_id': self.post.id
                }
            )
        )

        comment_url = reverse(
            self.add_comment_url_name,
            kwargs={
                'username': self.user.username,
                'post_id': self.post.id
            }
        )
        self.assertRedirects(
            get_response,
            f'{self.login_url}?next={comment_url}',
            302,
            200
        )

    def test_authorized_user_post_delete_confirm(self) -> None:
        """Test authorized user post delete confirm page GET response."""
        get_response: HttpResponse = self.authorized_client.get(
            reverse(
                self.post_delete_confirm_url_name,
                kwargs={
                    'username': self.user.username,
                    'post_id': self.post.id
                }
            )
        )
        self.assertEqual(get_response.status_code, 200)

    def test_unauthorized_user_post_delete_confirm(self):
        """Test unauthorized user post delete confirm page GET response."""
        post_delete_confirm_url = reverse(
            self.post_delete_confirm_url_name,
            kwargs={
                'username': self.user.username,
                'post_id': self.post.id
            }
        )

        get_response: HttpResponse = self.unauthorized_client.get(
            post_delete_confirm_url
        )
        self.assertRedirects(
            get_response,
            f'{self.login_url}?next={post_delete_confirm_url}',
            302,
            200
        )

    def test_authorized_user_post_delete(self) -> None:
        """Test post delete page GET response."""
        author_response: HttpResponse = self.authorized_client.get(
            reverse(
                self.post_delete_url_name,
                kwargs={
                    'username': self.user.username,
                    'post_id': self.post.id
                }
            )
        )
        self.assertEqual(author_response.status_code, 200)

    def test_unauthorized_user_post_delete(self):
        """Test unauthorized user post delete page GET response."""
        post_delete_url = reverse(
            self.post_delete_url_name,
            kwargs={
                'username': self.user.username,
                'post_id': self.post.id
            }
        )

        get_response: HttpResponse = self.unauthorized_client.get(
            post_delete_url
        )
        self.assertRedirects(
            get_response,
            f'{self.login_url}?next={post_delete_url}',
            302,
            200
        )

    def test_not_author_post_delete(self) -> None:
        """Test authorized user
        that is not post's author, post delete page GET response.
        """
        test_user: User = User.objects.create_user(username='AnotherTestUser')
        test_post: Post = Post.objects.create(
            text='test post',
            author=test_user
        )
        not_author_response: HttpResponse = self.authorized_client.get(
            reverse(
                self.post_delete_url_name,
                kwargs={
                    'username': test_user,
                    'post_id': test_post.pk
                }
            )
        )

        post_url = reverse(
            self.post_url_name,
            kwargs={
                'username': test_post.author,
                'post_id': test_post.pk
            }
        )
        self.assertRedirects(
            not_author_response,
            post_url,
            302,
            200
        )

    def test_profile(self) -> None:
        """Test profile page GET response."""
        get_response: HttpResponse = self.authorized_client.get(
            reverse(
                self.profile_url_name,
                kwargs={'username': self.user.username}
            )
        )
        self.assertEqual(get_response.status_code, 200)

    def test_post_page(self) -> None:
        """Test post page GET response."""
        get_response: HttpResponse = self.authorized_client.get(
            reverse(
                self.post_url_name,
                kwargs={
                    'username': self.user.username,
                    'post_id': self.post.id
                }
            )
        )
        self.assertEqual(get_response.status_code, 200)

    def post_edit_get(self) -> None:
        """Test post edit page GET response."""
        get_response: HttpResponse = self.authorized_client.get(
            reverse(
                self.post_edit_url_name,
                kwargs={
                    'username': self.user.username,
                    'post_id': self.post.id
                }
            )
        )
        self.assertEqual(get_response.status_code, 200)

    def test_post_edit_post(self) -> None:
        """Test post edit page POST response."""
        post_response: HttpResponse = self.authorized_client.post(
            reverse(
                self.post_edit_url_name,
                kwargs={
                    'username': self.user.username,
                    'post_id': self.post.id
                }
            ),
            {
                'text': 'its new text',
                'group': self.group.id
            }
        )

        post_url = reverse(
            self.post_url_name,
            kwargs={
                'username': self.user.username,
                'post_id': self.post.id
            }
        )
        self.assertRedirects(
            post_response,
            post_url,
            302,
            200
        )

    def test_unauthorized_user_post_edit(self) -> None:
        """Test unauthorized user post edit page GET response."""
        get_response: HttpResponse = self.unauthorized_client.get(
            reverse(
                self.post_edit_url_name,
                kwargs={
                    'username': self.user.username,
                    'post_id': self.post.id
                }
            )
        )

        post_edit_url = reverse(
            self.post_edit_url_name,
            kwargs={
                'username': self.user.username,
                'post_id': self.post.id
            }
        )
        self.assertRedirects(
            get_response,
            f'{self.login_url}?next={post_edit_url}',
            302,
            200
        )

    def test_not_author_post_edit(self) -> None:
        """Test authorized user
        that is not post's author, post edit page GET response.
        """
        user: User = User.objects.create_user(username='AnotherTestUser')
        post: Post = Post.objects.create(text='its text', author=user)
        response = self.authorized_client.get(
            reverse(
                self.post_edit_url_name,
                kwargs={
                    'username': user,
                    'post_id': post.id
                }
            )
        )

        post_url = reverse(
            self.post_url_name,
            kwargs={
                'username': user.username,
                'post_id': post.pk
            }
        )
        self.assertRedirects(
            response,
            post_url,
            302,
            200
        )

    def test_page_not_found(self):
        """Test page not found GET response."""
        for client in [self.authorized_client, self.unauthorized_client]:
            response = client.get(
                'give-me-404-code'
            )
            self.assertEqual(response.status_code, 404)
