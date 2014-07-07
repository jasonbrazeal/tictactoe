from django.db import models

class Game(models.Model):
    '''Tic-tac-toe game. Inspired by http://inventwithpython.com/chapter10.html and https://github.com/sontek-archive/django-tictactoe/blob/master/small_tictactoe/apps/core/models.py
    '''
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    session_id = models.CharField(max_length=32)
    board_str = models.CharField(max_length=54, default=[None]*9) # max length: [None, None, None, None, None, None, None, None, None]
    player_x = models.CharField(max_length=1, default='X') # X, O
    player_o = models.CharField(max_length=1, default='O') # X, O
    winner = models.CharField(max_length=4, null=True, default=None) # X, O, None/NULL

    def get_board(self):
        '''Returns the tic-tac-toe board as a Python list object.
        '''
        return eval(self.board_str)

    def get_winner(self, board=None):
        '''Returns winner of game. Returns None if no winner.
        '''
        if board == None:
            board = self.get_board()

        if (((board[3] == board[4] == board[5])
          or (board[1] == board[4] == board[7])
          or (board[0] == board[4] == board[8])
          or (board[2] == board[4] == board[6]))
          and board[4] is not None):
            return board[4] # center

        elif (((board[0] == board[1] == board[2])
            or (board[0] == board[3] == board[6]))
            and board[0] is not None):
            return board[0] # top left

        elif (((board[6] == board[7] == board[8])
            or (board[2] == board[5] == board[8]))
            and board[8] is not None):
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
        '''Returns dictionary of lists.
        '''
        player_x_moves = list()
        player_o_moves = list()
        for space in self.get_possible_moves():
            board = self.get_board()
            board[space] = self.player_x
            print board
            if self.get_winner(board) == self.player_x:
                player_x_moves.append(space)
            board[space] = self.player_o
            print board
            if self.get_winner(board) == self.player_o:
                player_o_moves.append(space)
        return {'player_x': player_x_moves, 'player_o': player_o_moves}

    def make_move(self, player, space):
        board = self.get_board()
        board[space] = player
        self.board_str = str(board)
        self.save()

    def __unicode__(self):
        return self.board_str