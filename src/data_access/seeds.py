import os
import threading

import polars as pl
from django.core.management import call_command
from django.db import transaction

from data_access.models import Book, Review


class Seeds:
    BATCH_SIZE = 5000
    BOOK_COLUMNS = [
        "Id",
        "Title",
        "description",
        "authors",
        "image",
        "publisher",
        "publishedDate",
        "categories",
        "ratingsCount",
    ]
    RATING_COLUMNS = ["Id", "User_id", "review/score"]

    def seed_data(self):
        """Seeds book data and ratings from CSV file."""
        csv_path = os.path.join("src", "data_access", "merged_dataframe.csv")
        if not os.path.exists(csv_path):
            print(f"Warning: Could not find CSV file at {csv_path}")
            return

        df = pl.read_csv(csv_path)

        # --- Seed Book Data ---
        books_df = df.select(self.BOOK_COLUMNS).unique(subset=["Id"])
        book_objects = []

        for row in books_df.to_dicts():
            book_objects.append(
                Book(
                    id=str(row["Id"]),
                    title=row["Title"],
                    description=row.get("description"),
                    authors=str(row.get("authors")).strip("[]").replace("'", ""),
                    image=row.get("image"),
                    publisher=row.get("publisher"),
                    publishedDate=row.get("publishedDate"),
                    categories=str(row.get("categories")).strip("[]").replace("'", ""),
                    ratingsCount=row.get("ratingsCount"),
                )
            )

        self._process_batch(book_objects, Book)

        # --- Seed Book Ratings ---
        ratings_df = df.select(self.RATING_COLUMNS)
        rating_objects = []

        for row in ratings_df.to_dicts():
            rating_objects.append(
                Review(
                    book_id=str(row["Id"]),
                    user_id=row.get("User_id"),
                    review_score=row.get("review/score"),
                )
            )

        self._process_batch(rating_objects, Review)

    def _process_batch(self, objects, model_class):
        """Process objects in batches using Django's bulk_create."""
        for i in range(0, len(objects), self.BATCH_SIZE):
            chunk = objects[i : i + self.BATCH_SIZE]
            with transaction.atomic():
                model_class.objects.bulk_create(chunk, ignore_conflicts=True)

    def background_seed(self):
        """Start seeding data in a background thread."""
        thread = threading.Thread(target=self.seed_data)
        thread.daemon = True
        thread.start()


def seed():
    """Seeds the database."""
    # TODO: figure out if I should Flush the database or migrate
    # call_command('flush', interactive=False)

    call_command("migrate", interactive=False)

    seeds = Seeds()
    seeds.background_seed()
