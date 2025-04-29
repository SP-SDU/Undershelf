import pytest

from business_logic.top_k import BookRanker
from data_access.models import Book


class TestTopK:
    @pytest.fixture
    def sample_book(self, db):
        book = Book.objects.create(
            title="Test Book",
            ratingsCount=100,
            publishedDate="2023-01-01",
        )
        return book

    def test_top_k(self, sample_book, db):
        results = BookRanker.get_top_k(1)
        assert results[0]["title"] == "Test Book"
