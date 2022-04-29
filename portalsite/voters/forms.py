from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class CreateUserForm(UserCreationForm):
	first_name = forms.CharField(max_length=30, required=False, label="First Name")
	last_name = forms.CharField(max_length=30, required=False)
	check = forms.BooleanField(required = True)


	class Meta:
		model = User

		fields = ['first_name', 'last_name', 'email' ,'password1', 'password2']

	def save(self, commit=True):
		user = super(UserCreationForm, self).save(commit=False)
		user.set_password(self.cleaned_data["password1"])
		user.username = '{}.{}'.format(self.cleaned_data['first_name'].replace(" ", "").lower(),self.cleaned_data['last_name'].replace(" ", "").lower())
		user.is_voter=True
		if commit:
			user.save()
		return user

	def saverep(self, commit=True):
		user = super(UserCreationForm, self).save(commit=False)
		user.set_password(self.cleaned_data["password1"])
		user.username = '{}.{}'.format(self.cleaned_data['first_name'].replace(" ", "").lower(),self.cleaned_data['last_name'].replace(" ", "").lower())
		user.is_rep=True
		if commit:
			user.save()
		return user

	def savefaci(self, commit=True):
		user = super(UserCreationForm, self).save(commit=False)
		user.set_password(self.cleaned_data["password1"])
		user.username = '{}.{}'.format(self.cleaned_data['first_name'].replace(" ", "").lower(),self.cleaned_data['last_name'].replace(" ", "").lower())
		user.is_faci=True
		if commit:
			user.save()
		return user