import heapq

from django.db.models import Avg, ExpressionWrapper, F, FloatField

from business_logic.aspects import (
    input_validator,
    method_logger,
    performance_monitor,
    simple_cache,
    validate_positive_int,
)
from data_access.models import Book


class BookRanker:
    @staticmethod
    @input_validator(validate_positive_int)
    @method_logger
    @performance_monitor
    @simple_cache(300)
    def get_top_k(k=10):
        # 1. Annotate books with calculated scores
        books = Book.objects.annotate(
            avg_rating=Avg("reviews__review_score"),
            # Bayesian average to handle sparse ratings
            bayesian_score=ExpressionWrapper(
                (F("ratingsCount") * F("avg_rating") + 3 * 3.5)
                / (F("ratingsCount") + 3),
                output_field=FloatField(),
            ),
            # newer books get boost
            recency_score=ExpressionWrapper(
                1 / (1 + F("publishedDate")), output_field=FloatField()
            ),
        ).only("title", "ratingsCount", "image", "authors", "categories")

        # 2. Heap-based top-k selection
        heap = []
        counter = 0
        for book in books:
            bayesian = book.bayesian_score or 0
            recency = book.recency_score or 1.0

            # Combined score
            score = (
                0.7 * bayesian
                + 0.2 * recency
                + 0.1 * (1 if book.categories else 0.5)  # Genre bonus
            )

            book_data = {
                "id": book.id,
                "title": book.title,
                "score": score,
                "image": book.image,
                "authors": book.authors,
                "rating": book.avg_rating or 0,
            }

            if len(heap) < k:
                heapq.heappush(heap, (score, counter, book_data))
                counter += 1
            else:
                heapq.heappushpop(heap, (score, counter, book_data))
                counter += 1

        # Return sorted descending
        return [book for (_, _, book) in sorted(heap, reverse=True)]
