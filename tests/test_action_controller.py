import unittest
import sys
import os
import io
from unittest.mock import patch, MagicMock

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.controllers.action_controller import execute_action
from src.utils.common import Color


class TestActionController(unittest.TestCase):
    """Test the action controller functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock GameState
        self.mock_game_state = MagicMock()
        
        # Set up a player for testing
        player = MagicMock()
        player.reserved_cards = [100]  # Card 100 is reserved
        self.mock_game_state.players = [player]
        
        # Set up river for testing
        self.mock_game_state.level1_river = [10, 11, 12]
        self.mock_game_state.level2_river = [20, 21, 22]
        self.mock_game_state.level3_river = [30, 31, 32]
    
    def test_execute_take_tokens_action(self):
        """Test executing a take_tokens action."""
        # Set up the action
        action = {
            "action": "take_tokens",
            "colors": [Color.WHITE, Color.BLUE]
        }
        
        # Mock stdout to capture printed output
        with patch('sys.stdout', new=io.StringIO()) as fake_stdout:
            # Execute the action
            result = execute_action(self.mock_game_state, 0, action)
            
            # Verify the action was executed
            self.mock_game_state.take_tokens.assert_called_once_with(0, [Color.WHITE, Color.BLUE])
            self.assertTrue(result)
            
            # Check output
            output = fake_stdout.getvalue()
            self.assertIn("Player 1 takes tokens:", output)
            self.assertIn("WHT", output)
            self.assertIn("BLU", output)
    
    def test_execute_buy_card_from_river(self):
        """Test executing a buy_card action for a card in the river."""
        # Set up the action to buy a card from level 1 river
        action = {
            "action": "buy",
            "card_index": 10
        }
        
        # Configure mock return value
        self.mock_game_state.buy_card.return_value = None  # No tokens returned
        
        # Mock stdout to capture printed output
        with patch('sys.stdout', new=io.StringIO()) as fake_stdout:
            # Execute the action
            result = execute_action(self.mock_game_state, 0, action)
            
            # Verify the action was executed
            self.mock_game_state.buy_card.assert_called_once_with(0, 10)
            self.assertTrue(result)
            
            # Check output
            output = fake_stdout.getvalue()
            self.assertIn("Player 1 buys card 10 from level 1", output)
    
    def test_execute_buy_card_from_reserved(self):
        """Test executing a buy_card action for a reserved card."""
        # Set up the action to buy a reserved card
        action = {
            "action": "buy",
            "card_index": 100
        }
        
        # Configure mock return value for tokens returned
        returned_tokens = {Color.WHITE: 1, Color.BLUE: 2}
        self.mock_game_state.buy_card.return_value = returned_tokens
        
        # Mock stdout to capture printed output
        with patch('sys.stdout', new=io.StringIO()) as fake_stdout:
            # Execute the action
            result = execute_action(self.mock_game_state, 0, action)
            
            # Verify the action was executed
            self.mock_game_state.buy_card.assert_called_once_with(0, 100)
            self.assertTrue(result)
            
            # Check output
            output = fake_stdout.getvalue()
            self.assertIn("Player 1 buys card 100 from reserved cards", output)
            self.assertIn("returned tokens:", output)
    
    def test_execute_reserve_card_action(self):
        """Test executing a reserve_card action."""
        # Set up the action
        action = {
            "action": "reserve",
            "card_index": 20,
            "level": 2
        }
        
        # Configure mock return value for gold token
        self.mock_game_state.reserve_card.return_value = True  # Gold token taken
        
        # Mock stdout to capture printed output
        with patch('sys.stdout', new=io.StringIO()) as fake_stdout:
            # Execute the action
            result = execute_action(self.mock_game_state, 0, action)
            
            # Verify the action was executed
            self.mock_game_state.reserve_card.assert_called_once_with(0, 20)
            self.assertTrue(result)
            
            # Check output
            output = fake_stdout.getvalue()
            self.assertIn("Player 1 reserves card 20 from level 2", output)
            self.assertIn("took a gold token", output)
    
    def test_execute_reserve_card_without_gold(self):
        """Test executing a reserve_card action without getting a gold token."""
        # Set up the action
        action = {
            "action": "reserve",
            "card_index": 20,
            "level": 2
        }
        
        # Configure mock return value for gold token
        self.mock_game_state.reserve_card.return_value = False  # No gold token taken
        
        # Mock stdout to capture printed output
        with patch('sys.stdout', new=io.StringIO()) as fake_stdout:
            # Execute the action
            result = execute_action(self.mock_game_state, 0, action)
            
            # Verify the action was executed
            self.mock_game_state.reserve_card.assert_called_once_with(0, 20)
            self.assertTrue(result)
            
            # Check output
            output = fake_stdout.getvalue()
            self.assertIn("Player 1 reserves card 20 from level 2", output)
            self.assertNotIn("took a gold token", output)
    
    def test_execute_unknown_action(self):
        """Test executing an unknown action type."""
        # Set up an invalid action
        action = {
            "action": "unknown_action"
        }
        
        # Mock stdout to capture printed output
        with patch('sys.stdout', new=io.StringIO()) as fake_stdout:
            # Execute the action
            result = execute_action(self.mock_game_state, 0, action)
            
            # Verify the action failed
            self.assertFalse(result)
            
            # Check output
            output = fake_stdout.getvalue()
            self.assertIn("Unknown action type:", output)
    
    def test_execute_action_with_error(self):
        """Test error handling when executing an action."""
        # Set up the action
        action = {
            "action": "take_tokens",
            "colors": [Color.WHITE, Color.BLUE]
        }
        
        # Configure mock to raise an exception
        self.mock_game_state.take_tokens.side_effect = Exception("Test error")
        
        # Mock stdout to capture printed output
        with patch('sys.stdout', new=io.StringIO()) as fake_stdout:
            # Execute the action
            result = execute_action(self.mock_game_state, 0, action)
            
            # Verify the action failed
            self.assertFalse(result)
            
            # Check output
            output = fake_stdout.getvalue()
            self.assertIn("Error executing action:", output)
            self.assertIn("Test error", output)


if __name__ == '__main__':
    unittest.main()
