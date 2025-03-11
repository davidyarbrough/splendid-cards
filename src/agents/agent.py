"""Base class for all Splendid Cards agents."""
import sys
import os

# Add the project root directory to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
from abc import ABC, abstractmethod

class Agent(ABC):
    """Abstract base class that all agents must implement."""
    
    def __init__(self, name=None):
        """Initialize the agent with an optional name."""
        self.name = name or self.__class__.__name__
    
    @abstractmethod
    def take_turn(self, game_state, player_index):
        """
        Determine the action to take given the current game state.
        
        Args:
            game_state: Current state of the game
            player_index: Index of the player this agent is controlling
            
        Returns:
            action: A dictionary representing the action to take
        """
        pass
    
    def __str__(self):
        return self.name
