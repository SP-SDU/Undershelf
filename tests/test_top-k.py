from django.test import TestCase
from data_access.models import Book
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ..business_logic.top_k import BookRanker

class TopKTest(TestCase):
    def setUp(self):
        Book.objects.create(
            title="Test Book",
            ratingsCount=100,
            average_rating=4.5,
            publishedDate="2023-01-01"
        )

    def test_top_k(self):
        results = BookRanker.get_top_k(1)
        self.assertEqual(results[0]['title'], "Test Book")