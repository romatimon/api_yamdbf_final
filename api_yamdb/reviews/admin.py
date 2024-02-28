from django.contrib import admin

from .models import Category, Comment, Genre, Review, Title


class TitleAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'year',
        'description',
        'category',
        'get_genres'
    )
    list_editable = (
        'category',
    )
    list_display_links = ('pk', 'name')
    search_fields = ('title',)
    list_filter = ('category',)

    @admin.display(description='Жанры')
    def get_genres(self, obj):
        return [name for name in obj.genre.all()]


class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'slug'
    )
    search_fields = ('name',)


class GenreAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug'
    )
    search_fields = ('name',)


class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'text',
        'author',
        'pub_date',
        'review'
    )
    search_fields = ('text',)


class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'text',
        'title',
        'author',
        'score',
        'pub_date'
    )
    search_fields = ('text',)


admin.site.register(Review, ReviewAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Title, TitleAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Genre, GenreAdmin)
