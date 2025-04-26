import heapq
from datetime import datetime
from django.db.models import F, ExpressionWrapper, FloatField
from data_access.models import Book

class BookRanker:
    @staticmethod
    def get_top_k(k=10):

        # 1. Annotate books with calculated scores
        books = Book.objects.annotate(
            # Bayesian average to handle sparse ratings
            bayesian_score=ExpressionWrapper(
                (F('ratingsCount') * F('average_rating') + 3 * 3.5) / 
                (F('ratingsCount') + 3),
                output_field=FloatField()
            ),
            # newer books get boost
            recency_score=ExpressionWrapper(
                1 / (1 + F('publishedDate')),  
                output_field=FloatField()
            )
        ).only('title', 'average_rating', 'ratingsCount', 'image', 'authors', 'categories')

        # 2. Heap-based top-k selection
        heap = []
        for book in books:
            # Combined score 
            score = (
                0.7 * book.bayesian_score + 
                0.2 * book.recency_score +
                0.1 * (1 if book.categories else 0.5)  # Genre bonus
            )
            
            book_data = {
                'id': book.id,
                'title': book.title,
                'score': score,
                'image': book.image,
                'authors': book.authors,
                'rating': book.average_rating
            }
            
            if len(heap) < k:
                heapq.heappush(heap, (score, book_data))
            else:
                heapq.heappushpop(heap, (score, book_data))
        
        # Return sorted descending
        return [book for (_, book) in sorted(heap, reverse=True)]