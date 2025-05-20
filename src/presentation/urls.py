from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("search/", views.search, name="search"),
    path("book/<str:book_id>/", views.book_details, name="book_details"),
    path("login/", views.login_view, name="login"),
    path("sign-up/", views.signup_view, name="signup"),
    path("autocomplete/", views.autocomplete, name="autocomplete"),
    path("top-books/", views.top_books, name="top_books"),
    path('about/', views.about, name='about'),    
  #  path('logout/', logout_view, name='logout'),
]
