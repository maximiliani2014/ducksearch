from django import forms

# form for creating new user
class CreateForm(forms.Form):
    username = forms.CharField(label='', max_length=100,widget=forms.TextInput(attrs={'class': "plaintext_field", 'placeholder': 'Username'}))
    password = forms.CharField(label='', max_length=100, widget=forms.TextInput(attrs={'class': "plaintext_field", 'placeholder': 'Password'}))
    interest = forms.CharField(label='', max_length=100, widget=forms.TextInput(attrs={'class': "plaintext_field", 'placeholder': 'Interest'}))
    strength = forms.DecimalField(label='', max_digits=2, decimal_places=1, widget=forms.TextInput(attrs={'class': "plaintext_field", 'placeholder': 'Interest Strength: 0-1'}))

class LoginForm(forms.Form):
    username = forms.CharField(label='', max_length=100, widget=forms.TextInput(attrs={'class': "plaintext_field", 'placeholder': 'Username'}))
    password = forms.CharField(label='', max_length=100, widget=forms.TextInput(attrs={'class': "plaintext_field", 'placeholder': 'Password'}))

class SearchForm(forms.Form):
    value = forms.CharField(label='',max_length=300, widget=forms.TextInput(attrs={'class': "plaintext_field", 'placeholder': 'DuckSearch'}))
    additional_interest = forms.CharField(label='', required=False, max_length=100, widget=forms.TextInput(attrs={'class': "plaintext_field", 'placeholder': 'Additional Interest (Optional)'}))
    additional_interest_strength = forms.DecimalField(label='', max_digits=2, decimal_places=1, required=False, widget=forms.TextInput(attrs={'class': "plaintext_field", 'placeholder': 'Interest Strength: 0-1 (Optional)'}))

class SimpleSearchForm(forms.Form):
    value = forms.CharField(label='',max_length=300, widget=forms.TextInput(attrs={'class': "plaintext_field", 'placeholder': 'SimpleSearch'}))

class EditInterestsForm(forms.Form):
    interest = forms.CharField(label='', max_length=100, widget=forms.TextInput(attrs={'class': "plaintext_field", 'placeholder': 'Interest to Add/Remove'}))
    strength = forms.DecimalField(label='', max_digits=2, decimal_places=1, required=False, widget=forms.TextInput(attrs={'class': "plaintext_field", 'placeholder': 'Interest Strength: 0-1'}))

class ChangePasswordForm(forms.Form):
    new_password = forms.CharField(label='', max_length=100, widget=forms.TextInput(attrs={'class': "plaintext_field", 'placeholder': 'New Password'}))
    new_password_repeat = forms.CharField(label='', max_length=100, widget=forms.TextInput(attrs={'class': "plaintext_field", 'placeholder': 'New Password Again'}))

class DeleteAccountForm(forms.Form):
    confirmation = forms.CharField(label='', max_length=100, widget=forms.TextInput(attrs={'class': "plaintext_field", 'placeholder': 'Type Username Here to Confim Deletion'}))
