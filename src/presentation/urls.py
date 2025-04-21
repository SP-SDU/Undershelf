from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("search/", views.search, name="search"),
    path("book/<str:book_id>/", views.book_details, name="book_details"),
    path("login/", views.login, name="login"),
    path("sign-up/", views.signup, name="signup"),
    path("autocomplete/", views.autocomplete, name="autocomplete"),
]
