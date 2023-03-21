from django.shortcuts import get_object_or_404
from webapp.models import Tournament, Game
import math

RANK_FROM_RATING = [{-400: "25k"}, {-300: "24k"}, {-200: "23k"}, {-100: "22k"}, {0: "21k"}, {100: "20k"}, {200: "19k"},
                    {300: "18k"}, {400: "17k"}, {500: "16k"}, {600: "15k"}, {700: "14k"}, {800: "13k"}, {900: "12k"},
                    {1000: "11k"}, {1100: "10k"}, {1200: "9k"}, {1300: "8k"}, {1400: "7k"}, {1500: "6k"}, {1600: "5k"},
                    {1700: "4k"}, {1800: "3k"}, {1900: "2k"}, {2000: "1k"}, {2100: "1d"}, {2200: '2d'}, {2300: "3d"},
                    {2400: "4d"}, {2500: "5d"}, {2600: "6d"}, {2700: "7d"}, {2800: "8d"}, {2900: "9d"}, {3000: "10d"},
                    ]


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
                con = get_con(element.rating)
                bonus = get_bonus(element.rating)
                se = get_se(element.rating, get_opponent_rating(game.white_id, game.round_num))
                score = get_score(con, game.black_score, se, bonus)
                new_dict['score'] = score
                new_dict['result'] = game.black_score
                new_dict['opponent'] = game.white_id
                new_dict['opponent_rating'] = get_opponent_rating(game.white_id, game.round_num)
                if game.white_id:
                    opponent_rating = get_opponent_rating(game.white_id, game.round_num)
                    opponent_con = get_con(opponent_rating)
                    opponent_bonus = get_bonus(opponent_rating)
                    opponent_se = get_se(opponent_rating, element.rating)
                    opponent_score = get_score(opponent_con, game.white_score, opponent_se, opponent_bonus)
                    new_dict['opponent_score'] = opponent_score
                else:
                    pass
                new_dict['round'] = game.round_num
                new_list.append(new_dict)
    print(new_list)
    for item in new_list:
        print(item)
    return new_list


def get_opponent_rating(pk, number):
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
    if num:
        con = ((3300 - num) / 200) ** 1.6
        return con
    else:
        return None


def get_bonus(num):
    if num:
        bonus = math.log(1 + math.exp((2300 - num) / 80)) / 5
        return bonus
    else:
        return None


def get_beta(num):
    if num is not None:
        beta = -7 * math.log(3300 - num)
        return beta
    else:
        return None


def get_se(num1, num2):
    if num2 and num1:
        se = 1 / (1 + math.exp(get_beta(num2) - get_beta(num1)))
        return se
    else:
        return None


def get_new_rank_from_rating(num):
    for element in RANK_FROM_RATING:
        for k, v in element.items():
            if num <= k:
                return v


def get_score(con, result, se, bonus):
    if se:
        score = con * (result - se) + bonus
        return score
    else:
        return None
