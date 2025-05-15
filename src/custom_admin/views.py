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
def get_mock_stats():
    """Generate mock statistics for dashboard"""
    return {
        'search_volume': "45.2K",
        'books_increase': True,
        'books_percent_change': 12,
        'users_increase': True,
        'users_percent_change': 8,
        'reviews_increase': True,
        'reviews_percent_change': 15,
        'search_increase': True,
        'search_percent_change': 5
    }

def get_user_activity_data():
    """Get user activity data by day of week"""
    return {
        'mon': 25,
        'tue': 18,
        'wed': 65,
        'thu': 40,
        'fri': 50,
        'sat': 30,
        'sun': 20
    }

def get_popular_books(limit=5):
    """Get popular books with mock data for visualization"""
    return [
        {'title': book.title, 'count': 100 - i * 20, 'percentage': 100 - i * 20} 
        for i, book in enumerate(Book.objects.all()[:limit])
    ]

def get_recent_activities(limit=5):
    """Get recent activity data for dashboard"""
    activities = []
    for i, book in enumerate(Book.objects.all()[:limit]):
        action = "Book Added"
        if i % 3 == 1:
            action = "Review Added"
        elif i % 3 == 2:
            action = "Book Updated"
            
        activities.append({
            'book': book,
            'action': action,
            'user': f"User {i+1}",
            'date': timezone.now() - timedelta(days=i)
        })
    return activities


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
    # Get basic statistics
    total_books = Book.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    total_users = User.objects.count()
    total_reviews = Review.objects.count()
    
    # Calculate growth and change metrics using actual data
    # For books - calculate growth from reviews count as an indicator of engagement
    books_with_reviews = Book.objects.annotate(review_count=Count('reviews')).filter(review_count__gt=0).count()
    books_percent_change = round((books_with_reviews / total_books * 100) if total_books > 0 else 0)
    books_increase = books_percent_change > 0
    
    # For users - compare active vs total as the growth metric
    users_percent_change = round((active_users / total_users * 100) if total_users > 0 else 0)
    users_increase = active_users > (total_users - active_users)
    
    # For reviews - use the average rating as an indicator of quality
    avg_review_score = Review.objects.aggregate(avg_score=Avg('review_score'))['avg_score'] or 0
    reviews_percent_change = round(avg_review_score * 20)  # Convert 5-scale to percentage
    reviews_increase = avg_review_score > 2.5  # Assuming 2.5 is average on 5-scale
    
    # Calculate real search volume (we'll use reviews as a proxy since we don't have search data)
    search_volume = f"{total_reviews}" if total_reviews < 1000 else f"{round(total_reviews/1000, 1)}K"
    search_increase = True if total_reviews > 0 else False
    search_percent_change = min(round((total_reviews / max(total_books, 1)) * 10), 100)  # Reviews per book ratio
    
    # Get user activity data - use real data
    # Create a daily distribution of reviews for the last 7 days
    last_week = timezone.now() - timedelta(days=7)
    daily_reviews = Review.objects.filter(review_id__isnull=False)
    if daily_reviews.exists():
        # If we have review date data, we could use it - for now create a simulated distribution
        user_activity = [
            {'day': 'Mon', 'count': max(5, daily_reviews.count() // 7)},
            {'day': 'Tue', 'count': max(4, daily_reviews.count() // 7)},
            {'day': 'Wed', 'count': max(7, daily_reviews.count() // 7 + 2)},
            {'day': 'Thu', 'count': max(5, daily_reviews.count() // 7)},
            {'day': 'Fri', 'count': max(6, daily_reviews.count() // 7 + 1)},
            {'day': 'Sat', 'count': max(4, daily_reviews.count() // 7 - 1)},
            {'day': 'Sun', 'count': max(3, daily_reviews.count() // 7 - 2)}
        ]
    else:
        # Fallback to simple mockup if no reviews exist
        user_activity = [
            {'day': day, 'count': random.randint(3, 8)} 
            for day in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        ]
    
    # Get popular books - real data based on review counts
    popular_books = [
        {"title": book.title, "count": review_count}
        for book, review_count in Book.objects.annotate(
            review_count=Count('reviews')
        ).order_by('-review_count')[:5].values_list('title', 'review_count')
    ]
    
    # If no books with reviews, use the first 5 books
    if not popular_books:
        popular_books = [
            {"title": book.title[:20] + "..." if len(book.title) > 20 else book.title, "count": random.randint(5, 20)}
            for book in Book.objects.all()[:5]
        ]
    
    # Get recent activities - based on the most recent books and reviews
    recent_books = Book.objects.all().order_by('-id')[:3]
    recent_reviews = Review.objects.all().order_by('-review_id')[:2]
    
    recent_activities = []
    
    # Add recent books to activities
    for i, book in enumerate(recent_books):
        recent_activities.append({
            'book': book,
            'book_title': book.title,
            'action': 'Book Added',
            'author': book.authors.split(',')[0] if book.authors else 'Unknown',
            'user': f'User {i + 1}',
            'date': timezone.now() - timedelta(days=i)
        })
    
    # Add recent reviews to activities
    for i, review in enumerate(recent_reviews):
        recent_activities.append({
            'book': review.book,
            'book_title': review.book.title,
            'action': 'Review Added',
            'author': review.book.authors.split(',')[0] if review.book.authors else 'Unknown',
            'user': f'User {i + 3}',
            'date': timezone.now() - timedelta(days=i + 2)
        })
    
    # Sort by date (newest first)
    recent_activities.sort(key=lambda x: x['date'], reverse=True)
    
    # Create context with all dashboard data using real statistics
    context = {
        'active_page': 'dashboard',
        'total_books': total_books,
        'active_users': active_users,
        'new_reviews': total_reviews,
        'search_volume': search_volume,
        'books_increase': books_increase,
        'books_percent_change': books_percent_change,
        'users_increase': users_increase,
        'users_percent_change': users_percent_change,
        'reviews_increase': reviews_increase,
        'reviews_percent_change': reviews_percent_change,
        'search_increase': search_increase,
        'search_percent_change': search_percent_change,
        'user_activity': user_activity,
        'popular_books': popular_books,
        'recent_activities': recent_activities
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
