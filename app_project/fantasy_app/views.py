from django.shortcuts import render
from .models import Player, Team, Match, League, Matchup, Transfer


def player_details(request, name):
    player = Player.objects.get(id = name)
    return render(request, 'player_details.html', {'player': player})
# Create your views here.
