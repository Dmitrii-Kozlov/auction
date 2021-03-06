from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("listing", views.listing, name="listing"),
    path("listing_page/<int:page_id>", views.listing_page, name="listing_page"),
    path("listing_page/<int:page_id>/comment", views.create_comment, name="create_comment"),
    path("category", views.category, name="category"),
    path("category_view/<str:category>", views.category_view, name="category_view"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("listing_page/<int:page_id>/bid", views.place_bid, name="place_bid"),
    path("close_auction", views.close_auction, name="close_auction")

]
