from django.shortcuts import get_object_or_404
from webapp.models import Tournament, Game


def get_data():
    tournament = get_object_or_404(Tournament, pk=3)
    print(tournament)
    players = tournament.playerintournament_set.all()
    games = Game.objects.all().filter(tournament_id=tournament.pk)
    new_list = []
    for game in games:
        for player in players:
            new_dict = dict()
            if game.black_id == player.pk:
                new_dict['player'] = game.black
                new_dict['rating'] = player.rating
                new_dict['result'] = game.white_score
                new_dict['opponent'] = game.white
                new_dict['opponent_rating'] = get_rating(players, game.white, game.round_num)
                new_dict['round'] = game.round_num
                new_list.append(new_dict)
    return new_list


def get_rating(data, element, number):
    tournament = get_object_or_404(Tournament, pk=3)
    games = Game.objects.all().filter(tournament_id=tournament.pk)
    for game in games:
        for player in data:
            try:
                if player.pk == element.pk and game.round_num == number:
                    return player.rating
            except:
                pass
