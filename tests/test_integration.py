import json

import pytest
from django.test import Client
from django.urls import reverse

from business_logic.bfs import GraphRecommender
from business_logic.bst import BST
from business_logic.cbf import BookRecommender
from business_logic.merge_sort import MergeSort
from business_logic.top_k import BookRanker
from data_access.models import Book, Review


@pytest.mark.django_db
class TestSystemIntegration:
    """Integration tests for end-to-end system functionality"""

    @pytest.fixture
    def client(self):
        """Create a test client"""
        return Client()

    @pytest.fixture
    def sample_books_for_integration(self):
        """Create a comprehensive set of books for integration testing"""
        books = [
            Book.objects.create(
                id="int_book1",
                title="Python Programming Fundamentals",
                authors="John Smith",
                description="Learn Python programming from basics to advanced",
                publishedDate="2022",
                categories="Programming,Computer Science",
                ratingsCount=150,
            ),
            Book.objects.create(
                id="int_book2",
                title="Data Science with Python",
                authors="Jane Doe",
                description="Comprehensive guide to data science using Python",
                publishedDate="2021",
                categories="Data Science,Programming",
                ratingsCount=120,
            ),
            Book.objects.create(
                id="int_book3",
                title="Machine Learning Algorithms",
                authors="Robert Johnson",
                description="Understanding ML algorithms and implementation",
                publishedDate="2020",
                categories="Machine Learning,Data Science",
                ratingsCount=90,
            ),
            Book.objects.create(
                id="int_book4",
                title="Web Development with Django",
                authors="Alice Brown",
                description="Building web applications with Django framework",
                publishedDate="2023",
                categories="Web Development,Django",
                ratingsCount=80,
            ),
            Book.objects.create(
                id="int_book5",
                title="Advanced Python Techniques",
                authors="John Smith",
                description="Advanced programming patterns in Python",
                publishedDate="2023",
                categories="Programming,Advanced",
                ratingsCount=95,
            ),
        ]
        return books

    @pytest.fixture
    def sample_reviews_for_integration(self, sample_books_for_integration):
        """Create reviews for integration testing"""
        user_id = "integration_test_user"
        reviews = [
            Review.objects.create(
                book=sample_books_for_integration[0],
                user_id=user_id,
                review_score=4.5,
            ),
            Review.objects.create(
                book=sample_books_for_integration[1],
                user_id=user_id,
                review_score=5.0,
            ),
            Review.objects.create(
                book=sample_books_for_integration[2],
                user_id=user_id,
                review_score=3.5,
            ),
        ]
        return reviews

    def test_search_view_integration_with_bst(
        self, client, sample_books_for_integration
    ):
        """Test end-to-end search functionality using BST"""
        # Test search with query parameter
        url = reverse("search") + "?q=Python"
        response = client.get(url)

        assert response.status_code == 200
        assert "Python Programming Fundamentals" in str(response.content)
        assert "Data Science with Python" in str(response.content)
        assert "Advanced Python Techniques" in str(response.content)

        # Verify BST is working in the background
        books = Book.objects.all()
        results = BST.search_in_books(books, "Python")
        assert len(results) == 3

    def test_sorting_view_integration_with_merge_sort(
        self, client, sample_books_for_integration
    ):
        """Test end-to-end sorting functionality using MergeSort"""
        # Test sorting by title ascending
        url = reverse("search") + "?sort=title&order=asc"
        response = client.get(url)
        assert response.status_code == 200

        # Test sorting by ratings count descending
        url = reverse("search") + "?sort=ratings_count&order=desc"
        response = client.get(url)
        assert response.status_code == 200

        # Verify MergeSort is working correctly
        books = list(Book.objects.all())
        sorted_books = MergeSort.sort_books(books, "ratings_count", ascending=False)
        assert sorted_books[0].ratingsCount >= sorted_books[-1].ratingsCount

    def test_recommendation_system_integration(
        self, client, sample_books_for_integration, sample_reviews_for_integration
    ):
        """Test end-to-end recommendation system integration"""
        book = sample_books_for_integration[0]
        url = reverse("book_details", kwargs={"book_id": book.id})
        response = client.get(url)

        assert response.status_code == 200
        assert book.title in str(response.content)

        # Verify BFS recommendations work
        bfs_recommendations = GraphRecommender.get_recommendations(book.id)
        assert isinstance(bfs_recommendations, list)

        # Verify CBF recommendations work
        user_id = "integration_test_user"
        cbf_recommendations = BookRecommender.get_cbf_list(user_id)
        assert isinstance(cbf_recommendations, list)

    def test_top_k_ranking_integration(self, client, sample_books_for_integration):
        """Test end-to-end Top-K ranking functionality"""
        url = reverse("index")
        response = client.get(url)

        assert response.status_code == 200
        assert "k_value" in response.context

        # Verify Top-K ranking works
        top_books = BookRanker.get_top_k(3)
        assert len(top_books) <= 3
        assert isinstance(top_books, list)

    def test_autocomplete_integration_with_bst(
        self, client, sample_books_for_integration
    ):
        """Test end-to-end autocomplete functionality"""
        url = reverse("autocomplete") + "?q=Py"
        response = client.get(url)

        assert response.status_code == 200
        data = json.loads(response.content.decode("utf-8"))
        assert "suggestions" in data
        assert len(data["suggestions"]) > 0

        # Verify suggestions contain Python-related books
        titles = [item["title"] for item in data["suggestions"]]
        python_books = [title for title in titles if "Python" in title]
        assert len(python_books) > 0

    def test_error_handling_integration(self, client):
        """Test system resilience and error handling"""
        # Test with non-existent book ID
        url = reverse("book_details", kwargs={"book_id": "nonexistent"})
        response = client.get(url)
        assert response.status_code == 404

        # Test autocomplete with very long query
        long_query = "x" * 1000
        url = reverse("autocomplete") + f"?q={long_query}"
        response = client.get(url)
        assert response.status_code == 200

    def test_view_type_switching_integration(
        self, client, sample_books_for_integration
    ):
        """Test switching between grid and list view types"""
        # Test grid view (default)
        url = reverse("search")
        response = client.get(url)
        assert response.status_code == 200

        # Test list view
        url = reverse("search") + "?view=list"
        response = client.get(url)
        assert response.status_code == 200
        assert '<table class="table w-full">' in str(response.content)

    def test_search_with_multiple_filters_integration(
        self, client, sample_books_for_integration
    ):
        """Test complex search with multiple filters and sorting"""
        url = reverse("search") + "?q=Python&sort=title&order=asc&view=list&page=1"
        response = client.get(url)

        assert response.status_code == 200
        assert "Python" in str(response.content)
        assert '<table class="table w-full">' in str(response.content)

    def test_full_system_workflow_integration(
        self, client, sample_books_for_integration, sample_reviews_for_integration
    ):
        """Test complete user workflow from search to book details"""
        # Step 1: Visit homepage
        response = client.get(reverse("index"))
        assert response.status_code == 200

        # Step 2: Search for books
        response = client.get(reverse("search") + "?q=Python")
        assert response.status_code == 200

        # Step 3: Use autocomplete
        response = client.get(reverse("autocomplete") + "?q=Py")
        assert response.status_code == 200
        data = json.loads(response.content.decode("utf-8"))
        assert len(data["suggestions"]) > 0

        # Step 4: View book details
        book = sample_books_for_integration[0]
        response = client.get(reverse("book_details", kwargs={"book_id": book.id}))
        assert response.status_code == 200
        assert book.title in str(response.content)

        # Step 5: Verify recommendations are shown
        assert "recommended_books" in response.context
