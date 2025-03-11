# Greedy buyer will prefer the most expensive card they can afford. If none can be bought, it will get tokens to buy 
# the most expensive card it can afford next turn

from src.agents.agent import Agent
from src.common import Color

class GreedyBuyer(Agent):
    """Agent that implements a greedy strategy - always buy the most expensive card that is affordable."""
    
    def __init__(self, name="GreedyBuyer"):
        super().__init__(name)
    
    def take_turn(self, game_state, player_index):
        """Decide on the action for this turn.
        
        Args:
            game_state: Current state of the game
            player_index: Index of the player this agent is controlling
            
        Returns:
            action: A dictionary with the chosen action
        """
        player = game_state.players[player_index]
        
        # Try to buy the most expensive card possible
        purchase_action = self._try_buy_most_expensive_card(game_state, player)
        if purchase_action:
            return purchase_action
        
        # If no card can be purchased, collect tokens
        token_action = self._collect_tokens_for_expensive_card(game_state, player)
        if token_action:
            return token_action
        
        # If no other action is available, reserve a card
        return self._reserve_high_value_card(game_state, player)
    
    def _try_buy_most_expensive_card(self, game_state, player):
        """Attempt to buy the most expensive card available."""
        # Combine all visible cards from the rivers
        all_cards = []
        all_cards.extend([(card_idx, 1) for card_idx in game_state.level1_river])
        all_cards.extend([(card_idx, 2) for card_idx in game_state.level2_river])
        all_cards.extend([(card_idx, 3) for card_idx in game_state.level3_river])
        
        # Sort cards by total cost (most expensive first)
        def card_total_cost(card_info):
            card_idx, _ = card_info
            # Logic to calculate total cost of the card
            # This is a placeholder - actual implementation would get cost from cards.csv
            return sum(game_state.get_card_cost(card_idx).values())
        
        all_cards.sort(key=card_total_cost, reverse=True)
        
        # Check each card to see if the player can afford it
        for card_idx, level in all_cards:
            if self._can_afford_card(game_state, player, card_idx):
                return {
                    "action": "buy",
                    "card_index": card_idx,
                    "level": level
                }
        
        return None
    
    def _can_afford_card(self, game_state, player, card_idx):
        """Check if player can afford a specific card."""
        # Get card cost and player resources
        card_cost = game_state.get_card_cost(card_idx)
        
        # Calculate color discounts from owned cards
        discounts = {}
        for color in Color:
            if color != Color.GOLD:  # Gold is not a discount color
                discounts[color] = len(player.cards.get(color, []))
        
        # Check if player can afford the card with their tokens and discounts
        remaining_gold = player.tokens.get(Color.GOLD, 0)
        
        for color, amount in card_cost.items():
            # Apply discount from owned cards
            required = max(0, amount - discounts.get(color, 0))
            
            # Check if player has enough regular tokens
            available = player.tokens.get(color, 0)
            
            if available < required:
                # Not enough regular tokens, see if gold tokens can cover the difference
                gold_needed = required - available
                if remaining_gold < gold_needed:
                    return False  # Can't afford the card
                remaining_gold -= gold_needed
        
        return True
    
    def _collect_tokens_for_expensive_card(self, game_state, player):
        """Collect tokens that will help buy expensive cards."""
        # Find the most expensive card this player might buy next turn
        target_card_idx = self._find_next_expensive_card(game_state, player)
        
        if not target_card_idx:
            # No good card to aim for, collect diverse tokens
            return self._collect_diverse_tokens(game_state)
        
        # Get the cost of the target card
        card_cost = game_state.get_card_cost(target_card_idx)
        
        # Determine which tokens would be most helpful
        needed_colors = []
        for color, amount in card_cost.items():
            if amount > 0:
                # How many more tokens of this color are needed?
                discount = len(player.cards.get(color, []))
                have = player.tokens.get(color, 0)
                need = max(0, amount - discount - have)
                
                if need > 0 and game_state.tokens.get(color, 0) > 0:
                    needed_colors.append(color)
        
        # Take up to 3 tokens of different colors the player needs
        if len(needed_colors) > 0:
            take_colors = needed_colors[:min(3, len(needed_colors))]
            return {
                "action": "take_tokens",
                "colors": take_colors
            }
        
        # If no specific colors are needed, collect diverse tokens
        return self._collect_diverse_tokens(game_state)
    
    def _find_next_expensive_card(self, game_state, player):
        """Find the most expensive card that the player could potentially afford soon."""
        # This is a simplified placeholder
        # A more sophisticated implementation would evaluate which cards 
        # could be purchased with a few more tokens
        all_cards = []
        all_cards.extend(game_state.level1_river)
        all_cards.extend(game_state.level2_river)
        all_cards.extend(game_state.level3_river)
        
        if not all_cards:
            return None
            
        # Just return the first card as a placeholder
        return all_cards[0]
    
    def _collect_diverse_tokens(self, game_state):
        """Collect a diverse set of tokens."""
        available_colors = []
        
        for color in Color:
            if color != Color.GOLD and game_state.tokens.get(color, 0) > 0:
                available_colors.append(color)
        
        # Take up to 3 different tokens
        take_colors = available_colors[:min(3, len(available_colors))]
        
        if take_colors:
            return {
                "action": "take_tokens",
                "colors": take_colors
            }
        
        # If no tokens available, return a null action
        return {"action": "pass"}
    
    def _reserve_high_value_card(self, game_state, player):
        """Reserve a high-value card."""
        # Prefer level 3 cards if available
        if game_state.level3_river and len(game_state.level3_river) > 0:
            return {
                "action": "reserve",
                "card_index": game_state.level3_river[0],
                "level": 3
            }
        elif game_state.level2_river and len(game_state.level2_river) > 0:
            return {
                "action": "reserve",
                "card_index": game_state.level2_river[0],
                "level": 2
            }
        elif game_state.level1_river and len(game_state.level1_river) > 0:
            return {
                "action": "reserve",
                "card_index": game_state.level1_river[0],
                "level": 1
            }
        
        # If no cards available in rivers, pass
        return {"action": "pass"}
