from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from business_logic.bst import BST
from business_logic.merge_sort import MergeSort
from data_access.models import Book


def index(request):
    return render(request, "index.html")


def search(request):
    page = request.GET.get("page", 1)
    per_page = 50
    sort = request.GET.get("sort", "title")
    order = request.GET.get("order", "asc")
    view = request.GET.get("view", "grid")
    query = request.GET.get("q", "").strip()
    books_query = Book.objects.all().order_by("id")
    if query:
        books_query = books_query.filter(title__icontains=query) | books_query.filter(
            authors__icontains=query
        )
        books_query = books_query.distinct()

    # Pagination
    paginator = Paginator(books_query, per_page)
    page_obj = paginator.get_page(page)
    page_books = list(page_obj.object_list)

    # Search BST
    if query:
        books = BST.search_in_books(page_books, query)
    else:
        books = page_books

    sorted_books = MergeSort.sort_books(books, sort, ascending=(order == "asc"))

    context = {
        "books": sorted_books,
        "page_obj": page_obj,
        "current_sort": sort,
        "current_order": order,
        "view": view,
        "request": request,
    }
    return render(request, "search.html", context)


def autocomplete(request):
    prefix = request.GET.get("q", "").strip()
    max_results = int(request.GET.get("max", 10))
    if not prefix:
        return JsonResponse({"suggestions": []})
    # Custom BST is super slow and is required for search.
    # This uses indexed DB query (O(log n + k)) since it is not required for autocomplete.
    books = Book.objects.filter(title__istartswith=prefix).order_by("title")[
        :max_results
    ]
    data = [{"id": b.id, "title": b.title, "authors": b.authors} for b in books]
    return JsonResponse({"suggestions": data})


def book_details(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    return render(request, "book_details.html", {"book": book})


def login(request):
    return render(request, "login.html")


def signup(request):
    return render(request, "signup.html")
