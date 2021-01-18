from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


POSTS_PER_PAGE = 10


def check_following(user, author):
    """Проверяет наличие одписки на автора."""
    has_follow = False
    if user.is_authenticated and user != author:
        has_follow = Follow.objects.select_related('follower').filter(
            author=author
        ).exists()

    return has_follow


def index(request):
    post_list = Post.objects.select_related('group').all()
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html', {'page': page,
                                          'paginator': paginator})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html', {'group': group,
                                          'page': page,
                                          'paginator': paginator})


@login_required
def new_post(request):
    form = PostForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('index')

    return render(request, 'new_post.html', {'form': form,
                                             'edit_mode': False})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    has_follow = check_following(request.user, author)
    return render(request, 'profile.html', {'profile': author,
                                            'page': page,
                                            'paginator': paginator,
                                            'following': has_follow})


def post_view(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    comments = post.comments.all()
    form = CommentForm()
    has_follow = check_following(request.user, post.author)
    return render(request, 'post.html', {'profile': post.author,
                                         'post': post,
                                         'comments': comments,
                                         'form': form,
                                         'following': has_follow})


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
    return redirect('post', username=username, post_id=post_id)


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    if request.user != post.author:
        return redirect('post', username=username, post_id=post_id)
    form = PostForm(request.POST or None, files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        form.save()
        return redirect('post', username=username, post_id=post_id)

    return render(request, 'new_post.html', {'form': form,
                                             'edit_mode': True,
                                             'post': post})


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'follow.html', {'page': page,
                                           'paginator': paginator})


@login_required
def profile_follow(request, username):
    profile = get_object_or_404(User, username=username)
    if request.user != profile:
        Follow.objects.get_or_create(user=request.user, author=profile)
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    profile = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=profile).delete()
    return redirect('profile', username=username)


def page_not_found(request, exception):
    return render(
        request,
        'misc/404.html',
        {'path': request.path},
        status=404
    )


def server_error(request):
    return render(request, 'misc/500.html', status=500)
