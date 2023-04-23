import xmltodict
import json
from django.shortcuts import get_object_or_404
from .models import Game, Player, Country, Club, Tournament, PlayerInTournament


def handle_uploaded_file(thisFile):
    with open('uploads/files/' + str(thisFile).replace(' ', '_').replace(',', '').replace('(', '').replace(')',
                                                                                                           '')) as fd:
        doc = xmltodict.parse(fd.read())
        my_dict = doc['Tournament']
        for key, value in my_dict.items():
            if key == 'Name':
                tournament_name = value
        json_data = json.dumps(doc, indent=4)
    with open(f"uploads/json/{tournament_name}.json", 'w') as json_file:
        json_file.write(json_data)

    with open(f"uploads/json/{tournament_name}.json", 'w') as json_file:
        json_data = json.load(json_file)

    # my_dict = doc['Tournament']

    # # for tournament
    # for key, value in my_dict.items():
    #     if key == 'Name':
    #         tournament_name = value
    #     elif key == "NumberOfRounds":
    #         round_num = value
    #     elif key == "Boardsize":
    #         board_size = value
    #         try:
    #             tournament = Tournament.objects.get(name=tournament_name)
    #             return False
    #
    #         except Tournament.DoesNotExist:
    #             tournament = Tournament.objects.create(name=tournament_name,
    #                                                    rounds=round_num,
    #                                                    board_size=board_size)
    #
    #     # for country and clubs
    #     if key == 'Country':
    #         next_list = value
    #         for el in next_list:
    #             for k, v in el.items():
    #                 if k == 'InternetCode':
    #                     code = v
    #                     try:
    #                         Country.objects.get(country_code=code)
    #                     except:
    #                         Country.objects.create(country_code=code)
    #
    #                 elif k == 'Club':
    #                     list_of_clubs = v
    #                     for elem in list_of_clubs:
    #                         try:
    #                             name = elem.get("Name")
    #                             if name in ["Seng", "Sengoku", "Sengoku Go Club"]:
    #                                 name = "Sengoku Go Club"
    #                         except:
    #                             name = None
    #                         try:
    #                             EGDName = elem.get("EGDName")
    #                             if name == "Sengoku Go Club":
    #                                 EGDName = 'Seng'
    #                         except:
    #                             EGDName = None
    #                         try:
    #                             Club.objects.get(name=name, EGDName=EGDName)
    #                         except Club.DoesNotExist:
    #                             if name is not None:
    #                                 Club.objects.create(name=name, EGDName=EGDName)
    #
    #     # for players
    #     if key == 'IndividualParticipant':
    #         list_of_players = value
    #         for element in list_of_players:
    #             for k, v in element.items():
    #                 if k == "Id":
    #                     id_in_game = v
    #                 elif k == 'GoPlayer':
    #                     person = v
    #                     first_name = person.get('FirstName')
    #                     last_name = person.get('Surname')
    #                     GoLevel = person.get('GoLevel')
    #                     rating = person.get('Rating')
    #                     country_code = person.get('Country')
    #                     EgdPin = person.get('EgdPin')
    #                     country = get_object_or_404(Country, country_code=country_code)
    #                     club_name = person.get('Club')
    #                     if club_name in ["Seng", "Sengoku", "Sengoku Go Club"]:
    #                         club_name = "Sengoku Go Club"
    #                         club = get_object_or_404(Club, name=club_name)
    #                     elif not club_name:
    #                         club = None
    #                     else:
    #                         club = get_object_or_404(Club, name=club_name)
    #
    #                     try:
    #                         player = get_object_or_404(Player, last_name=last_name, first_name=first_name)
    #                         if club is not None:
    #                             club_id = club.pk
    #                             club.country = country
    #                             club.save()
    #                             clubs_list = [club_id]
    #                             if club_id not in player.clubs.all():
    #                                 player.clubs.set(clubs_list)
    #                         if country != player.country:
    #                             player.country = country
    #                             player.save()
    #                         if EgdPin != 0 and player.EgdPin == 0:
    #                             player.EgdPin = EgdPin
    #                             player.save()
    #                             PlayerInTournament.objects.create(game_id=id_in_game,
    #                                                               player=player,
    #                                                               tournament=tournament,
    #                                                               GoLevel=GoLevel,
    #                                                               rating=rating,
    #                                                               club=club)
    #
    #                         elif (EgdPin != 0 and player.EgdPin == EgdPin) or (
    #                                 EgdPin == 0 and player.EgdPin == EgdPin):
    #                             PlayerInTournament.objects.create(game_id=id_in_game,
    #                                                               player=player,
    #                                                               tournament=tournament,
    #                                                               GoLevel=GoLevel,
    #                                                               rating=rating,
    #                                                               club=club)
    #
    #                         elif player.EgdPin != EgdPin != 0:
    #                             new_player = Player.objects.create(first_name=first_name,
    #                                                                last_name=last_name,
    #                                                                country=country,
    #                                                                EgdPin=EgdPin)
    #                             if club is not None:
    #                                 club_id = club.pk
    #                                 club.country = country
    #                                 club.save()
    #                                 clubs_list = [club_id]
    #                                 if club_id not in player.clubs.all():
    #                                     player.clubs.set(clubs_list)
    #                                 PlayerInTournament.objects.create(game_id=id_in_game,
    #                                                                   player=new_player,
    #                                                                   tournament=tournament,
    #                                                                   GoLevel=GoLevel,
    #                                                                   rating=rating,
    #                                                                   club=club)
    #
    #                     except:
    #                         new_player = Player.objects.create(first_name=first_name,
    #                                                            last_name=last_name,
    #                                                            country=country,
    #                                                            EgdPin=EgdPin)
    #                         if club is not None:
    #                             club_id = club.pk
    #                             club.country = country
    #                             club.save()
    #                             clubs_list = [club_id]
    #                             if club_id not in new_player.clubs.all():
    #                                 new_player.clubs.set(clubs_list)
    #                         PlayerInTournament.objects.create(game_id=id_in_game,
    #                                                           player=new_player,
    #                                                           tournament=tournament,
    #                                                           GoLevel=GoLevel,
    #                                                           rating=rating,
    #                                                           club=club)
    #
    #     # for game
    #     if key == "TournamentRound":
    #         list_of_elements = value
    #         for element in list_of_elements:
    #             for k, v in element.items():
    #                 if k == "RoundNumber":
    #                     round_number = v
    #                 elif k == "Pairing":
    #                     list_of_pairing = v
    #                     try:
    #                         for pair in list_of_pairing:
    #                             black_id = pair.get("Black")
    #                             white_id = pair.get('White')
    #                             result = pair.get('Result')
    #                             board_num = pair.get('BoardNumber')
    #                             date = pair.get("CreationTime")
    #
    #                             if white_id:
    #                                 white_player = get_object_or_404(PlayerInTournament, game_id=white_id,
    #                                                                  tournament=tournament)
    #                                 white = white_player.player
    #                             else:
    #                                 white = None
    #                             if black_id:
    #                                 black_player = get_object_or_404(PlayerInTournament, game_id=black_id,
    #                                                                  tournament=tournament)
    #                                 black = black_player.player
    #                             else:
    #                                 black = None
    #                             if result == '1-0':
    #                                 black_score = 1
    #                                 white_score = 0
    #                             elif result == '0-1':
    #                                 black_score = 0
    #                                 white_score = 1
    #                             elif result == '0-0':
    #                                 black_score = 0.5
    #                                 white_score = 0.5
    #                             else:
    #                                 black_score = None
    #                                 white_score = None
    #                             try:
    #                                 game = get_object_or_404(Game, black=black, white=white, result=result,
    #                                                          board_number=board_num, date=date, round_num=round_number,
    #                                                          tournament=tournament, black_score=black_score,
    #                                                          white_score=white_score)
    #                             except:
    #                                 Game.objects.create(black=black, white=white, result=result,
    #                                                     board_number=board_num, date=date, round_num=round_number,
    #                                                     tournament=tournament, black_score=black_score,
    #                                                     white_score=white_score)
    #                     except:
    #                         black_id = v.get("Black")
    #                         white_id = v.get('White')
    #                         result = v.get('Result')
    #                         board_num = v.get('BoardNumber')
    #                         date = v.get("CreationTime")
    #
    #                         if white_id:
    #                             white_player = get_object_or_404(PlayerInTournament, game_id=white_id,
    #                                                              tournament=tournament)
    #                             white = white_player.player
    #                         else:
    #                             white = None
    #                         if black_id:
    #                             black_player = get_object_or_404(PlayerInTournament, game_id=black_id,
    #                                                              tournament=tournament)
    #                             black = black_player.player
    #                         else:
    #                             black = None
    #                         if result == '1-0':
    #                             black_score = 1
    #                             white_score = 0
    #                         elif result == '0-1':
    #                             black_score = 0
    #                             white_score = 1
    #                         elif result == '0-0':
    #                             black_score = 0.5
    #                             white_score = 0.5
    #                         else:
    #                             black_score = None
    #                             white_score = None
    #                         try:
    #                             game = get_object_or_404(Game, black=black, white=white, result=result,
    #                                                      board_number=board_num, date=date, round_num=round_number,
    #                                                      tournament=tournament, black_score=black_score,
    #                                                      white_score=white_score)
    #                         except:
    #                             Game.objects.create(black=black, white=white, result=result,
    #                                                 board_number=board_num, date=date, round_num=round_number,
    #                                                 tournament=tournament, black_score=black_score,
    #                                                 white_score=white_score)
    #
    # return tournament
