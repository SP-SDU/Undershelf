from django.contrib import admin

from .models import Book, Review


class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    readonly_fields = ['review_id', 'user_id', 'review_score']


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "authors",
        "publisher",
        "publishedDate",
        "display_categories",
        "ratingsCount",
        "average_rating_display",
    )
    search_fields = ("title", "authors", "publisher", "description", "categories")
    list_filter = ("publisher", "publishedDate")
    readonly_fields = ('id', 'average_rating_display')
    fieldsets = (
        ('Book Information', {
            'fields': ('id', 'title', 'description', 'authors')
        }),
        ('Publishing Details', {
            'fields': ('publisher', 'publishedDate', 'categories')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Ratings', {
            'fields': ('ratingsCount', 'average_rating_display')
        }),
    )
    inlines = [ReviewInline]
    
    def display_categories(self, obj):
        return obj.categories if obj.categories else "N/A"
    display_categories.short_description = 'Categories'
    
    def average_rating_display(self, obj):
        avg = obj.average_rating()
        return f"{avg:.2f}" if avg else "No ratings"
    average_rating_display.short_description = 'Avg. Rating'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("review_id", "book_title", "user_id", "review_score")
    search_fields = ("book__title", "user_id")
    list_filter = ("review_score",)
    
    def book_title(self, obj):
        return obj.book.title
    book_title.short_description = 'Book'
    book_title.admin_order_field = 'book__title'
