import os
import json
import threading
import string
import random
import uuid
from flask_security.utils import hash_password
from data.models import Book, Role, User, db

def seed_books(app):
    print("Starting database seeding...")
    
    json_path = os.path.join(app.root_path, 'data', 'merged_dataframe.json')
    if os.path.exists(json_path):
        print(f"Found data file at {json_path}")
        with open(json_path, 'r', encoding='utf-8') as file:
            books_data = json.load(file)
            batch_size = 1000
            processed = 0
            seen_ids = set()
            
            for i in range(0, len(books_data), batch_size):
                batch = books_data[i:i + batch_size]
                with app.app_context():
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

def background_seed(app):
    print("Initializing background seeding...")
    thread = threading.Thread(target=lambda: seed_books(app))
    thread.daemon = True
    thread.start()

def build_sample_db(app, user_datastore):
    with app.app_context():
        db.drop_all()
        db.create_all()

        user_role = Role(name='user')
        super_user_role = Role(name='superuser')
        db.session.add(user_role)
        db.session.add(super_user_role)
        db.session.commit()

        user_datastore.create_user(
            first_name='Admin',
            email='admin',
            password=hash_password('admin'),
            fs_uniquifier=str(uuid.uuid4()),
            roles=[user_role, super_user_role]
        )

        first_names = [
            'Harry', 'Amelia', 'Oliver', 'Jack', 'Isabella'
            # ...existing names...
        ]
        last_names = [
            'Brown', 'Smith', 'Patel', 'Jones', 'Williams'
            # ...existing names...
        ]

        for i in range(len(first_names)):
            tmp_email = f"{first_names[i].lower()}.{last_names[i].lower()}@example.com"
            tmp_pass = ''.join(random.choice(string.ascii_lowercase + string.digits) for i in range(10))
            user_datastore.create_user(
                first_name=first_names[i],
                last_name=last_names[i],
                email=tmp_email,
                password=hash_password(tmp_pass),
                fs_uniquifier=str(uuid.uuid4()),
                roles=[user_role]
            )
        db.session.commit()
        seed_books(app)
