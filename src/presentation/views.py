from flask import Blueprint, render_template, redirect, url_for, request, abort
from flask_admin.contrib import sqla
from flask_security import current_user
from business.merge_sort import MergeSort
from data.models import Book

views = Blueprint('views', __name__)


class MyModelView(sqla.ModelView):
    def is_accessible(self):
        return (current_user.is_active and
                current_user.is_authenticated)

    def _handle_view(self, name):
        if not self.is_accessible():
            return redirect(url_for('security.login'))


class CustomView(MyModelView):
    list_template = 'admin/model/custom_list.html'


@views.route('/')
def index():
    return render_template('index.html')


@views.route('/admin/')
def admin_index():
    return render_template('admin/index.html')


@views.route('/search')
def search():
    page = request.args.get('page', 1, type=int)
    per_page = 50
    sort = request.args.get('sort', 'title')
    order = request.args.get('order', 'asc')
    view = request.args.get('view', 'grid')

    pagination = Book.query.paginate(page=page, per_page=per_page, error_out=False)
    books = pagination.items

    # Sort the books using the MergeSort class
    sorted_books = MergeSort.sort_books(books, sort, ascending=(order == 'asc'))

    return render_template(
        'search.html',
        books=sorted_books,
        pagination=pagination,
        current_sort=sort,
        current_order=order,
        view=view
    )


@views.route('/book/<string:book_id>')
def book_details(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template('book_details.html', book=book)
