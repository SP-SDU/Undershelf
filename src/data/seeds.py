import os
import threading
import pandas as pd  # type: ignore
from flask_security.utils import hash_password
from data.models import Role, Book, Review
from extensions import db


class Seeds:
    def __init__(self, app, user_datastore):
        self.app = app
        self.user_datastore = user_datastore

    def create_roles(self):
        """Create default roles."""
        roles = {
            'user': Role(name='user'),
            'superuser': Role(name='superuser')
        }
        db.session.add_all(roles.values())
        db.session.commit()
        return roles

    def create_users(self, roles):
        """Create default users."""
        self.user_datastore.create_user(
            first_name='Admin',
            email='admin@example.com',
            password=hash_password('admin'),
            roles=[roles['user'], roles['superuser']]
        )
        db.session.commit()

    def seed_data(self):
        """Seed book data and ratings from CSV file."""
        print("Starting CSV database seeding...")
        
        # Path to your CSV file (adjust if needed)
        csv_path = os.path.join(self.app.root_path, 'data', 'merged_dataframe.csv')
        if os.path.exists(csv_path):
            print(f"Found CSV file at {csv_path}")
            # Read the merged CSV into a DataFrame.
            df = pd.read_csv(csv_path)
            
            # --- Seed Book Data ---
            book_data_cols = [
                'Id', 'Title', 'description', 'authors', 'image',
                'publisher', 'publishedDate', 'categories', 'ratingsCount'
            ]
            # Drop duplicates by the unique book identifier.
            books_df = df[book_data_cols].drop_duplicates(subset=['Id'])
            
            batch_size = 1000  # Number of records to process per batch.
            processed_books = 0
            for i in range(0, len(books_df), batch_size):
                batch = books_df.iloc[i:i + batch_size]
                with self.app.app_context():
                    for _, row in batch.iterrows():
                        book = Book(
                            id=str(row['Id']),
                            title=row['Title'],
                            description=row.get('description'),
                            authors=row.get('authors'),
                            image=row.get('image'),
                            publisher=row.get('publisher'),
                            publishedDate=row.get('publishedDate'),
                            categories=row.get('categories'),
                            ratingsCount=row.get('ratingsCount')
                        )
                        db.session.add(book)
                    
                    db.session.commit()
                    processed_books += len(batch)
                print(f"Processed batch of {processed_books} books")

            # --- Seed Book Ratings ---
            rating_cols = ['Id', 'User_id', 'review/score']
            ratings_df = df[rating_cols]
            
            processed_ratings = 0
            for i in range(0, len(ratings_df), batch_size):
                batch = ratings_df.iloc[i:i + batch_size]
                with self.app.app_context():
                    for _, row in batch.iterrows():
                        rating = Review(
                            book_id=str(row['Id']),
                            user_id=row.get('User_id'),
                            review_score=row.get('review/score')
                        )
                        db.session.add(rating)
                    
                    db.session.commit()
                    processed_ratings += len(batch)
                print(f"Processed batch of {processed_ratings} ratings")
            
            print("CSV database seeding completed successfully.")
        else:
            print(f"Warning: Could not find CSV file at {csv_path}")

    def background_seed(self):
        """Start seeding data in a background thread."""
        print("Initializing background CSV seeding...")
        thread = threading.Thread(target=self.seed_data)
        thread.daemon = True
        thread.start()


def seed(app, user_datastore):
    """Seeds the database."""
    with app.app_context():
        db.drop_all()
        db.create_all()

        seeds = Seeds(app, user_datastore)
        roles = seeds.create_roles()
        seeds.create_users(roles)
        seeds.background_seed()
