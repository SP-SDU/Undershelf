from typing import List

import numpy as np

from data.models import Book


class MergeSort:
    # Define valid sorting criteria
    SORT_CRITERIA = {
        "rating": "average_rating",
        "title": "title",
        "author": "authors",
        "date": "publishedDate",
        "ratings_count": "ratingsCount",
    }

    @staticmethod
    def sort_books(
        books: List[Book], criteria: str, ascending: bool = True
    ) -> List[Book]:
        """Sorts books based on specified criteria ('rating', 'title', 'date', 'ratings_count')"""
        if not books or criteria not in MergeSort.SORT_CRITERIA:
            return books

        # Extract key values based on the selected criteria
        key_values = []
        for book in books:
            if criteria == "rating":
                key_values.append(book.average_rating())
            elif criteria == "ratings_count":
                key_values.append(book.ratingsCount if book.ratingsCount else 0.0)
            elif criteria == "author":
                key_values.append(
                    book.authors.split(",")[0].strip().lower() if book.authors else ""
                )
            elif criteria == "date":
                key_values.append(
                    int(book.publishedDate[:4] if book.publishedDate else "0")
                )
            else:
                field = MergeSort.SORT_CRITERIA[criteria]
                value = getattr(book, field, "")
                key_values.append(value.lower() if isinstance(value, str) else value)

        # Convert to numpy array and sort
        key_values = np.array(key_values)
        sorted_indices = np.argsort(key_values, kind="mergesort")

        if not ascending:
            sorted_indices = sorted_indices[::-1]

        return [books[i] for i in sorted_indices]
