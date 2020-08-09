"""
Definition of urls for python_webapp_django.
"""

from datetime import datetime
from django.conf.urls import url
from django.contrib.auth.views import LoginView
import django.contrib.auth.views
from django.urls import path

import app.forms
import app.views

# Uncomment the next lines to enable the admin:
# from django.conf.urls import include
# from django.contrib import admin
# admin.autodiscover()
print('Before url pattern')
urlpatterns = [
    # Examples:
    
    # url(r'^login_submit/$', app.views.login, name='login_button'),
    # url(r'^$',
    #     django.contrib.auth.views.LoginView.as_view(template_name='app/login.html',
    #                                                 authentication_form=app.forms.BootstrapAuthenticationForm),
    #         name='login',
    # ), 
    url(r'^$', app.views.home, name='home'),
    url(r'^home_ML$', app.views.home_ML, name='home_ML'),
    url(r'^contact$', app.views.contact, name='contact'),
    url(r'^about', app.views.about, name='about'),
    url('^weather/$', app.views.graphs, name="weather_graph"),
    # url(r'^login/$',
    #     app.views.login,
    #     {
    #         'template_name': 'app/login.html',
    #         'authentication_form': app.forms.BootstrapAuthenticationForm,
    #         'extra_context':
    #         { 
    #             'title': 'Log in',
    #             'year': datetime.now().year,
    #         }
    #     },
    #     name='login'),    

    url(r'^login/$',
        django.contrib.auth.views.LoginView.as_view(template_name='app/login.html',
                                                    authentication_form=app.forms.BootstrapAuthenticationForm),        
        name='login',
    ),
    url(r'^logout$',
        django.contrib.auth.views.LogoutView.as_view(next_page='/'),
        name='logout'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
]
