from collections import defaultdict, deque
from typing import List

from business_logic.aspects import (
    error_handler,
    input_validator,
    performance_monitor,
    simple_cache,
    validate_non_empty_string,
    validate_positive_int,
)
from data_access.models import Book


class GraphRecommender:
    """
    Graph-based recommender using BFS.
    Nodes: books; edges: same author or same category.
    """

    @staticmethod
    @error_handler([], propagate=[Book.DoesNotExist])
    @input_validator(validate_positive_int, validate_non_empty_string)
    @performance_monitor
    @simple_cache(300)
    def get_recommendations(
        start_book_id: str, max_depth: int = 2, max_results: int = 10
    ) -> List[Book]:
        # Build feature maps: author -> books, category -> books
        author_map = defaultdict(set)
        category_map = defaultdict(set)

        all_books = list(Book.objects.only("id", "authors", "categories"))  # O(n)
        for b in all_books:  # O(n * f)
            if b.authors:
                for author in b.authors.split(","):
                    author_map[author.strip().lower()].add(b.id)
            if b.categories:
                for cat in b.categories.split(","):
                    category_map[cat.strip().lower()].add(b.id)

        visited = set([start_book_id])
        queue = deque([(start_book_id, 0)])
        recommendations = []

        while queue and len(recommendations) < max_results:
            current_id, depth = queue.popleft()
            if depth >= max_depth:
                continue

            # neighbors by author
            b = Book.objects.only("id", "authors", "categories").get(pk=current_id)
            neighbors = set()
            if b.authors:
                for author in b.authors.split(","):
                    neighbors |= author_map[author.strip().lower()]
            if b.categories:
                for cat in b.categories.split(","):
                    neighbors |= category_map[cat.strip().lower()]

            for nb_id in neighbors:
                if nb_id not in visited:
                    visited.add(nb_id)
                    queue.append((nb_id, depth + 1))
                    if nb_id != start_book_id:
                        recommendations.append(nb_id)
                        if len(recommendations) >= max_results:
                            break

        # Fetch Book instances preserving order
        books = list(Book.objects.filter(id__in=recommendations))
        # maintain recommendation order
        id_to_book = {book.id: book for book in books}
        ordered = [id_to_book[rid] for rid in recommendations if rid in id_to_book]
        return ordered
