import json

import pytest
from django.urls import reverse

from business_logic.bst import BST
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

    @pytest.fixture
    def multiple_books(self):
        """Create multiple books for testing search functionality"""
        books = [
            Book.objects.create(
                id="book1",
                title="Python Programming",
                authors="John Smith",
                publishedDate="2022",
            ),
            Book.objects.create(
                id="book2",
                title="Introduction to Django",
                authors="Jane Python",
                publishedDate="2023",
            ),
            Book.objects.create(
                id="book3",
                title="Advanced Python",
                authors="Robert Johnson",
                publishedDate="2021",
            ),
        ]
        return books

    def test_index_view(self, client):
        """Test index view"""
        url = reverse("index")
        response = client.get(url)
        assert response.status_code == 200
        assert "Undershelf" in str(response.content)
        # Check if the correct template was used
        assert "index.html" in [t.name for t in response.templates]
        # Check if 'top_books' is in the context (even if empty)
        assert "top_books" in response.context
        # Check context for unauthenticated user
        assert response.context["user_is_authenticated"] is False
        assert response.context["current_user"].is_anonymous

    def test_search_view(self, client, sample_book):
        """Test search view"""
        url = reverse("search")
        response = client.get(url)
        assert response.status_code == 200
        assert "Books" in str(response.content)

    def test_search_view_with_query(self, client, multiple_books):
        """Test search view with query parameters"""
        # Test basic query
        url = reverse("search") + "?q=Python"
        response = client.get(url)
        assert response.status_code == 200
        assert "Python" in str(response.content)

        # Test sorting
        url = reverse("search") + "?sort=title&order=desc"
        response = client.get(url)
        assert response.status_code == 200

        # Test view type
        url = reverse("search") + "?view=list"
        response = client.get(url)
        assert response.status_code == 200
        assert '<table class="table w-full">' in str(response.content)

        # Test pagination
        url = reverse("search") + "?page=1"
        response = client.get(url)
        assert response.status_code == 200

    def test_book_details_view(self, client, sample_book):
        """Test book details view"""
        url = reverse("book_details", kwargs={"book_id": sample_book.id})
        response = client.get(url)
        assert response.status_code == 200
        assert sample_book.title in str(response.content)

    def test_autocomplete(self, client, multiple_books):
        """Test autocomplete functionality"""
        # Test with a prefix that should return results
        url = reverse("autocomplete") + "?q=Py"
        response = client.get(url)
        assert response.status_code == 200

        # Parse JSON response
        data = json.loads(response.content.decode("utf-8"))
        assert "suggestions" in data
        assert len(data["suggestions"]) > 0

        # Check if the suggestions contain the expected books
        titles = [item["title"] for item in data["suggestions"]]
        assert "Python Programming" in titles

        # Test with a prefix that should return no results
        url = reverse("autocomplete") + "?q=ZZZ"
        response = client.get(url)
        assert response.status_code == 200
        data = json.loads(response.content.decode("utf-8"))
        assert len(data["suggestions"]) == 0

        # Test with max results parameter
        url = reverse("autocomplete") + "?q=P&max=1"
        response = client.get(url)
        assert response.status_code == 200
        data = json.loads(response.content.decode("utf-8"))
        assert len(data["suggestions"]) <= 1

        # Test with empty query
        url = reverse("autocomplete") + "?q="
        response = client.get(url)
        assert response.status_code == 200
        data = json.loads(response.content.decode("utf-8"))
        assert len(data["suggestions"]) == 0


@pytest.mark.django_db
class TestBST:
    """Tests for the BST functionality in views"""

    @pytest.fixture
    def sample_books(self):
        """Create sample books for BST testing"""
        books = [
            Book.objects.create(
                id="book1",
                title="Python for Beginners",
                authors="John Smith",
                publishedDate="2022",
            ),
            Book.objects.create(
                id="book2",
                title="Learn Django",
                authors="Jane Python",
                publishedDate="2023",
            ),
            Book.objects.create(
                id="book3",
                title="Data Science with Python",
                authors="Robert Johnson",
                publishedDate="2021",
            ),
        ]
        return books

    def test_search_in_books(self, sample_books):
        """Test BST.search_in_books method"""
        # Search by title substring
        results = BST.search_in_books(sample_books, "Python")
        assert len(results) == 3
        # Verify the books with Python in title are found
        book_titles = [book.title for book in results]
        assert "Python for Beginners" in book_titles
        assert "Data Science with Python" in book_titles

        # Verify the book with Python in author name is found
        authors = [book.authors for book in results]
        assert "Jane Python" in authors

        # Search by author substring
        results = BST.search_in_books(sample_books, "John")
        assert len(results) == 2
        assert results[0].authors == "John Smith"

        # Search with no matches
        results = BST.search_in_books(sample_books, "JavaScript")
        assert len(results) == 0

    def test_bst_build_and_insert(self):
        """Test creating a BST and inserting books"""
        book1 = Book(id="test1", title="Test Book 1", authors="Author 1")
        book2 = Book(id="test2", title="Test Book 2", authors="Author 2")

        # Create BST
        bst = BST()
        assert bst.root is None

        # Insert first book
        bst.insert(book1)
        assert bst.root is not None
        assert bst.root.book.id == "test1"

        # Insert second book
        bst.insert(book2)

        # Search in the built tree
        results = []
        bst._search(bst.root, "test", results)
        assert len(results) == 2
