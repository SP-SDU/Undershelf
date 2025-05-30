import pytest

from business_logic.bst import BST, BSTNode
from data_access.models import Book


class TestBSTClass:
    """Comprehensive tests for BST implementation"""

    @pytest.fixture
    def sample_books(self):
        """Create sample books for testing"""
        books = [
            Book(
                id="book1",
                title="Harry Potter",
                authors="J.K. Rowling",
                publishedDate="1997",
            ),
            Book(
                id="book2",
                title="The Hobbit",
                authors="J.R.R. Tolkien",
                publishedDate="1937",
            ),
            Book(
                id="book3",
                title="Pride and Prejudice",
                authors="Jane Austen",
                publishedDate="1813",
            ),
            Book(
                id="book4",
                title="To Kill a Mockingbird",
                authors="Harper Lee",
                publishedDate="1960",
            ),
            Book(
                id="book5", title="1984", authors="George Orwell", publishedDate="1949"
            ),
        ]
        return books

    def test_bst_node_creation(self):
        """Test BSTNode initialization"""
        book = Book(id="test", title="Test Book")
        node = BSTNode("test_key", book)

        assert node.key == "test_key"
        assert node.book == book
        assert node.left is None
        assert node.right is None

    def test_bst_initialization(self):
        """Test BST initialization with default and custom key functions"""
        # Default key function
        bst = BST()
        assert bst.root is None
        book = Book(id="test", title="Test Book", authors="Test Author")
        key = bst.key_func(book)
        assert key == "Test BookTest Author"

        # Custom key function
        custom_bst = BST(key_func=lambda b: b.id)
        assert custom_bst.root is None
        key = custom_bst.key_func(book)
        assert key == "test"

    def test_build_from_books(self, sample_books):
        """Test building a BST from a list of books"""
        bst = BST()
        bst.build(sample_books)

        # Verify tree is built
        assert bst.root is not None

        # Test traversal to ensure all books are in the tree
        results = []
        bst._search(bst.root, "", results)
        assert len(results) == len(sample_books)

        # Check if all book IDs are in the results
        result_ids = {book.id for book in results}
        original_ids = {book.id for book in sample_books}
        assert result_ids == original_ids

    def test_search(self, sample_books):
        """Test search functionality"""
        bst = BST()
        bst.build(sample_books)

        # Search for books by title
        results = bst.search("harry")
        assert len(results) == 1
        assert results[0].title == "Harry Potter"

        # Search for books by author
        results = bst.search("tolkien")
        assert len(results) == 1
        assert results[0].authors == "J.R.R. Tolkien"

        # Search for multiple matches
        results = bst.search("J.")
        assert len(results) == 2  # Should find both J.K. Rowling and J.R.R. Tolkien

        # Search with no matches
        results = bst.search("nonexistent")
        assert len(results) == 0

    def test_insert_and_search(self):
        """Test inserting individual books and searching"""
        bst = BST()

        # Insert books one by one
        book1 = Book(id="book1", title="Book One", authors="Author A")
        book2 = Book(id="book2", title="Book Two", authors="Author B")
        book3 = Book(
            id="book3", title="Book Two Clone", authors="Author C"
        )  # Same title as book2

        bst.insert(book1)
        bst.insert(book2)
        bst.insert(book3)

        # Search for exact match
        results = bst.search("Book One")
        assert len(results) == 1
        assert results[0].id == "book1"

        # Search for multiple matches
        results = bst.search("Book Two")
        assert len(results) == 2
        ids = {book.id for book in results}
        assert "book2" in ids
        assert "book3" in ids
