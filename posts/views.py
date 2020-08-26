from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect

from .models import Comment, Follow, Post, Group, User
from .forms import PostForm, CommentForm


def index(request):
    post_list = Post.objects.select_related("author", "group").all()

    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)

    return render(request, "index.html", {"page": page, "paginator": paginator})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()

    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)

    return render(request, "group.html", {"group": group, "page": page, "paginator": paginator})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=author).all()

    paginator = Paginator(post_list, 5)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)

    return render(request, "profile.html", {"author": author, "page": page, "paginator": paginator})


def post_view(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    comments = Comment.objects.filter(post=post)
    form = CommentForm()
    return render(request, "post.html", {"author": post.author, "post": post, "items": comments, "form": form})


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if request.method == "POST":
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("index")
    return render(request, "new_post.html", {"form": form, "post": None})


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)

    if request.user == post.author:
        form = PostForm(request.POST or None, instance=post, files=request.FILES or None)
        if request.method == "POST":
            if form.is_valid():
                form.edit()
                return redirect("post", post.author, post_id)
        return render(request, "new_post.html", {"form": form, "post": post})
    return redirect("post", post.author, post_id)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    form = CommentForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect("post", post.author, post_id)
    return redirect("post", post.author, post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)

    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "follow.html", {"page": page, "paginator": paginator})


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    if user == author:
        return redirect("profile", username)
    Follow.objects.get_or_create(user=user, author=author)
    return redirect("profile", username)


@login_required
def profile_unfollow(request, username):
    get_object_or_404(Follow, user=request.user, author__username=username).delete()
    return redirect("profile", username)


def page_not_found(request, exception):
    return render(request, "misc/404.html", {"path": request.path}, status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)
