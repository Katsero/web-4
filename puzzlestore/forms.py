from django import forms
from .models import BoardGame

class BoardGameForm(forms.ModelForm):
    class Meta:
        model = BoardGame
        fields = ['name', 'image', 'rules_file', 'description', 'price', 
                  'age_limit', 'publisher', 'genres']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'genres': forms.CheckboxSelectMultiple(),
        }