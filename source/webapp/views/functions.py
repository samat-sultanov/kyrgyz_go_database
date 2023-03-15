import re
from webapp.models import Country, Player, Tournament


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


def get_rank():
    players = Player.objects.all()
    tournaments = Tournament.objects.order_by("date")
    new_list = []
    for player in players:
        new_dict = dict()
        for tournament in tournaments:
            for data in tournament.playerintournament_set.all():
                if player.pk == data.player_id:
                    if player not in new_dict:
                        new_dict['player'] = player
                        new_dict['GoLevel'] = data.GoLevel
        new_list.append(new_dict)
    return new_list


def sorted_list_of_players(data, key_word, key_reverse):
    new_list = []
    for el in data:
        new_dict = dict()
        for key, value in el.items():
            if key == "GoLevel" and value.endswith(key_word):
                new_dict['player'] = el['player']
                new_dict['GoLevel'] = el['GoLevel']
                new_dict['position'] = int(el['GoLevel'][:-1])
                new_list.append(new_dict)
    result = sorted(new_list, key=get_element_to_sort, reverse=key_reverse)
    return result


def get_element_to_sort(x):
    return x['position']


def sorted_list(data, key_word, reverse):
    new_list = []
    for el in data:
        new_dict = dict()
        if el.GoLevel.endswith(key_word):
            new_dict['player'] = el.player
            new_dict['GoLevel'] = el.GoLevel
            new_dict['position'] = int(el.GoLevel[:-1])
            new_list.append(new_dict)
    result = sorted(new_list, key=get_element_to_sort, reverse=reverse)
    return result

