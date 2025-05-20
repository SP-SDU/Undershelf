from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.db.models import Count, Avg, Q
from django.urls import reverse
from django.utils import timezone
from django.http import HttpResponse
from data_access.models import Book, Review
from .forms import BookForm, BookFilterForm, UserFilterForm, UserForm
import json
import csv
from datetime import datetime, timedelta
import random

# Helper functions for admin views

# Dashboard helper functions
def get_stats():
    """Generate real statistics for dashboard from database"""
    from django.db.models import Count, Sum, F, FloatField, ExpressionWrapper
    from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
    from datetime import timedelta
    
    # Get current date and calculate comparison periods
    today = timezone.now().date()
    last_week = today - timedelta(days=7)
    previous_week_start = last_week - timedelta(days=7)
    
    # Book statistics
    total_books = Book.objects.count()
    # Use publishedDate instead of created_at
    books_last_week = Book.objects.filter(publishedDate__gte=last_week.isoformat()).count()
    books_previous_week = Book.objects.filter(
        publishedDate__range=(
            previous_week_start.isoformat(), 
            (last_week - timedelta(days=1)).isoformat()
        )
    ).count()
    
    # Calculate book percentage change
    books_percent_change = 0
    if books_previous_week > 0:
        books_percent_change = round(
            ((books_last_week - books_previous_week) / books_previous_week) * 100
        )
    
    # User statistics
    total_users = User.objects.count()
    users_last_week = User.objects.filter(date_joined__date__gte=last_week).count()
    users_previous_week = User.objects.filter(
        date_joined__date__range=(previous_week_start, last_week - timedelta(days=1))
    ).count()
    
    # Calculate user percentage change
    users_percent_change = 0
    if users_previous_week > 0:
        users_percent_change = round(
            ((users_last_week - users_previous_week) / users_previous_week) * 100
        )
    
    # Review statistics
    total_reviews = Review.objects.count()
    # Since Review model doesn't have created_at, we'll use the current count
    # This is a temporary solution - consider adding a timestamp field to Review model
    reviews_last_week = 0
    reviews_previous_week = 0
    
    # Calculate review percentage change - set to 0 since we don't have historical data
    reviews_percent_change = 0
    
    # Average rating - using review_score instead of rating
    avg_rating = Review.objects.aggregate(avg_rating=Avg('review_score'))['avg_rating'] or 0
    
    return {
        'total_books': total_books,
        'books_change': books_percent_change,
        'books_increase': books_percent_change >= 0,
        'total_users': total_users,
        'users_change': users_percent_change,
        'users_increase': users_percent_change >= 0,
        'total_reviews': total_reviews,
        'reviews_change': reviews_percent_change,
        'reviews_increase': reviews_percent_change >= 0,
        'avg_rating': round(avg_rating, 1) if avg_rating else 0,
        'avg_rating_percent': round((avg_rating / 5) * 100) if avg_rating else 0,
    }

def get_user_activity_data(days=7):
    """Get real user activity data by day from the database
    
    Args:
        days (int): Number of past days to include in the data
        
    Returns:
        dict: Dictionary with day names as keys and activity counts as values
    """
    from django.db.models.functions import TruncDate
    from django.db.models import Count
    from datetime import datetime, timedelta
    
    # Get the date range
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days-1)
    
    # Get user signups by day
    user_activity = (
        User.objects
        .filter(date_joined__date__range=[start_date, end_date])
        .annotate(date=TruncDate('date_joined'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )
    
    # Create a dictionary with all days in the range initialized to 0
    activity_data = {}
    for i in range(days):
        date = (end_date - timedelta(days=i)).strftime('%Y-%m-%d')
        activity_data[date] = 0
    
    # Update with actual data
    for activity in user_activity:
        date_str = activity['date'].strftime('%Y-%m-%d')
        if date_str in activity_data:
            activity_data[date_str] = activity['count']
    
    # Format for the frontend chart
    return {
        'labels': list(activity_data.keys()),
        'data': list(activity_data.values()),
        'total': sum(activity_data.values()),
        'average': round(sum(activity_data.values()) / days, 1) if days > 0 else 0
    }

def get_popular_books(limit=5):
    """Get popular books based on number of reviews and average rating
    
    Args:
        limit (int): Maximum number of books to return
        
    Returns:
        list: List of dictionaries containing book data with title, review count, and rating
    """
    from django.db.models import Count, Avg, F
    
    # Get books with their review counts and average ratings
    popular_books = (
        Book.objects
        .annotate(
            review_count=Count('reviews'),
            avg_rating=Avg('reviews__review_score')
        )
        .filter(review_count__gt=0)  # Only include books with reviews
        .order_by('-review_count', '-avg_rating')[:limit]
    )
    
    # Find max review count for percentage calculation
    max_reviews = max(book.review_count for book in popular_books) if popular_books else 1
    
    # Format the data for the frontend
    result = []
    for book in popular_books:
        percentage = (book.review_count / max_reviews) * 100 if max_reviews > 0 else 0
        result.append({
            'id': book.id,
            'title': book.title[:50] + '...' if len(book.title) > 50 else book.title,
            'author': book.authors,
            'review_count': book.review_count,
            'avg_rating': round(book.avg_rating, 1) if book.avg_rating else 0,
            'percentage': round(percentage, 1)
        })
    
    return result

def get_recent_activities(limit=5):
    """Get recent activity data for dashboard from the database
    
    Args:
        limit (int): Maximum number of activities to return
        
    Returns:
        list: List of recent activities with book, action, user, and timestamp
    """
    from django.contrib.contenttypes.models import ContentType
    from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
    from django.utils.text import Truncator
    
    # Get recent admin actions
    content_type = ContentType.objects.get_for_model(Book)
    log_entries = LogEntry.objects.filter(
        content_type=content_type
    ).select_related('user').order_by('-action_time')[:limit]
    
    activities = []
    
    for entry in log_entries:
        # Determine action type
        if entry.action_flag == ADDITION:
            action = "Book Added"
        elif entry.action_flag == CHANGE:
            action = "Book Updated"
        else:
            action = "Modified"
            
        # Get the book if it still exists
        try:
            book = Book.objects.get(pk=entry.object_id)
            book_title = book.title
        except Book.DoesNotExist:
            book_title = "[Deleted Book]"
        
        # Truncate the change message if it's too long
        change_message = Truncator(entry.change_message).chars(100)
        
        activities.append({
            'id': entry.id,
            'book_title': book_title,
            'book_id': entry.object_id,
            'action': action,
            'user': entry.user.get_username(),
            'user_id': entry.user_id,
            'date': entry.action_time,
            'change_message': change_message
        })
    
    # If we don't have enough activities, fill with recent reviews
    if len(activities) < limit:
        # Use review_id instead of created_at for ordering
        recent_reviews = Review.objects.select_related('book').order_by('-review_id')[:limit - len(activities)]
        
        for review in recent_reviews:
            activities.append({
                'id': f"review_{review.review_id}",
                'book_title': review.book.title,
                'book_id': review.book.id,
                'action': "Review Added",
                'user': review.user_id or 'Anonymous',
                'user_id': review.user_id or 0,
                'date': timezone.now() - timedelta(days=review.review_id % 30),  # Generate a fake date
                'change_message': f"Rated {review.review_score} stars"
            })
    
    # Sort all activities by date and limit
    activities.sort(key=lambda x: x['date'], reverse=True)
    return activities[:limit]


# Analytics helper functions
def get_analytics_summary():
    """Generate summary statistics for analytics page"""
    return {
        'visits_count': 12458,
        'visits_change': 15,
        'avg_time_on_site': "8m 24s",
        'time_change': 12,
        'search_count': 4521,
        'search_change': 8,
        'active_users': 325,
        'user_change': 5
    }

def get_daily_traffic(days=30):
    """Generate daily traffic data for analytics chart"""
    traffic = []
    for i in range(days):
        percentage = 20 + (i % 5) * 15  # Generate some variation
        date = timezone.now() - timedelta(days=days-i)
        traffic.append({
            'date': date,
            'count': percentage * 10,
            'percentage': percentage,
            'label': date.strftime('%d %b') if i % 4 == 0 else ''
        })
    return traffic

def get_top_pages():
    """Get top pages for analytics"""
    return [
        {'path': '/', 'views': 4500, 'percentage': 100},
        {'path': '/search/', 'views': 3200, 'percentage': 71},
        {'path': '/book/details/', 'views': 2100, 'percentage': 47},
        {'path': '/login/', 'views': 1800, 'percentage': 40},
        {'path': '/signup/', 'views': 1500, 'percentage': 33},
    ]

def get_popular_searches():
    """Get popular search terms for analytics"""
    return [
        {'term': 'fantasy', 'count': 245, 'change': 12},
        {'term': 'science fiction', 'count': 198, 'change': 8},
        {'term': 'romance', 'count': 156, 'change': -3},
        {'term': 'mystery', 'count': 142, 'change': 5},
        {'term': 'biography', 'count': 98, 'change': 15},
    ]

def get_device_stats():
    """Get device usage statistics"""
    return {
        'desktop': 65,
        'mobile': 30,
        'tablet': 5
    }

def get_user_stats():
    """Get user statistics"""
    return {
        'total': 8245,
        'new_percent': 35,
        'returning_percent': 65
    }


def is_admin(user):
    """Check if user is an admin"""
    return user.is_staff or user.is_superuser


# Login view
from django.views.decorators.csrf import ensure_csrf_cookie

@ensure_csrf_cookie
def login_view(request):
    """Custom login view for admin interface"""
    # If user is already authenticated, redirect to dashboard
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
        return redirect('custom_admin:dashboard')
        
    # Get the next URL to redirect to after login
    next_url = request.GET.get('next', '')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        next_url = request.POST.get('next', '') or next_url
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None and (user.is_staff or user.is_superuser):
            login(request, user)
            # If next_url is provided, redirect there, otherwise to dashboard
            if next_url:
                return redirect(next_url)
            else:
                return redirect('custom_admin:dashboard')
        else:
            messages.error(request, 'Invalid credentials or insufficient permissions.')
    
    context = {
        'next': next_url,
        'csrf_token': request.META.get('CSRF_COOKIE', ''),
    }
    return render(request, 'custom_admin/login.html', context)


# Logout view
def logout_view(request):
    logout(request)
    return redirect('custom_admin:login')


@login_required
@user_passes_test(is_admin)
def dashboard(request):
    """Admin dashboard with overview statistics using real data"""
    # Get statistics using our new get_stats function
    stats = get_stats()
    
    # Get user activity data for the chart (last 7 days)
    activity_data = get_user_activity_data(days=7)
    
    # Get popular books data (top 5 by review count and rating)
    popular_books = get_popular_books(limit=5)
    
    # Get recent activities (admin actions and reviews)
    recent_activities = get_recent_activities(limit=10)
    
    # Get recently added books (last 5)
    # Using publishedDate as substitute for created_at
    recent_books = Book.objects.order_by('-publishedDate')[:5]
    
    # Get recent reviews with related data
    # Since Review doesn't have created_at, we'll just use the primary key
    recent_reviews = Review.objects.select_related('book').order_by('-review_id')[:5]
    
    # Get top categories by book count
    from django.db.models import Count
    # Since categories is a CharField, we need to query differently
    # This splits the categories string and counts books by category
    from collections import Counter
    categories_counter = Counter()
    
    # Get all books with categories
    books_with_categories = Book.objects.exclude(categories__isnull=True).exclude(categories='').values_list('id', 'categories')
    
    # Count categories
    for _, cats in books_with_categories:
        if cats:
            # Split categories and count each one
            for cat in cats.split(','):
                cat = cat.strip()
                if cat:
                    categories_counter[cat] += 1
    
    # Get top 5 categories
    top_categories = [{'category': cat, 'count': count} 
                     for cat, count in categories_counter.most_common(5)]
    
    # Format categories data for the template
    categories_data = [
        {'name': cat['category'], 'count': cat['count']} 
        for cat in top_categories
    ]
    
    # Calculate total books for percentage calculations
    total_books = stats.get('total_books', 1)  # Avoid division by zero
    
    # Add percentage to categories
    for cat in categories_data:
        cat['percentage'] = round((cat['count'] / total_books) * 100, 1)
    
    # Format user activity data for the chart
    user_activity = [
        {'day': label[-5:], 'count': count}  # Just show day and month (e.g., "01-01")
        for label, count in zip(activity_data['labels'], activity_data['data'])
    ]
    
    # Create context with all dashboard data
    context = {
        'active_page': 'dashboard',
        'title': 'Dashboard',
        'current_date': timezone.now().strftime('%B %d, %Y'),
        
        # Statistics
        'total_books': stats.get('total_books', 0),
        'total_users': stats.get('total_users', 0),
        'total_reviews': stats.get('total_reviews', 0),
        'avg_rating': stats.get('avg_rating', 0),
        'avg_rating_percent': stats.get('avg_rating_percent', 0),
        
        # Change metrics
        'books_increase': stats.get('books_change', 0) >= 0,
        'books_percent_change': abs(stats.get('books_change', 0)),
        'users_increase': stats.get('users_change', 0) >= 0,
        'users_percent_change': abs(stats.get('users_change', 0)),
        'reviews_increase': stats.get('reviews_change', 0) >= 0,
        'reviews_percent_change': abs(stats.get('reviews_change', 0)),
        
        # Charts and activity data
        'user_activity': user_activity,
        'activity_data': json.dumps(activity_data),
        'popular_books': popular_books,
        'recent_activities': recent_activities,
        'recent_books': recent_books,
        'recent_reviews': recent_reviews,
        'top_categories': categories_data,
        
        # For backward compatibility
        'active_users': stats.get('total_users', 0),
        'new_reviews': stats.get('total_reviews', 0),
        'search_volume': f"{stats.get('total_reviews', 0) // 10}K",
        'search_increase': stats.get('reviews_change', 0) >= 0,
        'search_percent_change': min(abs(stats.get('reviews_change', 0)), 100)
    }
    
    return render(request, 'custom_admin/dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def book_list(request):
    """Book management page with filtering, sorting, and pagination"""
    # Initialize filter form with request data
    filter_form = BookFilterForm(request.GET)
    
    # Start with all books
    books = Book.objects.all()
    
    # Process filters if form is valid
    if filter_form.is_valid():
        search_query = filter_form.cleaned_data.get('search')
        category = filter_form.cleaned_data.get('category')
        
        # Apply search filter
        if search_query:
            books = books.filter(
                Q(title__icontains=search_query) | 
                Q(authors__icontains=search_query) | 
                Q(description__icontains=search_query) |
                Q(id__icontains=search_query)
            )
        
        # Apply category filter
        if category:
            books = books.filter(categories__icontains=category)
    
    # Get unique categories for filter dropdown - more organized and cleaned up
    all_categories = []
    for book in Book.objects.all():
        if book.categories:
            for category in book.categories.split(','):
                category_clean = category.strip()
                if category_clean and category_clean not in all_categories and len(category_clean) > 1:
                    # Only add meaningful categories (not single characters or symbols)
                    all_categories.append(category_clean)
    
    # Group categories and sort them alphabetically
    main_categories = sorted(all_categories, key=lambda x: x.lower())
    
    # Sort books if requested (defaulting to title)
    sort_by = request.GET.get('sort', 'title')
    if isinstance(books, list):
        # If books is a list (rare case), sort in-memory
        reverse = sort_by.startswith('-')
        sort_field = sort_by[1:] if reverse else sort_by
        
        if sort_field == 'average_rating':
            books = sorted(books, key=lambda x: x.average_rating() or 0, reverse=reverse)
        else:
            books = sorted(books, key=lambda x: getattr(x, sort_field, ''), reverse=reverse)
            
        # Manual pagination for list
        paginator = Paginator(books, 10)
    else:
        # QuerySet pagination
        paginator = Paginator(books, 10)
    
    page = request.GET.get('page', 1)
    books_page = paginator.get_page(page)
    
    context = {
        'active_page': 'books',
        'books': books_page,
        'filter_form': filter_form,
        'total_books': len(books) if isinstance(books, list) else books.count(),
        'categories': main_categories
    }
    
    return render(request, 'custom_admin/book_list.html', context)


@login_required
@user_passes_test(is_admin)
def book_add(request):
    """Add new book page with form processing"""
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save()
            messages.success(request, f'Book "{book.title}" has been added successfully.')
            return redirect('custom_admin:book_list')
    else:
        form = BookForm()
    
    context = {
        'active_page': 'books',
        'form': form,
        'title': 'Add New Book'
    }
    
    return render(request, 'custom_admin/book_form.html', context)


@login_required
@user_passes_test(is_admin)
def book_edit(request, book_id):
    """Edit book page with form processing"""
    book = get_object_or_404(Book, id=book_id)
    
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            book = form.save()
            messages.success(request, f'Book "{book.title}" has been updated successfully.')
            return redirect('custom_admin:book_list')
    else:
        form = BookForm(instance=book)
    
    context = {
        'active_page': 'books',
        'form': form,
        'book': book,
        'title': f'Edit Book: {book.title}'
    }
    
    return render(request, 'custom_admin/book_form.html', context)


@login_required
@user_passes_test(is_admin)
def book_delete(request, book_id):
    """Delete book with confirmation"""
    book = get_object_or_404(Book, id=book_id)
    
    if request.method == 'POST':
        book_title = book.title
        book.delete()
        messages.success(request, f'Book "{book_title}" has been deleted successfully.')
        return redirect('custom_admin:book_list')
    
    context = {
        'active_page': 'books',
        'book': book,
        'title': f'Delete Book: {book.title}'
    }
    
    return render(request, 'custom_admin/book_confirm_delete.html', context)


@login_required
@user_passes_test(is_admin)
def book_import(request):
    """Import books from CSV file"""
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        
        # Check if the file is CSV
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Please upload a CSV file.')
            return redirect('custom_admin:book_list')
        
        # Process CSV file
        try:
            # Decode the file
            file_data = csv_file.read().decode('utf-8-sig')
            csv_data = csv.reader(file_data.splitlines(), delimiter=',')
            
            # Skip header row
            header = next(csv_data)
            expected_headers = ['Title', 'Author', 'ISBN', 'Publication Date', 'Categories', 'Description', 'Image URL', 'Rating']
            
            # Validate header row (case-insensitive)
            if len(header) < len(expected_headers):
                messages.error(request, f'CSV file missing required columns. Expected: {", ".join(expected_headers)}')
                return redirect('custom_admin:book_list')
            
            # Count of books to be imported
            books_added = 0
            books_updated = 0
            errors = 0
            
            # Process each data row
            for row in csv_data:
                if len(row) < 7:  # Minimum required fields
                    errors += 1
                    continue
                
                try:
                    # Extract data from row
                    title = row[0].strip()
                    author = row[1].strip()
                    isbn = row[2].strip() if len(row) > 2 and row[2].strip() else None
                    publication_date = row[3].strip() if len(row) > 3 and row[3].strip() else None
                    categories = [cat.strip() for cat in row[4].split(',')] if len(row) > 4 and row[4].strip() else []
                    description = row[5].strip() if len(row) > 5 and row[5].strip() else ''
                    image_url = row[6].strip() if len(row) > 6 and row[6].strip() else None
                    
                    # Check for required fields
                    if not title or not author:
                        errors += 1
                        continue
                    
                    # Try to find existing book by ISBN or title+author
                    if isbn:
                        book, created = Book.objects.update_or_create(
                            isbn=isbn,
                            defaults={
                                'title': title,
                                'author': author,
                                'publication_date': publication_date,
                                'categories': categories,
                                'description': description,
                                'image_url': image_url,
                            }
                        )
                    else:
                        book, created = Book.objects.update_or_create(
                            title=title,
                            author=author,
                            defaults={
                                'publication_date': publication_date,
                                'categories': categories,
                                'description': description,
                                'image_url': image_url,
                            }
                        )
                    
                    if created:
                        books_added += 1
                    else:
                        books_updated += 1
                        
                except Exception as e:
                    errors += 1
            
            # Show success message
            if books_added > 0 or books_updated > 0:
                messages.success(
                    request, 
                    f'Successfully imported {books_added} new books and updated {books_updated} existing books. '
                    f'{errors} rows had errors and were skipped.'
                )
            else:
                messages.warning(request, f'No books were imported. {errors} rows had errors and were skipped.')
                
        except Exception as e:
            messages.error(request, f'Error processing CSV file: {str(e)}')
    
    return redirect('custom_admin:book_list')


@login_required
@user_passes_test(is_admin)
def book_export(request):
    """Export books to CSV"""
    # Get all books
    books = Book.objects.all()
    
    # Create a CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="books-export.csv"'
    
    # Create CSV writer
    writer = csv.writer(response)
    
    # Write header
    writer.writerow(['title', 'authors', 'description', 'categories', 'image', 'publisher', 'publishedDate'])
    
    # Write data rows
    for book in books:
        categories = ','.join(book.categories) if book.categories else ''
        
        writer.writerow([
            book.title,
            book.authors,
            book.description,
            categories,
            book.image,
            book.publisher,
            book.publishedDate
        ])
    
    return response


@login_required
@user_passes_test(is_admin)
def user_list(request):
    """User management page with filtering, sorting, and pagination"""
    # Initialize filter form with request data
    filter_form = UserFilterForm(request.GET)
    
    # Get all users
    users = User.objects.all()
    
    # Process filters if form is valid
    if filter_form.is_valid():
        search_query = filter_form.cleaned_data.get('search')
        role = filter_form.cleaned_data.get('role')
        status = filter_form.cleaned_data.get('status')
        
        # Apply search filter
        if search_query:
            users = users.filter(
                Q(username__icontains=search_query) | 
                Q(email__icontains=search_query) | 
                Q(first_name__icontains=search_query) | 
                Q(last_name__icontains=search_query)
            )
        
        # Apply role filter
        if role == 'admin':
            users = users.filter(is_superuser=True)
        elif role == 'staff':
            users = users.filter(is_staff=True, is_superuser=False)
        elif role == 'reader':
            users = users.filter(is_staff=False, is_superuser=False)
        
        # Apply status filter
        if status == 'active':
            users = users.filter(is_active=True)
        elif status == 'inactive':
            users = users.filter(is_active=False)
    
    # Sort users (default by username ascending)
    sort_by = request.GET.get('sort', 'username')
    if sort_by.startswith('-'):
        sort_field = sort_by[1:]
        reverse = True
    else:
        sort_field = sort_by
        reverse = False
    
    # Apply sort - use order_by for querysets
    valid_sort_fields = ['username', 'email', 'first_name', 'last_name', 'date_joined', 'last_login']
    if sort_field in valid_sort_fields:
        if reverse:
            users = users.order_by(f'-{sort_field}')
        else:
            users = users.order_by(sort_field)
    
    # Calculate statistics
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    inactive_users = total_users - active_users
    staff_users = User.objects.filter(is_staff=True).count()
    
    # Recent registrations
    recent_users = User.objects.order_by('-date_joined')[:5]
    
    # Paginate users
    paginator = Paginator(users, 10)  # 10 users per page
    page = request.GET.get('page', 1)
    users_page = paginator.get_page(page)
    
    context = {
        'active_page': 'users',
        'users': users_page,
        'filter_form': filter_form,
        'total_users': total_users,
        'active_users': active_users,
        'inactive_users': inactive_users,
        'staff_users': staff_users,
        'recent_users': recent_users,
    }
    
    return render(request, 'custom_admin/user_list.html', context)


@login_required
@user_passes_test(is_admin)
def user_add(request):
    """Add new user with form processing"""
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'User "{user.username}" has been added successfully.')
            return redirect('custom_admin:user_list')
    else:
        form = UserForm()
    
    context = {
        'active_page': 'users',
        'form': form,
        'title': 'Add New User'
    }
    
    return render(request, 'custom_admin/user_form.html', context)


@login_required
@user_passes_test(is_admin)
def user_edit(request, user_id):
    """Edit user with form processing"""
    user = get_object_or_404(User, id=user_id)
    
    # Only superusers can edit other superusers
    if user.is_superuser and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to edit this user.')
        return redirect('custom_admin:user_list')
    
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'User "{user.username}" has been updated successfully.')
            return redirect('custom_admin:user_list')
    else:
        form = UserForm(instance=user)
    
    context = {
        'active_page': 'users',
        'form': form,
        'user': user,
        'title': f'Edit User: {user.username}'
    }
    
    return render(request, 'custom_admin/user_form.html', context)


@login_required
@user_passes_test(is_admin)
def user_delete(request, user_id):
    """Delete user with confirmation"""
    user = get_object_or_404(User, id=user_id)
    
    # Prevent deleting own account
    if user == request.user:
        messages.error(request, 'You cannot delete your own account.')
        return redirect('custom_admin:user_list')
    
    # Only superusers can delete superusers
    if user.is_superuser and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to delete this user.')
        return redirect('custom_admin:user_list')
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'User "{username}" has been deleted successfully.')
        return redirect('custom_admin:user_list')
    
    context = {
        'active_page': 'users',
        'user': user,
        'title': f'Delete User: {user.username}'
    }
    
    return render(request, 'custom_admin/user_confirm_delete.html', context)


@login_required
@user_passes_test(is_admin)
def user_toggle_status(request, user_id):
    """Toggle user active status"""
    user = get_object_or_404(User, id=user_id)
    
    # Only superusers can toggle status of superusers
    if user.is_superuser and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to modify this user.')
        return redirect('custom_admin:user_list')
    
    # Prevent deactivating own account
    if user == request.user and user.is_active:
        messages.error(request, 'You cannot deactivate your own account.')
        return redirect('custom_admin:user_list')
    
    # Toggle active status
    user.is_active = not user.is_active
    user.save()
    
    status = 'activated' if user.is_active else 'deactivated'
    messages.success(request, f'User "{user.username}" has been {status} successfully.')
    
    return redirect('custom_admin:user_list')


@login_required
@user_passes_test(is_admin)
def analytics(request):
    """Analytics page"""
    # Get time range from query params
    days = int(request.GET.get('days', 30))
    
    # Get analytics data using helper functions
    analytics_summary = get_analytics_summary()
    daily_traffic = get_daily_traffic(days)
    top_pages = get_top_pages()
    popular_searches = get_popular_searches()
    device_stats = get_device_stats()
    user_stats = get_user_stats()
    
    context = {
        'active_page': 'analytics',
        'days': days,
        **analytics_summary,  # Unpack analytics summary stats
        'daily_traffic': daily_traffic,
        'top_pages': top_pages,
        'popular_searches': popular_searches,
        'device_stats': device_stats,
        'user_stats': user_stats,
    }
    
    return render(request, 'custom_admin/analytics.html', context)


@login_required
@user_passes_test(is_admin)
def settings(request):
    """Settings page"""
    # In a real app, these would be loaded from a settings model
    settings_data = {
        'system_name': 'Undershelf',
        'language': 'en',
        'timezone': 'UTC',
        'min_password_length': 8,
        'require_uppercase': True,
        'require_numbers': True,
        'require_special': False,
        'two_factor_auth': False,
        'new_user_notifications': True,
        'new_book_notifications': True,
        'system_alerts': True,
        'review_notifications': True,
        'email_digest': 'daily',
    }
    
    if request.method == 'POST':
        # In a real app, you'd save the settings here
        # For now, just redirect back to the same page
        return redirect('custom_admin:settings')
    
    context = {
        'active_page': 'settings',
        'settings': settings_data,
    }
    
    return render(request, 'custom_admin/settings.html', context)


@login_required
@user_passes_test(is_admin)
def generate_report(request, type):
    """Generate a report - placeholder"""
    # In a real app, this would generate a report
    if type == 'users':
        return redirect('custom_admin:user_list')
    else:
        return redirect('custom_admin:dashboard')
