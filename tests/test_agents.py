import unittest
import sys
import os
from unittest.mock import MagicMock, patch

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agents.agent import Agent
from src.agents.greedy_buyer import GreedyBuyer
from src.agents.random_buyer import RandomBuyer
from src.agents.stingy_buyer import StingyBuyer
from src.agents.value_buyer import ValueBuyer
from src.utils.common import Color


class TestAgent(unittest.TestCase):
    """Test the base Agent class and its concrete implementations."""
    
    def test_agent_initialization(self):
        """Test agent initialization with and without a name."""
        # Creating a concrete subclass for testing the abstract base class
        class TestConcreteAgent(Agent):
            def take_turn(self, game_state, player_index):
                return {"action": "test"}
        
        # Test with default name
        agent = TestConcreteAgent()
        self.assertEqual(agent.name, "TestConcreteAgent")
        
        # Test with custom name
        agent_named = TestConcreteAgent("CustomName")
        self.assertEqual(agent_named.name, "CustomName")
        
        # Test string representation
        self.assertEqual(str(agent_named), "CustomName")
    
    def test_greedy_buyer_agent(self):
        """Test the GreedyBuyer agent implementation."""
        # Create a mock game state
        game_state = MagicMock()
        
        # Set up a mock player
        player = MagicMock()
        player.tokens = {
            Color.WHITE: 3,
            Color.BLUE: 2,
            Color.BLACK: 1,
            Color.RED: 0,
            Color.GREEN: 0,
            Color.GOLD: 0
        }
        game_state.players = [player]
        
        # Mock available cards that the player can afford
        # The agent should choose the highest point card it can afford
        
        # This card costs 3 WHITE which the player can afford, worth 2 points
        game_state.get_card_cost.side_effect = lambda card_idx: {
            101: {Color.WHITE: 3, Color.BLUE: 0, Color.BLACK: 0, Color.RED: 0, Color.GREEN: 0},
            102: {Color.WHITE: 2, Color.BLUE: 2, Color.BLACK: 0, Color.RED: 0, Color.GREEN: 0},
            103: {Color.WHITE: 1, Color.BLUE: 1, Color.BLACK: 1, Color.RED: 0, Color.GREEN: 0}
        }[card_idx]
        
        game_state.get_card_points.side_effect = lambda card_idx: {101: 2, 102: 1, 103: 3}[card_idx]
        
        # Set up card levels in rivers
        game_state.level1_river = [101]
        game_state.level2_river = [102]
        game_state.level3_river = [103]
        
        # Create agent and get action
        agent = GreedyBuyer()
        action = agent.take_turn(game_state, 0)
        
        # Greedy buyer should try to buy the most expensive card it can afford
        self.assertEqual(action["action"], "buy")
        self.assertEqual(action["card_index"], 102)
    
    @patch('src.agents.random_buyer.RandomBuyer._take_random_tokens')
    @patch('src.agents.random_buyer.RandomBuyer._try_buy_random_card')
    def test_random_buyer_agent(self, mock_buy, mock_tokens):
        """Test the RandomBuyer agent implementation."""
        # Create a mock game state
        game_state = MagicMock()
        
        # Set up a mock player
        player = MagicMock()
        player.tokens = {
            Color.WHITE: 3,
            Color.BLUE: 2,
            Color.BLACK: 1,
            Color.RED: 0,
            Color.GREEN: 0,
            Color.GOLD: 0
        }
        player.reserved_cards = []  # No reserved cards
        player.get_discount = lambda color: 0  # No discounts
        game_state.players = [player]
        
        # Set up to return an empty list of eligible tiles to avoid the IndexError
        game_state._check_tile_eligibility.return_value = []
        
        # Set up mock returns for buy and take tokens
        mock_buy.return_value = {"action": "buy", "card_index": 101}
        mock_tokens.return_value = {"action": "take_tokens", "colors": [Color.WHITE, Color.BLUE, Color.BLACK]}
        
        # Create the RandomBuyer agent
        agent = RandomBuyer("TestRandomBuyer")
        
        # First case: test buying a card
        mock_buy.return_value = {"action": "buy", "card_index": 101}
        action = agent.take_turn(game_state, 0)
        
        self.assertEqual(action["action"], "buy")
        self.assertEqual(action["card_index"], 101)
        
        # Second case: test taking tokens (when buying fails)
        mock_buy.return_value = None  # No cards to buy
        action = agent.take_turn(game_state, 0)
        
        self.assertEqual(action["action"], "take_tokens")
        self.assertEqual(len(action["colors"]), 3)
        for color in action["colors"]:
            self.assertIn(color, [Color.WHITE, Color.BLUE, Color.BLACK, Color.RED, Color.GREEN])
    
    def test_stingy_buyer_agent(self):
        """Test the StingyBuyer agent implementation."""
        # Create a mock game state
        game_state = MagicMock()
        
        # Set up a mock player
        player = MagicMock()
        player.tokens = {
            Color.WHITE: 3,
            Color.BLUE: 2,
            Color.BLACK: 1,
            Color.RED: 0,
            Color.GREEN: 0,
            Color.GOLD: 0
        }
        game_state.players = [player]
        
        # Mock available cards with different costs
        # Card 101: High cost (3 white) - 2 points
        # Card 102: Medium cost (2 white, 2 blue) - 1 point
        # Card 103: Low cost (1 white, 1 blue, 1 black) - 3 points
        game_state.get_card_cost.side_effect = lambda card_idx: {
            101: {Color.WHITE: 3, Color.BLUE: 0, Color.BLACK: 0, Color.RED: 0, Color.GREEN: 0},
            102: {Color.WHITE: 2, Color.BLUE: 2, Color.BLACK: 0, Color.RED: 0, Color.GREEN: 0},
            103: {Color.WHITE: 1, Color.BLUE: 1, Color.BLACK: 1, Color.RED: 0, Color.GREEN: 0}
        }[card_idx]
        
        game_state.get_card_points.side_effect = lambda card_idx: {101: 2, 102: 1, 103: 3}[card_idx]
        game_state.get_card_color.side_effect = lambda card_idx: {101: Color.WHITE, 102: Color.BLUE, 103: Color.BLACK}[card_idx]
        
        # Set up card levels in rivers
        game_state.level1_river = [101]
        game_state.level2_river = [102]
        game_state.level3_river = [103]
        
        # Create agent and get action
        agent = StingyBuyer()
        action = agent.take_turn(game_state, 0)
        
        # StingyBuyer should try to buy the cheapest card it can afford
        self.assertEqual(action["action"], "buy")
        self.assertEqual(action["card_index"], 103)  # Card 103 has the lowest total cost of 3


class TestValueBuyerAgent(unittest.TestCase):
    """Test the ValueBuyer agent implementation."""
    
    def test_card_evaluation_points(self):
        """Test that the ValueBuyer correctly values cards based on points."""
        # Create the agent
        agent = ValueBuyer("TestValueBuyer")
        
        # Create a mock game state
        game_state = MagicMock()
        player = MagicMock()
        player.cards = {}
        game_state.players = [player]
        game_state.available_tiles = []
        
        # Create two cards with different point values but same cost
        game_state.get_card_points.side_effect = lambda card_idx: {101: 3, 102: 1}[card_idx]
        game_state.get_card_color.side_effect = lambda card_idx: {101: Color.WHITE, 102: Color.WHITE}[card_idx]
        game_state.get_card_cost.side_effect = lambda card_idx: {
            101: {Color.WHITE: 2, Color.BLUE: 1, Color.BLACK: 0, Color.RED: 0, Color.GREEN: 0},
            102: {Color.WHITE: 2, Color.BLUE: 1, Color.BLACK: 0, Color.RED: 0, Color.GREEN: 0}
        }[card_idx]
        
        # Evaluate both cards
        value_high_points = agent._evaluate_card_purchase(game_state, player, 101)
        value_low_points = agent._evaluate_card_purchase(game_state, player, 102)
        
        # The higher point card should be valued significantly more
        self.assertGreater(value_high_points, value_low_points)
        self.assertGreaterEqual(value_high_points - value_low_points, 20)  # At least 2 points × 10 difference
    
    def test_card_evaluation_color_diversity(self):
        """Test that the ValueBuyer values color diversity."""
        # Create the agent
        agent = ValueBuyer("TestValueBuyer")
        
        # Create a mock game state
        game_state = MagicMock()
        player = MagicMock()
        game_state.players = [player]
        game_state.available_tiles = []
        
        # Player already has multiple white cards but no black cards
        player.cards = {
            Color.WHITE: [201, 202, 203],  # 3 white cards
            Color.BLACK: []                # 0 black cards
        }
        
        # Set up two cards with same points but different colors
        game_state.get_card_points.side_effect = lambda card_idx: {101: 1, 102: 1}[card_idx]
        game_state.get_card_color.side_effect = lambda card_idx: {101: Color.WHITE, 102: Color.BLACK}[card_idx]
        game_state.get_card_cost.side_effect = lambda card_idx: {
            101: {Color.WHITE: 1, Color.BLUE: 1, Color.BLACK: 0, Color.RED: 0, Color.GREEN: 0},
            102: {Color.WHITE: 1, Color.BLUE: 1, Color.BLACK: 0, Color.RED: 0, Color.GREEN: 0}
        }[card_idx]
        
        # Evaluate both cards
        value_common_color = agent._evaluate_card_purchase(game_state, player, 101)  # White (already has 3)
        value_rare_color = agent._evaluate_card_purchase(game_state, player, 102)    # Black (has 0)
        
        # The rare color should be valued more for diversity
        self.assertGreater(value_rare_color, value_common_color)
    
    def test_card_evaluation_tile_progress(self):
        """Test that the ValueBuyer prioritizes cards that help complete tiles."""
        # Create the agent
        agent = ValueBuyer("TestValueBuyer")
        
        # Create a mock game state with a tile that requires cards
        game_state = MagicMock()
        player = MagicMock()
        game_state.players = [player]
        
        # Tile requires 3 white and 2 black cards
        game_state.available_tiles = [901]
        game_state.get_tile_cost.return_value = {Color.WHITE: 3, Color.BLACK: 2}
        game_state.get_tile_points.return_value = 3
        
        # Player already has some cards toward the tile requirement
        player.cards = {
            Color.WHITE: [201, 202],  # 2 white cards (needs 1 more)
            Color.BLACK: []           # 0 black cards (needs 2 more)
        }
        
        # Set up two cards with same points and cost but different colors
        game_state.get_card_points.side_effect = lambda card_idx: {101: 0, 102: 0}[card_idx]  # Both 0 points
        game_state.get_card_color.side_effect = lambda card_idx: {101: Color.WHITE, 102: Color.BLACK}[card_idx]
        game_state.get_card_cost.side_effect = lambda card_idx: {
            101: {Color.RED: 1, Color.GREEN: 1},  # Same cost, different color
            102: {Color.RED: 1, Color.GREEN: 1}
        }[card_idx]
        
        # Evaluate both cards
        value_white_card = agent._evaluate_card_purchase(game_state, player, 101)  # Completes white requirement
        value_black_card = agent._evaluate_card_purchase(game_state, player, 102)  # First black card
        
        # Both cards should have elevated value due to tile progress
        self.assertGreater(value_white_card, 10)  # Base value would be near 0 (0 points)
        self.assertGreater(value_black_card, 5)   # Should have some value for tile progress
        
        # The white card should be valued more because it completes a requirement
        self.assertGreater(value_white_card, value_black_card)
    
    def test_token_collection_strategy(self):
        """Test that ValueBuyer prioritizes tokens needed for targeted purchases."""
        # Create the agent
        agent = ValueBuyer("TestValueBuyer")
        
        # Create a mock game state
        game_state = MagicMock()
        player = MagicMock()
        game_state.players = [player]
        game_state.available_tiles = []
        
        # Player has reserved a valuable card
        player.reserved_cards = [501]  # Card needs a lot of red tokens
        player.cards = {}
        player.tokens = {Color.RED: 1}  # Already has 1 red token
        
        # The reserved card needs 5 red tokens
        game_state.get_card_cost.side_effect = lambda card_idx: {
            501: {Color.RED: 5, Color.WHITE: 0, Color.BLUE: 0, Color.BLACK: 0, Color.GREEN: 0}
        }[card_idx]
        game_state.get_card_points.side_effect = lambda card_idx: {501: 3}[card_idx]
        
        # Set up available tokens
        game_state.tokens = {
            Color.RED: 4,
            Color.WHITE: 4,
            Color.BLUE: 4,
            Color.BLACK: 4,
            Color.GREEN: 4
        }
        
        # Evaluate token collections
        red_collection = [Color.RED, Color.RED]
        diverse_collection = [Color.WHITE, Color.BLUE, Color.BLACK]
        
        value_red = agent._evaluate_token_collection(game_state, player, red_collection)
        value_diverse = agent._evaluate_token_collection(game_state, player, diverse_collection)
        
        # Red tokens should be more valuable as they progress toward the reserved card
        self.assertGreater(value_red, value_diverse)
    
    def test_integrated_decision_making(self):
        """Test the complete decision-making process of ValueBuyer."""
        # Create a more complete game state with various options
        game_state = MagicMock()
        player = MagicMock()
        game_state.players = [player]
        
        # Player state
        player.tokens = {Color.WHITE: 2, Color.BLUE: 1, Color.RED: 1, Color.GREEN: 0, Color.BLACK: 0}
        player.cards = {Color.WHITE: [201], Color.BLACK: [202]}
        player.reserved_cards = []
        
        # Available cards in the rivers
        game_state.level1_river = [101, 102]  # Level 1 cards
        game_state.level2_river = [201]       # Level 2 card
        game_state.level3_river = [301]       # Level 3 card (high points)
        
        # Card properties
        game_state.get_card_points.side_effect = lambda card_idx: {
            101: 0,  # Level 1 cheap card
            102: 1,  # Level 1 card with 1 point
            201: 2,  # Level 2 card with 2 points
            301: 4   # Level 3 card with 4 points
        }[card_idx]
        
        game_state.get_card_color.side_effect = lambda card_idx: {
            101: Color.WHITE,
            102: Color.RED,
            201: Color.BLUE,
            301: Color.BLACK
        }[card_idx]
        
        game_state.get_card_cost.side_effect = lambda card_idx: {
            # Affordable cheap card
            101: {Color.WHITE: 2, Color.BLUE: 0, Color.BLACK: 0, Color.RED: 0, Color.GREEN: 0},
            # Affordable card with 1 point
            102: {Color.WHITE: 1, Color.BLUE: 1, Color.BLACK: 0, Color.RED: 0, Color.GREEN: 0},
            # Expensive card not currently affordable
            201: {Color.WHITE: 0, Color.BLUE: 0, Color.BLACK: 3, Color.RED: 2, Color.GREEN: 0},
            # Very expensive high-point card
            301: {Color.WHITE: 3, Color.BLUE: 3, Color.BLACK: 3, Color.RED: 3, Color.GREEN: 0}
        }[card_idx]
        
        # Available tokens
        game_state.tokens = {
            Color.WHITE: 4,
            Color.BLUE: 4,
            Color.BLACK: 4,
            Color.RED: 4,
            Color.GREEN: 4,
            Color.GOLD: 5
        }
        
        # Add a tile that requires 3 red cards
        game_state.available_tiles = [901]
        game_state.get_tile_cost.return_value = {Color.RED: 3}
        game_state.get_tile_points.return_value = 3
        game_state._check_tile_eligibility.return_value = []
        
        # Create ValueBuyer and get its decision
        agent = ValueBuyer()
        action = agent.take_turn(game_state, 0)
        
        # Since there are several valid strategies, we just verify it made a reasonable choice
        self.assertIn(action["action"], ["buy", "reserve", "take_tokens"])
        
        # If it chose to buy, it should pick card 102 (best value for immediate purchase)
        if action["action"] == "buy":
            self.assertEqual(action["card_index"], 102)
        
        # If it chose to reserve, it should pick the high-value card
        elif action["action"] == "reserve":
            self.assertEqual(action["card_index"], 301)
            self.assertEqual(action["level"], 3)
        
        # If it chose to take tokens, it should prioritize colors needed for valuable cards
        # or tile requirements (BLACK, RED)
        elif action["action"] == "take_tokens":
            self.assertTrue(any(color in [Color.BLACK, Color.RED] for color in action["colors"]))


if __name__ == '__main__':
    unittest.main()
