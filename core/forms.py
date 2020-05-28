from allauth.account.forms import SignupForm
from django import forms

from core.models import Profile, Account


class CustomSignupForm(SignupForm):
    account_type = forms.ChoiceField(choices=((Profile.REQUESTER, 'Requester'), (Profile.SHOPPER, 'Shopper')))

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        account = Account.objects.create(name=user.username)
        profile_model = Profile.get_profile_model(self.cleaned_data['account_type'])
        profile_model.objects.create(user=user, account=account)
        return user
