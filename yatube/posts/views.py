from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.views.decorators.cache import cache_page

from yatube.settings import LIMIT_POSTS, CACHE_TIMEOUT
from .models import Post, Group, Follow
from .forms import PostForm, CommentForm


@cache_page(CACHE_TIMEOUT, key_prefix='index_page')
def index(request):
    """Главная страница, отображающая общие посты."""

    posts = Post.objects.all()
    paginator = Paginator(posts, LIMIT_POSTS)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    context = {
        'page_obj': page,
    }

    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Страница с постами определённой группы."""

    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group)
    paginator = Paginator(posts, LIMIT_POSTS)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    context = {
        'group': group,
        'page_obj': page,
        'posts': posts,
        'paginator': paginator,
    }

    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """Все посты в профиле пользователя."""

    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    paginator = Paginator(posts, LIMIT_POSTS)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    context = {
        'page_obj': page,
        'author': author,
        'posts_count': author.posts.count(),
    }

    if request.user.is_authenticated:
        following_exist = request.user.follower.filter(author=author).exists()
        context["following"] = following_exist

    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Раскрыть пост полностью."""

    post = get_object_or_404(Post, pk=post_id)
    comments = post.comment.all()
    comment_form = CommentForm(request.POST or None)

    context = {
        'post': post,
        'author': post.author,
        'posts_count': post.author.posts.count(),
        'comment_form': comment_form,
        'comments': comments,
    }

    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """Создать новый пост."""

    user = request.user
    form = PostForm(request.POST or None)

    if form.is_valid():
        post = form.save(False)
        post.author = user
        post.save()
        return redirect("posts:profile", user.username)

    context = {
        'form': form,
    }

    return render(request, "posts/post_create.html", context)


@login_required
def post_edit(request, post_id):
    """Отредактировать пост."""
    post = get_object_or_404(Post, pk=post_id)

    if request.user == post.author:
        form = PostForm(
            request.POST or None,
            files=request.FILES or None,
            instance=post,
        )
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id=post_id)

        context = {
            'post': post,
            'form': form,
            'is_edit': True,
        }
        return render(request, 'posts/post_edit.html', context)

    return HttpResponseForbidden()


@login_required
def add_comment(request, post_id):
    """Добавление комментария."""

    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()

    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """Подписки."""

    authors_list = Follow.objects.filter(user=request.user).values_list('author')
    post_list = Post.objects.filter(author__in=authors_list)
    paginator = Paginator(post_list, LIMIT_POSTS)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    context = {
        'page_obj': page,
        'paginator': paginator,
    }

    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """Подписаться."""

    author = get_object_or_404(User, username=username)

    if request.user == author:
        return redirect('posts:profile', username=username)

    Follow.objects.get_or_create(user=request.user, author=author)

    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    """Отписаться."""

    following = request.user.follower.filter(author__username=username).first()

    if following:
        following.delete()

    return redirect('posts:profile', username=username)
