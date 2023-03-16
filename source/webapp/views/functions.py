import re
from django.shortcuts import get_object_or_404
from webapp.models import Country, Player, Tournament, Club, Game


# Функция считает средний ранг игроков одного клуба. Возвращает список, в котором словарь с ключами club
# (содержит pk клуба) и average (посчитанное значение). На доработке
def average_go_level():
    # Здесь нужно будет привязать фильтр через страну клуба, чтобы выводил только по Кыргызстану
    clubs = Club.objects.all()
    club_list = []
    for club in clubs:
        new_dict = dict()
        num_list = []
        num_players = club.players.count()
        for player in club.players.all():
            tournament = player.tournaments.all().order_by('-date')[:1]
            data = player.playerintournament_set.get(tournament_id=tournament)
            if data.GoLevel:
                p = re.compile('(\d*)')
                m = p.findall(data.GoLevel)
                for i in m:
                    if i != "":
                        num_list.append(int(i))
        total_go_level = sum(num_list)
        if num_players > 0:
            average_num = total_go_level // num_players
            new_dict['club'] = club.pk
            new_dict['average'] = average_num
        else:
            new_dict['club'] = club.pk
            new_dict['average'] = 0
        club_list.append(new_dict)
    return club_list


# На доработке
def get_position_in_kgf():
    country = Country.objects.get(country_code='kg')
    players = Player.objects.filter(country=country)
    tournaments = Tournament.objects.order_by("date")
    new_list = []
    for player in players:
        new_dict = dict()
        for tournament in tournaments:
            for data in tournament.playerintournament_set.all():
                if player.pk == data.player_id:
                    if player.pk not in new_dict:
                        new_dict['player'] = player.pk
                        p = re.compile('(\d*)')
                        m = p.findall(data.GoLevel)
                        for i in m:
                            if i != "":
                                new_dict['GoLevel'] = int(i)
        new_list.append(new_dict)
    new_list.sort(key=lambda dictionary: dictionary['GoLevel'])
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

