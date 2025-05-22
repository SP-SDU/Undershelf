import pytest

from business_logic.bfs import GraphRecommender
from data_access.models import Book


@pytest.mark.django_db
class TestGraphRecommender:
    """Tests for the GraphRecommender class"""

    @pytest.fixture
    def sample_books(self):
        """Create sample books for testing"""
        books = [
            Book.objects.create(
                id="book1",
                title="Python Basics",
                authors="John Smith",
                categories="Programming,Computer Science",
            ),
            Book.objects.create(
                id="book2",
                title="Advanced Python",
                authors="John Smith",
                categories="Programming,Advanced",
            ),
            Book.objects.create(
                id="book3",
                title="Data Science",
                authors="Jane Doe",
                categories="Data Science,Programming",
            ),
            Book.objects.create(
                id="book4",
                title="Machine Learning",
                authors="Robert Johnson",
                categories="Machine Learning,Data Science",
            ),
            Book.objects.create(
                id="book5",
                title="Web Development",
                authors="Alice Brown",
                categories="Web,Programming",
            ),
        ]
        return books

    def test_get_recommendations_basic(self, sample_books):
        """Test basic recommendation functionality"""
        recommendations = GraphRecommender.get_recommendations("book1")

        assert len(recommendations) > 0

        # Ensure all returned items are Book instances
        for book in recommendations:
            assert isinstance(book, Book)

    def test_get_recommendations_max_depth(self, sample_books):
        """Test recommendation with different max_depth values"""
        shallow_recommendations = GraphRecommender.get_recommendations(
            "book1", max_depth=1
        )

        deep_recommendations = GraphRecommender.get_recommendations(
            "book1", max_depth=2
        )

        # Deeper search should find at least as many books as shallow search
        assert len(deep_recommendations) >= len(shallow_recommendations)

    def test_get_recommendations_max_results(self, sample_books):
        """Test recommendation with different max_results values"""
        limited_recommendations = GraphRecommender.get_recommendations(
            "book1", max_results=2
        )
        assert len(limited_recommendations) <= 2

        default_recommendations = GraphRecommender.get_recommendations("book1")

        # If there are more than 2 books that could be recommended,
        # limited_recommendations should be strictly less than default_recommendations
        if len(default_recommendations) > 2:
            assert len(limited_recommendations) < len(default_recommendations)

    def test_get_recommendations_no_connections(self):
        """Test recommendation when there are no connections"""
        # Create an isolated book with no author or category connections
        _ = Book.objects.create(
            id="isolated",
            title="Isolated Book",
            authors="Unique Author",
            categories="Unique Category",
        )

        recommendations = GraphRecommender.get_recommendations("isolated")

        assert recommendations == []

    def test_get_recommendations_nonexistent_book(self):
        """Test recommendation with a nonexistent book ID"""
        with pytest.raises(Book.DoesNotExist):
            GraphRecommender.get_recommendations("nonexistent_id")
