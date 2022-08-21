from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.contrib.auth import get_user_model

from posts.models import Group, Post, Comment, Follow

User = get_user_model()


class ModelsTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.post = Post.objects.create(text='test', author=cls.user)
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9'
            b'\x04\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00'
            b'\x00\x02\x02\x4c\x01\x00\x3b'
        )

    def check_instances_count(self, instance, current_count):
        """Check if amount of class instances incremented."""
        self.assertIsNotNone(instance)
        self.assertEqual(
            current_count + 1,
            instance.__class__.objects.count()
        )

    def test_follow_model(self):
        """Test follow model."""
        current_follows_count: int = Follow.objects.count()
        user = User.objects.create_user(username='AnotherTestUser')
        follow: Follow = Follow.objects.create(
            user=self.user,
            author=user
        )
        self.check_instances_count(follow, current_follows_count)

    def test_comment_model(self):
        """Test comment model."""
        current_comments_count: int = Comment.objects.count()
        comment: Comment = Comment.objects.create(
            post=self.post,
            author=self.user,
            text='test comment'
        )
        self.check_instances_count(comment, current_comments_count)

    def test_post_model(self) -> None:
        """Test Post model."""
        current_posts_count: int = Post.objects.count()
        group: Group = Group.objects.create(
            title='title',
            slug='slug',
            description='desc'
        )
        post: Post = Post.objects.create(
            text='its text',
            author=self.user,
            group=group,
            image=SimpleUploadedFile(
                'small.gif', self.small_gif, content_type='image/gif'
            )
        )
        self.check_instances_count(post, current_posts_count)

    def test_group_model(self) -> None:
        """Test Group model."""
        current_groups_count: int = Group.objects.count()
        group: Group = Group.objects.create(
            title='its title',
            slug='its-slug_',
            description='its desc'
        )
        self.check_instances_count(group, current_groups_count)
