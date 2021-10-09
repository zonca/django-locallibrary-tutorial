from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
import datetime  # for checking renewal date range.

from django import forms


class RenewBookForm(forms.Form):
    """Form for a librarian to renew books."""
    renewal_date = forms.DateField(
            help_text="Enter a date between now and 3 weeks (default 1).")

    def clean_renewal_date(self):
        data = self.cleaned_data['renewal_date']

        # Check date is not in past.
        if data < datetime.date.today():
            raise ValidationError(_('Invalid date - renewal in past'))
        # Check date is in range librarian allowed to change (+4 weeks)
        if data > datetime.date.today() + datetime.timedelta(weeks=3):
            raise ValidationError(
                _('Invalid date - renewal more than 4 weeks ahead'))

        # Remember to always return the cleaned data.
        return data


from django_registration.forms import RegistrationForm

from .models import User


class MyCustomUserForm(RegistrationForm):

    students_at_Italian_school = forms.IntegerField(required=True, default=1, help_text="Number of students at Italian school, set to 0 if you just donated books, you will still be able to borrow 1 book")
    class Meta(RegistrationForm.Meta):
        model = User
        help_texts = {
            'username': 'Required. Please set to "Firstname_Lastname" one of the students of Italian school. Letters, digits and @/./+/-/_ only',
        }


    def save(self, commit=True):
        user = super(MyCustomUserForm, self).save(commit=False)
        user.students_at_Italian_school = self.cleaned_data["students_at_Italian_school"]
        if commit:
            user.save()
        return user

MyCustomUserForm.Meta.fields  += ['students_at_Italian_school']