"""Random agent implementation for Splendid Cards."""

import random
from src.agents.agent import Agent
from src.utils.common import Color


class RandomBuyer(Agent):
    """Agent that decides randomly from available legal actions.
    
    When a card can be purchased (distance 0), this agent randomly selects one to buy.
    Otherwise, it takes 3 tokens at random.
    """
    
    def __init__(self, name):
        """Initialize a RandomBuyer agent.
        
        Args:
            name: Name for this agent
        """
        super().__init__(name)
    
    def take_turn(self, game_state, player_index):
        """Decide action for this turn.
        
        Args:
            game_state: Current game state
            player_index: Index of this player in the game
            
        Returns:
            Action: The action to take
        """
        player = game_state.players[player_index]
        
        # First, check if player is eligible for any tiles
        eligible_tiles = game_state._check_tile_eligibility(player_index)
        if eligible_tiles:
            # Pick a random tile from eligible tiles (random strategy)
            random_tile = random.choice(eligible_tiles)
            
            # Claim the selected tile
            game_state.claim_tile(player_index, random_tile)
            return {
                "action": "claim_tile",
                "tile_index": random_tile
            }
        
        # Try to buy a random available card
        purchase_action = self._try_buy_random_card(game_state, player)
        if purchase_action:
            return purchase_action
        
        # If we can't buy a card, take 3 random tokens
        return self._take_random_tokens(game_state)
    
    def _try_buy_random_card(self, game_state, player):
        """Try to buy a random card that is immediately available.
        
        Args:
            game_state: Current game state
            player: Player making the decision
            
        Returns:
            BuyCardAction or None: Action to buy a card, or None if no card can be bought
        """
        affordable_cards = []
        
        # Check cards in the three rivers
        rivers = [game_state.level1_river, game_state.level2_river, game_state.level3_river]
        for level in range(3):
            for i, card_idx in enumerate(rivers[level]):
                if self._can_afford_card(card_idx, player, game_state):
                    affordable_cards.append((level, i, card_idx))
        
        # Check reserved cards
        for i, card_idx in enumerate(player.reserved_cards):
            if card_idx >= 0:  # Valid card index
                if self._can_afford_card(card_idx, player, game_state):
                    affordable_cards.append((-1, i, card_idx))  # -1 indicates reserved card
        
        # If there are affordable cards, randomly select one to buy
        if affordable_cards:
            level, position, card_idx = random.choice(affordable_cards)
            if level == -1:  # Reserved card
                return {
                    "action": "buy",
                    "card_index": card_idx,
                    "from_river": False,
                    "river_position": position
                }
            else:  # Card from river
                return {
                    "action": "buy",
                    "card_index": card_idx,
                    "from_river": True,
                    "river_level": level,
                    "river_position": position
                }
        
        return None
    
    def _can_afford_card(self, card_idx, player, game_state):
        """Check if player can afford to buy a card.
        
        Args:
            card_idx: Index of the card to check
            player: Player to check for
            game_state: Current game state
            
        Returns:
            bool: Whether player can afford this card
        """
        # Get the card cost from the game state
        card_cost = game_state.get_card_cost(card_idx)
        
        # Calculate color discounts from owned cards
        discounts = {}
        for color in Color:
            if color != Color.GOLD:  # Gold is not a discount color
                discounts[color] = len(player.cards.get(color, []))
        
        # Calculate how many tokens of each color we need after applying discounts
        needed_tokens = {}
        for color in Color:
            if color != Color.GOLD:
                needed = max(0, card_cost.get(color, 0) - discounts.get(color, 0))
                needed_tokens[color] = needed
        
        # Calculate how many gold tokens we need to use
        total_needed = sum(needed_tokens.values())
        available_without_gold = sum(min(needed_tokens.get(color, 0), player.tokens.get(color, 0)) 
                                    for color in Color if color != Color.GOLD)
        gold_needed = total_needed - available_without_gold
        
        # Check if we have enough tokens including gold
        return gold_needed <= player.tokens.get(Color.GOLD, 0)
    
    def _take_random_tokens(self, game_state):
        """Take 3 random tokens from those available.
        
        Args:
            game_state: Current game state
            
        Returns:
            TakeTokensAction: Action to take tokens
        """
        # Get all available non-GOLD token colors (those with at least 1 token)
        # GOLD tokens are special and cannot be taken directly
        standard_colors = [Color.WHITE, Color.BLUE, Color.BLACK, Color.RED, Color.GREEN]
        available_colors = [color for color in standard_colors 
                           if game_state.tokens.get(color, 0) > 0]
        
        # If there are less than 3 available colors, take all available
        if len(available_colors) <= 3:
            return {
                "action": "take_tokens",
                "colors": available_colors
            }
        
        # Otherwise, take 3 random colors
        selected_colors = random.sample(available_colors, 3)
        return {
            "action": "take_tokens",
            "colors": selected_colors
        }
