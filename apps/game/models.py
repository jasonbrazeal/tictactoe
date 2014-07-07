from django.db import models

class Game(models.Model):
    '''Tic-tac-toe game. Inspired by http://inventwithpython.com/chapter10.html and https://github.com/sontek-archive/django-tictactoe/blob/master/small_tictactoe/apps/core/models.py
    '''
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    session_id = models.CharField(max_length=32)
    board_str = models.CharField(max_length=54, default=[None]*9) # max length: [None, None, None, None, None, None, None, None, None]
    player1 = models.CharField(max_length=1, default='X') # X, O
    player2 = models.CharField(max_length=1, default='O') # X, O
    winner = models.CharField(max_length=4, null=True, default=None) # X, O, None/NULL

    # def save(self, *args, **kwargs):
    #     ''' Converts board list to string before saving model.
    #     '''
    #     self.board_str = str(self.get_board())
    #     super(Game, self).save(*args, **kwargs)

    def get_board(self):
        '''Returns the tic-tac-toe board as a Python list object.
        '''
        return eval(self.board_str)

    def get_winner(self, board=None):
        '''Returns winner of game. Returns None if no winner.
        '''
        if board == None:
            board = self.get_board()
        if ((board[3] == board[4] == board[5])
        or (board[1] == board[4] == board[7])
        or (board[0] == board[4] == board[8])
        or (board[2] == board[4] == board[6])):
            return board[4] # center

        elif ((board[0] == board[1] == board[2])
        or (board[0] == board[3] == board[6])):
            return board[0] # top left

        elif ((board[6] == board[7] == board[8])
        or (board[2] == board[5] == board[8])):
            return board[8] # bottom right

    def is_tie(self):
        '''Returns None
        '''
        if not self.get_winner():
            return None not in self.get_board()
        # returns None

    def get_possible_moves(self):
        '''
        '''
        return [i for i, space in enumerate(self.get_board()) if space==None]

    def get_winning_moves(self):
        '''Returns tuple of lists. First list is player1's winning move(s) and second list is player2's winning move(s).
        '''
        player1_moves = list()
        player2_moves = list()
        # check player1's winning moves
        for space in self.get_possible_moves():
            board = self.get_board()
            board[space] = self.player1
            if self.get_winner(board) == self.player1:
                player1_moves.append(space)
            board[space] = self.player2
            if self.get_winner(board) == self.player2:
                player2_moves.append(space)
        return player1_moves, player2_moves

    def make_move(self, player, space):
        board = self.get_board()
        board[space] = player
        self.board_str = str(board)
        self.save()

    def __unicode__(self):
        return self.board_str