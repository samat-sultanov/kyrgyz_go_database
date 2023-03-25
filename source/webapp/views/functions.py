import re
from operator import itemgetter

from django.db.models import Q
from django.shortcuts import get_object_or_404
from webapp.models import Country, Player, Tournament, Club, Game
from webapp.views.GoR_calculator import get_new_rank_from_rating, RANK_FROM_RATING


# Функция считает средний ранг игроков одного клуба. Возвращает список, в котором словарь с ключами club
# (содержит pk клуба) и average (посчитанное значение). На доработке
def average_go_level():
    # Здесь нужно будет привязать фильтр через страну клуба, чтобы выводил только по Кыргызстану
    clubs = Club.objects.all()
    club_list = []
    for club in clubs:
        new_dict = dict()
        total_rating = 0
        num_players = club.players.count()
        for player in club.players.all():
            total_rating += player.current_rating
        if num_players > 0:
            result = total_rating // num_players
            average_num = get_new_rank_from_rating(result)
            new_dict['club'] = club.pk
            new_dict['average'] = average_num
        else:
            new_dict['club'] = club.pk
            new_dict['average'] = 0
        club_list.append(new_dict)
    return club_list


def get_total_wins(data):
    new_list = []
    for club in data:
        new_dict = dict()
        total_wins = 0
        for player in club.players.all():
            player_wins = 0
            games = Game.objects.filter(Q(black=player) | Q(white=player))
            for game in games:
                if game.result is not None:
                    if game.result.startswith('1'):
                        if game.black == player:
                            player_wins += 1
                    elif game.result.startswith('0'):
                        if game.white == player:
                            player_wins += 1
            total_wins += player_wins
        new_dict['club'] = club.pk
        new_dict['total'] = total_wins
        new_list.append(new_dict)
    return new_list


# На доработке
def get_position_in_kgf():
    country = Country.objects.get(country_code='kg')
    players = Player.objects.filter(country=country)
    # tournaments = Tournament.objects.order_by("date")
    new_list = []
    for player in players:
        new_dict = dict()
        new_dict['player'] = player
        new_dict['rating'] = player.current_rating
        new_dict['rank'] = player.current_rank
        new_list.append(new_dict)
    new_list.sort(key=itemgetter('rating'))
    new_list.reverse()
    position = 1
    for element in new_list:
        element['position'] = position
        position += 1
    return new_list


# Функция принимает список игроков, возвращает список из словарей с ключами Player и Golevel из последнего турнира,
# в котором участвовал игрок
def get_rank(data):
    tournaments = Tournament.objects.order_by("-date")
    new_list = []
    for player in data:
        new_dict = dict()
        for tournament in tournaments:
            for el in tournament.playerintournament_set.all():
                if player.pk == el.player_id:
                    if player not in new_dict:
                        new_dict['player'] = player
                        new_dict['GoLevel'] = el.GoLevel
        new_list.append(new_dict)
    return new_list


def get_element_to_sort(x):
    return x['position']


# Функция принимает список игроков формата tournament.playerintournament_set.all или после функции get_rank(), key_word
# (буква от Golevel - k  или d), и reverse (прямую или обратную сортировку), возвращает отсортированный список из
# словарей с ключами player, Golevel и position (позиция здесь - это цифра Golevel без учёта буквы).
# Список сортируется в прямом или обратном порядке, зависит от значения reverse.
def sort_players(data, key_word, reverse):
    new_list = []
    for el in data:
        new_dict = dict()
        if isinstance(el, dict):
            for key, value in el.items():
                if key == "GoLevel" and value.endswith(key_word):
                    new_dict['player'] = el['player']
                    new_dict['GoLevel'] = el['GoLevel']
                    new_dict['position'] = int(el['GoLevel'][:-1])
                    new_list.append(new_dict)
        else:
            if el.GoLevel.endswith(key_word):
                new_dict['player'] = el.player
                new_dict['GoLevel'] = el.GoLevel
                new_dict['position'] = int(el.GoLevel[:-1])
                new_list.append(new_dict)
    result = sorted(new_list, key=get_element_to_sort, reverse=reverse)
    return result


# Функция принимает список игроков формата tournament.playerintournament_set.all или после функции get_rank(),
# вызывает у себя функцию sort_players, делает сортировку игроков по рангу d от большего к меньшему и сортировку по
# рангу k от меньшего к большему, соединяет два списка словарей и возвращает одним списком
def get_list_of_filtered_players(data):
    players_with_rate_k = sort_players(data, 'k', reverse=False)
    players_with_rate_d = sort_players(data, 'd', reverse=True)
    filtered_players_list = players_with_rate_d + players_with_rate_k
    return filtered_players_list


# Функция принимает pk турнира и возвращает список из словарей с ключами - player, wins (победы в этом турнире), losses
# (поражения в рамках турнира)
def get_wins_losses(pk):
    tournament = get_object_or_404(Tournament, pk=pk)
    players = tournament.player_set.all()
    games = Game.objects.filter(tournament=tournament)
    new_list = []
    for player in players:
        new_dict = dict()
        wins = 0
        losses = 0
        for game in games:
            if game.result:
                if game.black == player and game.black_score > 0:
                    wins += game.black_score
                elif game.white == player and game.white_score > 0:
                    wins += game.white_score
                elif game.black == player and game.white_score > 0:
                    losses += 1
                elif game.white == player and game.black_score > 0:
                    losses += 1
            new_dict['player'] = player.pk
            new_dict['wins'] = wins
            new_dict['losses'] = losses
        new_list.append(new_dict)
    return new_list

def get_rank_for_json(data):
    tournaments = Tournament.objects.order_by("-date")
    new_list = []
    for player in data:
        new_dict = dict()
        for tournament in tournaments:
            for el in tournament.playerintournament_set.all():
                if player.pk == el.player_id:
                    if player not in new_dict:
                        new_dict['last_name'] = player.last_name
                        new_dict['first_name'] = player.first_name
                        new_dict['patronymic'] = player.patronymic
                        new_dict['GoLevel'] = el.GoLevel
        new_list.append(new_dict)
    return new_list


def get_rating_from_rank(x):
    for element in RANK_FROM_RATING:
        for k, v in element.items():
            if x == v:
                return k
