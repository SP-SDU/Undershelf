from django.db import models
from django.db.models import Avg, QuerySet


class Book(models.Model):
    id = models.CharField(primary_key=True, max_length=255)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    authors = models.CharField(max_length=255, blank=True, null=True)
    image = models.URLField(blank=True, null=True)
    publisher = models.CharField(max_length=255, blank=True, null=True)
    publishedDate = models.CharField(max_length=50, blank=True, null=True)
    categories = models.CharField(max_length=255, blank=True, null=True)
    ratingsCount = models.FloatField(blank=True, null=True)
    reviews: QuerySet

    def __str__(self):
        return self.title

    def average_rating(self):
        """Return the average rating for the book."""
        result = self.reviews.aggregate(avg_rating=Avg("review_score"))
        return result["avg_rating"]


class Review(models.Model):
    review_id = models.AutoField(primary_key=True)
    book = models.ForeignKey(Book, related_name="reviews", on_delete=models.CASCADE)
    user_id = models.CharField(max_length=255, blank=True, null=True)
    review_score = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"Review {self.review_id} for {self.book.title}"
