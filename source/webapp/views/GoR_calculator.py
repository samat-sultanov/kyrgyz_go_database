from django.shortcuts import get_object_or_404
from webapp.models import Tournament, Game


def get_data():
    tournament = get_object_or_404(Tournament, pk=13)
    players = tournament.playerintournament_set.all()
    games = Game.objects.all().filter(tournament_id=tournament.pk)
    new_list = []
    for game in games:
        for element in players:
            new_dict = dict()
            if element.player.pk == game.black_id:
                new_dict['player'] = element.player
                new_dict['rating'] = element.rating
                new_dict['con'] = get_con(element.rating)
                new_dict['result'] = game.black_score
                new_dict['opponent'] = game.white_id
                new_dict['opponent_rating'] = get_rating(game.white_id, game.round_num)
                new_dict['round'] = game.round_num
                new_list.append(new_dict)
    print(new_list)
    return new_list


def get_rating(pk, number):
    tournament = get_object_or_404(Tournament, pk=13)
    games = Game.objects.all().filter(tournament_id=tournament.pk)
    players = tournament.playerintournament_set.all()
    for game in games:
        for element in players:
            try:
                if element.player.pk == pk and game.round_num == number:
                    return element.rating
            except:
                pass


def get_con(num):
    con = ((3300 - num) / 200) ** 1.6
    return con
