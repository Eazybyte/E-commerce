from django import forms
from .models import ReviewRating

class ReviewForm(forms.ModelForm):
    class meta:
        model = ReviewRating
        fields= ['subject','review','rating']
        