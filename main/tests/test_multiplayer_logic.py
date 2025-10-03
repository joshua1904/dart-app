from django.test import TestCase
from main.business_logic.multiplayer_game import get_queue, get_turn, get_left_score, get_game_context, add_round, get_needed_rounds, get_ending_context, get_average_points, create_follow_up_game, get_wins
from main.models import MultiplayerGame, MultiplayerRound, MultiplayerPlayer, Session
from main.utils import MultiplayerGameStatus
from django.contrib.auth.models import User


class MultiplayerGameTests(TestCase):
    
    def setUp(self):
        """Set up test data for each test method."""
        self.user1 = User.objects.create_user(username="testuser1", password="testpass")
        self.user2 = User.objects.create_user(username="testuser2", password="testpass")
        
    def create_game(self, score=100, max_players=1, online=True, status=MultiplayerGameStatus.PROGRESS.value, creator=None, session=None):
        """Helper method to create a multiplayer game with default values."""
        if creator is None:
            creator = self.user1
        return MultiplayerGame.objects.create(
            score=score,
            creator=creator,
            max_players=max_players,
            online=online,
            status=status,
            session=session or Session.objects.create(),
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
        self.assertEqual(new_game.session, game.session)
        self.assertEqual(new_game.game_players.count(), 2)
        
        # Players should be rotated: original rank 2 becomes rank 1, original rank 1 becomes rank 2
        new_player_1 = self.get_player(new_game, 1)
        new_player_2 = self.get_player(new_game, 2)
        
        self.assertEqual(new_player_1.player, original_player_2.player)
        self.assertEqual(new_player_2.player, original_player_1.player)

    def test_get_wins_with_null_session(self):
        """Test get_wins returns 0 when session is None."""
        game = self.create_game(score=100, max_players=1)
        self.create_players(game, 1)
        player = self.get_player(game, 1)
        
        wins = get_wins(None, player)
        self.assertEqual(wins, 0)

    def test_get_wins_authenticated_user_no_wins(self):
        """Test get_wins returns 0 for authenticated user with no wins."""
        session = Session.objects.create()
        game = self.create_game(score=100, max_players=1, session=session)
        
        # Create player with authenticated user
        player = MultiplayerPlayer.objects.create(game=game, rank=1, player=self.user1)
        
        wins = get_wins(session, player)
        self.assertEqual(wins, 0)

    def test_get_wins_authenticated_user_with_wins(self):
        """Test get_wins returns correct count for authenticated user with wins."""
        session = Session.objects.create()
        
        # Create multiple games in the session
        game1 = self.create_game(score=100, max_players=2, session=session)
        game2 = self.create_game(score=100, max_players=2, session=session)
        game3 = self.create_game(score=100, max_players=2, session=session)
        
        # Create players for each game
        player1_game1 = MultiplayerPlayer.objects.create(game=game1, rank=1, player=self.user1)
        player2_game1 = MultiplayerPlayer.objects.create(game=game1, rank=2, player=self.user2)
        
        player1_game2 = MultiplayerPlayer.objects.create(game=game2, rank=1, player=self.user1)
        player2_game2 = MultiplayerPlayer.objects.create(game=game2, rank=2, player=self.user2)
        
        player1_game3 = MultiplayerPlayer.objects.create(game=game3, rank=1, player=self.user1)
        player2_game3 = MultiplayerPlayer.objects.create(game=game3, rank=2, player=self.user2)
        
        # Set winners: user1 wins game1 and game3, user2 wins game2
        game1.winner = player1_game1
        game1.save()
        
        game2.winner = player2_game2
        game2.save()
        
        game3.winner = player1_game3
        game3.save()
        
        # Test wins for user1 (should have 2 wins)
        wins_user1 = get_wins(session, player1_game1)
        self.assertEqual(wins_user1, 2)
        
        # Test wins for user2 (should have 1 win)
        wins_user2 = get_wins(session, player2_game1)
        self.assertEqual(wins_user2, 1)

    def test_get_wins_guest_player_no_wins(self):
        """Test get_wins returns 0 for guest player with no wins."""
        session = Session.objects.create()
        game = self.create_game(score=100, max_players=1, session=session)
        
        # Create guest player
        guest_player = MultiplayerPlayer.objects.create(game=game, rank=1, guest_name="GuestPlayer")
        
        wins = get_wins(session, guest_player)
        self.assertEqual(wins, 0)

    def test_get_wins_guest_player_with_wins(self):
        """Test get_wins returns correct count for guest player with wins."""
        session = Session.objects.create()
        
        # Create multiple games in the session
        game1 = self.create_game(score=100, max_players=2, session=session)
        game2 = self.create_game(score=100, max_players=2, session=session)
        game3 = self.create_game(score=100, max_players=2, session=session)
        
        # Create guest players for each game
        guest1_game1 = MultiplayerPlayer.objects.create(game=game1, rank=1, guest_name="Guest1")
        guest2_game1 = MultiplayerPlayer.objects.create(game=game1, rank=2, guest_name="Guest2")
        
        guest1_game2 = MultiplayerPlayer.objects.create(game=game2, rank=1, guest_name="Guest1")
        guest2_game2 = MultiplayerPlayer.objects.create(game=game2, rank=2, guest_name="Guest2")
        
        guest1_game3 = MultiplayerPlayer.objects.create(game=game3, rank=1, guest_name="Guest1")
        guest2_game3 = MultiplayerPlayer.objects.create(game=game3, rank=2, guest_name="Guest2")
        
        # Set winners: Guest1 wins game1 and game2, Guest2 wins game3
        game1.winner = guest1_game1
        game1.save()
        
        game2.winner = guest1_game2
        game2.save()
        
        game3.winner = guest2_game3
        game3.save()
        
        # Test wins for Guest1 (should have 2 wins)
        wins_guest1 = get_wins(session, guest1_game1)
        self.assertEqual(wins_guest1, 2)
        
        # Test wins for Guest2 (should have 1 win)
        wins_guest2 = get_wins(session, guest2_game1)
        self.assertEqual(wins_guest2, 1)

    def test_get_wins_mixed_players(self):
        """Test get_wins works correctly with mix of authenticated and guest players."""
        session = Session.objects.create()
        
        # Create games with mixed player types
        game1 = self.create_game(score=100, max_players=2, session=session)
        game2 = self.create_game(score=100, max_players=2, session=session)
        
        # Game 1: authenticated user vs guest
        auth_player_game1 = MultiplayerPlayer.objects.create(game=game1, rank=1, player=self.user1)
        guest_player_game1 = MultiplayerPlayer.objects.create(game=game1, rank=2, guest_name="TestGuest")
        
        # Game 2: same players
        auth_player_game2 = MultiplayerPlayer.objects.create(game=game2, rank=1, player=self.user1)
        guest_player_game2 = MultiplayerPlayer.objects.create(game=game2, rank=2, guest_name="TestGuest")
        
        # Set winners: authenticated user wins game1, guest wins game2
        game1.winner = auth_player_game1
        game1.save()
        
        game2.winner = guest_player_game2
        game2.save()
        
        # Test wins
        auth_wins = get_wins(session, auth_player_game1)
        guest_wins = get_wins(session, guest_player_game1)
        
        self.assertEqual(auth_wins, 1)
        self.assertEqual(guest_wins, 1)

    def test_get_game_context_includes_wins(self):
        """Test get_game_context includes wins information for all players."""
        session = Session.objects.create()
        
        # Create a game with session
        game = self.create_game(score=100, max_players=3, session=session)
        
        # Create players with different types
        auth_player = MultiplayerPlayer.objects.create(game=game, rank=1, player=self.user1)
        guest_player = MultiplayerPlayer.objects.create(game=game, rank=2, guest_name="TestGuest")
        auth_player2 = MultiplayerPlayer.objects.create(game=game, rank=3, player=self.user2)
        
        # Create previous games in the session to establish win history
        prev_game1 = self.create_game(score=100, max_players=2, session=session)
        prev_auth_player1 = MultiplayerPlayer.objects.create(game=prev_game1, rank=1, player=self.user1)
        prev_guest_player1 = MultiplayerPlayer.objects.create(game=prev_game1, rank=2, guest_name="TestGuest")
        prev_game1.winner = prev_auth_player1  # user1 wins
        prev_game1.save()
        
        prev_game2 = self.create_game(score=100, max_players=2, session=session)
        prev_auth_player2 = MultiplayerPlayer.objects.create(game=prev_game2, rank=1, player=self.user1)
        prev_guest_player2 = MultiplayerPlayer.objects.create(game=prev_game2, rank=2, guest_name="TestGuest")
        prev_game2.winner = prev_guest_player2  # guest wins
        prev_game2.save()
        
        prev_game3 = self.create_game(score=100, max_players=2, session=session)
        prev_auth_player3 = MultiplayerPlayer.objects.create(game=prev_game3, rank=1, player=self.user2)
        prev_guest_player3 = MultiplayerPlayer.objects.create(game=prev_game3, rank=2, guest_name="TestGuest")
        prev_game3.winner = prev_guest_player3  # guest wins again
        prev_game3.save()

        context = get_game_context(game)

        # Current turn is rank 1 (auth_player)
        self.assertEqual(context["wins"], 1)

        # Queue contains the other two players; verify their wins counts
        guest_in_queue = next(p for p in context["queue"] if p["player"].guest_name == "TestGuest")
        auth2_in_queue = next(p for p in context["queue"] if p["player"].player == self.user2)

        self.assertEqual(guest_in_queue["wins"], 2)
        self.assertEqual(auth2_in_queue["wins"], 0)
      
