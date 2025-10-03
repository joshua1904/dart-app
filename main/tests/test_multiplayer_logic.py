from django.test import TestCase
from main.business_logic.multiplayer_game import get_queue, get_turn, get_left_score, get_game_context, add_round, get_needed_rounds, get_ending_context, get_average_points, create_follow_up_game
from main.models import MultiplayerGame, MultiplayerRound
from main.models import MultiplayerPlayer
from main.utils import MultiplayerGameStatus
from django.contrib.auth.models import User


def create_players(game: MultiplayerGame, num_players: int):
    for i in range(1, num_players + 1):
        MultiplayerPlayer.objects.create(game=game, rank=i)

class ConstantsTests(TestCase):

    def test_get_turn(self):
        game = MultiplayerGame.objects.create(
            score=100,
            creator=User.objects.create(username="test"),
            max_players=10,
            online=True,
            status=MultiplayerGameStatus.PROGRESS.value,
            session=None,
        )
        create_players(game, 10)
        for i in range(1, 11):
            self.assertEqual(get_turn(game), i)
            MultiplayerRound.objects.create(game=game, player=MultiplayerPlayer.objects.get(rank=i), points=100)
      
    def test_get_left_score_after_valid_round(self):
        game = MultiplayerGame.objects.create(
            score=100,
            creator=User.objects.create(username="test"),
            max_players=1,
            online=True,
            status=MultiplayerGameStatus.PROGRESS.value,
            session=None,
        )
        create_players(game, 1)
        # go from 100 to 50 to 30 to 0
        self.assertEqual(get_left_score(game, MultiplayerPlayer.objects.get(rank=1)), 100)
        MultiplayerRound.objects.create(game=game, player=MultiplayerPlayer.objects.get(rank=1), points=50)
        self.assertEqual(get_left_score(game, MultiplayerPlayer.objects.get(rank=1)), 50)
        MultiplayerRound.objects.create(game=game, player=MultiplayerPlayer.objects.get(rank=1), points=20)
        self.assertEqual(get_left_score(game, MultiplayerPlayer.objects.get(rank=1)), 30)
        MultiplayerRound.objects.create(game=game, player=MultiplayerPlayer.objects.get(rank=1), points=30)
        self.assertEqual(get_left_score(game, MultiplayerPlayer.objects.get(rank=1)), 0)


    def test_get_queue(self):
        game = MultiplayerGame.objects.create(
            score=100,
            creator=User.objects.create(username="test"),
            max_players=4,
            online=True,
            status=MultiplayerGameStatus.PROGRESS.value,
            session=None,
        )
        create_players(game, 4)
        que_round_map = {
            1: [2, 3, 4],
            2: [3, 4, 1],
            3: [4, 1, 2],
            4: [1, 2, 3],
            5: [2, 3, 4],
        }
        for i in range(1, 5):
            self.assertEqual(get_queue(game, i), que_round_map[i])
            MultiplayerRound.objects.create(game=game, player=MultiplayerPlayer.objects.get(rank=i), points=0)
    def test_get_game_context(self):
        game = MultiplayerGame.objects.create(
            score=100,
            creator=User.objects.create(username="test"),
            max_players=4,
            online=True,
            status=MultiplayerGameStatus.PROGRESS.value,
            session=None,
        )
        create_players(game, 4)
        
        # Test initial context (turn 1, no rounds played yet)
        context = get_game_context(game)
        
        # Verify basic structure
        self.assertEqual(context["game"], game)
        self.assertEqual(context["turn"].rank, 1)
        self.assertEqual(context["left_score"], 100)
        self.assertEqual(context["checkout_suggestion"], "T20 D20")  # checkout for 100
        
        # Verify queue structure (should contain players 2, 3, 4 in order)
        self.assertEqual(len(context["queue"]), 3)
        self.assertEqual(context["queue"][0]["player"].rank, 2)
        self.assertEqual(context["queue"][1]["player"].rank, 3)
        self.assertEqual(context["queue"][2]["player"].rank, 4)
        
        # All players should start with full score
        for queue_player in context["queue"]:
            self.assertEqual(queue_player["left_score"], 100)
            self.assertEqual(queue_player["checkout_suggestion"], "T20 D20")
        
        # Add a round for player 1 and test turn 2
        MultiplayerRound.objects.create(game=game, player=MultiplayerPlayer.objects.get(rank=1), points=50)
        
        context = get_game_context(game)
        self.assertEqual(context["turn"].rank, 2)  # Should be player 2's turn
        self.assertEqual(context["left_score"], 100)  # Player 2 hasn't played yet
        
        # Queue should now be [3, 4, 1] for player 2's turn
        self.assertEqual(context["queue"][0]["player"].rank, 3)
        self.assertEqual(context["queue"][1]["player"].rank, 4)
        self.assertEqual(context["queue"][2]["player"].rank, 1)
        
        # Player 1 should have 50 points left in the queue
        player_1_in_queue = next(p for p in context["queue"] if p["player"].rank == 1)
        self.assertEqual(player_1_in_queue["left_score"], 50)
        self.assertEqual(player_1_in_queue["checkout_suggestion"], "S10 D20")  # checkout for 50
        
        # Test after all players have played one round
        MultiplayerRound.objects.create(game=game, player=MultiplayerPlayer.objects.get(rank=2), points=30)
        MultiplayerRound.objects.create(game=game, player=MultiplayerPlayer.objects.get(rank=3), points=40)
        MultiplayerRound.objects.create(game=game, player=MultiplayerPlayer.objects.get(rank=4), points=25)
        
        # Should be back to player 1's turn
        context = get_game_context(game)
        self.assertEqual(context["turn"].rank, 1)
        self.assertEqual(context["left_score"], 50)  # Player 1 has 50 left from previous round
        
        # Verify all players have correct scores in queue
        queue_scores = {p["player"].rank: p["left_score"] for p in context["queue"]}
        self.assertEqual(queue_scores[2], 70)  # 100 - 30
        self.assertEqual(queue_scores[3], 60)  # 100 - 40  
        self.assertEqual(queue_scores[4], 75)  # 100 - 25

    def test_add_round_valid_round(self):
        game = MultiplayerGame.objects.create(
            score=100,
            creator=User.objects.create(username="test"),
            max_players=1,
            online=True,
            status=MultiplayerGameStatus.PROGRESS.value,
            session=None,
        )
        create_players(game, 1)
        self.assertEqual(add_round(game, MultiplayerPlayer.objects.get(rank=1), 50), False)
        self.assertEqual(game.status, MultiplayerGameStatus.PROGRESS.value)
        self.assertEqual(game.game_rounds.count(), 1)   
        self.assertEqual(game.game_rounds.get(player=MultiplayerPlayer.objects.get(rank=1)).points, 50)
    def test_add_round_checkout(self):
        game = MultiplayerGame.objects.create(
            score=100,
            creator=User.objects.create(username="test"),
            max_players=1,
            online=True,
            status=MultiplayerGameStatus.PROGRESS.value,
            session=None,
        )
        create_players(game, 1) 
        self.assertEqual(add_round(game, MultiplayerPlayer.objects.get(rank=1), 100), True)
        self.assertEqual(game.status, MultiplayerGameStatus.FINISHED.value)
        self.assertEqual(game.winner, MultiplayerPlayer.objects.get(rank=1))
        self.assertEqual(game.game_rounds.get(player=MultiplayerPlayer.objects.get(rank=1)).points, 100)

    def test_add_rounds_invalid_checkout(self):
        game = MultiplayerGame.objects.create(
            score=170,
            creator=User.objects.create(username="test"),
            max_players=1,
            online=True,
            status=MultiplayerGameStatus.PROGRESS.value,
            session=None,
        )
        create_players(game, 1)     
        self.assertEqual(add_round(game, MultiplayerPlayer.objects.get(rank=1), 169), False)
        self.assertEqual(game.status, MultiplayerGameStatus.PROGRESS.value)
        self.assertEqual(game.game_rounds.get(player=MultiplayerPlayer.objects.get(rank=1)).points, 0)

    def test_add_rounds_invalid_round(self):
        game = MultiplayerGame.objects.create(
            score=100,
            creator=User.objects.create(username="test"),
            max_players=1,
            online=True,
            status=MultiplayerGameStatus.PROGRESS.value,
            session=None,
        )
        create_players(game, 1)     
        self.assertEqual(add_round(game, MultiplayerPlayer.objects.get(rank=1), 181), False)
        self.assertEqual(game.game_rounds.last().points, 0)

        self.assertEqual(add_round(game, MultiplayerPlayer.objects.get(rank=1), -1), False)
        self.assertEqual(game.game_rounds.last().points, 0)

    def test_get_average_points(self):
        game = MultiplayerGame.objects.create(
            score=100,
            creator=User.objects.create(username="test"),
            max_players=1,
            online=True,
            status=MultiplayerGameStatus.PROGRESS.value,
            session=None,
        )
        create_players(game, 1)     
        MultiplayerRound.objects.create(game=game, player=MultiplayerPlayer.objects.get(rank=1), points=50)
        self.assertEqual(get_average_points(game, MultiplayerPlayer.objects.get(rank=1)), 50)
        MultiplayerRound.objects.create(game=game, player=MultiplayerPlayer.objects.get(rank=1), points=30)
        self.assertEqual(get_average_points(game, MultiplayerPlayer.objects.get(rank=1)), 40)

    def test_get_needed_rounds(self):
        game = MultiplayerGame.objects.create(
            score=100,
            creator=User.objects.create(username="test"),
            max_players=1,
            online=True,
            status=MultiplayerGameStatus.PROGRESS.value,
            session=None,
        )
        create_players(game, 1)     
        MultiplayerRound.objects.create(game=game, player=MultiplayerPlayer.objects.get(rank=1), points=20)
        MultiplayerRound.objects.create(game=game, player=MultiplayerPlayer.objects.get(rank=1), points=80)
        self.assertEqual(get_needed_rounds(game, MultiplayerPlayer.objects.get(rank=1)), 2)

    def test_get_ending_context(self):
        game = MultiplayerGame.objects.create(
            score=140,
            creator=User.objects.create(username="test"),
            max_players=1,
            online=True,
            status=MultiplayerGameStatus.PROGRESS.value,
            session=None,
        )
        create_players(game, 1)  
        game.status = MultiplayerGameStatus.PROGRESS.value
        game.winner = MultiplayerPlayer.objects.get(rank=1)
        game.save()
        MultiplayerRound.objects.create(game=game, player=MultiplayerPlayer.objects.get(rank=1), points=90)
        MultiplayerRound.objects.create(game=game, player=MultiplayerPlayer.objects.get(rank=1), points=50)
        self.assertEqual(get_ending_context(game)["game"], game)
        self.assertEqual(get_ending_context(game)["winner"], MultiplayerPlayer.objects.get(rank=1))
        self.assertEqual(get_ending_context(game)["winner_stats"]["average_points"], 70)
        self.assertEqual(get_ending_context(game)["winner_stats"]["needed_rounds"], 2)

    def test_create_follow_up_game(self):
        creator = User.objects.create(username="test_follow_up")
        game = MultiplayerGame.objects.create(
            score=100,
            creator=creator,
            max_players=2,
            online=True,
            status=MultiplayerGameStatus.FINISHED.value,
            session=None,
        )
        create_players(game, 2)
        new_game = create_follow_up_game(game)
        self.assertEqual(new_game.score, 100)
        self.assertEqual(new_game.creator, creator)
        self.assertEqual(new_game.max_players, 2)
        self.assertEqual(new_game.online, True)
        self.assertEqual(new_game.status, MultiplayerGameStatus.PROGRESS.value)
        self.assertEqual(new_game.session, None)
        self.assertEqual(new_game.game_players.count(), 2)
        self.assertEqual(new_game.game_players.get(game=new_game, rank=1).player, MultiplayerPlayer.objects.get(game=game, rank=2).player)
        self.assertEqual(new_game.game_players.get(game=new_game, rank=2).player, MultiplayerPlayer.objects.get(game=game, rank=1).player)