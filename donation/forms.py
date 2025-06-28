from django import forms
from .models import Donation

class DonationForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = ['amount', 'cause']
        widgets = {
            'cause': forms.Select(choices=Donation.CAUSES),
        }
