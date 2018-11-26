from django.urls import path

from tictactoe.game import views

urlpatterns = [
    path('', views.home, name='home'),
    path('setup', views.setup, name='setup'),
    path('clear', views.clear, name='clear'),
    path('play', views.play, name='play'),
    path('thanks', views.thanks, name='thanks'),
]
