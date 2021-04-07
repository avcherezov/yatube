from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group, User, Comment, Follow
from .forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator


def index(request):
    post_list = Post.objects.order_by("-pub_date").all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'index.html',
        {'page': page, 'paginator': paginator}
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.filter(group=group).order_by("-pub_date").all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        "group.html",
        {"group": group, 'page': page, 'paginator': paginator}
    )


@login_required
def new_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('index')
    else:
        form = PostForm()
    return render(request, "post_new.html", {"form": form})


def profile(request, username):
    post_list = Post.objects.filter(
        author__username=username).order_by("-pub_date").all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    count_post = Post.objects.filter(author__username=username).count()
    author = get_object_or_404(User, username=username)
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user).filter(author=author)
        return render(
            request,
            "profile.html",
            {
                'page': page,
                'paginator': paginator,
                'count_post': count_post,
                'author': author,
                'following': following
            }
        )
    else:
        return render(
            request,
            "profile.html",
            {
                'page': page,
                'paginator': paginator,
                'count_post': count_post,
                'author': author
            }
        )


def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id, author=author)
    count_post = Post.objects.filter(author__username=username).count()
    items = Comment.objects.filter(post=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = author
            comment.save()
            return redirect('post', username, post_id)
    else:
        form = CommentForm()
    return render(
        request,
        "post.html",
        {
            'author': author,
            'post': post,
            'count_post': count_post,
            'items': items,
            "form": form
        }
    )


def post_edit(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author == request.user:
        if request.method == 'POST':
            form = PostForm(
                request.POST or None,
                files=request.FILES or None,
                instance=post
            )
            if form.is_valid():
                post = form.save(commit=False)
                post.author = request.user
                post.save()
                return redirect('post', username, post_id)
        else:
            form = PostForm(instance=post)
        return render(request, "post_new.html", {"form": form, "post": post})
    else:
        return redirect('post', username, post_id)


def page_not_found(request, exception):
    return render(request, "misc/404.html", {"path": request.path}, status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def add_comment(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id, author=author)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = author
            comment.save()
            return redirect('post', username, post_id)
    else:
        form = CommentForm()
    return render(request, "comments.html", {"form": form})


@login_required
def follow_index(request):
    follow = Follow.objects.filter(user=request.user)
    authors = []
    for obj in follow:
        follow_author = obj.author
        authors.append(follow_author)
    post_list = Post.objects.filter(
        author__in=authors).order_by("-pub_date").all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        "follow.html",
        {'page': page, 'paginator': paginator}
    )


@login_required
def profile_follow(request, username):
    user = get_object_or_404(User, username=username)
    author = get_object_or_404(User, username=username)
    count = Follow.objects.filter(
        user=request.user).filter(author=author).count()
    if request.user != user:
        if count == 0:
            Follow.objects.create(user=request.user, author=author)
            return redirect('profile', username)
        else:
            return redirect('profile', username)
    else:
        return redirect('profile', username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(user=request.user).filter(author=author)
    follow.delete()
    return redirect('profile', username)
