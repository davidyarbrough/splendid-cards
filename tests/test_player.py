import unittest
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models.player import Player
from src.utils.common import Color


class TestPlayer(unittest.TestCase):
    """Test the Player class functionality."""
    
    def test_player_initialization(self):
        """Test that a player is initialized with correct default values."""
        # Test with default name
        player = Player()
        self.assertIsNone(player.name)
        
        # Test with custom name
        player_named = Player("TestPlayer")
        self.assertEqual(player_named.name, "TestPlayer")
        
        # Verify tokens are initialized to zero for all colors
        for color in Color:
            if color != Color.GOLD:  # All regular colors should have token counters
                self.assertEqual(player.tokens[color], 0)
                
        # Verify cards dictionaries are initialized as empty lists for all colors except GOLD
        for color in Color:
            if color != Color.GOLD:  # No cards of color GOLD
                self.assertEqual(player.cards[color], [])
                
        # Verify reserved cards and tiles start empty
        self.assertEqual(player.reserved_cards, [])
        self.assertEqual(player.tiles, [])
        
    def test_tokens_are_separate_objects(self):
        """Test that token dictionaries are separate objects for different players."""
        player1 = Player("Player1")
        player2 = Player("Player2")
        
        # Modify player1's tokens
        player1.tokens[Color.WHITE] = 3
        
        # Verify player2's tokens are unchanged
        self.assertEqual(player2.tokens[Color.WHITE], 0)
        
    def test_cards_are_separate_objects(self):
        """Test that card dictionaries are separate objects for different players."""
        player1 = Player("Player1")
        player2 = Player("Player2")
        
        # Add a card to player1
        player1.cards[Color.WHITE].append(42)
        
        # Verify player2's cards are unchanged
        self.assertEqual(player2.cards[Color.WHITE], [])


if __name__ == '__main__':
    unittest.main()
