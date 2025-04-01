#!venv/bin/python
import os
import uuid
import json
from flask import Flask, url_for, redirect, render_template, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required, current_user
from flask_security.utils import hash_password
import flask_admin
from flask_admin.contrib import sqla
from flask_admin import helpers as admin_helpers
from flask_admin import BaseView, expose
from wtforms import PasswordField
from business.book_sorter import BookSorter
import threading

# Create Flask application
app = Flask(__name__, 
           template_folder='presentation/templates',
           static_folder='presentation/static')
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)

# Add seeding status flag
is_seeding = False
has_checked_db = False

# Define models
roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    def __str__(self):
        return self.email


# Add Book model
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.JSON, nullable=False)

    @property
    def book_id(self):
        """Get the book's ID from the JSON data"""
        return self.data.get('Id')

    @staticmethod
    def from_json(json_data):
        """Create a Book instance from JSON data"""
        if not json_data.get('Id'):
            raise ValueError("Book data must contain an 'Id' field")
        return Book(data=json_data)

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# Initialize the database after all models are defined
with app.app_context():
    db.create_all()

# Create customized model view class
class MyModelView(sqla.ModelView):

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.has_role('superuser'):
            return True

        return False

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))


    # can_edit = True
    edit_modal = True
    create_modal = True    
    can_export = True
    can_view_details = True
    details_modal = True

class UserView(MyModelView):
    column_editable_list = ['email', 'first_name', 'last_name']
    column_searchable_list = column_editable_list
    column_exclude_list = ['password']
    #form_excluded_columns = column_exclude_list
    column_details_exclude_list = column_exclude_list
    column_filters = column_editable_list
    form_overrides = {
        'password': PasswordField
    }


class CustomView(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/custom_index.html')

# Flask views
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    global has_checked_db
    # Check if we need to initialize database
    if not has_checked_db:
        with app.app_context():
            try:
                count = db.session.query(Book).count()
                if count == 0:
                    background_seed()
            except Exception as e:
                print(f"Error checking database: {e}")
                background_seed()
            has_checked_db = True
    
    page = request.args.get('page', 1, type=int)
    per_page = 50  # Number of books per page
    sort = request.args.get('sort', 'title')
    order = request.args.get('order', 'asc')
    
    # Get paginated books
    pagination = Book.query.paginate(page=page, per_page=per_page, error_out=False)
    books_data = [{'id': book.id, 'data': book.data} for book in pagination.items]
    
    # Sort current page
    sorted_data = BookSorter.sort_books(
        [book['data'] for book in books_data], 
        sort, 
        ascending=(order == 'asc')
    )
    # Reattach IDs to sorted data
    books = [{'id': books_data[i]['id'], 'data': book} for i, book in enumerate(sorted_data)]

    return render_template(
        'search.html',
        books=books,
        pagination=pagination,
        current_sort=sort,
        current_order=order,
        is_seeding=is_seeding
    )

@app.route('/book/<int:book_id>')
def book_details(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template('book_details.html', book=book)

# Create admin
admin = flask_admin.Admin(
    app,
    'My Dashboard',
    base_template='my_master.html',
    template_mode='bootstrap4',
)

# Add model views
admin.add_view(MyModelView(Role, db.session, menu_icon_type='fa', menu_icon_value='fa-server', name="Roles"))
admin.add_view(UserView(User, db.session, menu_icon_type='fa', menu_icon_value='fa-users', name="Users"))
admin.add_view(CustomView(name="Custom view", endpoint='custom', menu_icon_type='fa', menu_icon_value='fa-connectdevelop',))
admin.add_view(MyModelView(Book, db.session, menu_icon_type='fa', menu_icon_value='fa-book', name="Books"))

# define a context processor for merging flask-admin's template context into the
# flask-security views.
@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
        get_url=url_for
    )

def seed_books():
    """
    Seed the database with books from merged_dataframe.json
    """
    global is_seeding
    is_seeding = True
    print("Starting database seeding...")
    
    json_path = os.path.join(os.path.dirname(__file__), 'data', 'merged_dataframe.json')
    if os.path.exists(json_path):
        print(f"Found data file at {json_path}")
        with open(json_path, 'r', encoding='utf-8') as file:
            books_data = json.load(file)
            # Process books in batches
            batch_size = 1000
            processed = 0
            seen_ids = set()  # Track processed IDs in memory
            
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
    
    is_seeding = False
    print("Database seeding completed")

def background_seed():
    """Start seeding in a background thread"""
    print("Initializing background seeding...")
    thread = threading.Thread(target=seed_books)
    thread.daemon = True
    thread.start()

def build_sample_db():
    """
    Populate a small db with some example entries.
    """

    import string
    import random

    db.drop_all()
    db.create_all()

    with app.app_context():
        user_role = Role(name='user')
        super_user_role = Role(name='superuser')
        db.session.add(user_role)
        db.session.add(super_user_role)
        db.session.commit()

        test_user = user_datastore.create_user(
            first_name='Admin',
            email='admin',
            password=hash_password('admin'),
            fs_uniquifier=str(uuid.uuid4()),
            roles=[user_role, super_user_role]
        )

        first_names = [
            'Harry', 'Amelia', 'Oliver', 'Jack', 'Isabella', 'Charlie', 'Sophie', 'Mia',
            'Jacob', 'Thomas', 'Emily', 'Lily', 'Ava', 'Isla', 'Alfie', 'Olivia', 'Jessica',
            'Riley', 'William', 'James', 'Geoffrey', 'Lisa', 'Benjamin', 'Stacey', 'Lucy'
        ]
        last_names = [
            'Brown', 'Smith', 'Patel', 'Jones', 'Williams', 'Johnson', 'Taylor', 'Thomas',
            'Roberts', 'Khan', 'Lewis', 'Jackson', 'Clarke', 'James', 'Phillips', 'Wilson',
            'Ali', 'Mason', 'Mitchell', 'Rose', 'Davis', 'Davies', 'Rodriguez', 'Cox', 'Alexander'
        ]

        for i in range(len(first_names)):
            tmp_email = first_names[i].lower() + "." + last_names[i].lower() + "@example.com"
            tmp_pass = ''.join(random.choice(string.ascii_lowercase + string.digits) for i in range(10))
            user_datastore.create_user(
                first_name=first_names[i],
                last_name=last_names[i],
                email=tmp_email,
                password=hash_password(tmp_pass),
                fs_uniquifier=str(uuid.uuid4()),
                roles=[user_role, ]
            )
        db.session.commit()
        # Seed books after creating users
        seed_books()
    return

if __name__ == '__main__':
    # Initialize database tables
    with app.app_context():
        db.create_all()
        # Check if we need to start seeding
        if Book.query.count() == 0:
            background_seed()
    
    # Start app
    app.run(debug=True)
