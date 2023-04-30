from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from accounts.models import User
from webapp.models import Game, Player, Country, Club, Tournament, PlayerInTournament, City
from webapp.views.functions import unpack_data_json_players


def unpack_tournament_to_bd(data):
    tournament_data = {
        'Name': 'name',
        'NumberOfRounds': 'rounds',
        'Boardsize': 'board_size',
        'tournament_class': 'tournament_class',
        'city': 'city',
        "regulations": "regulations",
        "uploaded_by": "uploaded_by",
        'date': 'date',
    }
    tournament_args = {}
    for key, value in data.items():
        if key == 'Tournament':
            pack = value
            for k, v in pack.items():
                if k in tournament_data:
                    tournament_args[tournament_data[k]] = v
                    try:
                        city = get_object_or_404(City, city=tournament_args['city'])
                        tournament_args['city'] = city
                    except:
                        city = None
                        tournament_args['city'] = city
                    try:
                        uploaded_by = get_object_or_404(User, username=tournament_args['uploaded_by'])
                        tournament_args['uploaded_by'] = uploaded_by
                    except:
                        uploaded_by = get_object_or_404(User, pk=1)
                        tournament_args['uploaded_by'] = uploaded_by
        try:
            existing_tournament = Tournament.objects.get(name=tournament_args['name'])
            raise ValidationError("Турнир с таким именем уже загружен в базу данных.")
        except Tournament.DoesNotExist:
            tournament = Tournament.objects.create(**tournament_args)
            return tournament.pk


def unpack_countries_clubs(data):
    my_dict = data['Tournament']
    new_list = []
    for key, value in my_dict.items():
        if key == 'Country':
            next_list = value
            for el in next_list:
                for k, v in el.items():
                    if k == 'InternetCode':
                        code = v
                        try:
                            Country.objects.get(country_code=code)
                        except:
                            Country.objects.create(country_code=code)


def unpack_players(data, pk):
    tournament = get_object_or_404(Tournament, pk=pk)
    list_of_players = unpack_data_json_players(data)

    for player in list_of_players:
        first_name = player.get('FirstName')
        last_name = player.get('Surname')
        GoLevel = player.get('GoLevel')
        rating = int(player.get('Rating'))
        country_code = player.get('Country')
        EgdPin = player.get('EgdPin')
        country = get_object_or_404(Country, country_code=country_code)
        club_name = player.get('Club')
        id_in_tournament = player.get('id_in_tournament')
        birth_date = player.get('birth_date')
        position = player.get('position')
        results = player.get('results')
        if birth_date == '':
            birth_date = None
        if club_name in ["Seng", "Sengoku", "Sengoku Go Club"]:
            club_name = "Sengoku Go Club"
            EGDName = 'Seng'
            try:
                club = Club.objects.get(name=club_name)
            except:
                club = Club.objects.create(name=club_name, EGDName=EGDName)
                club.country = country
                club.save()
        elif not club_name:
            club = None
        else:
            EGDName = None
            try:
                club = Club.objects.get(name=club_name)
            except:
                club = Club.objects.create(name=club_name, EGDName=EGDName)
                club.country = country
                club.save()
        try:
            player = get_object_or_404(Player, last_name=last_name, first_name=first_name)
            if country != player.country:
                player.country = country
                player.save()
            if club is not None:
                club_id = club.pk
                clubs_list = [club_id]
                if club_id not in player.clubs.all():
                    player.clubs.set(clubs_list)
            if EgdPin != 0 and player.EgdPin == 0:
                player.EgdPin = EgdPin
                player.save()
                PlayerInTournament.objects.create(game_id=id_in_tournament,
                                                  player=player,
                                                  tournament=tournament,
                                                  GoLevel=GoLevel,
                                                  rating=rating,
                                                  club=club,
                                                  position=position,
                                                  results=results)

            elif (EgdPin != 0 and player.EgdPin == EgdPin) or (EgdPin == 0 and player.EgdPin == EgdPin):
                PlayerInTournament.objects.create(game_id=id_in_tournament,
                                                  player=player,
                                                  tournament=tournament,
                                                  GoLevel=GoLevel,
                                                  rating=rating,
                                                  club=club,
                                                  position=position,
                                                  results=results)

            elif player.EgdPin != EgdPin != 0:
                new_player = Player.objects.create(first_name=first_name,
                                                   last_name=last_name,
                                                   country=country,
                                                   EgdPin=EgdPin,
                                                   birth_date=birth_date)
                if club is not None:
                    club_id = club.pk
                    clubs_list = [club_id]
                    if club_id not in player.clubs.all():
                        player.clubs.set(clubs_list)
                PlayerInTournament.objects.create(game_id=id_in_tournament,
                                                  player=new_player,
                                                  tournament=tournament,
                                                  GoLevel=GoLevel,
                                                  rating=rating,
                                                  club=club,
                                                  position=position,
                                                  results=results)
        except:
            new_player = Player.objects.create(first_name=first_name,
                                               last_name=last_name,
                                               country=country,
                                               EgdPin=EgdPin,
                                               birth_date=birth_date)
            if club is not None:
                club_id = club.pk
                clubs_list = [club_id]
                if club_id not in new_player.clubs.all():
                    new_player.clubs.set(clubs_list)
            PlayerInTournament.objects.create(game_id=id_in_tournament,
                                              player=new_player,
                                              tournament=tournament,
                                              GoLevel=GoLevel,
                                              rating=rating,
                                              club=club,
                                              position=position,
                                              results=results)


def unpack_games(data, pk):
    tournament = get_object_or_404(Tournament, pk=pk)
    my_dict = data['Tournament']
    for key, value in my_dict.items():
        if key == 'TournamentRound':
            list_of_elements = value
            for element in list_of_elements:
                for k, v in element.items():
                    if k == "RoundNumber":
                        round_number = v
                    elif k == "Pairing":
                        list_of_pairing = v
                        try:
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
                                elif result == '0-0':
                                    black_score = 0.5
                                    white_score = 0.5
                                else:
                                    black_score = None
                                    white_score = None
                                try:
                                    game = get_object_or_404(Game, black=black, white=white, result=result,
                                                             board_number=board_num, date=date, round_num=round_number,
                                                             tournament=tournament, black_score=black_score,
                                                             white_score=white_score)
                                    raise ValidationError("Данные игры уже были загружены в базу данных")
                                except:
                                    Game.objects.create(black=black, white=white, result=result,
                                                        board_number=board_num, date=date, round_num=round_number,
                                                        tournament=tournament, black_score=black_score,
                                                        white_score=white_score)
                        except:
                            black_id = v.get("Black")
                            white_id = v.get('White')
                            result = v.get('Result')
                            board_num = v.get('BoardNumber')
                            date = v.get("CreationTime")

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
                            elif result == '0-0':
                                black_score = 0.5
                                white_score = 0.5
                            else:
                                black_score = None
                                white_score = None
                            try:
                                game = get_object_or_404(Game, black=black, white=white, result=result,
                                                         board_number=board_num, date=date, round_num=round_number,
                                                         tournament=tournament, black_score=black_score,
                                                         white_score=white_score)
                                raise ValidationError("Данные игры уже были загружены в базу данных")
                            except:
                                Game.objects.create(black=black, white=white, result=result,
                                                    board_number=board_num, date=date, round_num=round_number,
                                                    tournament=tournament, black_score=black_score,
                                                    white_score=white_score)
