"""
Definition of views.
"""

import warnings
import unicodedata

#--------------------------------------------------------------
#Custom imports for authentication
#--------------------------------------------------------------
from django import forms
from django.contrib.auth import (
    authenticate, get_user_model, password_validation,
)
from django.contrib.auth.hashers import (
    UNUSABLE_PASSWORD_PREFIX, identify_hasher,
)
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.text import capfirst
from django.utils.translation import gettext, gettext_lazy as _
from django.conf import settings

UserModel = get_user_model()
#--------------------------------------------------------------
#Custom imports for authentication
#--------------------------------------------------------------

#--------------------------------------------------------------
#Custom imports
#--------------------------------------------------------------
from django.shortcuts import render
from django.http import HttpRequest
from django.template import RequestContext
from datetime import datetime
#--------------------------------------------------------------
#Custom imports
#--------------------------------------------------------------


#--------------------------------------------------------------
#Custom views
#--------------------------------------------------------------

def home(request):
    """Renders the home page."""
    print('Inside Home')
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/index.html',
        {
            'title':'Home Page',
            'year':datetime.now().year,
        }
    )

def home_ML(request):
    """Renders the home page."""
    print('Inside ML Home')
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/index_ML.html',
        {
            'title':'ML Home Page',
            'year':datetime.now().year,
        }
    )

def contact(request):
    """Renders the contact page."""
    print('Inside contact')
    return render(
        request,
        'app/contact.html',
        {
            'title':'Contact',
            'message':'Your contact page.',
            'year':datetime.now().year,            
        }
    )

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        {
            'title':'About',
            'message':'Your application description page.',
            'year':datetime.now().year,
        }
    )

# def login(request):
#     """Renders the about page."""
#     assert isinstance(request, HttpRequest)
#     return render(
#         request,
#         'app/login.html',
        
#         {
#             'title':'Login',
#             'message':'Your application Login page.',
#             'year':datetime.now().year,
#         }
#     )
#--------------------------------------------------------------
#Custom views
#--------------------------------------------------------------

#--------------------------------------------------------------
#Custom submit
#--------------------------------------------------------------

def login(request):
    print('Inside login button')
    print(type(request))
    return render(
        request,
        'app/index.html',        
        {
            'title':'Home Page',
            'message':'Your application home page.',
            'year':datetime.now().year,
        }
    )
#--------------------------------------------------------------
#Custom submit
#--------------------------------------------------------------

#--------------------------------------------------------------
#Custom authentication
#--------------------------------------------------------------
class UsernameField(forms.CharField):
    def to_python(self, value):
        return unicodedata.normalize('NFKC', super().to_python(value))

    def widget_attrs(self, widget):
        return {
            **super().widget_attrs(widget),
            'autocapitalize': 'none',
            'autocomplete': 'username',
        }

class AuthenticationForm(forms.Form):
    """
    Base class for authenticating users. Extend this to get a form that accepts
    username/password logins.
    """
    username = UsernameField(widget=forms.TextInput(attrs={'autofocus': True}))
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'}),
    )

    error_messages = {
        'invalid_login': _(
            "Please enter a correct %(username)s and password. Note that both "
            "fields may be case-sensitive."
        ),
        'inactive': _("This account is inactive."),
    }

    def __init__(self, request=None, *args, **kwargs):
        """
        The 'request' parameter is set for custom auth use by subclasses.
        The form data comes in via the standard 'data' kwarg.
        """
        print('within form __init__')
        print('settings.AUTH_USER_MODEL: ' + settings.AUTH_USER_MODEL)
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

        # Set the max length and label for the "username" field.
        self.username_field = UserModel._meta.get_field(UserModel.USERNAME_FIELD)
        username_max_length = self.username_field.max_length or 254
        self.fields['username'].max_length = username_max_length
        self.fields['username'].widget.attrs['maxlength'] = username_max_length
        print(self.fields['username'].label)
        if self.fields['username'].label is None:
            self.fields['username'].label = capfirst(self.username_field.verbose_name)
        

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username is not None and password:
            print('username: ' + username + ': password : ' + password)
            # print(authenticate(self.request, username=username, password=password))
            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None:
                print('From user cache is none def __clean')
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)
                print('From user cache is notn none def __clean')

        return self.cleaned_data

    def confirm_login_allowed(self, user):
        """
        Controls whether the given User may log in. This is a policy setting,
        independent of end-user authentication. This default behavior is to
        allow login by active users, and reject login by inactive users.

        If the given user cannot log in, this method should raise a
        ``forms.ValidationError``.

        If the given user may log in, this method should return None.
        """
        print('from within confirm_login_allowed')
        
        if not user.is_active:
            raise forms.ValidationError(
                self.error_messages['inactive'],
                code='inactive',
            )

    def get_user(self):
        print('from within get_user')
        return self.user_cache

    def get_invalid_login_error(self):
        print('from within get_invalid_login_error')
        
        return forms.ValidationError(
            self.error_messages['invalid_login'],
            code='invalid_login',
            params={'username': self.username_field.verbose_name},
        )

#--------------------------------------------------------------
#Custom authentication
#--------------------------------------------------------------
