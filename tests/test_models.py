import pytest
from django.db.models import Avg

from data_access.models import Book, Review


@pytest.mark.django_db
class TestBookModel:
    """Tests for the Book model"""

    @pytest.fixture
    def sample_book(self):
        """Create a sample book"""
        book = Book.objects.create(
            id="test123",
            title="Test Book",
            description="Test description",
            authors="Test Author",
            publishedDate="2023",
        )
        return book

    def test_book_creation(self, sample_book):
        """Test book creation"""
        assert Book.objects.count() == 1
        assert sample_book.title == "Test Book"

    def test_book_str(self, sample_book):
        """Test book string representation"""
        assert str(sample_book) == "Test Book"

    def test_average_rating(self, sample_book):
        """Test average_rating method"""
        # Create some reviews
        Review.objects.create(book=sample_book, review_score=4.0)
        Review.objects.create(book=sample_book, review_score=5.0)
        Review.objects.create(book=sample_book, review_score=3.0)

        # Calculate expected average
        expected_avg = Review.objects.filter(book=sample_book).aggregate(
            avg=Avg("review_score")
        )["avg"]

        # Test the method
        assert sample_book.average_rating() == expected_avg
