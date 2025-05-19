# Use importlib to import module with hyphen in name

from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.cache import cache_page

from business_logic.bst import BST
from business_logic.merge_sort import MergeSort
from business_logic.top_k import BookRanker
from data_access.models import Book
from django.contrib import messages
#from django.contrib.auth.models import User
#from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import SignUpForm
from django.contrib.auth.forms import AuthenticationForm


def index(request):
    k = int(request.GET.get("k", 10))  # Get k parameter, default to 10
    top_books = BookRanker.get_top_k(k)  # Fetch top k books

    context = {
        "top_books": top_books,
        "k_value": k,
        "title": f"Top {k} Books",
    }
    return render(request, "index.html", context)


@cache_page(60 * 5)
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
    # This uses indexed DB query (O(log n + k)) since it is not required for
    # autocomplete.
    books = Book.objects.filter(title__istartswith=prefix).order_by("title")[
        :max_results
    ]
    data = [{"id": b.id, "title": b.title, "authors": b.authors} for b in books]
    return JsonResponse({"suggestions": data})


@cache_page(60 * 10)
def book_details(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    reviews = book.reviews.all()
    
    # Clean up book description if it exists and has encoding issues
    if book.description:
        # Replace common encoding artifacts
        import re
        # Remove random character sequences that look like encoding artifacts
        half_length = len(book.description) // 2
        first_half = book.description[:half_length]
        
        if first_half in book.description[half_length:]:
            book.description = first_half
        
        # Process description content to improve readability
        book.description = book.description.replace('\r\n', '\n')
        
        # Remove excessive line breaks
        while '\n\n\n' in book.description:
            book.description = book.description.replace('\n\n\n', '\n\n')
        
        # Limit description length to 2000 characters to prevent layout issues
        if len(book.description) > 2000:
            book.description = book.description[:2000] + "..."
            
    # Get related books based on categories and authors
    related_books = []
    
    if book.categories:
        # Try to get books with similar categories
        category_matches = Book.objects.filter(categories__contains=book.categories).exclude(id=book.id)[:3]
        related_books.extend(list(category_matches))
        
    # If we don't have enough related books, add some based on author
    if len(related_books) < 5 and book.authors:
        author_matches = Book.objects.filter(authors__contains=book.authors).exclude(id=book.id).exclude(id__in=[b.id for b in related_books])[:5-len(related_books)]
        related_books.extend(list(author_matches))
    # Still need more? Add some random popular books
    if len(related_books) < 5:
        popular_books = Book.objects.exclude(id=book.id).exclude(id__in=[b.id for b in related_books]).order_by('-ratingsCount')[:5-len(related_books)]
        related_books.extend(list(popular_books))
    
    # If still no related books, just get some random popular ones
    if not related_books:
        related_books = Book.objects.exclude(id=book.id).order_by('?')[:5]

    return render(request, "book_details.html", {
        "book": book, 
        "reviews": reviews,
        "related_books": related_books
    })


@cache_page(60 * 15)
def top_books(request):
    k = int(request.GET.get("k", 10))
    top_rated_books = BookRanker.get_top_k(k)

    context = {"top_books": top_rated_books, "k_value": k, "title": f"Top {k} Books"}
    return render(request, "top_books.html", context)


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatically log in after signup
            messages.success(request, "Signup successful!")
            return redirect('index')
        else:
            messages.error(request, "Signup failed. Please correct the errors below.")
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect('index')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


#*def logout_view(request):
#    logout(request)
#    messages.info(request, "Logged out successfully.")
#   return redirect('login')

def about(request):
    return render(request, 'about.html')    
