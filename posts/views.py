from typing import Tuple

from django.core.paginator import Page, Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required

from django.forms.fields import SlugField
from django.http.request import HttpRequest
from django.http.response import HttpResponse

from .models import Post, Group, Follow
from .forms import PostForm, GroupForm, CommentForm

User = get_user_model()


def is_following(request, author) -> bool:
    """Return True if request.user is following author."""
    if not request.user.is_anonymous:
        return(
            Follow.objects.filter(
                user=request.user, author=author
            ).exists()
        )
    return False


def get_paginator(
    query_set, page_number, per_page=10
) -> Tuple[Paginator, Page]:
    """Return paginator and page."""
    paginator = Paginator(query_set, per_page)

    return(
        paginator,
        paginator.get_page(page_number)
    )


def page_not_found(request: HttpRequest, exception) -> HttpResponse:
    """Return 404 page."""
    return render(
        request,
        'misc/404.html',
        {'path': request.path},
        status=404
    )


def server_error(request: HttpRequest) -> HttpResponse:
    """Return 500 page."""
    return render(
        request,
        'misc/500.html',
        status=500
    )


@login_required
def profile_follow(request: HttpRequest, username: str) -> HttpResponse:
    """Follow author."""
    author = User.objects.get(username=username)
    if request.user != author:
        Follow.objects.get_or_create(
            user=request.user,
            author=author
        )

    return redirect('profile', username=username)


@login_required
def profile_unfollow(request: HttpRequest, username: str) -> HttpResponse:
    """Unfollow author."""
    author = User.objects.get(username=username)
    Follow.objects.filter(
        user=request.user, author=author
    ).delete()

    return redirect('profile', username=username)


@login_required
def follow_index(request: HttpRequest) -> HttpResponse:
    """Return followed author's posts."""
    posts = Post.objects.filter(
        author__following__user=request.user
    ).select_related('author', 'group')
    paginator, page = get_paginator(posts, request.GET.get('page'))

    return render(
        request,
        'follow.html',
        {'page': page, 'paginator': paginator}
    )


def index(request: HttpRequest) -> HttpResponse:
    """Return homepage."""
    posts = Post.objects.select_related('author', 'group')
    paginator, page = get_paginator(posts, request.GET.get('page'))

    return render(
        request,
        'index.html',
        {'page': page, 'paginator': paginator}
    )


def group_posts(request: HttpRequest, slug: SlugField) -> HttpResponse:
    """Return group page."""
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('author')
    paginator, page = get_paginator(posts, request.GET.get('page'))

    return render(
        request,
        'group.html',
        {'group': group, 'page': page, 'paginator': paginator}
    )


@login_required
def new_post(request: HttpRequest) -> HttpResponse:
    """Add new post."""
    form = PostForm(request.POST or None, files=request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            post: Post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('index')

    return render(request, 'post_new.html', {'form': form})


@login_required
def add_comment(
    request: HttpRequest, username: str, post_id: int
) -> HttpResponse:
    """Add comment to post."""
    form = CommentForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post_id = post_id
            comment.save()
            return redirect('post', username=username, post_id=post_id)

    post = get_object_or_404(Post, id=post_id, author__username=username)
    author = post.author
    comments = post.comments.select_related('author')

    return render(
        request,
        'post.html',
        {
            'form': form,
            'post': post,
            'author': author,
            'comments': comments,
            'posts_count': author.posts.count(),
            'following': is_following(request, author)
        }
    )


@login_required
def new_group(request: HttpRequest) -> HttpResponse:
    """Add new group."""
    form = GroupForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('group', form.cleaned_data['slug'])

    return render(request, 'new_group.html', {'form': form})


def profile(request: HttpRequest, username: str) -> HttpResponse:
    """Return user profile page."""
    author = get_object_or_404(User, username=username)
    posts = author.posts.select_related('author', 'group')
    paginator, page = get_paginator(posts, request.GET.get('page'))

    return render(
        request,
        'profile.html',
        {
            'author': author,
            'paginator': paginator,
            'page': page,
            'posts_count': posts.count(),
            'following': is_following(request, author)
        }
    )


def post_view(
    request: HttpRequest, username: str, post_id: int
) -> HttpResponse:
    """Return post page."""
    post = get_object_or_404(Post, id=post_id, author__username=username)
    author = post.author
    comments = post.comments.select_related('author')

    return render(
        request,
        'post.html',
        {
            'post': post,
            'author': author,
            'comments': comments,
            'form': CommentForm(request.POST or None),
            'posts_count': author.posts.count(),
            'following': is_following(request, author)
        }
    )


@login_required
def post_edit(
    request: HttpRequest, username: str, post_id: int
) -> HttpResponse:
    """Return post edit page."""
    post = get_object_or_404(Post, id=post_id, author__username=username)
    if post.author != request.user:
        return redirect('post', username, post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('post', username, post_id)

    return render(
        request,
        'post_new.html',
        {
            'post': post,
            'form': form,
            'edit': True
        }
    )


@login_required
def post_delete_confirm(
    request: HttpRequest, username: str, post_id: int
) -> HttpResponse:
    """Confirm post delete."""
    return render(
        request,
        'post_delete_confirm.html',
        {'username': username, 'post_id': post_id}
    )


@login_required
def post_delete(
    request: HttpRequest, username: str, post_id: int
) -> HttpResponse:
    """Delete post."""
    post = get_object_or_404(Post, id=post_id, author__username=username)
    if post.author != request.user:
        return redirect('post', username, post_id)
    post.delete()

    return render(request, 'post_delete_success.html')
