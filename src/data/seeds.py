import os
import json
import threading
from flask_security.utils import hash_password
from data.models import Role, Book
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

    def seed_books(self):
        """Seed books from JSON file."""
        print("Starting database seeding...")
        
        json_path = os.path.join(self.app.root_path, 'data', 'merged_dataframe.json')
        if os.path.exists(json_path):
            print(f"Found data file at {json_path}")
            with open(json_path, 'r', encoding='utf-8') as file:
                books_data = json.load(file)
                batch_size = 1000
                processed = 0
                seen_ids = set()
                
                for i in range(0, len(books_data), batch_size):
                    batch = books_data[i:i + batch_size]
                    with self.app.app_context():
                        for book_data in batch:
                            try:
                                book_id = str(book_data['Id'])
                                if book_id not in seen_ids:
                                    book = Book.from_json(book_data)
                                    db.session.add(book)
                                    seen_ids.add(book_id)
                                    processed += 1
                            except Exception as e:
                                print(f"Error processing book: {e}")
                        db.session.commit()
                    print(f"Processed batch: {processed} books added")
        else:
            print(f"Warning: Could not find {json_path}")
        
        print("Database seeding completed")

    def background_seed(self):
        """Start book seeding in background thread."""
        print("Initializing background seeding...")
        thread = threading.Thread(target=self.seed_books)
        thread.daemon = True
        thread.start()


def seed(app, user_datastore):
    """seeds database."""
    with app.app_context():
        db.drop_all()
        db.create_all()
        
        seeds = Seeds(app, user_datastore)
        roles = seeds.create_roles()
        seeds.create_users(roles)
        seeds.background_seed()
