from operator import itemgetter
from collections import Counter
from django.db.models import Q
from django.shortcuts import get_object_or_404
from webapp.models import Country, Player, Tournament, Club, Game, DEFAULT_CLASS
from webapp.views.GoR_calculator import get_new_rank_from_rating, get_total_score_for_player


# Функция считает средний ранг игроков одного клуба. Возвращает список, в котором словарь с ключами club
# (содержит pk клуба) и average (посчитанное значение)
def average_go_level():
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


def get_position_in_kgf():
    country = Country.objects.get(country_code='kg')
    players = Player.objects.filter(country=country)
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


def get_data_for_table_games(pk):
    player = Player.objects.get(pk=pk)
    tournaments = player.playerintournament_set.all().order_by('-tournament__date')
    new_list = []
    for element in tournaments:
        tournament = Tournament.objects.get(pk=element.tournament_id)
        games = Game.objects.filter(tournament=tournament)
        for game in games:
            new_dict = dict()
            new_dict['tournament'] = tournament
            if game.black == player:
                new_dict['round'] = game.round_num
                opponent = game.white
                if opponent:
                    data = opponent.playerintournament_set.filter(tournament=tournament)
                    for el in data:
                        new_dict['rank'] = el.GoLevel
                        if el.club is not None:
                            new_dict['club'] = el.club.name
                new_dict['opponent'] = game.white
                if game.result is not None:
                    if game.black_score == 0:
                        new_dict['result'] = '-'
                    elif game.black_score == 1:
                        new_dict['result'] = '+'
                new_dict['color'] = 'b'
                new_list.append(new_dict)
            elif game.white == player:
                new_dict['round'] = game.round_num
                opponent = game.black
                if opponent:
                    data = opponent.playerintournament_set.filter(tournament=tournament)
                    for el in data:
                        new_dict['rank'] = el.GoLevel
                        if el.club is not None:
                            new_dict['club'] = el.club.name
                new_dict['opponent'] = game.black
                if game.result is not None:
                    if game.white_score == 0:
                        new_dict['result'] = '-'
                    elif game.white_score == 1:
                        new_dict['result'] = '+'
                new_dict['color'] = 'w'
                new_list.append(new_dict)
    for item in new_list:
        if item['opponent'] is None:
            new_list.remove(item)
    return new_list


def get_data_for_gor_evolution(pk):
    player = Player.objects.get(pk=pk)
    tournaments = player.playerintournament_set.all()
    new_list = []
    for element in tournaments:
        tournament = Tournament.objects.get(pk=element.tournament_id)
        games = Game.objects.filter(tournament=tournament)
        for game in games:
            new_dict = dict()
            if game.black == player and game.black_gor_change:
                new_dict['tournament'] = tournament
                new_dict['round'] = game.round_num
                new_dict['gor_change'] = game.black_gor_change
                opponent = game.white
                if opponent:
                    data = opponent.playerintournament_set.filter(tournament=tournament)
                    for el in data:
                        new_dict['opponent_rank'] = el.GoLevel
                        new_dict['opponent_rating'] = el.rating
                new_dict['opponent'] = game.white
                new_dict['opponent_gor_change'] = game.white_gor_change
                if game.result is not None:
                    if game.black_score == 0:
                        new_dict['result'] = 'Loss'
                    elif game.black_score == 1:
                        new_dict['result'] = 'Win'
                new_dict['color'] = 'b'
                new_list.append(new_dict)
            elif game.white == player and game.white_gor_change:
                new_dict['tournament'] = tournament
                new_dict['round'] = game.round_num
                new_dict['gor_change'] = game.white_gor_change
                opponent = game.black
                if opponent:
                    data = opponent.playerintournament_set.filter(tournament=tournament)
                    for el in data:
                        new_dict['opponent_rank'] = el.GoLevel
                        new_dict['opponent_rating'] = el.rating
                new_dict['opponent'] = game.black
                new_dict['opponent_gor_change'] = game.black_gor_change
                if game.result is not None:
                    if game.white_score == 0:
                        new_dict['result'] = 'Loss'
                    elif game.white_score == 1:
                        new_dict['result'] = 'Win'
                new_dict['color'] = 'w'
                new_list.append(new_dict)
            else:
                pass
    for item in new_list:
        if item['opponent'] is None:
            new_list.remove(item)
    return new_list


def get_tournaments_list_for_gor_evolution(pk):
    player = Player.objects.get(pk=pk)
    tournaments = player.playerintournament_set.all()
    new_list = []
    for element in tournaments:
        new_dict = dict()
        tournament = Tournament.objects.get(pk=element.tournament_id)
        total_score = get_total_score_for_player(tournament.pk)
        for el in total_score:
            if el['player'] == player:
                new_dict['total'] = el['total']
        if element.rating != 0:
            new_dict['tournament'] = tournament
            new_dict['rating_before'] = element.rating
            new_dict['rating_after'] = element.rating_after
            new_dict['rank_after'] = element.GoLevel_after
            new_list.append(new_dict)
    return new_list


def player_wins_loses(pk):
    player = Player.objects.get(pk=pk)
    games = Game.objects.filter(Q(black=player) | Q(white=player))
    wl = []
    for game in games:
        new_dict = dict()
        wins_stronger = 0
        wins_weaker = 0
        losses_stronger = 0
        losses_weaker = 0
        wins_equal = 0
        losses_equal = 0
        if game.result:
            if game.black == player and game.black_score > 0 and game.black.current_rating > game.white.current_rating:
                wins_weaker += game.black_score
            elif game.black == player and game.black_score > 0 and game.black.current_rating < game.white.current_rating:
                wins_stronger += game.black_score
            elif game.white == player and game.white_score > 0 and game.white.current_rating > game.black.current_rating:
                wins_weaker += game.white_score
            elif game.white == player and game.white_score > 0 and game.white.current_rating < game.black.current_rating:
                wins_stronger += game.white_score
            elif game.black == player and game.white_score > 0 and game.black.current_rating > game.white.current_rating:
                losses_weaker += 1
            elif game.black == player and game.white_score > 0 and game.black.current_rating < game.white.current_rating:
                losses_stronger += 1
            elif game.white == player and game.black_score > 0 and game.white.current_rating > game.black.current_rating:
                losses_weaker += 1
            elif game.white == player and game.black_score > 0 and game.white.current_rating < game.black.current_rating:
                losses_stronger += 1
            elif game.black == player and game.white_score > 0 and game.black.current_rating == game.white.current_rating:
                losses_equal += 1
            elif game.black == player and game.black_score > 0 and game.black.current_rating == game.white.current_rating:
                wins_equal += 1
            elif game.white == player and game.black_score > 0 and game.white.current_rating == game.black.current_rating:
                losses_equal += 1
            elif game.white == player and game.white_score > 0 and game.white.current_rating == game.black.current_rating:
                wins_equal += 1
        new_dict['player'] = player.pk
        new_dict['wins_weaker'] = wins_weaker
        new_dict['wins_stronger'] = wins_stronger
        new_dict['losses_weaker'] = losses_weaker
        new_dict['losses_stronger'] = losses_stronger
        new_dict['losses_equal'] = losses_equal
        new_dict['wins_equal'] = wins_equal
        wl.append(new_dict)
    c = Counter()
    for d in wl:
        c.update(d)
    statistics = dict(c)
    return statistics

def club_active_players(pk):
    club = get_object_or_404(Club, pk=pk)
    players = club.players.all()
    all_players = dict()
    under_21k = []
    under_11k = []
    under_6k = []
    under_1k = []
    under_5d = []
    under_10d = []
    for player in players:
        if player.current_rating <= 0:
            under_21k.append(player)
        elif player.current_rating > 0 and player.current_rating <= 1000:
            under_11k.append(player)
        elif player.current_rating > 1000 and player.current_rating <= 1500:
            under_6k.append(player)
        elif player.current_rating > 1500 and player.current_rating <= 2000:
            under_1k.append(player)
        elif player.current_rating > 2000 and player.current_rating <= 2500:
            under_5d.append(player)
        elif player.current_rating > 2500 and player.current_rating <= 3000:
            under_10d.append(player)
    all_players['all'] = len(players)
    all_players['under_21k'] = len(under_21k)
    all_players['under_11k'] = len(under_11k)
    all_players['under_6k'] = len(under_6k)
    all_players['under_1k'] = len(under_1k)
    all_players['under_5d'] = len(under_5d)
    all_players['under_10d'] = len(under_10d)
    # print(f'21{under_21k}')
    # print(f'11{under_11k}')
    # print(f'6{under_6k}')
    # print(f'1{under_1k}')
    # print(f'5{under_5d}')
    # print(f'10{under_10d}')
    return all_players


def unpack_data_json_tournament(data):
    new_dict = dict()
    for key, value in data.items():
        if key == "Tournament":
            items = value
            for k, v in items.items():
                if k == 'Name':
                    tournament_name = v
                    new_dict['Name'] = tournament_name
                elif k == "NumberOfRounds":
                    round_num = int(v)
                    new_dict['NumberOfRounds'] = round_num
                elif k == "Boardsize":
                    board_size = int(v)
                    new_dict['Boardsize'] = board_size
                    new_dict['date'] = ''
                    new_dict['tournament_class'] = DEFAULT_CLASS
                    new_dict['location'] = ''
                    new_dict['city'] = ''
                    new_dict['regulations'] = ''
    return new_dict


def unpack_data_json_players(data):
    new_list = []
    for key, value in data.items():
        if key == "Tournament":
            items = value
            for k, v in items.items():
                if k == 'IndividualParticipant':
                    list_of_players = v
                    for element in list_of_players:
                        new_dict = dict()
                        for m, n in element.items():
                            if m == "Id":
                                id_in_game = n
                            elif m == 'GoPlayer':
                                person = n
                                new_dict['FirstName'] = person.get('FirstName')
                                new_dict['Surname'] = person.get('Surname')
                                new_dict['GoLevel'] = person.get('GoLevel')
                                new_dict['Rating'] = float(person.get('Rating'))
                                new_dict['EgdPin'] = int(person.get('EgdPin'))
                                new_dict['Club'] = person.get('Club')
                                new_dict['birth_date'] = ''
                                new_dict['id_in_game'] = id_in_game
                                new_list.append(new_dict)
    return new_list


def update_json_tournament(data, some_dict, some_list):
    updated_data = {}
    for key, value in data.items():
        if key == "Tournament":
            items = value.copy()
            element = {}
            for k, v in items.items():
                element[k] = v
                element.update({
                    'Name': some_dict['Name'],
                    'NumberOfRounds': some_dict['NumberOfRounds'],
                    'Boardsize': some_dict['Boardsize'],
                    'date': some_dict['date'],
                    'city': some_dict['city'],
                    'tournament_class': some_dict['tournament_class'],
                    'regulations': some_dict['regulations'],
                    'uploaded_by': some_dict['uploaded_by'],
                })
            updated_data['Tournament'] = element
            if 'IndividualParticipant' in items:
                list_of_players = items['IndividualParticipant']
                for element in list_of_players:
                    for m, n in element.items():
                        for el in some_list:
                            if m == 'Id':
                                id_in_game = n
                            elif m == 'GoPlayer':
                                d = n
                                new_element = {}
                                for g, h in d.items():
                                    new_element[g] = h
                                if id_in_game == el['id_in_game']:
                                    new_element.update({
                                        'FirstName': el['FirstName'],
                                        'Surname': el['Surname'],
                                        'GoLevel': el['GoLevel'],
                                        'Rating': el['Rating'],
                                        'EgdPin': el['EgdPin'],
                                        'birth_date': el['birth_date'],
                                        'id_in_game': el['id_in_game']
                                    })
                                    element['GoPlayer'] = new_element

    return updated_data


def unpack_data_for_moderation_tournament(data):
    new_dict = {}
    for k, v in data.get('Tournament', {}).items():
        if k in {'Name', 'NumberOfRounds', 'Boardsize', 'date', 'tournament_class', 'location', 'city', 'regulations'}:
            new_dict[k] = int(v) if k == 'NumberOfRounds' or k == 'Boardsize' else v
    return new_dict


def unpack_data_for_moderation_players(data):
    new_list = []
    for player in data.get('Tournament', {}).get('IndividualParticipant', []):
        person = player.get('GoPlayer', {})
        new_dict = {
            'FirstName': person.get('FirstName'),
            'Surname': person.get('Surname'),
            'GoLevel': person.get('GoLevel'),
            'Rating': float(person.get('Rating', 0)),
            'EgdPin': int(person.get('EgdPin', 0)),
            'Club': person.get('Club'),
            'birth_date': person.get('birth_date')
        }
        new_list.append(new_dict)
    return new_list


