import pytest

from business_logic.cbf import BookRecommender
from data_access.models import Book, Review


@pytest.mark.django_db
class TestBookRecommender:
    """Tests for the BookRecommender class"""

    @pytest.fixture
    def sample_user_id(self):
        """Create a sample user ID"""
        return "test_user_123"

    @pytest.fixture
    def sample_books(self):
        """Create sample books for testing"""
        books = [
            Book.objects.create(
                id="book1",
                title="Python Programming",
                description="Learn Python programming",
                authors="John Smith",
                publishedDate="2022",
                categories="Programming,Computer Science",
                ratingsCount=100,
            ),
            Book.objects.create(
                id="book2",
                title="Data Science Essentials",
                description="Introduction to data science",
                authors="Jane Doe",
                publishedDate="2021",
                categories="Data Science,Programming",
                ratingsCount=80,
            ),
            Book.objects.create(
                id="book3",
                title="Machine Learning Basics",
                description="Getting started with ML",
                authors="Robert Johnson",
                publishedDate="2020",
                categories="Machine Learning,Data Science",
                ratingsCount=90,
            ),
            Book.objects.create(
                id="book4",
                title="Advanced Python",
                description="Advanced Python concepts",
                authors="Sarah Williams",
                publishedDate="2023",
                categories="Programming,Computer Science",
                ratingsCount=70,
            ),
        ]
        return books

    @pytest.fixture
    def sample_reviews(self, sample_books, sample_user_id):
        """Create sample reviews for testing"""
        reviews = [
            Review.objects.create(
                book=sample_books[0], user_id=sample_user_id, review_score=4.5
            ),
            Review.objects.create(
                book=sample_books[1], user_id=sample_user_id, review_score=3.5
            ),
            Review.objects.create(
                book=sample_books[2], user_id=sample_user_id, review_score=5.0
            ),
            # No review for book4 to test recommendation logic
        ]
        return reviews

    def test_get_cbf_list_empty(self, sample_user_id):
        """Test get_cbf_list when no reviews exist"""
        # Test with a user who has no reviews
        result = BookRecommender.get_cbf_list("nonexistent_user")
        assert result == []

    def test_get_cbf_list_with_reviews(
        self, sample_books, sample_reviews, sample_user_id
    ):
        """Test get_cbf_list with user reviews"""
        result = BookRecommender.get_cbf_list(sample_user_id)

        # Check that we got recommendations
        assert isinstance(result, list)

        # Ensure all returned items are Book instances
        for item in result:
            assert isinstance(item, Book)

    def test_get_cbf_list_limit(self, sample_books, sample_reviews, sample_user_id):
        """Test get_cbf_list with custom n_recommendations"""
        # Test with n_recommendations=2
        result = BookRecommender.get_cbf_list(sample_user_id, n_recommendations=2)

        # Check that we got at most 2 recommendations
        assert len(result) <= 2

        # Test with n_recommendations=1
        result = BookRecommender.get_cbf_list(sample_user_id, n_recommendations=1)

        # Check that we got at most 1 recommendation
        assert len(result) <= 1
