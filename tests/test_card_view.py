import unittest
import sys
import os
import io
from unittest.mock import patch, MagicMock

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.views.card_view import format_card_compact, print_card_details, print_card_row
from src.utils.common import Color


class TestCardView(unittest.TestCase):
    """Test the card view functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock GameState
        self.mock_game_state = MagicMock()
        
        # Configure return values for the mock methods
        self.mock_game_state.get_card_color.return_value = Color.BLUE
        self.mock_game_state.get_card_points.return_value = 3
        self.mock_game_state.get_card_cost.return_value = {
            Color.WHITE: 2,
            Color.BLUE: 0,
            Color.BLACK: 1,
            Color.RED: 3,
            Color.GREEN: 0
        }

    def test_format_card_compact(self):
        """Test the format_card_compact function."""
        # Call the function
        result = format_card_compact(self.mock_game_state, 42)
        
        # Check that GameState methods were called with correct parameters
        self.mock_game_state.get_card_color.assert_called_with(42)
        self.mock_game_state.get_card_points.assert_called_with(42)
        self.mock_game_state.get_card_cost.assert_called_with(42)
        
        # Check that result contains key parts (ignoring ANSI color codes)
        self.assertIn("42", result)  # Card ID
        self.assertIn("BLU", result)  # Card color
        self.assertIn("3", result)   # Card points
        
        # Check for cost representations in the result
        for c, v in [("W", "2"), ("U", "0"), ("B", "1"), ("R", "3"), ("G", "0")]:
            self.assertIn(f"{c}{v}", result)
    
    def test_format_card_compact_different_card(self):
        """Test format_card_compact with a different card."""
        # Change mock behavior for a different card
        def get_card_color_red(card_idx):
            return Color.RED
            
        def get_card_points_2(card_idx):
            return 2
            
        def get_card_cost_even(card_idx):
            return {
                Color.WHITE: 1,
                Color.BLUE: 1,
                Color.BLACK: 1,
                Color.RED: 0,
                Color.GREEN: 1
            }
            
        self.mock_game_state.get_card_color = get_card_color_red
        self.mock_game_state.get_card_points = get_card_points_2
        self.mock_game_state.get_card_cost = get_card_cost_even
        
        # Call the function
        result = format_card_compact(self.mock_game_state, 24)
        
        # Check that result contains key parts (ignoring ANSI color codes)
        self.assertIn("24", result)  # Card ID
        self.assertIn("RED", result)  # Card color
        self.assertIn("2", result)   # Card points
        
        # Check for cost representations in the result
        for c, v in [("W", "1"), ("U", "1"), ("B", "1"), ("R", "0"), ("G", "1")]:
            self.assertIn(f"{c}{v}", result)
    
    def test_print_card_details(self):
        """Test the print_card_details function."""
        # Mock stdout to capture printed output
        with patch('sys.stdout', new=io.StringIO()) as fake_stdout:
            # Call the function
            print_card_details(self.mock_game_state, 42, False)
            
            # Check that output contains key parts (ignoring ANSI color codes)
            output = fake_stdout.getvalue()
            self.assertIn("42", output)
            self.assertIn("BLU", output)
            self.assertIn("3", output)
    
    def test_print_card_row_with_cards(self):
        """Test print_card_row with a non-empty river."""
        # Create a river of cards
        river = [10, 20, 30]
        
        # Mock stdout to capture printed output
        with patch('sys.stdout', new=io.StringIO()) as fake_stdout:
            # Call the function
            print_card_row(self.mock_game_state, river, False)
            
            # Check that output contains each card ID (ignoring ANSI color codes)
            output = fake_stdout.getvalue()
            for card_id in river:
                self.assertIn(str(card_id), output)
    
    def test_print_card_row_empty(self):
        """Test print_card_row with an empty river."""
        # Create an empty river
        river = []
        
        # Mock stdout to capture printed output
        with patch('sys.stdout', new=io.StringIO()) as fake_stdout:
            # Call the function
            print_card_row(self.mock_game_state, river, False)
            
            # Check that output contains empty message
            output = fake_stdout.getvalue()
            self.assertIn("(Empty)", output)


if __name__ == '__main__':
    unittest.main()
