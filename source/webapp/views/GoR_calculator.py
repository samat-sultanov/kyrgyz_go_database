from django.shortcuts import get_object_or_404
from webapp.models import Tournament, Game
import math

RANK_FROM_RATING = [{-800: "29k"}, {-700: "28k"}, {-600: '27k'}, {-500: '26k'}, {-400: "25k"}, {-300: "24k"},
                    {-200: "23k"}, {-100: "22k"}, {0: "21k"}, {100: "20k"}, {200: "19k"}, {300: "18k"}, {400: "17k"},
                    {500: "16k"}, {600: "15k"}, {700: "14k"}, {800: "13k"}, {900: "12k"}, {1000: "11k"}, {1100: "10k"},
                    {1200: "9k"}, {1300: "8k"}, {1400: "7k"}, {1500: "6k"}, {1600: "5k"}, {1700: "4k"}, {1800: "3k"},
                    {1900: "2k"}, {2000: "1k"}, {2100: "1d"}, {2200: '2d'}, {2300: "3d"}, {2400: "4d"}, {2500: "5d"},
                    {2600: "6d"}, {2700: "7d"}, {2800: "8d"}, {2900: "9d"}, {3000: "10d"},
                    ]

CLASS_VALUE = {'A': 1, 'B': 0.75, 'C': 0.5, 'D': 0.25}


def get_class(x):
    for key, value in CLASS_VALUE.items():
        if x == key:
            return value


def get_data(pk):
    tournament = get_object_or_404(Tournament, pk=pk)
    class_value = get_class(tournament.tournament_class)
    players = tournament.playerintournament_set.all()
    games = Game.objects.all().filter(tournament_id=tournament.pk)
    new_list = []
    for game in games:
        for element in players:
            new_dict = dict()
            if element.player.pk == game.black_id:
                if game.white_id:
                    new_dict['player'] = element.player
                    new_dict['rating'] = element.rating
                    con = get_con(element.rating)
                    bonus = get_bonus(element.rating)

                    se = get_se(element.rating, get_opponent_rating(game.white_id, game.round_num, pk))
                    score = get_score(con, game.black_score, se, bonus)
                    if score:
                        score_with_class = score * class_value
                        game.black_gor_change = score_with_class
                    else:
                        game.black_gor_change = score
                    game.save()
                    new_dict['score'] = score
                    new_dict['result'] = game.black_score
                    new_dict['opponent'] = game.white
                    new_dict['opponent_rating'] = get_opponent_rating(game.white_id, game.round_num, pk)
                    opponent_rating = get_opponent_rating(game.white_id, game.round_num, pk)
                    opponent_con = get_con(opponent_rating)
                    opponent_bonus = get_bonus(opponent_rating)
                    opponent_se = get_se(opponent_rating, element.rating)
                    opponent_score = get_score(opponent_con, game.white_score, opponent_se, opponent_bonus)
                    new_dict['opponent_score'] = opponent_score
                    new_dict['round'] = game.round_num
                    if opponent_score:
                        score_with_class = opponent_score * class_value
                        game.white_gor_change = score_with_class
                    else:
                        game.white_gor_change = opponent_score
                    game.save()
                    new_list.append(new_dict)
                else:
                    pass

    return new_list


def get_opponent_rating(opponent_id, number_of_round, pk):
    tournament = get_object_or_404(Tournament, pk=pk)
    games = Game.objects.all().filter(tournament_id=tournament.pk)
    players = tournament.playerintournament_set.all()
    for game in games:
        for element in players:
            try:
                if element.player.pk == opponent_id and game.round_num == number_of_round:
                    return element.rating
            except:
                pass


def get_con(num):
    con = ((3300 - num) / 200) ** 1.6
    return con


def get_bonus(num):
    bonus = math.log(1 + math.exp((2300 - num) / 80)) / 5
    return bonus


def get_beta(num):
    beta = -7 * math.log(3300 - num)
    return beta


def get_se(num1, num2):
    se = 1 / (1 + math.exp(get_beta(num2) - get_beta(num1)))
    return se


def get_new_rank_from_rating(num):
    for element in RANK_FROM_RATING:
        for k, v in element.items():
            if num <= k + 99:
                return v


def get_score(con, result, se, bonus):
    if se:
        score = con * (result - se) + bonus
        return score
    else:
        return None


def get_total_score_for_player(pk):
    tournament = get_object_or_404(Tournament, pk=pk)
    players = tournament.player_set.all()
    data = get_data(pk)
    new_list = []
    for player in players:
        new_dict = dict()
        score = []
        new_dict['player'] = player
        for element in data:
            if player == element['player'] and element['score']:
                score.append(element['score'])
            if player == element['opponent'] and element['opponent_score']:
                score.append(element['opponent_score'])
        total = sum(score)
        new_dict['total'] = total
        new_list.append(new_dict)
    return new_list


def get_rating_from_rank(x):
    for element in RANK_FROM_RATING:
        for k, v in element.items():
            if x == v:
                return k


def get_new_rating(pk):
    tournament = get_object_or_404(Tournament, pk=pk)
    players = tournament.playerintournament_set.all()
    data = get_total_score_for_player(pk)
    for element in data:
        for item in players:
            if element['player'].pk == item.player.pk:
                if item.rating >= 100:
                    new_rating = item.rating + element['total']
                    new_rank = get_new_rank_from_rating(new_rating)
                    item.rating_after = new_rating
                    item.GoLevel_after = new_rank
                    item.save()
                elif 100 > item.rating > item.rating + element['total']:
                    new_rating = item.rating
                    item.rating_after = new_rating
                    item.GoLevel_after = item.GoLevel
                    item.save()
                elif 100 > item.rating < item.rating + element['total']:
                    new_rating = item.rating + element['total']
                    new_rank = get_new_rank_from_rating(new_rating)
                    item.rating_after = new_rating
                    item.GoLevel_after = new_rank
                    item.save()


def get_current_rating_and_rank(pk):
    tournament = get_object_or_404(Tournament, pk=pk)
    players = tournament.player_set.all()
    for player in players:
        last_tournament = player.tournaments.order_by('-date')[0]
        data = player.playerintournament_set.filter(tournament=last_tournament)
        for element in data:
            player.current_rank = element.GoLevel_after
            player.current_rating = element.rating_after
            player.save()

