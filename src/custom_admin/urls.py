from django.urls import path
from . import views

app_name = 'custom_admin'

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Book management
    path('books/', views.book_list, name='book_list'),
    path('books/add/', views.book_add, name='book_add'),
    path('books/<str:book_id>/edit/', views.book_edit, name='book_edit'),
    path('books/<str:book_id>/delete/', views.book_delete, name='book_delete'),
    path('books/import/', views.book_import, name='book_import'),
    path('books/export/', views.book_export, name='book_export'),
    
    # User management
    path('users/', views.user_list, name='user_list'),
    path('users/add/', views.user_add, name='user_add'),
    path('users/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:user_id>/delete/', views.user_delete, name='user_delete'),
    path('users/<int:user_id>/toggle-status/', views.user_toggle_status, name='user_toggle_status'),
    
    # Analytics
    path('analytics/', views.analytics, name='analytics'),
    
    # Settings
    path('settings/', views.settings, name='settings'),
    
    # Reports
    path('reports/<str:type>/', views.generate_report, name='generate_report'),
]
