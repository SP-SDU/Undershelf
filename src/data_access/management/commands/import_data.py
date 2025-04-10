import csv
import os
from django.core.management.base import BaseCommand
from django.db import transaction
from data_access.models import Book, Review

BOOK_BATCH_SIZE = 500
REVIEW_BATCH_SIZE = 1000

class Command(BaseCommand):
    help = "Seeds the database with book and review data from a CSV file."

    def add_arguments(self, parser):
        parser.add_argument(
            'file_path',
            type=str,
            help='Path to the CSV file.'
        )

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"File not found: {file_path}"))
            return

        self.stdout.write("Starting database seeding...")
        seed_data(file_path)
        self.stdout.write("Database seeding complete.")


def seed_data(file_path):
    """Seeds Books and Reviews using batch insertions."""
    books = {}
    reviews = []

    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            book_id = row['Id']
            if book_id not in books:
                books[book_id] = Book(
                    id=book_id,
                    title=row['Title'],
                    description=row.get('description') or None,
                    authors=str(row.get('authors')).strip("[]").replace("'", ""),
                    image=row.get('image') or None,
                    publisher=row.get('publisher') or None,
                    publishedDate=row.get('publishedDate') or None,
                    categories=str(row.get('categories')).strip("[]").replace("'", ""),
                    ratingsCount=float(row['ratingsCount']) if row.get('ratingsCount') not in [None, '', 'null'] else None,
                )

            reviews.append(Review(
                book_id=book_id,
                user_id=row.get('User_id') or None,
                review_score=float(row['review/score']) if row.get('review/score') not in [None, '', 'null'] else None,
            ))

            # Check batch sizes: if the batch sizes are reached, flush the objects.
            if len(books) >= BOOK_BATCH_SIZE and len(reviews) >= REVIEW_BATCH_SIZE:
                bulk_insert(books, reviews)
                books.clear()
                reviews.clear()

        # Insert any remaining objects after processing the whole CSV.
        if books or reviews:
            bulk_insert(books, reviews)


def bulk_insert(books_dict, reviews_list):
    """Bulk-insert them into the database inside a single transaction ensuring atomicity."""
    with transaction.atomic():
        book_objs = list(books_dict.values())
        # Use bulk_create with ignore_conflicts in case a Book already exists.
        Book.objects.bulk_create(book_objs, ignore_conflicts=True)
        # Insert reviews in smaller chunks.
        for i in range(0, len(reviews_list), REVIEW_BATCH_SIZE):
            Review.objects.bulk_create(reviews_list[i:i+REVIEW_BATCH_SIZE])
