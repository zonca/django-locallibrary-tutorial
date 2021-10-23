from datetime import date
from django.shortcuts import render
from django.db.models import Count
from django.http import HttpResponseRedirect

# Create your views here.

from .models import Book, Author, BookInstance, Genre, Loan

def toggle_available_only(request):
    if "available_only" in request.session:
        request.session["available_only"] = not request.session["available_only"]
    else:
        request.session["available_only"] = True
    return HttpResponseRedirect(request.GET.get('next', "/books"))

def index(request):
    """View function for home page of site."""
    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    # Available copies of books
    num_instances_available = num_instances - Loan.objects.filter(return_date__isnull=True).count()
    num_authors = Author.objects.count()  # The 'all()' is implied by default.

    # Render the HTML template index.html with the data in the context variable.
    return render(
        request,
        'index.html',
        context={'num_books': num_books, 'num_instances': num_instances,
                 'num_instances_available': num_instances_available, 'num_authors': num_authors,
                 },
    )


from django.views import generic


class BookListView(generic.ListView):
    """Generic class-based view for a list of books."""
    model = Book
    paginate_by = 12


class BookDetailView(generic.DetailView):
    """Generic class-based detail view for a book."""
    model = Book


class AuthorListView(generic.ListView):
    """Generic class-based list view for a list of authors."""
    model = Author
    paginate_by = 20
    queryset = Author.objects.all().annotate(book_count=Count("book"))


class AuthorDetailView(generic.DetailView):
    """Generic class-based detail view for an author."""
    model = Author

class GenreListView(generic.ListView):
    model = Genre
    paginate_by = 20
    queryset = Genre.objects.all().annotate(book_count=Count("book"))


class GenreDetailView(generic.DetailView):
    model = Genre

from django.contrib.auth.mixins import LoginRequiredMixin


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = Loan
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return Loan.objects.filter(borrower=self.request.user).order_by('due_date')


# Added as part of challenge!
from django.contrib.auth.mixins import PermissionRequiredMixin


class LoanedBooksAllListView(PermissionRequiredMixin, generic.ListView):
    """Generic class-based view listing all books on loan. Only visible to users with can_mark_returned permission."""
    model = BookInstance
    permission_required = 'catalog.can_mark_returned'
    template_name = 'catalog/bookinstance_list_borrowed_all.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.order_by('due_back')


from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime
from django.contrib.auth.decorators import login_required, permission_required

# from .forms import RenewBookForm
from catalog.forms import RenewBookForm


@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    """View function for renewing a specific BookInstance by librarian."""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed'))

    # If this is a GET (or any other method) create the default form
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=1)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)

from django.contrib import messages

@login_required
def reserve_book(request, pk):
    """View function for reserving a book."""
    if request.user.loan_set.filter(reserved_date__isnull=False, return_date__isnull=True).count() >= request.user.max_books:
        messages.error(request, 'Already reached the maximum number of {} Reserved books.'.format(request.user.max_books))
    else:
        book_instance= get_object_or_404(BookInstance, pk=pk)
        if book_instance.status != "Available":
            messages.error(request, 'Book not available')
        else:
            loan = Loan(book_instance=book_instance, borrower=request.user, reserved_date=date.today())
            loan.save()
    return HttpResponseRedirect(reverse('my-borrowed'))

@login_required
def cancel_reservation(request, pk):
    loan = get_object_or_404(Loan, pk=pk)
    if loan.borrower == request.user and loan.is_reservation:
        loan.return_date = date.today()
        loan.save()
    return HttpResponseRedirect(reverse('my-borrowed'))
