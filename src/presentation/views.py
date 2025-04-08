from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

from buisness_logic.merge_sort import MergeSort
from data_access.models import Book


def index(request):
    return render(request, "index.html")


def search(request):
    page = request.GET.get("page", 1)
    per_page = 50
    sort = request.GET.get("sort", "title")
    order = request.GET.get("order", "asc")
    view = request.GET.get("view", "grid")
    books_query = Book.objects.all().order_by("id")

    # Create paginator
    paginator = Paginator(books_query, per_page)
    page_obj = paginator.get_page(page)

    # Get books for current page and sort them
    books = list(page_obj.object_list)
    sorted_books = MergeSort.sort_books(books, sort, ascending=(order == "asc"))

    context = {
        "books": sorted_books,
        "page_obj": page_obj,
        "current_sort": sort,
        "current_order": order,
        "view": view,
    }

    return render(request, "search.html", context)


def book_details(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    return render(request, "book_details.html", {"book": book})


def login(request):
    return render(request, "login.html")


def signup(request):
    return render(request, "signup.html")
