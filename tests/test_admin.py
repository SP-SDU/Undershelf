import pytest
from django.contrib import admin
from django.urls import reverse
from django.test import Client

from data_access.models import Book, Review
from data_access.admin import BookAdmin, ReviewAdmin


@pytest.mark.django_db
class TestAdminConfiguration:
    """Tests for the Admin configuration"""

    def test_book_registered(self):
        """Test that the Book model is registered with BookAdmin"""
        assert isinstance(admin.site._registry[Book], BookAdmin)

    def test_review_registered(self):
        """Test that the Review model is registered with ReviewAdmin"""
        assert isinstance(admin.site._registry[Review], ReviewAdmin)

    def test_book_admin_configuration(self):
        """Test BookAdmin configuration"""
        book_admin = admin.site._registry[Book]
        
        # Test list_display
        assert 'id' in book_admin.list_display
        assert 'title' in book_admin.list_display
        assert 'authors' in book_admin.list_display
        assert 'display_categories' in book_admin.list_display
        assert 'average_rating_display' in book_admin.list_display
        
        # Test list_filter
        assert 'publisher' in book_admin.list_filter
        assert 'publishedDate' in book_admin.list_filter
        
        # Test search_fields
        assert 'title' in book_admin.search_fields
        assert 'authors' in book_admin.search_fields
        assert 'description' in book_admin.search_fields
        
        # Test inlines and fieldsets
        assert len(book_admin.inlines) == 1
        assert len(book_admin.fieldsets) > 0
        
    def test_review_admin_configuration(self):
        """Test ReviewAdmin configuration"""
        review_admin = admin.site._registry[Review]
        
        # Test list_display
        assert 'review_id' in review_admin.list_display
        assert 'book_title' in review_admin.list_display
        assert 'user_id' in review_admin.list_display
        assert 'review_score' in review_admin.list_display


@pytest.mark.django_db
class TestAdminCustomMethods:
    """Tests for custom admin methods"""
    
    @pytest.fixture
    def sample_book(self):
        """Create a sample book"""
        book = Book.objects.create(
            id="test123",
            title="Test Book",
            description="Test description",
            authors="Test Author",
            categories="Fiction, Drama",
            ratingsCount=10
        )
        return book
        
    @pytest.fixture
    def sample_review(self, sample_book):
        """Create a sample review"""
        review = Review.objects.create(
            book=sample_book,
            user_id="user123",
            review_score=4.5
        )
        return review
    
    def test_display_categories(self, sample_book):
        """Test the display_categories method"""
        book_admin = admin.site._registry[Book]
        assert book_admin.display_categories(sample_book) == "Fiction, Drama"
        
        # Test with empty categories
        sample_book.categories = None
        sample_book.save()
        assert book_admin.display_categories(sample_book) == "N/A"
    
    def test_average_rating_display(self, sample_book, sample_review):
        """Test the average_rating_display method"""
        book_admin = admin.site._registry[Book]
        
        # With a review
        assert book_admin.average_rating_display(sample_book) == "4.50"
        
        # Without reviews
        Review.objects.all().delete()
        assert book_admin.average_rating_display(sample_book) == "No ratings"
    
    def test_book_title(self, sample_book, sample_review):
        """Test the book_title method"""
        review_admin = admin.site._registry[Review]
        assert review_admin.book_title(sample_review) == "Test Book"


@pytest.mark.django_db
class TestAdminPages:
    """Tests for admin page accessibility"""
    
    @pytest.fixture
    def admin_client(self, admin_user):
        """Create an admin client"""
        client = Client()
        client.force_login(admin_user)
        return client
        
    def test_book_admin_page(self, admin_client):
        """Test access to Book admin page"""
        url = reverse('admin:data_access_book_changelist')
        response = admin_client.get(url)
        assert response.status_code == 200
        
    def test_review_admin_page(self, admin_client):
        """Test access to Review admin page"""
        url = reverse('admin:data_access_review_changelist')
        response = admin_client.get(url)
        assert response.status_code == 200
