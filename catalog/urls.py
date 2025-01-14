from django.urls import path

from . import views


urlpatterns = [
    # path('', views.index, name='index'),
    path('books/', views.BookListView.as_view(), name='books'),
    path('toggle-available-only/', views.toggle_available_only, name='toggle-available-only'),
    path('book/<int:pk>', views.BookDetailView.as_view(), name='book-detail'),
    path('authors/', views.AuthorListView.as_view(), name='authors'),
    path('author/<int:pk>',
         views.AuthorDetailView.as_view(), name='author-detail'),
    path('genres/', views.GenreListView.as_view(), name='genres'),
    path('genre/<int:pk>',
         views.GenreDetailView.as_view(), name='genre-detail'),
]


urlpatterns += [
    path('mybooks/', views.LoanedBooksByUserListView.as_view(), name='my-borrowed'),
    path(r'borrowed/', views.LoanedBooksAllListView.as_view(), name='all-borrowed'),  # Added for challenge
]


# Add URLConf for librarian to renew a book.
urlpatterns += [
    path('loan/<int:pk>/renew/', views.renew_book_librarian, name='renew-book-librarian'),
    path('loan/<uuid:pk>/reserve/', views.reserve_book, name='reserve-book'),
    path('loan/<int:pk>/cancel/', views.cancel_reservation, name='cancel-reservation'),
]
