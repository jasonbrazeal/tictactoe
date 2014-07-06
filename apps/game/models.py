from django.db import models

class Game(models.Model):
    '''Tic-tac-toe game
    '''
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    board_str = models.CharField(max_length=54, default=[None]*9) # max length: [None, None, None, None, None, None, None, None, None]
    player1 = models.CharField(max_length=1, default='X') # X, O
    player2 = models.CharField(max_length=1, default='O') # X, O
    winner = models.CharField(max_length=4, null=True, default=None) # X, O, None/NULL

    def _get_board(self):
        '''Returns the tic-tac-toe board as a Python list object.
        '''
        return eval(self.board_str)

    board = property(_get_board)

    def get_winner(self):
        if ((self.board[3] == self.board[4] == self.board[5])
        or (self.board[1] == self.board[4] == self.board[7])
        or (self.board[0] == self.board[4] == self.board[8])
        or (self.board[2] == self.board[4] == self.board[6])):
            return self.board[4] # center

        elif ((self.board[0] == self.board[1] == self.board[2])
        or (self.board[0] == self.board[3] == self.board[6])):
            return self.board[0] # top left

        elif ((self.board[6] == self.board[7] == self.board[8])
        or (self.board[2] == self.board[5] == self.board[8])):
            return self.board[8] # bottom right

        # returns None

    def is_tie(self):
        '''Returns None
        '''
        if not self.get_winner():
            return None not in self.board
        # returns None

    # def _get_full_name(self):
    #     "Returns the person's full name."
    #     return u'%s %s' % (self.first_name, self.last_name)
    # full_name = property(_get_full_name)


    def __unicode__(self):
        return self.board_str