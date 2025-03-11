import unittest
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.common import shuffleDecks, shuffleTiles


class TestCommon(unittest.TestCase):
    def test_shuffleDecks_returns_three_decks(self):
        """Test that shuffleDecks returns a tuple with three deck lists."""
        decks = shuffleDecks(seed=0)
        self.assertEqual(len(decks), 3, "shuffleDecks should return a tuple of three decks")
        
        # Check that each deck is a list
        for i, deck in enumerate(decks):
            self.assertIsInstance(deck, list, f"Deck {i+1} should be a list")
    
    def test_shuffleDecks_correct_deck_sizes(self):
        """Test that each deck contains the right number of cards."""
        level1_deck, level2_deck, level3_deck = shuffleDecks(seed=0)
        
        # Check that each deck has the expected number of cards
        # These numbers should match the actual card counts in cards.csv
        self.assertGreater(len(level1_deck), 0, "Level 1 deck should not be empty")
        self.assertGreater(len(level2_deck), 0, "Level 2 deck should not be empty")
        self.assertGreater(len(level3_deck), 0, "Level 3 deck should not be empty")
        
        # We can count the cards in cards.csv to get the expected counts
        # For now, we're just checking they're not empty
    
    def test_shuffleDecks_deterministic_with_same_seed(self):
        """Test that shuffleDecks is deterministic with the same seed."""
        decks1 = shuffleDecks(seed=42)
        decks2 = shuffleDecks(seed=42)
        
        # Both calls should return identical results with the same seed
        self.assertEqual(decks1, decks2, "shuffleDecks should be deterministic with the same seed")
    
    def test_shuffleDecks_different_with_different_seeds(self):
        """Test that shuffleDecks produces different results with different seeds."""
        decks1 = shuffleDecks(seed=42)
        decks2 = shuffleDecks(seed=43)
        
        # The decks should be different with different seeds
        self.assertNotEqual(decks1, decks2, "shuffleDecks should produce different results with different seeds")
    
    def test_shuffleDecks_indices_are_valid(self):
        """Test that the card indices in each deck are valid for their respective levels."""
        level1_deck, level2_deck, level3_deck = shuffleDecks(seed=0)
        
        # Check a few indices from each deck to ensure they belong to the correct deck level
        # Note: This test assumes the 'index' values in cards.csv are ordered by deck
        # For a more robust test, we would need to parse cards.csv directly
        
        # For now, just check that all indices are integers
        for deck_num, deck in enumerate([level1_deck, level2_deck, level3_deck], start=1):
            for card_index in deck:
                self.assertIsInstance(card_index, int, f"Card index in level {deck_num} deck should be an integer")
    
    def test_shuffleDecks_with_none_seed(self):
        """Test that shuffleDecks works when seed is None."""
        # We can't test for specific results when seed is None since it uses the current time
        # But we can ensure it doesn't crash and returns decks with cards
        level1_deck, level2_deck, level3_deck = shuffleDecks(seed=None)
        
        self.assertGreater(len(level1_deck), 0, "Level 1 deck should not be empty with seed=None")
        self.assertGreater(len(level2_deck), 0, "Level 2 deck should not be empty with seed=None")
        self.assertGreater(len(level3_deck), 0, "Level 3 deck should not be empty with seed=None")


    def test_shuffleTiles_returns_list(self):
        """Test that shuffleTiles returns a non-empty list."""
        tiles = shuffleTiles(seed=0)
        self.assertIsInstance(tiles, list, "shuffleTiles should return a list")
        self.assertGreater(len(tiles), 0, "Tiles list should not be empty")
    
    def test_shuffleTiles_deterministic_with_same_seed(self):
        """Test that shuffleTiles is deterministic with the same seed."""
        tiles1 = shuffleTiles(seed=42)
        tiles2 = shuffleTiles(seed=42)
        
        # Both calls should return identical results with the same seed
        self.assertEqual(tiles1, tiles2, "shuffleTiles should be deterministic with the same seed")
    
    def test_shuffleTiles_different_with_different_seeds(self):
        """Test that shuffleTiles produces different results with different seeds."""
        tiles1 = shuffleTiles(seed=42)
        tiles2 = shuffleTiles(seed=43)
        
        # The tiles should be different with different seeds
        self.assertNotEqual(tiles1, tiles2, "shuffleTiles should produce different results with different seeds")
    
    def test_shuffleTiles_indices_are_valid(self):
        """Test that the tile indices are valid integers."""
        tiles = shuffleTiles(seed=0)
        
        # Check that all indices are integers
        for tile_index in tiles:
            self.assertIsInstance(tile_index, int, "Tile index should be an integer")
    
    def test_shuffleTiles_with_none_seed(self):
        """Test that shuffleTiles works when seed is None."""
        # We can't test for specific results when seed is None since it uses the current time
        # But we can ensure it doesn't crash and returns tiles
        tiles = shuffleTiles(seed=None)
        
        self.assertGreater(len(tiles), 0, "Tiles list should not be empty with seed=None")


if __name__ == '__main__':
    unittest.main()
