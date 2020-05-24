from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

from .models import User


class UserAdminCreateForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("email",)

    def clean_invited_by(self):
        invited_by = self.cleaned_data['invited_by']
        if invited_by is None:
            try:
                User.objects.get(invited_by=None)
            except User.MultipleObjectsReturned:
                raise ValidationError(_("Tree must have only one root user"))
            except User.DoesNotExist:
                pass

        user = self.instance
        if user == invited_by:
            raise ValidationError(_("User can't be invited by himself"))

        user.invited_by = invited_by
        user_copy = user
        while user.invited_by:
            user = user.invited_by
            if user == user_copy:
                raise ValidationError(_("This connection violates tree structure"))

        return invited_by
