from django.shortcuts import render
from django.shortcuts import get_object_or_404

from yatube.settings import LIMIT_POSTS
from .models import Post, Group


def index(request):
    posts = Post.objects.all()[:LIMIT_POSTS]
    context = {
        'posts': posts,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.all()[:LIMIT_POSTS]
    context = {
        'group': group,
        'posts': posts,
    }
    return render(request, 'posts/group_list.html', context)
