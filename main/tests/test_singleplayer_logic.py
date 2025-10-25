from django.test import TestCase
from django.contrib.auth.models import User
from main.business_logic.singleplayer_game import (
    get_game_context,
    get_left_points,
    add_round,
)
from main.models import Game, Round
from main.utils import GameStatus


class SingleplayerGameTests(TestCase):

    def setUp(self):
        """Set up test data for each test method."""
        self.user = User.objects.create_user(username="testuser", password="testpass")

    def create_game(self, score=501, rounds=20, status=GameStatus.PROGRESS.value):
        """Helper method to create a game with default values."""
        return Game.objects.create(
            score=score, rounds=rounds, status=status, player=self.user
        )

    def test_get_game_context_new_game(self):
        """Test get_game_context for a new game with no rounds."""
        game = self.create_game(score=501, rounds=20)

        context = get_game_context(game)

        self.assertEqual(context["game"], game)
        self.assertEqual(context["rounds"].count(), 0)
        self.assertEqual(context["round_count"], 0)
        self.assertEqual(context["current_score_left"], 501)
        self.assertEqual(context["checkout_suggestion"], None)  # No checkout for 501
        self.assertEqual(context["average_score"], 0)
        self.assertEqual(context["total_points_scored"], 0)

    def test_get_game_context_with_rounds(self):
        """Test get_game_context for a game with some rounds played."""
        game = self.create_game(score=501, rounds=20)

        # Add some rounds
        Round.objects.create(game=game, points=60)
        Round.objects.create(game=game, points=100)
        Round.objects.create(game=game, points=85)

        context = get_game_context(game)

        self.assertEqual(context["game"], game)
        self.assertEqual(context["rounds"].count(), 3)
        self.assertEqual(context["round_count"], 3)
        self.assertEqual(context["current_score_left"], 256)  # 501 - 245
        self.assertEqual(context["checkout_suggestion"], None)  # No checkout for 256
        self.assertEqual(
            context["average_score"], 81.7
        )  # 245 / 3 = 81.666... rounded to 81.7
        self.assertEqual(context["total_points_scored"], 245)

    def test_get_game_context_checkout_suggestion(self):
        """Test get_game_context when checkout suggestion is available."""
        game = self.create_game(score=501, rounds=20)

        # Add rounds to get to 100 points left (has checkout suggestion)
        Round.objects.create(game=game, points=401)

        context = get_game_context(game)

        self.assertEqual(context["current_score_left"], 100)
        self.assertEqual(context["checkout_suggestion"], "T20 D20")

    def test_get_left_points_new_game(self):
        """Test get_left_points for a new game."""
        game = self.create_game(score=501)

        left_points = get_left_points(game)

        self.assertEqual(left_points, 501)

    def test_get_left_points_with_rounds(self):
        """Test get_left_points after adding rounds."""
        game = self.create_game(score=501)

        Round.objects.create(game=game, points=60)
        self.assertEqual(get_left_points(game), 441)

        Round.objects.create(game=game, points=100)
        self.assertEqual(get_left_points(game), 341)

        Round.objects.create(game=game, points=85)
        self.assertEqual(get_left_points(game), 256)

    def test_add_round_valid_points(self):
        """Test adding a valid round that doesn't end the game."""
        game = self.create_game(score=501, rounds=20)

        status = add_round(game, 60)

        self.assertEqual(status, GameStatus.PROGRESS.value)
        self.assertEqual(game.status, GameStatus.PROGRESS.value)
        self.assertEqual(game.game_rounds.count(), 1)
        self.assertEqual(game.game_rounds.first().points, 60)
        self.assertEqual(get_left_points(game), 441)

    def test_add_round_winning_game(self):
        """Test adding a round that wins the game (reaches exactly 0)."""
        game = self.create_game(score=100, rounds=20)

        # Add a round that wins the game
        status = add_round(game, 100)

        # Refresh game from database
        game.refresh_from_db()

        self.assertEqual(status, GameStatus.WON.value)
        self.assertEqual(game.status, GameStatus.WON.value)
        self.assertEqual(game.game_rounds.count(), 1)
        self.assertEqual(game.game_rounds.first().points, 100)
        self.assertEqual(get_left_points(game), 0)

    def test_add_round_winning_with_valid_checkout(self):
        """Test winning with a valid checkout combination."""
        game = self.create_game(score=50, rounds=20)

        # 50 has a valid checkout (S10 D20)
        status = add_round(game, 50)

        game.refresh_from_db()

        self.assertEqual(status, GameStatus.WON.value)
        self.assertEqual(game.status, GameStatus.WON.value)
        self.assertEqual(get_left_points(game), 0)

    def test_add_round_losing_max_rounds(self):
        """Test losing the game by reaching maximum rounds."""
        game = self.create_game(score=501, rounds=3)

        # Add 3 rounds without winning
        add_round(game, 100)
        add_round(game, 100)
        status = add_round(game, 100)

        game.refresh_from_db()

        self.assertEqual(status, GameStatus.LOST.value)
        self.assertEqual(game.status, GameStatus.LOST.value)
        self.assertEqual(game.game_rounds.count(), 3)
        self.assertEqual(get_left_points(game), 201)  # 501 - 300

    def test_add_round_points_too_high(self):
        """Test adding points higher than 180 (should be capped at 180)."""
        game = self.create_game(score=501, rounds=20)

        status = add_round(game, 200)

        self.assertEqual(status, GameStatus.PROGRESS.value)
        self.assertEqual(game.game_rounds.first().points, 180)  # Capped at 180
        self.assertEqual(get_left_points(game), 321)  # 501 - 180

    def test_add_round_negative_points(self):
        """Test adding negative points (should be set to 0)."""
        game = self.create_game(score=501, rounds=20)

        status = add_round(game, -50)

        self.assertEqual(status, GameStatus.PROGRESS.value)
        self.assertEqual(game.game_rounds.first().points, 0)
        self.assertEqual(get_left_points(game), 501)  # No change

    def test_add_round_bust_scenario(self):
        """Test bust scenario (going below 0 or to 1)."""
        game = self.create_game(score=50, rounds=20)

        # Try to score 51 points (would go to -1, which is a bust)
        status = add_round(game, 51)

        self.assertEqual(status, GameStatus.PROGRESS.value)
        self.assertEqual(game.game_rounds.first().points, 0)  # Bust results in 0 points
        self.assertEqual(get_left_points(game), 50)  # Score unchanged

    def test_add_round_bust_to_one(self):
        """Test bust scenario when going to exactly 1 point."""
        game = self.create_game(score=50, rounds=20)

        # Try to score 49 points (would go to 1, which is a bust)
        status = add_round(game, 49)

        self.assertEqual(status, GameStatus.PROGRESS.value)
        self.assertEqual(game.game_rounds.first().points, 0)  # Bust results in 0 points
        self.assertEqual(get_left_points(game), 50)  # Score unchanged

    def test_add_round_invalid_checkout(self):
        """Test invalid checkout scenario (finishing on non-checkout number)."""
        game = self.create_game(score=169, rounds=20)

        # 169 is not a valid checkout (not in checkout_map)
        status = add_round(game, 169)

        self.assertEqual(status, GameStatus.PROGRESS.value)
        self.assertEqual(
            game.game_rounds.first().points, 0
        )  # Invalid checkout results in 0 points
        self.assertEqual(get_left_points(game), 169)  # Score unchanged

    def test_add_round_valid_checkout_edge_cases(self):
        """Test various valid checkout scenarios."""
        # Test checkout for 2 (D1)
        game = self.create_game(score=2, rounds=20)
        status = add_round(game, 2)
        game.refresh_from_db()
        self.assertEqual(status, GameStatus.WON.value)
        self.assertEqual(get_left_points(game), 0)

        # Test checkout for 170 (T20 T20 D25)
        game2 = self.create_game(score=170, rounds=20)
        status = add_round(game2, 170)
        game2.refresh_from_db()
        self.assertEqual(status, GameStatus.WON.value)
        self.assertEqual(get_left_points(game2), 0)

    def test_multiple_rounds_progression(self):
        """Test a complete game progression with multiple rounds."""
        game = self.create_game(score=301, rounds=10)

        # Round 1: 60 points
        status = add_round(game, 60)
        self.assertEqual(status, GameStatus.PROGRESS.value)
        self.assertEqual(get_left_points(game), 241)

        # Round 2: 100 points
        status = add_round(game, 100)
        self.assertEqual(status, GameStatus.PROGRESS.value)
        self.assertEqual(get_left_points(game), 141)

        # Round 3: 85 points
        status = add_round(game, 85)
        self.assertEqual(status, GameStatus.PROGRESS.value)
        self.assertEqual(get_left_points(game), 56)

        # Round 4: Bust attempt (57 points would go to -1)
        status = add_round(game, 57)
        self.assertEqual(status, GameStatus.PROGRESS.value)
        self.assertEqual(get_left_points(game), 56)  # No change due to bust

        # Round 5: Valid checkout (56 = T16 D4)
        status = add_round(game, 56)
        game.refresh_from_db()
        self.assertEqual(status, GameStatus.WON.value)
        self.assertEqual(get_left_points(game), 0)

        # Verify final game state
        self.assertEqual(game.game_rounds.count(), 5)
        self.assertEqual(game.status, GameStatus.WON.value)

    def test_game_context_average_calculation(self):
        """Test that average score calculation is correct with various scenarios."""
        game = self.create_game(score=501, rounds=20)

        # Add rounds with different point values
        Round.objects.create(game=game, points=60)
        Round.objects.create(game=game, points=100)
        Round.objects.create(game=game, points=0)  # Bust round
        Round.objects.create(game=game, points=85)

        context = get_game_context(game)

        # Average should be (60 + 100 + 0 + 85) / 4 = 61.25 rounded to 61.2
        self.assertEqual(context["average_score"], 61.2)
        self.assertEqual(context["total_points_scored"], 245)
        self.assertEqual(context["round_count"], 4)
