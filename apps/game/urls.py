from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls import patterns, include, url
from tic_tac_toe.apps.game import views


urlpatterns = patterns('',
    url(r'^$', views.home, name='home'),
)