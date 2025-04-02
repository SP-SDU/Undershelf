from flask import Blueprint, render_template, redirect, url_for, request, abort
from flask_admin.contrib import sqla
from flask_admin import BaseView, expose
from flask_security import current_user
from wtforms import PasswordField
from business.book_sorter import BookSorter
from data.models import Role, User, Book, db

# Create Blueprint
views = Blueprint('views', __name__)

class MyModelView(sqla.ModelView):
    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False
        return current_user.has_role('superuser')

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            if current_user.is_authenticated:
                abort(403)
            else:
                return redirect(url_for('security.login', next=request.url))

    edit_modal = True
    create_modal = True    
    can_export = True
    can_view_details = True
    details_modal = True

class UserView(MyModelView):
    column_editable_list = ['email', 'first_name', 'last_name']
    column_searchable_list = column_editable_list
    column_exclude_list = ['password']
    column_details_exclude_list = column_exclude_list
    column_filters = column_editable_list
    form_overrides = {
        'password': PasswordField
    }

class CustomView(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/custom_index.html')

@views.route('/')
def index():
    return render_template('index.html')

@views.route('/search')
def search():
    page = request.args.get('page', 1, type=int)
    per_page = 50
    sort = request.args.get('sort', 'title')
    order = request.args.get('order', 'asc')
    view = request.args.get('view', 'grid')
    
    pagination = Book.query.paginate(page=page, per_page=per_page, error_out=False)
    books_data = [{'id': book.id, 'data': book.data} for book in pagination.items]
    
    # Create a dictionary mapping book data to IDs before sorting
    id_map = {str(book['data']): book['id'] for book in books_data}
    
    sorted_data = BookSorter.sort_books(
        [book['data'] for book in books_data], 
        sort, 
        ascending=(order == 'asc')
    )
    
    # Use the id_map to maintain correct IDs after sorting
    books = [{'id': id_map[str(book)], 'data': book} for book in sorted_data]

    return render_template(
        'search.html',
        books=books,
        pagination=pagination,
        current_sort=sort,
        current_order=order,
        view=view
    )

@views.route('/book/<int:book_id>')
def book_details(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template('book_details.html', book=book)
