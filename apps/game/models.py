from django.db import models

class Game(models.Model):
    '''Tic-tac-toe game
    '''
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    board = models.CharField(max_length=54) # max length: [None, None, None, None, None, None, None, None, None]
    player1 = models.CharField(max_length=1) # X, O
    player2 = models.CharField(max_length=1) # X, O
    winner = models.CharField(max_length=4) # X, O, None