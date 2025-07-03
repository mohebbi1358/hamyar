from django import forms
from donation.models import Donation, DonationCause

class DonationForm(forms.ModelForm):
    cause = forms.ModelChoiceField(
        queryset=DonationCause.objects.filter(is_active=True),
        empty_label="یک علت را انتخاب کنید",
        widget=forms.Select()
    )

    class Meta:
        model = Donation
        fields = ['amount', 'cause']



# donation/forms.py
from django import forms
from .models import DonationCause

class DonationCauseForm(forms.ModelForm):
    class Meta:
        model = DonationCause
        fields = ['title', 'is_active']
