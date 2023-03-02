import xmltodict
from django.shortcuts import get_object_or_404
from .models import Game, Player, Country, Club, Tournament, PlayerInTournament


def handle_uploaded_file(thisFile):
    with open('uploads/files/' + str(thisFile).replace(' ', '_').replace(',', '').replace('(', '').replace(')',
                                                                                                           '')) as fd:
        doc = xmltodict.parse(fd.read())
    my_dict = doc['Tournament']

    # for tournament
    for key, value in my_dict.items():
        # print(f'{k} {v}')
        if key == 'Name':
            tournament_name = value
        elif key == "NumberOfRounds":
            round_num = value
        elif key == "Boardsize":
            board_size = value
            try:
                tournament = get_object_or_404(Tournament, name=tournament_name)
            except:
                tournament = Tournament.objects.create(name=tournament_name, rounds=round_num, board_size=board_size)

        # for country and clubs
        if key == 'Country':
            next_list = value
            for el in next_list:
                for k, v in el.items():
                    if k == 'InternetCode':
                        code = v
                        try:
                            country = get_object_or_404(Country, country_code=code)
                        except:
                            Country.objects.create(country_code=code)

                    elif k == 'Club':
                        list_of_clubs = v
                        for elem in list_of_clubs:
                            # print(elem)
                            try:
                                name = elem.get("Name")
                                # print(name)
                            except:
                                name = None
                            try:
                                EGDName = elem.get("EGDName")
                            except:
                                EGDName = None
                            try:
                                club = get_object_or_404(Club, name=name, EGDName=EGDName)
                            except:
                                if name or EGDName:
                                    Club.objects.create(name=name, EGDName=EGDName)

        # for players
        if key == 'IndividualParticipant':
            list_of_players = value
            for element in list_of_players:
                for k, v in element.items():
                    if k == "Id":
                        id_in_game = v
                    elif k == 'GoPlayer':
                        person = v
                        first_name = person.get('FirstName')
                        last_name = person.get('Surname')
                        GoLevel = person.get('GoLevel')
                        rating = person.get('Rating')
                        country_code = person.get('Country')
                        country = get_object_or_404(Country, country_code=country_code)
                        club_name = person.get('Club')

                        try:
                            player = get_object_or_404(Player, last_name=last_name, first_name=first_name)

                            try:
                                player_in_tour = get_object_or_404(PlayerInTournament, game_id=id_in_game,
                                                                   player=player, tournament=tournament)
                            except:
                                PlayerInTournament.objects.create(game_id=id_in_game, player=player,
                                                                  tournament=tournament, GoLevel=GoLevel, rating=rating)
                            try:
                                club = get_object_or_404(Club, name=club_name)
                                club_id = club.pk
                                clubs_list = [club_id]
                                player.clubs.set(clubs_list)
                            except:
                                pass
                        except:
                            new_player = Player.objects.create(first_name=first_name,
                                                               last_name=last_name,
                                                               country=country)
                            try:
                                player_in_tour = get_object_or_404(PlayerInTournament, game_id=id_in_game,
                                                                   player=new_player, tournament=tournament)
                            except:
                                PlayerInTournament.objects.create(game_id=id_in_game, player=new_player,
                                                                  tournament=tournament, GoLevel=GoLevel, rating=rating)
                            try:
                                club = get_object_or_404(Club, name=club_name)
                                club_id = club.pk
                                clubs_list = [club_id]
                                new_player.clubs.set(clubs_list)
                            except:
                                pass

        # for game
        if key == "TournamentRound":
            list_of_elements = value
            for element in list_of_elements:
                for k, v in element.items():
                    if k == "RoundNumber":
                        round_number = v
                    elif k == "Pairing":
                        list_of_pairing = v
                        for pair in list_of_pairing:
                            black_id = pair.get("Black")
                            white_id = pair.get('White')
                            result = pair.get('Result')
                            board_num = pair.get('BoardNumber')
                            date = pair.get("CreationTime")

                            if white_id:
                                white_player = get_object_or_404(PlayerInTournament, game_id=white_id,
                                                                 tournament=tournament)
                                white = white_player.player
                            else:
                                white = None
                            if black_id:
                                black_player = get_object_or_404(PlayerInTournament, game_id=black_id,
                                                                 tournament=tournament)
                                black = black_player.player
                            else:
                                black = None
                            if result == '1-0':
                                black_score = 1
                                white_score = 0
                            elif result == '0-1':
                                black_score = 0
                                white_score = 1
                            else:
                                black_score = 0
                                white_score = 0
                            try:
                                game = get_object_or_404(Game, black=black, white=white, result=result,
                                                         board_number=board_num, date=date, round_num=round_number,
                                                         tournament=tournament, black_score=black_score,
                                                         white_score=white_score)
                            except:
                                Game.objects.create(black=black, white=white, result=result,
                                                    board_number=board_num, date=date, round_num=round_number,
                                                    tournament=tournament, black_score=black_score,
                                                    white_score=white_score)
