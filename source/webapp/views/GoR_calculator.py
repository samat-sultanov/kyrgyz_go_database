from django.shortcuts import get_object_or_404
from webapp.models import Tournament, Game


def get_data():
    tournament = get_object_or_404(Tournament, pk=10)
    players = tournament.playerintournament_set.all()
    games = Game.objects.all().filter(tournament_id=tournament.pk)
    new_list = []
    for game in games:
        for element in players:
            new_dict = dict()
            if element.player.pk == game.black_id:
                new_dict['player'] = element.player
                new_dict['rating'] = element.rating
                new_dict['result'] = game.black_score
                new_dict['opponent'] = game.white_id
                new_dict['opponent_rating'] = get_rating(game.white_id, game.round_num)
                new_dict['round'] = game.round_num
                new_list.append(new_dict)
    print(new_list)
    return new_list


def get_rating(pk, number):
    tournament = get_object_or_404(Tournament, pk=10)
    games = Game.objects.all().filter(tournament_id=tournament.pk)
    players = tournament.playerintournament_set.all()
    for game in games:
        for element in players:
            try:
                if element.player.pk == pk and game.round_num == number:
                    return element.rating
            except:
                pass


def get_probability_win():
    data = get_data()
    for element in data:
        new_dict = dict()
        for key, value in element.items():
            try:
                if element['rating'] > element['opponent_rating']:
                    result = element['rating'] - element['opponent_rating']
                    new_dict['player'] = element['player']
                    new_dict['opponent'] = element['opponent']
                    new_dict['difference'] = result
                    if 200 > element['rating'] >= 100:
                        if 0 >= result > 25:
                            new_rate = element['rating'] + 116 * (element['result'] - 0.5)
                        elif 25 >= result > 50:
                            new_rate = element['rating'] + 116 * (element['result'] - 0.469)
                            print(new_rate)
                        elif 50 >= result > 75:
                            new_rate = element['rating'] + 116 * (element['result'] - 0.438)
                            print(new_rate)
                        elif 75 >= result > 100:
                            new_rate = element['rating'] + 116 * (element['result'] - 0.407)
                            print(new_rate)
                        elif 100 >= result > 125:
                            new_rate = element['rating'] + 116 * (element['result'] - 0.378)
                            print(new_rate)
                        elif 125 >= result > 150:
                            new_rate = element['rating'] + 116 * (element['result'] - 0.349)
                            print(new_rate)
                        elif 150 >= result > 175:
                            new_rate = element['rating'] + 116 * (element['result'] - 0.321)
                            print(new_rate)
                        elif 175 >= result > 200:
                            new_rate = element['rating'] + 116 * (element['result'] - 0.294)
                            print(new_rate)
                        elif 200 >= result > 225:
                            new_rate = element['rating'] + 116 * (element['result'] - 0.269)
                            print(new_rate)
                        elif 225 >= result > 250:
                            new_rate = element['rating'] + 116 * (element['result'] - 0.245)
                            print(new_rate)
                        elif 250 >= result > 275:
                            new_rate = element['rating'] + 116 * (element['result'] - 0.223)
                            print(new_rate)
                        elif 275 >= result > 300:
                            new_rate = element['rating'] + 116 * (element['result'] - 0.202)
                            print(new_rate)
                        elif 300 >= result > 325:
                            new_rate = element['rating'] + 116 * (element['result'] - 0.182)
                            print(new_rate)
                        elif 325 >= result > 350:
                            new_rate = element['rating'] + 116 * (element['result'] - 0.165)
                            print(new_rate)
                        elif 350 >= result > 375:
                            new_rate = element['rating'] + 116 * (element['result'] - 0.148)
                            print(new_rate)
                        elif 375 >= result > 400:
                            new_rate = element['rating'] + 116 * (element['result'] - 0.133)
                            print(new_rate)
                        elif 400 >= result > 425:
                            new_rate = element['rating'] + 116 * (element['result'] - 0.119)
                            print(new_rate)
                        elif 425 >= result > 450:
                            new_rate = element['rating'] + 116 * (element['result'] - 0.107)
                            print(new_rate)
                        elif 450 >= result > 475:
                            new_rate = element['rating'] + 116 * (element['result'] - 0.095)
                            print(new_rate)
                        elif 475 >= result > 500:
                            new_rate = element['rating'] + 116 * (element['result'] - 0.085)
                            print(new_rate)
                        elif 500 >= result:
                            new_rate = element['rating'] + 116 * (element['result'] - 0.076)
                            print(new_rate)




            except:
                pass
