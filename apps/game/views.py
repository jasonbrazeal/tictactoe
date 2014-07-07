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
    possible_moves = g.get_possible_moves()
    possible_corner_moves = list(set([0,2,6,8]) & set(possible_moves))

    if winning_moves['player_o']: # win if possible
        space_AI = winning_moves['player_o'][0] # there should only be one item in the list unless someone has missed an opportunity
    elif winning_moves['player_x']: # block human win
        space_AI = winning_moves['player_x'][0]
    elif 5 in possible_moves: # play center
        space_AI = 5
    elif possible_corner_moves: # play corner
        space_AI = possible_corner_moves[randint(0,len(possible_corner_moves)-1)]
    else: # play side
        space_AI = possible_moves[randint(0,len(possible_moves)-1)]

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