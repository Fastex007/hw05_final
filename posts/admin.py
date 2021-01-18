from django.contrib import admin
from django.utils.html import format_html

from .models import Comment, Follow, Group, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('pk', 'group', 'text', 'pub_date', 'author')
    search_fields = ('text',)
    list_filter = ('pub_date',)
    readonly_fields = ('image_tag',)
    fields = ('image_tag', 'group', 'text')
    empty_value_display = '-пусто-'

    def image_tag(self, instance):
        return format_html(
            '<img src="{0}" style="max-width: 100%"/>',
            instance.image.url
        )


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'slug', 'description')
    search_fields = ('title',)
    list_filter = ('title',)
    empty_value_display = '-пусто-'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'author', 'post', 'text', 'created')
    search_fields = ('author', 'post', 'text', 'created')
    list_filter = ('author', 'post', 'text', 'created')
    empty_value_display = '-пусто-'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'author')
    search_fields = ('author', 'user', 'author')
    list_filter = ('author', 'user', 'author')
    empty_value_display = '-пусто-'
