from django.test import TestCase
from main.business_logic.multiplayer_game import get_queue, get_turn, get_left_score, get_game_context, add_round, get_needed_rounds, get_ending_context, get_average_points, create_follow_up_game
from main.models import MultiplayerGame, MultiplayerRound
from main.models import MultiplayerPlayer
from main.utils import MultiplayerGameStatus
from django.contrib.auth.models import User


class MultiplayerGameTests(TestCase):
    
    def setUp(self):
        """Set up test data for each test method."""
        self.user1 = User.objects.create_user(username="testuser1", password="testpass")
        self.user2 = User.objects.create_user(username="testuser2", password="testpass")
        
    def create_game(self, score=100, max_players=1, online=True, status=MultiplayerGameStatus.PROGRESS.value, creator=None):
        """Helper method to create a multiplayer game with default values."""
        if creator is None:
            creator = self.user1
        return MultiplayerGame.objects.create(
            score=score,
            creator=creator,
            max_players=max_players,
            online=online,
            status=status,
            session=None,
        )
    
    def create_players(self, game: MultiplayerGame, num_players: int):
        """Helper method to create players for a game."""
        for i in range(1, num_players + 1):
            MultiplayerPlayer.objects.create(game=game, rank=i)
    
    def get_player(self, game: MultiplayerGame, rank: int):
        """Helper method to get a player by rank."""
        return MultiplayerPlayer.objects.get(game=game, rank=rank)
    
    def add_round_for_player(self, game: MultiplayerGame, rank: int, points: int):
        """Helper method to add a round for a specific player."""
        player = self.get_player(game, rank)
        return MultiplayerRound.objects.create(game=game, player=player, points=points)

    def test_get_turn(self):
        """Test that get_turn returns the correct player turn."""
        game = self.create_game(score=100, max_players=10)
        self.create_players(game, 10)
        
        for i in range(1, 11):
            self.assertEqual(get_turn(game), i)
            self.add_round_for_player(game, i, 100)
      
    def test_get_left_score_after_valid_round(self):
        """Test get_left_score calculation after adding rounds."""
        game = self.create_game(score=100, max_players=1)
        self.create_players(game, 1)
        player = self.get_player(game, 1)
        
        # go from 100 to 50 to 30 to 0
        self.assertEqual(get_left_score(game, player), 100)
        
        self.add_round_for_player(game, 1, 50)
        self.assertEqual(get_left_score(game, player), 50)
        
        self.add_round_for_player(game, 1, 20)
        self.assertEqual(get_left_score(game, player), 30)
        
        self.add_round_for_player(game, 1, 30)
        self.assertEqual(get_left_score(game, player), 0)


    def test_get_queue(self):
        """Test that get_queue returns the correct player queue order."""
        game = self.create_game(score=100, max_players=4)
        self.create_players(game, 4)
        
        que_round_map = {
            1: [2, 3, 4],
            2: [3, 4, 1],
            3: [4, 1, 2],
            4: [1, 2, 3],
            5: [2, 3, 4],
        }
        
        for i in range(1, 5):
            self.assertEqual(get_queue(game, i), que_round_map[i])
            self.add_round_for_player(game, i, 0)
    def test_get_game_context(self):
        """Test get_game_context returns correct game state and player information."""
        game = self.create_game(score=100, max_players=4)
        self.create_players(game, 4)
        
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
        self.add_round_for_player(game, 1, 50)
        
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
        self.add_round_for_player(game, 2, 30)
        self.add_round_for_player(game, 3, 40)
        self.add_round_for_player(game, 4, 25)
        
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
        """Test adding a valid round that doesn't end the game."""
        game = self.create_game(score=100, max_players=1)
        self.create_players(game, 1)
        player = self.get_player(game, 1)
        
        result = add_round(game, player, 50)
        
        self.assertEqual(result, False)
        self.assertEqual(game.status, MultiplayerGameStatus.PROGRESS.value)
        self.assertEqual(game.game_rounds.count(), 1)   
        self.assertEqual(game.game_rounds.get(player=player).points, 50)
    def test_add_round_checkout(self):
        """Test adding a round that wins the game (checkout)."""
        game = self.create_game(score=100, max_players=1)
        self.create_players(game, 1)
        player = self.get_player(game, 1)
        
        result = add_round(game, player, 100)
        
        self.assertEqual(result, True)
        self.assertEqual(game.status, MultiplayerGameStatus.FINISHED.value)
        self.assertEqual(game.winner, player)
        self.assertEqual(game.game_rounds.get(player=player).points, 100)

    def test_add_rounds_invalid_checkout(self):
        """Test adding a round with invalid checkout (169 is not valid)."""
        game = self.create_game(score=170, max_players=1)
        self.create_players(game, 1)
        player = self.get_player(game, 1)
        
        result = add_round(game, player, 169)
        
        self.assertEqual(result, False)
        self.assertEqual(game.status, MultiplayerGameStatus.PROGRESS.value)
        self.assertEqual(game.game_rounds.get(player=player).points, 0)

    def test_add_rounds_invalid_round(self):
        """Test adding rounds with invalid points (too high, negative)."""
        game = self.create_game(score=100, max_players=1)
        self.create_players(game, 1)
        player = self.get_player(game, 1)
        
        # Test points too high (>180)
        result1 = add_round(game, player, 181)
        self.assertEqual(result1, False)
        self.assertEqual(game.game_rounds.last().points, 0)

        # Test negative points
        result2 = add_round(game, player, -1)
        self.assertEqual(result2, False)
        self.assertEqual(game.game_rounds.last().points, 0)

    def test_get_average_points(self):
        """Test get_average_points calculation for a player."""
        game = self.create_game(score=100, max_players=1)
        self.create_players(game, 1)
        player = self.get_player(game, 1)
        
        self.add_round_for_player(game, 1, 50)
        self.assertEqual(get_average_points(game, player), 50)
        
        self.add_round_for_player(game, 1, 30)
        self.assertEqual(get_average_points(game, player), 40)

    def test_get_needed_rounds(self):
        """Test get_needed_rounds calculation for a player."""
        game = self.create_game(score=100, max_players=1)
        self.create_players(game, 1)
        player = self.get_player(game, 1)
        
        self.add_round_for_player(game, 1, 20)
        self.add_round_for_player(game, 1, 80)
        
        self.assertEqual(get_needed_rounds(game, player), 2)

    def test_get_ending_context(self):
        """Test get_ending_context returns correct game ending information."""
        game = self.create_game(score=140, max_players=1)
        self.create_players(game, 1)
        player = self.get_player(game, 1)
        
        game.status = MultiplayerGameStatus.PROGRESS.value
        game.winner = player
        game.save()
        
        self.add_round_for_player(game, 1, 90)
        self.add_round_for_player(game, 1, 50)
        
        context = get_ending_context(game)
        
        self.assertEqual(context["game"], game)
        self.assertEqual(context["winner"], player)
        self.assertEqual(context["winner_stats"]["average_points"], 70)
        self.assertEqual(context["winner_stats"]["needed_rounds"], 2)

    def test_create_follow_up_game(self):
        """Test create_follow_up_game creates a new game with rotated player order."""
        game = self.create_game(score=100, max_players=2, creator=self.user2, status=MultiplayerGameStatus.FINISHED.value)
        self.create_players(game, 2)
        
        original_player_1 = self.get_player(game, 1)
        original_player_2 = self.get_player(game, 2)
        
        new_game = create_follow_up_game(game)
        
        self.assertEqual(new_game.score, 100)
        self.assertEqual(new_game.creator, self.user2)
        self.assertEqual(new_game.max_players, 2)
        self.assertEqual(new_game.online, True)
        self.assertEqual(new_game.status, MultiplayerGameStatus.PROGRESS.value)
        self.assertEqual(new_game.session, None)
        self.assertEqual(new_game.game_players.count(), 2)
        
        # Players should be rotated: original rank 2 becomes rank 1, original rank 1 becomes rank 2
        new_player_1 = self.get_player(new_game, 1)
        new_player_2 = self.get_player(new_game, 2)
        
        self.assertEqual(new_player_1.player, original_player_2.player)
        self.assertEqual(new_player_2.player, original_player_1.player)
