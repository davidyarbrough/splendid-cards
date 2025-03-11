import unittest
import sys
import os
import io
from unittest.mock import patch, MagicMock

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.views.game_view import print_game_state, print_end_game_summary
from src.views.card_view import print_card_row, print_card_details
from src.utils.common import Color


class TestGameView(unittest.TestCase):
    """Test the game view functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock GameState
        self.mock_game_state = MagicMock()
        
        # Configure mock game state
        self.mock_game_state.seed = 12345
        self.mock_game_state.tokens = {
            Color.WHITE: 5,
            Color.BLUE: 4,
            Color.BLACK: 3,
            Color.RED: 2,
            Color.GREEN: 1,
            Color.GOLD: 5
        }
        self.mock_game_state.available_tiles = [1, 2, 3]
        self.mock_game_state.level1_river = [10, 11, 12, 13]
        self.mock_game_state.level2_river = [20, 21, 22, 23]
        self.mock_game_state.level3_river = [30, 31, 32, 33]
        
        # Mock players
        player1 = MagicMock()
        player1.tokens = {
            Color.WHITE: 1,
            Color.BLUE: 2,
            Color.BLACK: 0,
            Color.RED: 0,
            Color.GREEN: 0,
            Color.GOLD: 0
        }
        player1.cards = {
            Color.WHITE: [],
            Color.BLUE: [101],
            Color.BLACK: [],
            Color.RED: [],
            Color.GREEN: []
        }
        player1.reserved_cards = [201]
        
        player2 = MagicMock()
        player2.tokens = {
            Color.WHITE: 0,
            Color.BLUE: 0,
            Color.BLACK: 3,
            Color.RED: 1,
            Color.GREEN: 0,
            Color.GOLD: 0
        }
        player2.cards = {
            Color.WHITE: [],
            Color.BLUE: [],
            Color.BLACK: [],
            Color.RED: [102],
            Color.GREEN: [103]
        }
        player2.reserved_cards = []
        
        self.mock_game_state.players = [player1, player2]
        self.mock_game_state.calculate_player_points.side_effect = [3, 5]  # Player 1 has 3 points, Player 2 has 5
        
        # Create mock agents
        self.mock_agents = [MagicMock(), MagicMock()]
        self.mock_agents[0].name = "TestAgent1"
        self.mock_agents[1].name = "TestAgent2"

    def test_print_game_state(self):
        """Test the print_game_state function."""
        # Instead of patching imports, directly patch the module-level functions
        # This approach may work better in scenarios where import patching fails
        with patch('src.views.game_view.print_card_row') as mock_print_card_row, \
             patch('src.views.game_view.print_card_details') as mock_print_card_details, \
             patch('sys.stdout', new=io.StringIO()) as fake_stdout:
             
            # Configure mocks
            mock_print_card_row.return_value = None
            mock_print_card_details.return_value = None
            
            # Call the function we're testing
            print_game_state(self.mock_game_state, current_player=0, agents=self.mock_agents)
            
            # Check output contains key elements
            output = fake_stdout.getvalue()
            
            # Check game state header
            self.assertIn("Game State (Seed: 12345)", output)
            
            # Check tokens
            for color in [Color.WHITE, Color.BLUE, Color.BLACK, Color.RED, Color.GREEN, Color.GOLD]:
                self.assertIn(color.value.upper(), output)
            
            # Check tiles
            for tile in [1, 2, 3]:
                self.assertIn(str(tile), output)
            
            # Check player info
            self.assertIn("Player 1 (TestAgent1) (Current Turn)", output)
            self.assertIn("Player 2 (TestAgent2)", output)
            
            # Check points
            self.assertIn("Points: 3", output)
            self.assertIn("Points: 5", output)
            
            # The print_card_row function should be called 3 times (once for each level)
            self.assertEqual(mock_print_card_row.call_count, 3)
    
    def test_print_end_game_summary_single_winner(self):
        """Test the print_end_game_summary function with a single winner."""
        # Configure for a single winner
        self.mock_game_state.calculate_player_points.side_effect = [3, 5]  # Player 2 wins
        
        # Mock stdout to capture printed output
        with patch('sys.stdout', new=io.StringIO()) as fake_stdout:
            # Call the function
            print_end_game_summary(self.mock_game_state, self.mock_agents)
            
            # Check output
            output = fake_stdout.getvalue()
            
            # Check final scores
            self.assertIn("Final Scores:", output)
            self.assertIn("Player 1 (TestAgent1): 3 points", output)
            self.assertIn("Player 2 (TestAgent2): 5 points", output)
            
            # Check winner message
            self.assertIn("Player 2 (TestAgent2) wins with 5 points!", output)
    
    def test_print_end_game_summary_tie(self):
        """Test the print_end_game_summary function with a tie."""
        # Configure for a tie
        # Using side_effect with a list to return a different value for each call
        self.mock_game_state.calculate_player_points.side_effect = [5, 5]
        
        # Mock stdout to capture printed output
        with patch('sys.stdout', new=io.StringIO()) as fake_stdout:
            # Call the function
            print_end_game_summary(self.mock_game_state, self.mock_agents)
            
            # Check output
            output = fake_stdout.getvalue()
            
            # Check final scores
            self.assertIn("Final Scores:", output)
            self.assertIn("Player 1 (TestAgent1): 5 points", output)
            self.assertIn("Player 2 (TestAgent2): 5 points", output)
            
            # Check tie message
            self.assertIn("Tie game!", output)
            self.assertIn("Player 1 (TestAgent1), Player 2 (TestAgent2)", output)
            
            # Look for the tie message in a more flexible way
            self.assertTrue("tied with" in output and "points each!" in output)


if __name__ == '__main__':
    unittest.main()
