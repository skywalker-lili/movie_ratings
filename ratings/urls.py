from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^', views.index, name='index'), # any url will be directed to index page, the only page we have
]