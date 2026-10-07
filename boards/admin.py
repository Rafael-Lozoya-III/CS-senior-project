from django.contrib import admin
from .models import Class, Team, Thread, Post


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'teacher', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('members',)


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'class_group', 'created_at')
    list_filter = ('class_group',)
    filter_horizontal = ('members',)


@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'class_group', 'team',
                    'is_pinned', 'is_locked', 'created_at')
    list_filter = ('is_pinned', 'is_locked', 'class_group', 'team')
    search_fields = ('title', 'body')


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('thread', 'author', 'created_at')
    search_fields = ('body',)