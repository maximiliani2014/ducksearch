from django.urls import path
from django.conf.urls import url
from . import views

app_name = 'app'
urlpatterns = [
    path('', views.index, name="index"),
    url(r'^ajax/display_form/$', views.display_form, name='display_form'),
    path('search_page', views.search_page, name="search_page"),
    path('search', views.search, name="search"),
    path('simple_search', views.simple_search, name="simple_search"),
    path('edit_account', views.edit_account, name="edit_account"),
]
