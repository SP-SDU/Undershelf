import pytest
from django.urls import reverse

from data_access.models import Book


@pytest.mark.django_db
class TestViews:
    """Tests for the views"""

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

    def test_index_view(self, client):
        """Test index view"""
        url = reverse("index")
        response = client.get(url)
        assert response.status_code == 200
        assert "Undershelf" in str(response.content)

    def test_search_view(self, client, sample_book):
        """Test search view"""
        url = reverse("search")
        response = client.get(url)
        assert response.status_code == 200
        assert "Books" in str(response.content)

    def test_book_details_view(self, client, sample_book):
        """Test book details view"""
        url = reverse("book_details", kwargs={"book_id": sample_book.id})
        response = client.get(url)
        assert response.status_code == 200
        assert sample_book.title in str(response.content)
