from django import forms


class ExampleEntityForm(forms.Form):
    name = forms.CharField(max_length=255)