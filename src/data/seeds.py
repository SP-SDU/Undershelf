import os
import threading
import polars as pl
from flask_security.utils import hash_password
from data.models import Role, Book, Review
from extensions import db


class Seeds:
    BATCH_SIZE = 5000
    BOOK_COLUMNS = [
        'Id', 'Title', 'description', 'authors', 'image',
        'publisher', 'publishedDate', 'categories', 'ratingsCount'
    ]
    RATING_COLUMNS = ['Id', 'User_id', 'review/score']

    def __init__(self, app, user_datastore):
        self.app = app
        self.user_datastore = user_datastore

    def seed_roles(self):
        """Seeds default roles."""
        roles = {
            'user': Role(name='user'),
            'superuser': Role(name='superuser')
        }
        db.session.add_all(roles.values())
        db.session.commit()
        return roles

    def seed_users(self, roles):
        """Seeds default users."""
        self.user_datastore.create_user(
            first_name='Admin',
            email='admin@example.com',
            password=hash_password('admin'),
            roles=[roles['user'], roles['superuser']]
        )
        db.session.commit()

    def seed_data(self):
        """Seeds book data and ratings from CSV file."""
        csv_path = os.path.join(self.app.root_path, 'data', 'merged_dataframe.csv')
        if not os.path.exists(csv_path):
            print(f"Warning: Could not find CSV file at {csv_path}")
            return

        df = pl.read_csv(csv_path)

        # --- Seed Book Data ---
        books_df = df.select(self.BOOK_COLUMNS).unique(subset=['Id'])
        book_objects = []

        for row in books_df.to_dicts():
            book_objects.append(Book(
                id=str(row['Id']),
                title=row['Title'],
                description=row.get('description'),
                authors=str(row.get('authors')).strip("[]").replace("'", ""),
                image=row.get('image'),
                publisher=row.get('publisher'),
                publishedDate=row.get('publishedDate'),
                categories=str(row.get('categories')).strip("[]").replace("'", ""),
                ratingsCount=row.get('ratingsCount')
            ))

        self._process_batch(book_objects)

        # --- Seed Book Ratings ---
        ratings_df = df.select(self.RATING_COLUMNS)
        rating_objects = []

        for row in ratings_df.to_dicts():
            rating_objects.append(Review(
                book_id=str(row['Id']),
                user_id=row.get('User_id'),
                review_score=row.get('review/score')
            ))

        self._process_batch(rating_objects)

    def _process_batch(self, objects):
        with self.app.app_context():
            for i in range(0, len(objects), self.BATCH_SIZE):
                chunk = objects[i:i + self.BATCH_SIZE]
                db.session.bulk_save_objects(chunk)
                db.session.commit()

    def background_seed(self):
        """Start seeding data in a background thread."""
        thread = threading.Thread(target=self.seed_data)
        thread.daemon = True
        thread.start()


def seed(app, user_datastore):
    """Seeds the database."""
    with app.app_context():
        db.drop_all()
        db.create_all()

        seeds = Seeds(app, user_datastore)
        roles = seeds.seed_roles()
        seeds.seed_users(roles)
        seeds.background_seed()
