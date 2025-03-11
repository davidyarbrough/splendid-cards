"""
Value-based agent for Splendid Cards.

This agent uses a heuristic function to evaluate all possible moves and selects the one with the highest value.
"""

from src.agents.agent import Agent
from src.utils.common import Color

class ValueBuyer(Agent):
    """Agent that evaluates all possible moves using a heuristic function and selects the best one."""
    
    def __init__(self, name="ValueBuyer"):
        super().__init__(name)
    
    def take_turn(self, game_state, player_index):
        """Decide on the action for this turn using a value-based approach.
        
        Args:
            game_state: Current state of the game
            player_index: Index of the player this agent is controlling
            
        Returns:
            action: A dictionary with the chosen action
        """
        player = game_state.players[player_index]
        
        # Track the best action and its value
        best_action = None
        best_value = float('-inf')
        
        # 2. Evaluate buying cards from all levels and reserved cards
        all_cards = []
        all_cards.extend([(card_idx, 1) for card_idx in game_state.level1_river])
        all_cards.extend([(card_idx, 2) for card_idx in game_state.level2_river])
        all_cards.extend([(card_idx, 3) for card_idx in game_state.level3_river])
        all_cards.extend([(card_idx, 0) for card_idx in player.reserved_cards])  # Level 0 for reserved cards
        
        for card_idx, level in all_cards:
            if self._can_afford_card(game_state, player, card_idx):
                value = self._evaluate_card_purchase(game_state, player, card_idx)
                if value > best_value:
                    best_value = value
                    best_action = {
                        "action": "buy",
                        "card_index": card_idx,
                        "level": level
                    }
        
        # 3. Evaluate reserving cards
        if len(player.reserved_cards) < 3:  # Max 3 reserved cards allowed
            reservable_cards = []
            reservable_cards.extend([(card_idx, 1) for card_idx in game_state.level1_river])
            reservable_cards.extend([(card_idx, 2) for card_idx in game_state.level2_river])
            reservable_cards.extend([(card_idx, 3) for card_idx in game_state.level3_river])
            
            for card_idx, level in reservable_cards:
                value = self._evaluate_card_reservation(game_state, player, card_idx)
                if value > best_value:
                    best_value = value
                    best_action = {
                        "action": "reserve",
                        "card_index": card_idx,
                        "level": level
                    }
        
        # 4. Evaluate taking tokens
        # Generate all valid token combinations (1 of any color, 2 of the same color, or 3 different colors)
        token_options = self._generate_token_options(game_state)
        for tokens in token_options:
            value = self._evaluate_token_collection(game_state, player, tokens)
            if value > best_value:
                best_value = value
                best_action = {
                    "action": "take_tokens",
                    "colors": tokens
                }
        
        # If somehow no valid action was found, take a random token
        if best_action is None:
            default_colors = [color for color in [Color.WHITE, Color.BLUE, Color.BLACK, Color.RED, Color.GREEN] 
                             if game_state.tokens[color] > 0]
            if default_colors:
                return {
                    "action": "take_tokens",
                    "colors": [default_colors[0]]
                }
        
        return best_action
    

    
    def _evaluate_card_purchase(self, game_state, player, card_idx):
        """Evaluate the value of purchasing a specific card.
        
        Args:
            game_state: Current game state
            player: Player object
            card_idx: Index of the card to evaluate
            
        Returns:
            float: Value score for purchasing this card
        """
        card_color = game_state.get_card_color(card_idx)
        card_points = game_state.get_card_points(card_idx)
        card_cost = game_state.get_card_cost(card_idx)
        
        # Start with points value (each point is worth 10)
        value = card_points * 10
        
        # Add value for the card's color based on our strategy
        # More valuable if we don't have many cards of this color
        cards_of_color = len(player.cards.get(card_color, []))
        color_variety_bonus = max(0, 5 - cards_of_color)  # Up to 5 points for color diversity
        value += color_variety_bonus
        
        # Calculate how efficient this purchase is (points per token spent)
        total_cost = sum(card_cost.values())
        if total_cost > 0:
            efficiency = card_points / total_cost
            value += efficiency * 5  # Bonus for efficient purchases
        
        # Add significant value for cards that help with tile acquisition
        # Check each available tile and see if this card's color would contribute
        for tile_idx in game_state.available_tiles:
            tile_cost = game_state.get_tile_cost(tile_idx)
            if card_color in tile_cost:
                required_count = tile_cost[card_color]
                current_count = len(player.cards.get(card_color, []))
                
                # Higher bonus if this card would help complete a tile requirement
                if current_count < required_count:
                    # Calculate how much closer this card gets us to the requirement
                    progress_percentage = 1 / required_count
                    
                    # Check how close we are to completing all requirements for this tile
                    tile_completion = 0
                    for color, count in tile_cost.items():
                        owned = len(player.cards.get(color, []))
                        if color == card_color:  # Account for the card we're evaluating
                            owned += 1
                        tile_completion += min(1.0, owned / count)
                    
                    tile_completion = tile_completion / len(tile_cost)  # Average completion percentage
                    
                    # Check if this card would complete the color requirement
                    completes_requirement = (current_count + 1 >= required_count)
                    
                    # Bonus points - more if we're close to completing the tile
                    tile_points = game_state.get_tile_points(tile_idx)  # Usually 3 points
                    if completes_requirement:
                        # Substantially higher value if this completes a color requirement
                        value += 25 + (tile_points * 5)  # Very high priority
                    elif tile_completion >= 0.75:  # Very close to completing
                        value += 20  # High priority
                    elif tile_completion >= 0.5:  # Halfway there
                        value += 15
                    else:  # Early stages
                        value += 10
        
        return value
    
    def _evaluate_card_reservation(self, game_state, player, card_idx):
        """Evaluate the value of reserving a specific card.
        
        Args:
            game_state: Current game state
            player: Player object
            card_idx: Index of the card to evaluate
            
        Returns:
            float: Value score for reserving this card
        """
        # Reserving is generally less valuable than buying directly
        # But it can be good to secure high-value cards or get a gold token
        value = self._evaluate_card_purchase(game_state, player, card_idx) * 0.6  # 60% of purchase value
        
        # Extra value if we get a gold token
        if game_state.tokens.get(Color.GOLD, 0) > 0 and player.tokens.get(Color.GOLD, 0) < 5:
            value += 5
        
        # Reduced value if we already have many reserved cards
        if len(player.reserved_cards) >= 2:
            value -= 5
        
        return value
    
    def _evaluate_token_collection(self, game_state, player, tokens):
        """Evaluate the value of collecting a specific set of tokens.
        
        Args:
            game_state: Current game state
            player: Player object
            tokens: List of token colors to collect
            
        Returns:
            float: Value score for collecting these tokens
        """
        # Base value for taking tokens
        value = 5
        
        # Higher priority for reserved cards (they've already been invested in)
        reserved_value = 0
        for card_idx in player.reserved_cards:
            missing_tokens = self._calculate_missing_tokens(game_state, player, card_idx)
            card_points = game_state.get_card_points(card_idx)
            
            # Check how many of the missing tokens we're collecting for reserved cards
            reserved_helpful = 0
            for token in tokens:
                if token in missing_tokens and missing_tokens[token] > 0:
                    reserved_helpful += 1
                    # Higher value if collecting multiple of the same token type needed
                    if tokens.count(token) > 1 and missing_tokens[token] > 1:
                        reserved_helpful += 1  # Extra bonus for collecting duplicates we need
            
            # Substantial bonus for tokens that help with reserved cards
            # (scaled by the card's point value)
            if reserved_helpful > 0:
                reserved_value += reserved_helpful * 3 * max(1, card_points)
        
        value += reserved_value
        
        # Evaluate how these tokens help with future purchases (visible cards)
        future_cards = self._identify_target_cards(game_state, player)
        for card_idx in future_cards:
            # Skip reserved cards (already handled above)
            if card_idx in player.reserved_cards:
                continue
                
            missing_tokens = self._calculate_missing_tokens(game_state, player, card_idx)
            
            # Check how many of the missing tokens we're collecting
            helpful_tokens = 0
            for token in tokens:
                if token in missing_tokens and missing_tokens[token] > 0:
                    helpful_tokens += 1
            
            # Higher value if tokens directly help with purchasing target cards
            value += helpful_tokens * 2
        
        # Bonus for token diversity (only if not collecting for specific cards)
        if reserved_value == 0:
            unique_colors = len(set(tokens))
            if unique_colors == 3:  # Maximum diversity
                value += 3
        
        # Penalty for taking tokens when we already have many
        current_token_count = sum(player.tokens.values())
        if current_token_count > 7:  # Approaching the 10-token limit
            value -= 3
        
        return value
    
    def _generate_token_options(self, game_state):
        """Generate all valid token-taking options.
        
        Args:
            game_state: Current game state
            
        Returns:
            list: List of valid token combinations to take
        """
        options = []
        standard_colors = [Color.WHITE, Color.BLUE, Color.BLACK, Color.RED, Color.GREEN]
        
        # Option 1: Take 2 of the same color (if 4+ tokens available)
        for color in standard_colors:
            if game_state.tokens.get(color, 0) >= 4:
                options.append([color, color])
        
        # Option 2: Take 3 different colors
        for i, color1 in enumerate(standard_colors):
            if game_state.tokens.get(color1, 0) <= 0:
                continue
            for j, color2 in enumerate(standard_colors[i+1:], i+1):
                if game_state.tokens.get(color2, 0) <= 0:
                    continue
                for color3 in standard_colors[j+1:]:
                    if game_state.tokens.get(color3, 0) <= 0:
                        continue
                    options.append([color1, color2, color3])
        
        # Option 3: Take 1 of any color
        for color in standard_colors:
            if game_state.tokens.get(color, 0) > 0:
                options.append([color])
        
        return options
    
    def _can_afford_card(self, game_state, player, card_idx):
        """Check if player can afford a specific card.
        
        Args:
            game_state: Current game state
            player: Player object
            card_idx: Index of the card to evaluate
            
        Returns:
            bool: True if card can be afforded, False otherwise
        """
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
                # Need to use gold tokens
                gold_needed = required - available
                if gold_needed > remaining_gold:
                    return False  # Not enough gold tokens
                remaining_gold -= gold_needed
        
        return True
    
    def _calculate_missing_tokens(self, game_state, player, card_idx):
        """Calculate what tokens are still needed to purchase a card.
        
        Args:
            game_state: Current game state
            player: Player object
            card_idx: Index of the card to evaluate
            
        Returns:
            dict: Color -> amount of tokens needed
        """
        # Get card cost and player resources
        card_cost = game_state.get_card_cost(card_idx)
        
        # Calculate color discounts from owned cards
        discounts = {}
        for color in Color:
            if color != Color.GOLD:  # Gold is not a discount color
                discounts[color] = len(player.cards.get(color, []))
        
        # Calculate missing tokens
        missing = {}
        for color, amount in card_cost.items():
            # Apply discount from owned cards
            required = max(0, amount - discounts.get(color, 0))
            
            # Check how many tokens are missing
            available = player.tokens.get(color, 0)
            if required > available:
                missing[color] = required - available
        
        return missing
    
    def _identify_target_cards(self, game_state, player):
        """Identify cards that would be good targets for future purchase.
        
        Args:
            game_state: Current game state
            player: Player object
            
        Returns:
            list: List of card indices that are good targets
        """
        # Get all visible cards
        all_cards = []
        all_cards.extend(game_state.level1_river)
        all_cards.extend(game_state.level2_river)
        all_cards.extend(game_state.level3_river)
        all_cards.extend(player.reserved_cards)
        
        # Identify cards that are affordable or close to being affordable
        target_cards = []
        for card_idx in all_cards:
            # Always include reserved cards as targets
            if card_idx in player.reserved_cards:
                target_cards.append(card_idx)
                continue
                
            missing = self._calculate_missing_tokens(game_state, player, card_idx)
            
            # Card is a target if it requires 3 or fewer additional tokens
            if sum(missing.values()) <= 3:
                target_cards.append(card_idx)
        
        return target_cards
