from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("search/", views.search, name="search"),
    path("book/<str:book_id>/", views.book_details, name="book_details"),
    path("autocomplete/", views.autocomplete, name="autocomplete"),
    path("about/", views.about, name="about"),
    path("signup/", views.signup_view, name="signup"),
    path("profile/", views.profile_view, name="profile"),
    path("profile/delete/", views.delete_account_view, name="delete_account"),
]
