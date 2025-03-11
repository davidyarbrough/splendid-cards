import unittest
import sys
import os
from unittest.mock import MagicMock

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agents.agent import Agent
from src.agents.greedy_buyer import GreedyBuyer
from src.agents.random_buyer import RandomBuyer
from src.agents.stingy_buyer import StingyBuyer
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
    
    def test_random_buyer_agent(self):
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
        
        # Mock cards in the rivers
        game_state.card_rivers = [
            [101, 102],  # Level 1 river
            [203],       # Level 2 river
            [304, 305]   # Level 3 river
        ]
        
        # Create mock cards with different costs
        # Some are affordable, some are not
        mock_cards = {
            101: {'white_cost': 1, 'blue_cost': 1, 'black_cost': 0, 'red_cost': 0, 'green_cost': 0, 'points': 1},
            102: {'white_cost': 5, 'blue_cost': 0, 'black_cost': 0, 'red_cost': 0, 'green_cost': 0, 'points': 2},
            203: {'white_cost': 2, 'blue_cost': 2, 'black_cost': 0, 'red_cost': 0, 'green_cost': 0, 'points': 3},
            304: {'white_cost': 3, 'blue_cost': 3, 'black_cost': 0, 'red_cost': 0, 'green_cost': 0, 'points': 4},
            305: {'white_cost': 1, 'blue_cost': 1, 'black_cost': 1, 'red_cost': 1, 'green_cost': 1, 'points': 5}
        }
        game_state.cards = mock_cards
        
        # Set up token pool with available colors
        game_state.token_pool = {
            Color.WHITE: 4,
            Color.BLUE: 4,
            Color.BLACK: 4,
            Color.RED: 4,
            Color.GREEN: 4,
            Color.GOLD: 5
        }
        
        # Create the RandomBuyer agent
        agent = RandomBuyer("TestRandomBuyer")
        
        # Since the agent makes random choices, we can't test the exact card or tokens it chooses
        # But we can test that it returns a valid action
        action = agent.take_turn(game_state, 0)
        
        # The agent should either buy a card or take tokens
        self.assertIn(action["action"], ["buy", "take_tokens"])
        
        # If the action is to buy a card, it should be one of the affordable ones
        if action["action"] == "buy":
            affordable_cards = [101, 203]  # Based on the mock cards and player tokens
            self.assertIn(action["card_index"], affordable_cards)
        
        # If the action is to take tokens, it should take exactly 3 colors
        # (or fewer if less than 3 are available)
        elif action["action"] == "take_tokens":
            self.assertLessEqual(len(action["colors"]), 3)
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


if __name__ == '__main__':
    unittest.main()
