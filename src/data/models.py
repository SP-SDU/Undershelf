"""Database models for user authentication and book storage."""
from flask_security.core import UserMixin, RoleMixin
from extensions import db

# Define models
roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)


class Role(db.Model, RoleMixin):
    """Role model for user authentication."""
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        """Return string representation of role."""
        return self.name


class User(db.Model, UserMixin):
    """User model for authentication and authorization."""
    id = db.Column(db.Integer, primary_key=True)
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))  
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))

    def __str__(self):
        """Return string representation of user."""
        return self.email


class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.String, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    authors = db.Column(db.String)
    image = db.Column(db.String)
    publisher = db.Column(db.String)
    publishedDate = db.Column(db.String)
    categories = db.Column(db.String)
    ratingsCount = db.Column(db.Float)
    reviews = db.relationship('Review', backref='book', lazy=True)


class Review(db.Model):
    __tablename__ = 'reviews'
    review_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    book_id = db.Column(db.String, db.ForeignKey('books.id'), nullable=False)
    user_id = db.Column(db.String)
    review_score = db.Column(db.Float)
