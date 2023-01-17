from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new_listing", views.new_listing, name="new_listing"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("<int:id>", views.current_listing, name="current_listing"),
    path("<int:id>/comment", views.comment, name="comment"),
    path("category", views.category, name="category"),
    path("category_items/<str:category_name>", views.category_items, name="category_items"),
    path("bid/<int:id>", views.bid, name="bid"),
    path("close/<int:id>", views.close, name="close")

]
