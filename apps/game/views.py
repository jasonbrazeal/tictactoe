from django.shortcuts import render_to_response
from django.template import RequestContext
# from django.http import JsonResponse
from django.http import HttpResponse
from random import randint
import json

from game.models import Game

def home(request):
    request.session['has_game'] = True
    g = Game(session_id=request.session._session_key)
    g.save()

    return render_to_response('game/home.html',
                              {},
                              context_instance=RequestContext(request))

def play(request):
    if not request.is_ajax():
        return HttpResponse('Invalid call. AJAX required.')

    player_human = 'X'
    player_AI = 'O'

    space_human = int(request.POST.get('space', None))

    # get session object
    # session = Session.objects.get(session_key=request.session._session_key)
    # check that session exists
    # if not session:
    #     return 'Invalid call. Session required.'

    # if request.session['has_game']:
    g = Game.objects.filter(session_id=request.session._session_key).order_by('-date_created')[0]
    # else:
    #     g = Game(session_id=request.session._session_key)
    #     g.save()

    g.make_move(player_human, space_human)

    # winner = g.get_winner()
    # if winner:
    #     response = ({'win': winner,
    #                  'tie': '',
    #                  'winning_move': '',
    #                  'next_player': ''
    #                 })
    #     return HttpResponse(json.dumps(response), content_type="application/json")


    # if g.is_tie():
    #     response = ({'win': '',
    #                  'tie': 'tie',
    #                  'winning_move': '',
    #                  'next_player': ''
    #                 })
    #     return HttpResponse(json.dumps(response), content_type="application/json")

    # decide AI's move
    winning_moves = g.get_winning_moves()
    fork_moves = g.get_fork_moves()
    possible_moves = g.get_possible_moves()
    possible_corner_moves = list(set([0,2,6,8]) & set(possible_moves))
    possible_side_moves = list(set([1,3,5,7]) & set(possible_moves))

    if winning_moves['O']: # win if possible
        space_AI = winning_moves['O'][0] # there should only be one item in the list unless someone has missed an opportunity
    elif winning_moves['X']: # block human win
        space_AI = winning_moves['X'][0]
    elif fork_moves['O']: # make a move that would result in a fork (guaranteed win on next turn)
        space_AI = fork_moves['O'][0]
    elif len(fork_moves['X']) == 1: # block the opponent's fork
        space_AI = fork_moves['X'][0]
    elif len(fork_moves['X']) > 1: # 2 possible forks; force opponent block AI win on next turn
        space_AI = possible_side_moves[randint(0,len(possible_corner_moves)-1)]
    elif 4 in possible_moves: # play center
        space_AI = 4
    elif possible_corner_moves: # play corner
        space_AI = possible_corner_moves[randint(0,len(possible_corner_moves)-1)]
    elif possible_side_moves: # play side
        space_AI = possible_side_moves[randint(0,len(possible_corner_moves)-1)]
    else: # error
        return HttpResponse(json.dumps({'error': 'hit impossible condition'}), content_type="application/json")

    g.make_move(player_AI, space_AI)

    # winner = g.get_winner()
    # if winner:
    #     response = ({'win': winner,
    #                  'tie': '',
    #                  'winning_move': '',
    #                  'next_player': ''
    #                 })
    #     return HttpResponse(json.dumps(response), content_type="application/json")

    # if g.is_tie():
    #     response = ({'win': '',
    #                  'tie': 'tie',
    #                  'winning_move': '',
    #                  'next_player': ''
    #                 })
    #     return HttpResponse(json.dumps(response), content_type="application/json")

    # update session if needed
    board_json = json.dumps(g.get_board())
    response = ({'win': '',
                 'tie': 'tie',
                 'winning_move': '',
                 'next_player': '',
                 'board': board_json,
                 'space_AI': str(space_AI),
                 'player_AI': player_AI
                })
    return HttpResponse(json.dumps(response), content_type="application/json")