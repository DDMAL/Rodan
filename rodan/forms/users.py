from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


class SignupLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    email = forms.EmailField(required=False, help_text="If you wish to create a new account, enter your email address below.")

    # Make sure the username/password combination is valid, if email is empty
    # Otherwise, make sure that the username has not been taken already
    def clean(self):
        cleaned_data = super(SignupLoginForm, self).clean()
        email = cleaned_data['email']
        username = cleaned_data['username']
        password = cleaned_data['password']

        # If the email is set, we want to create a new user
        if email:
            if User.objects.filter(username__iexact=username).count() > 0:
                # This username already exists - show an error
                raise forms.ValidationError("The specified username has already been taken.")
        else:
            # We want to log in an existing user (case insensitive)
            try:
                username = User.objects.get(username__iexact=username)
                user = authenticate(username=username, password=password)
                if user is None:
                    # We should treat wrong passwords and usernames the same
                    raise User.DoesNotExist

                # Update the data dictionary (to fix wrong case issues)
                cleaned_data['username'] = username
            except User.DoesNotExist:
                raise forms.ValidationError("The username/password combination is incorrect. Please try again.")

        return cleaned_data
