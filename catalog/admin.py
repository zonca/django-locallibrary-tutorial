from django.contrib import admin

# Register your models here.

from .models import Author, Genre, Book, BookInstance, Language, Loan

admin.site.register(Genre)
admin.site.register(Language)


class BooksInline(admin.TabularInline):
    """Defines format of inline book insertion (used in AuthorAdmin)"""

    model = Book


class LoanReservationFilter(admin.SimpleListFilter):

    title = "Type"
    parameter_name = "type"

    def lookups(self, request, model_admin):
        return (("loans", "Loans"), ("reservations", "Reservations"))

    def queryset(self, request, queryset):
        if self.value() == "reservations":
            return queryset.filter(
                return_date__isnull=True,
                loan_date__isnull=True,
                reserved_date__isnull=False,
            )
        elif self.value() == "loans":
            return queryset.filter(return_date__isnull=True, loan_date__isnull=False)


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Loan._meta.get_fields()]
    list_filter = (LoanReservationFilter,)


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    """Administration object for Author models.
    Defines:
     - fields to be displayed in list view (list_display)
     - orders fields in detail view (fields),
       grouping the date fields horizontally
     - adds inline addition of books in author view (inlines)
    """

    list_display = ("last_name", "first_name")
    fields = ["first_name", "last_name"]


class BooksInstanceInline(admin.TabularInline):
    """Defines format of inline book instance insertion (used in BookAdmin)"""

    model = BookInstance


class BookAdmin(admin.ModelAdmin):
    """Administration object for Book models.
    Defines:
     - fields to be displayed in list view (list_display)
     - adds inline addition of book instances in book view (inlines)
    """

    list_display = ("title", "author", "display_genre")
    inlines = [BooksInstanceInline]


admin.site.register(Book, BookAdmin)


@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    """Administration object for BookInstance models.
    Defines:
     - fields to be displayed in list view (list_display)
     - filters that will be displayed in sidebar (list_filter)
     - grouping of fields into sections (fieldsets)
    """

    list_display = ("book", "id")
    # list_filter = ('status', 'due_back')

    # fieldsets = (
    #    (None, {
    #        'fields': ('book', 'imprint', 'id')
    #    }),
    #    ('Availability', {
    #        'fields': ('status', 'due_back', 'borrower')
    #    }),
    # )


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

UserAdmin.list_display += ("students_at_Italian_school", "supporter", "library_card_until")  # don't forget the commas
UserAdmin.list_filter += ("students_at_Italian_school", "supporter", "library_card_until")
UserAdmin.fieldsets += (
    ("Library card", {"fields": ("students_at_Italian_school", "supporter", "library_card_until")}),
)
admin.site.register(User, UserAdmin)
