from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Q, Max, Count
from .models import Class, Team, Thread, Post
from .forms import ThreadForm, PostForm


def _can_access_class(user, class_group):
    return (
        user == class_group.teacher
        or class_group.members.filter(id=user.id).exists()
    )


def _can_access_team(user, team):
    return (
        user == team.class_group.teacher
        or team.members.filter(id=user.id).exists()
    )


@login_required
def board_list(request):
    """Show all classes and teams the user belongs to."""
    my_classes = Class.objects.filter(
        Q(teacher=request.user) | Q(members=request.user)
    ).distinct()
    my_teams = Team.objects.filter(
        Q(members=request.user) | Q(class_group__teacher=request.user)
    ).distinct()
    return render(request, 'boards/board_list.html', {
        'my_classes': my_classes,
        'my_teams': my_teams,
    })


@login_required
def class_detail(request, slug):
    class_group = get_object_or_404(Class, slug=slug)
    if not _can_access_class(request.user, class_group):
        messages.error(request, "You don't have access to that class.")
        return redirect('board_list')

    threads = class_group.threads.annotate(
        num_posts=Count('posts'),
        latest=Max('posts__created_at'),
    ).select_related('author')

    return render(request, 'boards/class_detail.html', {
        'class_group': class_group,
        'threads': threads,
        'teams': class_group.teams.all(),
    })


@login_required
def team_detail(request, class_slug, team_slug):
    class_group = get_object_or_404(Class, slug=class_slug)
    team = get_object_or_404(Team, class_group=class_group, slug=team_slug)
    if not _can_access_team(request.user, team):
        messages.error(request, "You don't have access to that team.")
        return redirect('board_list')

    threads = team.threads.annotate(
        num_posts=Count('posts'),
        latest=Max('posts__created_at'),
    ).select_related('author')

    return render(request, 'boards/team_detail.html', {
        'class_group': class_group,
        'team': team,
        'threads': threads,
    })


@login_required
def thread_detail(request, slug):
    thread = get_object_or_404(
        Thread.objects.select_related('author', 'class_group', 'team'),
        slug=slug
    )
    # Check access
    if thread.class_group and not _can_access_class(request.user, thread.class_group):
        messages.error(request, "You don't have access to that thread.")
        return redirect('board_list')
    if thread.team and not _can_access_team(request.user, thread.team):
        messages.error(request, "You don't have access to that thread.")
        return redirect('board_list')

    posts = thread.posts.filter(parent__isnull=True).select_related('author')
    form = PostForm()

    if request.method == 'POST' and not thread.is_locked:
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.thread = thread
            post.author = request.user

            parent_id = request.POST.get('parent_id')
            if parent_id:
                try:
                    post.parent = Post.objects.get(id=parent_id, thread=thread)
                except Post.DoesNotExist:
                    pass

            post.save()
            thread.save(update_fields=['updated_at'])  # bump activity
            return redirect(thread.get_absolute_url())

    return render(request, 'boards/thread_detail.html', {
        'thread': thread,
        'posts': posts,
        'form': form,
    })


@login_required
def new_thread(request, scope, slug, team_slug=None):
    """scope is 'class' or 'team'."""
    class_group = None
    team = None

    if scope == 'class':
        class_group = get_object_or_404(Class, slug=slug)
        if not _can_access_class(request.user, class_group):
            return redirect('board_list')
    elif scope == 'team':
        class_group = get_object_or_404(Class, slug=slug)
        team = get_object_or_404(Team, class_group=class_group, slug=team_slug)
        if not _can_access_team(request.user, team):
            return redirect('board_list')
    else:
        return redirect('board_list')

    if request.method == 'POST':
        form = ThreadForm(request.POST)
        if form.is_valid():
            thread = form.save(commit=False)
            thread.author = request.user
            thread.class_group = class_group
            thread.team = team
            thread.save()
            return redirect(thread.get_absolute_url())
    else:
        form = ThreadForm()

    return render(request, 'boards/new_thread.html', {
        'form': form,
        'class_group': class_group,
        'team': team,
    })


@login_required
@require_POST
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    thread = post.thread

    if post.author != request.user and not request.user.is_staff:
        messages.error(request, "You can't delete that post.")
        return redirect(thread.get_absolute_url())

    if thread.class_group and not _can_access_class(request.user, thread.class_group):
        messages.error(request, "You don't have access to that thread.")
        return redirect('board_list')

    if thread.team and not _can_access_team(request.user, thread.team):
        messages.error(request, "You don't have access to that thread.")
        return redirect('board_list')

    post.delete()
    messages.success(request, "Post deleted.")
    return redirect(thread.get_absolute_url())