from collections import defaultdict, deque
from typing import Dict, Iterable, List

from data_access.models import Book


class GraphRecommender:
    def __init__(self) -> None:
        self.connections: Dict[str, Dict[str, float]] = defaultdict(dict)

    def add_book(self, asin: str) -> None:
        self.connections.setdefault(asin, {})

    def add_edge(self, a: str, b: str, weight: float = 1.0) -> None:
        self.connections[a][b] = max(self.connections[a].get(b, 0), weight)
        self.connections[b][a] = max(self.connections[b].get(a, 0), weight)

    def build(self, books: Iterable[Book]) -> None:
        by_category: Dict[str, List[str]] = defaultdict(list)
        by_author: Dict[str, List[str]] = defaultdict(list)

        for book in books:
            asin = book.id
            self.add_book(asin)
            if book.categories:
                for category in map(str.strip, book.categories.split(",")):
                    if category:
                        by_category[category].append(asin)
            if book.authors:
                by_author[book.authors].append(asin)

        for items in by_category.values():
            for i, src in enumerate(items[:-1]):
                for dst in items[i + 1 :]:
                    self.add_edge(src, dst, weight=0.5)

        for items in by_author.values():
            for i, src in enumerate(items[:-1]):
                for dst in items[i + 1 :]:
                    self.add_edge(src, dst, weight=1.0)

    def recommend(self, start: str, max_results: int = 5) -> List[str]:
        if start not in self.connections:
            return []

        visited = {start}
        queue = deque([start])
        results: List[str] = []

        while queue and len(results) < max_results:
            current = queue.popleft()
            for neighbor in self.connections[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
                    results.append(neighbor)
                    if len(results) == max_results:
                        break
        return results
