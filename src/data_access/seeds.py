import logging
import os
import threading
import time

import polars as pl
from django.core.management import call_command
from django.db import transaction

from data_access.models import Book, Review

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [SEEDER] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("seeder")


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
        start_time = time.time()
        logger.info("Starting database seeding process...")

        csv_path = os.path.join("src", "data_access", "merged_dataframe.csv")
        logger.info(f"Looking for CSV file at: {os.path.abspath(csv_path)}")

        if not os.path.exists(csv_path):
            logger.error(f"ERROR: Could not find CSV file at {csv_path}")
            return

        logger.info(f"CSV file found. Reading data from {csv_path}...")
        try:
            df = pl.read_csv(csv_path)
            logger.info(f"Successfully loaded CSV with {len(df)} rows")
        except Exception as e:
            logger.error(f"Failed to read CSV: {str(e)}")
            return

        # --- Seed Book Data ---
        logger.info("Processing book data...")
        try:
            books_df = df.select(self.BOOK_COLUMNS).unique(subset=["Id"])
            logger.info(f"Found {len(books_df)} unique books")

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
                        categories=str(row.get("categories"))
                        .strip("[]")
                        .replace("'", ""),
                        ratingsCount=row.get("ratingsCount"),
                    )
                )
            logger.info(f"Created {len(book_objects)} Book objects for insertion")
            books_inserted = self._process_batch(book_objects, Book)
            logger.info(
                f"Finished processing book data, inserted {books_inserted} books"
            )

            # Get the set of book IDs that were successfully inserted
            inserted_book_ids = set(Book.objects.values_list("id", flat=True))
            logger.info(
                f"Found {len(inserted_book_ids)} book IDs in database for validation"
            )
        except Exception as e:
            logger.error(f"Error processing book data: {str(e)}")
            return  # Exit early if book insertion fails

        # --- Seed Book Ratings ---
        logger.info("Processing ratings data...")
        try:
            ratings_df = df.select(self.RATING_COLUMNS)
            logger.info(f"Found {len(ratings_df)} ratings in CSV")

            rating_objects = []
            skipped_ratings = 0

            for row in ratings_df.to_dicts():
                # Get the book_id from the row and ensure it's a string
                book_id = str(row["Id"])

                # Only create reviews for books that exist in the database
                if book_id in inserted_book_ids:
                    rating_objects.append(
                        Review(
                            book_id=book_id,
                            user_id=row.get("User_id"),
                            review_score=row.get("review/score"),
                        )
                    )
                else:
                    skipped_ratings += 1

            logger.info(f"Created {len(rating_objects)} Review objects for insertion")
            logger.info(
                f"Skipped {skipped_ratings} reviews with missing book references"
            )

            if rating_objects:
                ratings_inserted = self._process_batch(rating_objects, Review)
                logger.info(
                    f"Finished processing ratings data, inserted {ratings_inserted} reviews"
                )
            else:
                logger.warning("No valid review objects to insert")
        except Exception as e:
            logger.error(f"Error processing ratings data: {str(e)}")

        elapsed_time = time.time() - start_time
        logger.info(f"Database seeding completed in {elapsed_time:.2f} seconds")

    def _process_batch(self, objects, model_class):
        """Process objects in batches using Django's bulk_create."""
        total_batches = (len(objects) + self.BATCH_SIZE - 1) // self.BATCH_SIZE
        total_inserted = 0
        logger.info(
            f"Processing {len(objects)} {model_class.__name__} objects in {total_batches} batches"
        )

        for i in range(0, len(objects), self.BATCH_SIZE):
            batch_num = (i // self.BATCH_SIZE) + 1
            chunk = objects[i : i + self.BATCH_SIZE]
            batch_start = time.time()
            logger.info(
                f"Processing batch {batch_num}/{total_batches} with {len(chunk)} objects..."
            )

            try:
                with transaction.atomic():
                    # Count before insertion
                    before_count = model_class.objects.count()

                    # Create objects WITHOUT ignore_conflicts parameter
                    created = model_class.objects.bulk_create(chunk)

                    # Count after insertion to determine how many were actually inserted
                    after_count = model_class.objects.count()
                    inserted_count = after_count - before_count
                    total_inserted += inserted_count

                    batch_time = time.time() - batch_start
                    logger.info(
                        f"Batch {batch_num} completed in {batch_time:.2f} seconds"
                    )
                    logger.info(f"Inserted {inserted_count} records")

                    # Check if we had unexpected data loss
                    if inserted_count < len(chunk):
                        logger.warning(
                            f"Expected to insert {len(chunk)} records but only inserted {inserted_count}"
                        )
            except Exception as e:
                logger.error(f"Error in batch {batch_num}: {str(e)}")

        logger.info(
            f"Total {model_class.__name__} records inserted: {total_inserted} out of {len(objects)} attempted"
        )
        return total_inserted

    def background_seed(self):
        """Start seeding data in a background thread."""
        logger.info("Starting background seeding thread...")
        thread = threading.Thread(target=self.seed_data)
        thread.daemon = True
        thread.start()
        logger.info("Background seeding thread started")


def seed(force=False):
    """Seeds the database.

    Args:
        force (bool): If True, will re-seed the database even if it contains data
    """
    logger.info("Seed function called")
    logger.info("Running database migrations...")
    call_command("migrate", interactive=False)
    logger.info("Migrations completed")

    # Count existing records to determine if seeding is necessary
    book_count = Book.objects.count()
    review_count = Review.objects.count()
    logger.info(f"Current database status: {book_count} books, {review_count} reviews")

    if book_count > 0 and not force:
        logger.info("Database already contains data. Skipping seeding.")
        return

    if force and (book_count > 0 or review_count > 0):
        logger.warning("Force flag set. Clearing existing data before re-seeding.")
        # Clear existing data
        with transaction.atomic():
            Review.objects.all().delete()
            Book.objects.all().delete()
        logger.info("Existing data cleared successfully")

    logger.info("Starting database seeding process")
    seeds = Seeds()
    seeds.background_seed()
    logger.info("Seed initialization complete - data loading continues in background")
