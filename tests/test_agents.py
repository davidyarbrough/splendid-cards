import unittest
import sys
import os
from unittest.mock import MagicMock

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agents.agent import Agent
from src.agents.greedy_buyer import GreedyBuyer
# RandomAgent is not yet implemented
# StingyBuyer is not yet implemented
# from src.agents.stingy_buyer import StingyBuyer
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
    
    # Note: RandomAgent test removed as this class is not yet implemented
    
    # StingyBuyer test removed as this class is not yet implemented


if __name__ == '__main__':
    unittest.main()
