from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils.cache import patch_cache_control, patch_vary_headers

from business_logic.aspects import error_handler, method_logger, performance_monitor
from business_logic.bst import BST
from business_logic.cbf import BookRecommender
from business_logic.merge_sort import MergeSort
from business_logic.top_k import BookRanker
from data_access.models import Book

from .forms import SignUpForm


def _cache_page(response):
    patch_vary_headers(response, ("Cookie",))
    patch_cache_control(response, max_age=60 * 15, public=False, private=True)


@performance_monitor
@method_logger
def index(request):
    k = int(request.GET.get("k", 10))  # Get k parameter, default to 10

    context = {
        "k_value": k,
        "title": f"Top {k} Books",
    }

    response = render(request, "index.html", context)
    _cache_page(response)
    return response


@performance_monitor
@method_logger
def top_books(request):
    k = int(request.GET.get("k", 10))
    top_books = BookRanker.get_top_k(k)
    html = render_to_string("top_books.html", {"books": top_books}, request=request)
    response = JsonResponse({"html": html})
    _cache_page(response)
    return response


@performance_monitor
@method_logger
def search(request):
    page = request.GET.get("page", 1)
    per_page = 100
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

    response = render(request, "search.html", context)
    _cache_page(response)
    return response


@performance_monitor
@method_logger
def autocomplete(request):
    prefix = request.GET.get("q", "").strip()
    max_results = int(request.GET.get("max", 10))
    if not prefix:
        return JsonResponse({"suggestions": []})
    # Custom BST is super slow and is required for search.
    # This uses indexed DB query (O(log n + k)) since it is not required for
    # autocomplete.
    books = Book.objects.filter(title__istartswith=prefix).order_by("title")[
        :max_results
    ]
    data = [{"id": b.id, "title": b.title, "authors": b.authors} for b in books]
    return JsonResponse({"suggestions": data})


@performance_monitor
@method_logger
def book_details(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    reviews = book.reviews.all()
    review = book.reviews.first()
    userid = review.user_id if review else None

    recommended_books = BookRecommender.get_cbf_list(userid, n_recommendations=8)

    response = render(
        request,
        "book_details.html",
        {"book": book, "reviews": reviews, "recommended_books": recommended_books},
    )
    _cache_page(response)
    return response


@performance_monitor
@method_logger
def about(request):
    return render(request, "about.html")


@performance_monitor
@method_logger
@error_handler(fallback=None)
def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("index")
    else:
        form = SignUpForm()
    return render(request, "registration/signup.html", {"form": form})


@login_required
@performance_monitor
@method_logger
@error_handler(fallback=None)
def profile_view(request):
    if request.method == "POST":
        password_form = PasswordChangeForm(request.user, request.POST)
        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)  # keeps the user logged in
            return redirect("profile")
    else:
        password_form = PasswordChangeForm(request.user)

    return render(
        request,
        "registration/profile.html",
        {
            "password_form": password_form,
        },
    )


@login_required
@performance_monitor
@method_logger
@error_handler(fallback=None)
def delete_account_view(request):
    if request.method == "POST":
        request.user.delete()
        return redirect("index")
    return render(request, "registration/delete_account_confirm.html")
