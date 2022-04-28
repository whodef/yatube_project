from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from yatube.settings import LIMIT_POSTS
from .models import Post, Group
from .forms import PostForm


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
    posts = Post.objects.all()
    paginator = Paginator(posts, LIMIT_POSTS)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    context = {
        'group': group,
        'page_obj': page,
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
        "posts_count": author.posts.count()
    }

    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Раскрыть пост полностью."""

    post = get_object_or_404(Post, pk=post_id)

    context = {
        "post": post,
        "author": post.author,
        "posts_count": post.author.posts.count()
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
        "form": form,
    }

    return render(request, "posts/post_create.html", context)


@login_required
def post_edit(request, post_id):
    """Отредактировать пост."""

    post = get_object_or_404(Post, pk=post_id)

    if request.user == post.author:
        form = PostForm(instance=post, data=request.POST or None)
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id=post_id)

        context = {
            'form': form,
        }
        return render(request, 'posts/post_edit.html', context)

    return redirect('posts:post_detail', post_id=post_id)
