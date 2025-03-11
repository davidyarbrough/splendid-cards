# StingyBuyer will prefer the cheapest card they can afford. If none can be bought, it will get tokens to buy 
# the cheapest card it can afford next turn. It uses the same distance calculation as GreedyBuyer.

from src.agents.agent import Agent
from src.utils.common import Color

class StingyBuyer(Agent):
    """Agent that implements a stingy strategy - always buy the cheapest card that is affordable."""
    
    def __init__(self, name="StingyBuyer"):
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
        
        # First, check if player is eligible for any tiles
        eligible_tiles = game_state._check_tile_eligibility(player_index)
        if eligible_tiles:
            # Pick the tile with the lowest combined cost (stingy strategy)
            # In case of a tie, pick the one with the lowest index
            best_tile = None
            lowest_cost = float('inf')
            
            for tile_idx in eligible_tiles:
                tile_cost = game_state.get_tile_cost(tile_idx)
                total_cost = sum(tile_cost.values())
                
                if total_cost < lowest_cost or (total_cost == lowest_cost and tile_idx < best_tile):
                    lowest_cost = total_cost
                    best_tile = tile_idx
            
            # Claim the selected tile
            if best_tile is not None:
                game_state.claim_tile(player_index, best_tile)
                return {
                    "action": "claim_tile",
                    "tile_index": best_tile
                }
        
        # Try to buy the cheapest card possible
        purchase_action = self._try_buy_cheapest_card(game_state, player)
        if purchase_action:
            return purchase_action
        
        # If no card can be purchased, collect tokens
        token_action = self._collect_tokens_for_cheapest_card(game_state, player)
        if token_action:
            return token_action
        
        # If no other action is available, reserve a card
        return self._reserve_low_cost_card(game_state, player)
    
    def _try_buy_cheapest_card(self, game_state, player):
        """Attempt to buy the cheapest card available."""
        # Combine all visible cards from the rivers
        all_cards = []
        all_cards.extend([(card_idx, 1) for card_idx in game_state.level1_river])
        all_cards.extend([(card_idx, 2) for card_idx in game_state.level2_river])
        all_cards.extend([(card_idx, 3) for card_idx in game_state.level3_river])
        
        # Sort cards by total cost (cheapest first)
        # For cards with the same total cost, secondary sort by number of different colors needed (more diverse is better)
        # and then by points (higher points are better)
        def card_sort_key(card_info):
            card_idx, _ = card_info
            cost_dict = game_state.get_card_cost(card_idx)
            total_cost = sum(cost_dict.values())
            # Count how many different colors are needed (negative because we want more diversity)
            color_diversity = -len([c for c, amt in cost_dict.items() if amt > 0])
            # Points (negative because we want higher points)
            points = -game_state.get_card_points(card_idx)
            return (total_cost, color_diversity, points)
        
        all_cards.sort(key=card_sort_key)  # Sort by total cost, then diversity, then points
        
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
    
    def _collect_tokens_for_cheapest_card(self, game_state, player):
        """Collect tokens that will help buy cheap cards using optimal strategy."""
        # Find the best card to target based on purchase distance
        target_card_idx = self._find_next_cheapest_card(game_state, player)
        
        if not target_card_idx:
            # No good card to aim for, collect diverse tokens
            return self._collect_diverse_tokens(game_state)
        
        # Calculate what tokens we need for this card
        missing_tokens = self._calculate_missing_tokens(game_state, player, target_card_idx)
        
        # STRATEGY 1: If we can take 2 of the same color and that would be beneficial
        for color, amount in missing_tokens.items():
            if amount >= 2 and game_state.tokens.get(color, 0) >= 4:  # Bank needs 4+ for us to take 2
                return {
                    "action": "take_tokens",
                    "colors": [color, color]  # Take 2 of the same color
                }
        
        # STRATEGY 2: Take up to 3 different colors we need
        needed_colors = []
        for color, amount in missing_tokens.items():
            if amount > 0 and game_state.tokens.get(color, 0) > 0:
                needed_colors.append(color)
        
        if needed_colors:
            # Take up to 3 different colors
            take_colors = needed_colors[:min(3, len(needed_colors))]
            return {
                "action": "take_tokens",
                "colors": take_colors
            }
        
        # STRATEGY 3: If we can't get exactly what we need, collect diverse tokens
        return self._collect_diverse_tokens(game_state)
    
    def _calculate_purchase_distance(self, game_state, player, card_idx):
        """Calculate how many token-taking turns it would take to afford the card.
        
        Args:
            game_state: Current game state
            player: Player object
            card_idx: Index of the card to evaluate
            
        Returns:
            int: Purchase distance (0 if affordable now, 1+ for future turns, -1 if unreachable)
        """
        # If player can already afford this card, distance is 0
        if self._can_afford_card(game_state, player, card_idx):
            return 0
            
        # Calculate what tokens we need to purchase this card
        missing_tokens = self._calculate_missing_tokens(game_state, player, card_idx)
        
        # Calculate how many token-collection turns are needed
        # A player can collect either 3 different tokens or 2 of the same color per turn
        
        # If all tokens needed are of the same color and there are 1-2 of them, distance is 1
        # If there's only one color with missing tokens and the amount is 1 or 2
        missing_colors = [color for color, amount in missing_tokens.items() if amount > 0]
        if len(missing_colors) == 1 and missing_tokens[missing_colors[0]] <= 2:
            # Check if enough tokens exist in the bank
            if game_state.tokens.get(missing_colors[0], 0) >= missing_tokens[missing_colors[0]]:
                return 1
        
        # For multiple colors, we can take up to 3 different tokens per turn
        turns_needed = 0
        remaining_tokens = missing_tokens.copy()
        
        # While we still need tokens
        while any(amount > 0 for amount in remaining_tokens.values()):
            turns_needed += 1
            
            # Can we take 2 of the same color this turn?
            double_color_option = None
            for color, amount in remaining_tokens.items():
                if amount >= 2 and game_state.tokens.get(color, 0) >= 4:  # Need 4+ in bank to take 2
                    double_color_option = color
                    break
            
            if double_color_option:
                # Take 2 of this color
                remaining_tokens[double_color_option] -= 2
                continue
            
            # Take up to 3 different colors
            colors_this_turn = 0
            for color in list(remaining_tokens.keys()):
                if remaining_tokens[color] > 0 and game_state.tokens.get(color, 0) > 0:
                    remaining_tokens[color] -= 1
                    colors_this_turn += 1
                    if colors_this_turn == 3:
                        break
            
            # If we couldn't collect any tokens this turn, the card is unreachable
            if colors_this_turn == 0:
                return -1
            
            # Limit maximum turns to consider to prevent unreasonable plans
            if turns_needed > 5:  # Arbitrary limit
                return -1
        
        return turns_needed
            
    def _calculate_missing_tokens(self, game_state, player, card_idx):
        """Calculate what tokens are still needed to purchase a card.
        
        Returns:
            dict: Color -> amount of tokens needed
        """
        card_cost = game_state.get_card_cost(card_idx)
        missing = {}
        
        # Calculate effective cost after discounts from owned cards
        for color, amount in card_cost.items():
            discount = len(player.cards.get(color, []))
            effective_cost = max(0, amount - discount)
            
            # How many more tokens are needed?
            player_tokens = player.tokens.get(color, 0)
            still_needed = max(0, effective_cost - player_tokens)
            
            if still_needed > 0:
                missing[color] = still_needed
        
        # Gold tokens can substitute for any color, but allocate optimally
        gold_available = player.tokens.get(Color.GOLD, 0)
        if gold_available > 0 and missing:
            # Allocate gold to the most expensive colors first
            colors_by_need = sorted(missing.keys(), key=lambda c: missing[c], reverse=True)
            
            for color in colors_by_need:
                if gold_available > 0 and missing[color] > 0:
                    used = min(gold_available, missing[color])
                    missing[color] -= used
                    gold_available -= used
                    
                    # Remove color if fully satisfied
                    if missing[color] == 0:
                        del missing[color]
        
        return missing
        
    def _find_next_cheapest_card(self, game_state, player):
        """Find the cheapest card that the player could potentially afford soon."""
        # Get all visible cards with their levels
        all_cards = []
        all_cards.extend([(card_idx, 1) for card_idx in game_state.level1_river])
        all_cards.extend([(card_idx, 2) for card_idx in game_state.level2_river])
        all_cards.extend([(card_idx, 3) for card_idx in game_state.level3_river])
        
        if not all_cards:
            return None
        
        # Calculate purchase distance and total cost for each card
        card_metrics = []
        for card_idx, level in all_cards:
            distance = self._calculate_purchase_distance(game_state, player, card_idx)
            total_cost = sum(game_state.get_card_cost(card_idx).values())
            points = game_state.get_card_points(card_idx)  # Still consider points as a secondary factor
            
            # Only consider cards that are reachable
            if distance >= 0:
                card_metrics.append((card_idx, level, distance, total_cost, points))
        
        if not card_metrics:
            return None
            
        # Sort by: distance (ascending), cost (ascending), diversity (descending), points (descending)
        def sort_key(item):
            card_idx, level, distance, total_cost, points = item
            cost_dict = game_state.get_card_cost(card_idx)
            # Count how many different colors are needed (negative because we want more diversity)
            color_diversity = -len([c for c, amt in cost_dict.items() if amt > 0])
            return (distance, total_cost, color_diversity, -points)
            
        card_metrics.sort(key=sort_key)
        
        # Return the best card's index
        return card_metrics[0][0]
    
    def _collect_diverse_tokens(self, game_state):
        """Collect tokens using the most efficient strategy available."""
        # STRATEGY 1: Try to take 2 of the same color if there are 4+ in the bank
        for color in Color:
            if color != Color.GOLD and game_state.tokens.get(color, 0) >= 4:
                return {
                    "action": "take_tokens",
                    "colors": [color, color]
                }
        
        # STRATEGY 2: Take up to 3 different tokens
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
    
    def _reserve_low_cost_card(self, game_state, player):
        """Reserve a low-cost card."""
        # Get all visible cards
        all_cards = []
        if game_state.level1_river and len(game_state.level1_river) > 0:
            all_cards.extend([(card_idx, 1) for card_idx in game_state.level1_river])
        if game_state.level2_river and len(game_state.level2_river) > 0:
            all_cards.extend([(card_idx, 2) for card_idx in game_state.level2_river])
        if game_state.level3_river and len(game_state.level3_river) > 0:
            all_cards.extend([(card_idx, 3) for card_idx in game_state.level3_river])
            
        if not all_cards:
            return {"action": "pass"}
            
        # Sort by total cost (cheapest first)
        def card_cost(card_info):
            card_idx, _ = card_info
            return sum(game_state.get_card_cost(card_idx).values())
            
        all_cards.sort(key=card_cost)
        
        # Reserve the cheapest card
        card_idx, level = all_cards[0]
        return {
            "action": "reserve",
            "card_index": card_idx,
            "level": level
        }