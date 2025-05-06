from django.contrib import admin

from .models import Book, Review


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "authors",
        "publisher",
        "publishedDate",
        "average_rating",
    )
    search_fields = ("title", "authors", "publisher")
    list_filter = ("publisher", "publishedDate")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("review_id", "book", "user_id", "review_score")
    search_fields = ("book__title", "user_id")
    list_filter = ("review_score",)
