from business_logic.aspects import (
    input_validator,
    method_logger,
    performance_monitor,
    simple_cache,
    validate_non_empty_string,
)


class BSTNode:
    def __init__(self, key, book):
        self.key = key
        self.book = book
        self.left = None
        self.right = None


class BST:
    def __init__(self, key_func=None):
        # Use a default key function if none is provided
        if key_func is None:
            self.key_func = lambda b: (b.title or "") + (b.authors or "")
        else:
            self.key_func = key_func
        self.root = None

    def build(self, books):
        """Builds the BST from a list of books."""
        self.root = None
        for book in books:
            self.insert(book)

    def insert(self, book):
        key = self.key_func(book)
        self.root = self._insert(self.root, key, book)

    def _insert(self, node, key, book):
        if node is None:
            return BSTNode(key, book)
        if key < node.key:
            node.left = self._insert(node.left, key, book)
        elif key > node.key:
            node.right = self._insert(node.right, key, book)
        else:
            # Duplicate keys: store in right subtree for simplicity
            node.right = self._insert(node.right, key, book)
        return node

    def search(self, query):
        """Case-insensitive search for books whose key contains the query as substring."""
        results = []
        self._search(self.root, query.lower(), results)
        return results

    def _search(self, node, query, results):
        if node is None:
            return
        if query in str(node.key).lower():
            results.append(node.book)
        self._search(node.left, query, results)
        self._search(node.right, query, results)

    @classmethod
    @input_validator(validate_non_empty_string)
    @method_logger
    @performance_monitor
    @simple_cache(600)
    def search_in_books(cls, books, query):
        """Builds a BST from books and searches for the query."""
        bst = cls()
        bst.build(books)
        return bst.search(query)
