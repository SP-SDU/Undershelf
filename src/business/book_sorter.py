import numpy as np
from typing import List

class BookSorter:
    # Define valid sorting criteria
    SORT_CRITERIA = {
        'rating': 'review/score',
        'title': 'Title',
        'date': 'publishedDate',
        'ratings_count': 'ratingsCount'
    }

    @staticmethod
    def sort_books(books: List[dict], criteria: str, ascending: bool = True) -> List[dict]:
        """
        Sorts books using numpy's sorting implementation
        Args:
            books: List of book dictionaries from Amazon dataset
            criteria: Sort criteria ('rating', 'title', 'date', 'ratings_count')
            ascending: Sort order
        """
        if not books or criteria not in BookSorter.SORT_CRITERIA:
            return books

        # Get the actual field name from the criteria mapping
        field = BookSorter.SORT_CRITERIA[criteria]

        # Convert to numpy array
        books_array = np.array(books)

        # Extract and convert the sort key values based on criteria
        if criteria in ['rating', 'ratings_count']:
            key_values = np.array([float(book.get(field, '0') or '0') for book in books])
        elif criteria == 'date':
            key_values = np.array([int(book.get(field, '0')[:4] or '0') for book in books])
        else:
            key_values = np.array([str(book.get(field, '')).lower() for book in books])

        # Get sorted indices using numpy's argsort
        sorted_indices = np.argsort(key_values, kind='stable')

        # Reverse if descending order required
        if not ascending:
            sorted_indices = sorted_indices[::-1]

        return books_array[sorted_indices].tolist()
