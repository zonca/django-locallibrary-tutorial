from django.db import models
from datetime import date, timedelta

# Create your models here.

from django.urls import reverse  # To generate URLS by reversing URL patterns

from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    class Meta:
        db_table = 'auth_user'

    students_at_Italian_school = models.IntegerField(default=1)
    library_card_until = models.DateField(blank=True, null=True)
    supporter = models.BooleanField(default=False)

    @property
    def is_expired(self):
        return if self.library_card_until is None or date.today() > self.library_card_until

    @property
    def max_books(self):
        # return self.students_at_Italian_school + 1
        return 1

    def current_loans_or_reservations(self):
        return self.loan_set.filter(returned_date__isnull=False)

class Genre(models.Model):
    """Model representing a book genre (e.g. Science Fiction, Non Fiction)."""
    name = models.CharField(
        max_length=200,
        help_text="Enter a book genre (e.g. Science Fiction, French Poetry etc.)"
        )

    def get_absolute_url(self):
        return reverse('genre-detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object (in Admin site etc.)"""
        return self.name


class Language(models.Model):
    """Model representing a Language (e.g. English, French, Japanese, etc.)"""
    name = models.CharField(max_length=200,
                            help_text="Enter the book's natural language (e.g. English, French, Japanese etc.)")

    def __str__(self):
        """String for representing the Model object (in Admin site etc.)"""
        return self.name


class Book(models.Model):
    """Model representing a book (but not a specific copy of a book)."""
    title = models.CharField(max_length=200)
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)
    # Foreign Key used because book can only have one author, but authors can have multiple books
    # Author as a string rather than object because it hasn't been declared yet in file.
    summary = models.TextField(max_length=1000, help_text="Enter a brief description of the book")
    genre = models.ManyToManyField(Genre, help_text="Select a genre for this book")
    # ManyToManyField used because a genre can contain many books and a Book can cover many genres.
    # Genre class has already been defined so we can specify the object above.
    language = models.ForeignKey('Language', default=1, on_delete=models.SET_NULL, null=True)

    cover = models.ImageField(upload_to='covers')
    url = models.URLField(null=True)

    class Meta:
        ordering = ['title', 'author']

    def display_genre(self):
        """Creates a string for the Genre. This is required to display genre in Admin."""
        return ', '.join([genre.name for genre in self.genre.all()[:3]])

    display_genre.short_description = 'Genre'

    def get_absolute_url(self):
        """Returns the url to access a particular book instance."""
        return reverse('book-detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return self.title

    @property
    def is_available(self):
        for bookinstance in self.bookinstance_set.all():
            if bookinstance.status == "Available":
                return True
        return False



import uuid  # Required for unique book instances

class BookInstance(models.Model):
    """Model representing a specific copy of a book (i.e. that can be borrowed from the library)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          help_text="Unique ID for this particular book across whole library")
    book = models.ForeignKey('Book', on_delete=models.RESTRICT, null=True)
    imprint = models.CharField(max_length=200)

    @property
    def status(self):
        loan = self.loan
        if not loan:
            return "Available"
        elif loan.is_reservation:
            return "Reserved"
        elif loan.is_loan:
            return "On loan"
        else:
            return "Unknown"

    @property
    def loan(self):
        try:
            return self.loan_set.get(return_date__isnull=True)
        except Loan.DoesNotExist:
            return None

    def __str__(self):
        """String for representing the Model object."""
        return '{0} ({1})'.format(self.book.title, self.imprint)

class Loan(models.Model):
    DEFAULT_LOAN_DURATION = timedelta(days=14)
    reserved_date = models.DateField(blank=True, null=True)
    loan_date = models.DateField(blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    return_date = models.DateField(blank=True, null=True)
    borrower = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    book_instance = models.ForeignKey(BookInstance, on_delete=models.DO_NOTHING)
    def save(self, *args, **kwargs):
        if self.loan_date is not None and self.due_date is None:
            self.due_date = self.loan_date + self.DEFAULT_LOAN_DURATION
        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        return self.due_date and date.today() > self.due_date and self.return_date is None

    @property
    def is_reservation(self):
        return self.reserved_date and self.loan_date is None and self.return_date is None

    @property
    def is_loan(self):
        return self.loan_date is not None and self.return_date is None

    def __str__(self):
        """String for representing the Model object."""
        return '{0} - {1}'.format(self.book_instance.book.title, self.borrower.username)

class Author(models.Model):
    """Model representing an author."""
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    class Meta:
        ordering = ['last_name', 'first_name']

    def get_absolute_url(self):
        """Returns the url to access a particular author instance."""
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return '{0}, {1}'.format(self.last_name, self.first_name)
