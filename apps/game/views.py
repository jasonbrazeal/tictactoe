from django.shortcuts import render_to_response
from django.template import RequestContext
# from django.http import JsonResponse

from game.models import Game

def home(request):
    request.session['has_game'] = True
    g = Game(session_id=request.session._session_key)
    # g.save()



    return render_to_response('game/home.html',
                              {},
                              context_instance=RequestContext(request))




def play(request):
    if not request.is_ajax():
        return 'Invalid call. AJAX required.'

    position = request.POST.get('position', None)
    player = request.POST.get('player', None)

    # get session object
    # session = Session.objects.get(session_key=request.session._session_key)
    # check that session exists
    # if not session:
    #     return 'Invalid call. Session required.'

    if request.session['has_game']:
        g = Game.objects.filter(session_key=request.session._session_key)
    else:
        g = Game(session_id=request.session._session_key)
        g.save()

        g.board.insert(position, player)
        g.save()

    winner = g.get_winner()
    if winner:
        return response

    is_tie = g.is_tie()
    if is_tie:
        return response

    # decide AI's move

    g.board.insert(position_AI, player_AI)
    g.save()

    winner = g.get_winner()
    if winner:
        return response

    is_tie = g.is_tie()
    if is_tie:
        return response

    # update session if needed

    # return JsonResponse({'win': '',
    #                      'tie': '',
    #                      'winning_move': ''
    #                     })
