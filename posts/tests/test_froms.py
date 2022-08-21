from django.test import TestCase
from django.contrib.auth import get_user_model

from posts.models import Group, Post, Comment
from posts.forms import PostForm, GroupForm, CommentForm

User = get_user_model()


class FormsTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.post = Post.objects.create(
            text='its post',
            author=cls.user,
        )
        cls.group = Group.objects.create(
            title='Title',
            slug='test-group'
        )

    def test_comment_form(self) -> None:
        """Test comment form."""
        current_comments_count: int = Comment.objects.count()
        form: CommentForm = CommentForm(
            data={'text': 'its comment'}
        )
        comment: Comment = form.save(commit=False)
        comment.author = self.user
        comment.post = self.post
        comment.save()
        self.assertEqual(current_comments_count + 1, Comment.objects.count())

    def test_post_form(self) -> None:
        """Test post form."""
        current_posts_count: int = Post.objects.count()
        form: PostForm = PostForm(
            data={'text': 'text', 'group': self.group.id}
        )
        post: Post = form.save(commit=False)
        post.author = self.user
        post.save()
        self.assertEqual(Post.objects.count(), current_posts_count + 1)

    def test_group_form(self) -> None:
        """Test group form."""
        current_groups_count: int = Group.objects.count()
        form: GroupForm = GroupForm(
            data={
                'title': 'title',
                'slug': 'slug',
                'description': 'desc'
            }
        )
        form.save()
        self.assertEqual(Group.objects.count(), current_groups_count + 1)
