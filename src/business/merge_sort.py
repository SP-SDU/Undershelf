import numpy as np
from typing import List
from data.models import Book


class MergeSort:
    # Define valid sorting criteria
    SORT_CRITERIA = {
        'rating': 'average_rating',
        'title': 'title',
        'author': 'authors',
        'date': 'published_date',
        'ratings_count': 'reviews'
    }

    @staticmethod
    def sort_books(books: List[Book], criteria: str, ascending: bool = True) -> List[Book]:
        """
        Sorts books based on specified criteria.
        
        Args:
            books: List of Book objects
            criteria: Sort criteria ('rating', 'title', 'date', 'ratings_count')
            ascending: Sort order (True for ascending, False for descending)
        """
        if not books or criteria not in MergeSort.SORT_CRITERIA:
            return books

        field = MergeSort.SORT_CRITERIA[criteria]
        
        # Extract key values based on the selected criteria
        if criteria in ['rating', 'ratings_count']:
            key_values = np.array([getattr(book, field) for book in books])
        elif criteria == 'author':
            key_values = np.array([book.authors.split(',')[0].strip().lower() if book.authors else '' for book in books])
        elif criteria == 'date':
            key_values = np.array([int(book.publishedDate[:4] if book.publishedDate else '0') for book in books])
        else:
            key_values = np.array([getattr(book, field, '').lower() for book in books])

        sorted_indices = np.argsort(key_values, kind='mergesort')

        if not ascending:
            sorted_indices = sorted_indices[::-1]

        return [books[i] for i in sorted_indices]
