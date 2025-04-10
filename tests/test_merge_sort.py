import pytest

from business_logic.merge_sort import MergeSort
from data_access.models import Book


class TestMergeSort:
    """Tests for the MergeSort class"""

    @pytest.fixture
    def sample_books(self):
        """Create sample books for testing"""
        books = [
            Book(id="1", title="Book C", publishedDate="2020", ratingsCount=10),
            Book(id="2", title="Book A", publishedDate="2022", ratingsCount=30),
            Book(id="3", title="Book B", publishedDate="2018", ratingsCount=20),
        ]
        return books

    def test_sort_by_title(self, sample_books):
        """Test sorting by title"""
        sorted_books = MergeSort.sort_books(sample_books, "title", ascending=True)
        assert sorted_books[0].title == "Book A"
        assert sorted_books[1].title == "Book B"
        assert sorted_books[2].title == "Book C"

    def test_sort_by_title_desc(self, sample_books):
        """Test sorting by title in descending order"""
        sorted_books = MergeSort.sort_books(sample_books, "title", ascending=False)
        assert sorted_books[0].title == "Book C"
        assert sorted_books[1].title == "Book B"
        assert sorted_books[2].title == "Book A"

    def test_sort_by_date(self, sample_books):
        """Test sorting by date"""
        sorted_books = MergeSort.sort_books(sample_books, "date", ascending=True)
        assert sorted_books[0].publishedDate == "2018"
        assert sorted_books[1].publishedDate == "2020"
        assert sorted_books[2].publishedDate == "2022"

    def test_sort_by_ratings_count(self, sample_books):
        """Test sorting by ratings count"""
        sorted_books = MergeSort.sort_books(
            sample_books, "ratings_count", ascending=True
        )
        assert sorted_books[0].ratingsCount == 10
        assert sorted_books[1].ratingsCount == 20
        assert sorted_books[2].ratingsCount == 30
