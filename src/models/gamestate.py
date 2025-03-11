import random
from enum import Enum
import time
import sys
from src.common import Color, Token, Card, Tile, CardCost, shuffleDecks, shuffleTiles

class GameState:
    def __init__(self, players=4, seed=None):
        # Set up a seeded random generator for reproducibility
        if seed is None:
            seed = int(time.time())
        self.seed = seed
        self.rng = random.Random(seed)
        
        # Initialize players
        self.num_players = min(max(2, players), 4)  # Ensure players is between 2 and 4
        self.players = []
        
        # Create player objects
        from src.models.player import Player
        for i in range(self.num_players):
            self.players.append(Player(f"Player-{i+1}"))
        
        # Initialize and shuffle decks using the seeded RNG
        self.level1_deck, self.level2_deck, self.level3_deck = shuffleDecks(seed)
        
        # Initialize rivers (face-up cards)
        self.level1_river = []
        self.level2_river = []
        self.level3_river = []
        
        # Draw initial cards for rivers
        for _ in range(4):
            if self.level1_deck:
                self.level1_river.append(self.level1_deck.pop())
            if self.level2_deck:
                self.level2_river.append(self.level2_deck.pop())
            if self.level3_deck:
                self.level3_river.append(self.level3_deck.pop())
        
        # Initialize token pool based on player count
        self.tokens = self.initialize_tokens()
        
        # Initialize and select tiles
        self.available_tiles = self.initialize_tiles()
    
    def initialize_tokens(self):
        """Initialize the token pool based on the number of players."""
        token_count = {
            2: 4,  # 4 tokens per color for 2 players
            3: 5,  # 5 tokens per color for 3 players
            4: 7   # 7 tokens per color for 4 players
        }
        
        count = token_count[self.num_players]
        
        # Create token pool
        tokens = {
            Color.WHITE: count,
            Color.BLUE: count,
            Color.BLACK: count,
            Color.RED: count,
            Color.GREEN: count,
            Color.GOLD: 5  # Gold tokens are always 5, regardless of player count
        }
        
        return tokens
    
    def initialize_tiles(self):
        """Initialize and select tiles based on the number of players."""
        # Get shuffled tile indices using the same seed
        shuffled_tile_indices = shuffleTiles(self.seed)
        
        # Select num_players + 1 tiles
        return shuffled_tile_indices[:self.num_players + 1]
    
    def serialize(self):
        """Serialize the game state to be sent to agents."""
        return {
            "seed": self.seed,
            "tokens": {color.name: count for color, count in self.tokens.items()},
            "level1_river": self.level1_river,
            "level2_river": self.level2_river,
            "level3_river": self.level3_river,
            "available_tiles": self.available_tiles,
            "players": [self._serialize_player(i) for i in range(len(self.players))]
        }
    
    def _serialize_player(self, player_index):
        """Serialize a player's state."""
        player = self.players[player_index]
        return {
            "tokens": {color.name: count for color, count in player.tokens.items()},
            "cards": {color.name: cards for color, cards in player.cards.items() if cards},
            "reserved_cards": player.reserved_cards,
            "tiles": player.tiles,
            "points": self.calculate_player_points(player_index)
        }
    
    def is_game_over(self):
        """Check if the game is over (any player has reached 15 points)."""
        for i in range(len(self.players)):
            if self.calculate_player_points(i) >= 15:
                return True
        return False
    
    def calculate_player_points(self, player_index):
        """Calculate the total prestige points for a player.
        
        Args:
            player_index: Index of the player
            
        Returns:
            Total prestige points
        """
        player = self.players[player_index]
        
        # Points from cards
        card_points = 0
        for color, cards in player.cards.items():
            for card_idx in cards:
                card_points += self.get_card_points(card_idx)
        
        # Points from tiles
        tile_points = 0
        for tile_idx in player.tiles:
            tile_points += self.get_tile_points(tile_idx)
        
        return card_points + tile_points
    
    def get_card_cost(self, card_idx):
        """Get the cost of a card by its index.
        
        Args:
            card_idx: Index of the card from the deck
            
        Returns:
            Dictionary of {Color: cost} representing the card's cost
        """
        # This is a placeholder implementation
        # In a real implementation, this would look up the card's cost from cards.csv
        costs = {}
        for color in Color:
            if color != Color.GOLD:  # Gold is not a cost color
                costs[color] = 0
        
        # Simple placeholder logic - more expensive cards for higher indices
        main_color = list(Color)[card_idx % 5]  # Cycle through colors
        if main_color != Color.GOLD:  # Skip GOLD color for costs
            costs[main_color] = (card_idx % 5) + 1  # 1-5 of the main color
        
        secondary_color = list(Color)[(card_idx + 2) % 5]
        if secondary_color != Color.GOLD:  # Skip GOLD color for costs
            costs[secondary_color] = (card_idx % 3)  # 0-2 of a secondary color
        
        return costs
    
    def get_card_color(self, card_idx):
        """Get the color of a card by its index.
        
        Args:
            card_idx: Index of the card from the deck
            
        Returns:
            Color enum representing the card's color
        """
        # This is a placeholder implementation
        # In a real implementation, this would look up the card's color from cards.csv
        colors = [color for color in Color if color != Color.GOLD]  # Cards can't be GOLD colored
        return colors[card_idx % len(colors)]
    
    def get_card_points(self, card_idx):
        """Get the prestige points of a card by its index.
        
        Args:
            card_idx: Index of the card from the deck
            
        Returns:
            Integer representing the card's prestige points
        """
        # This is a placeholder implementation
        # In a real implementation, this would look up the card's points from cards.csv
        return (card_idx % 5)  # 0-4 points
    
    def get_tile_points(self, tile_idx):
        """Get the prestige points of a tile by its index.
        
        Args:
            tile_idx: Index of the tile
            
        Returns:
            Integer representing the tile's prestige points
        """
        # This is a placeholder implementation
        # In a real implementation, this would look up the tile's points from tiles.csv
        return 3  # All tiles are worth 3 points
    
    def buy_card(self, player_index, card_index, level):
        """Process a player buying a card.
        
        Args:
            player_index: Index of the player buying the card
            card_index: Index of the card to buy
            level: Level of the river (1, 2, or 3) to buy from
            
        Returns:
            Boolean indicating success or failure
        """
        # Check for valid player index
        if player_index < 0 or player_index >= len(self.players):
            print(f"Invalid player index: {player_index}")
            return False
            
        player = self.players[player_index]
        
        # Verify the card is in the river
        if level == 1 and card_index in self.level1_river:
            river = self.level1_river
            deck = self.level1_deck
        elif level == 2 and card_index in self.level2_river:
            river = self.level2_river
            deck = self.level2_deck
        elif level == 3 and card_index in self.level3_river:
            river = self.level3_river
            deck = self.level3_deck
        elif card_index in player.reserved_cards:
            # Buying a reserved card
            river = player.reserved_cards
            deck = None  # No need to draw a replacement
        else:
            print(f"Card {card_index} not found in level {level} river or reserved cards")
            return False
        
        # Check if player can afford the card
        card_cost = self.get_card_cost(card_index)
        
        # Calculate color discounts from owned cards
        discounts = {}
        for color in Color:
            if color != Color.GOLD:  # Gold is not a discount color
                discounts[color] = len(player.cards.get(color, []))
        
        # Check if player can afford the card with their tokens and discounts
        required_tokens = {}
        for color, amount in card_cost.items():
            required = max(0, amount - discounts.get(color, 0))
            if required > 0:
                required_tokens[color] = required
        
        # Check if player has required tokens
        available_gold = player.tokens.get(Color.GOLD, 0)
        needed_gold_tokens = 0
        token_payments = {}
        
        # First pass: calculate how many tokens of each type will be used
        for color, amount in required_tokens.items():
            available = player.tokens.get(color, 0)
            
            if available >= amount:
                # Player has enough of this color
                token_payments[color] = amount
            else:
                # Not enough regular tokens, need to use gold tokens
                token_payments[color] = available
                gold_needed = amount - available
                needed_gold_tokens += gold_needed
        
        # Check if player has enough gold tokens
        if available_gold < needed_gold_tokens:
            print(f"Player {player_index + 1} cannot afford card {card_index}")
            return False
        
        # Remove card from river and add to player's collection
        river.remove(card_index)
        
        # Add to player's cards by color
        card_color = self.get_card_color(card_index)
        player.cards.setdefault(card_color, []).append(card_index)
        
        # Remove tokens from player and return to bank
        for color, amount in token_payments.items():
            # Return the colored tokens
            player.tokens[color] -= amount
            self.tokens[color] += amount
        
        # Return the gold tokens if any were used
        if needed_gold_tokens > 0:
            player.tokens[Color.GOLD] -= needed_gold_tokens
            self.tokens[Color.GOLD] += needed_gold_tokens
        
        # Debugging info
        print(f"Player {player_index + 1} returned tokens: {token_payments}")
        if needed_gold_tokens > 0:
            print(f"Player {player_index + 1} returned {needed_gold_tokens} gold tokens")
        
        # Draw a new card from the deck if available and if we're buying from a river
        if deck is not None and len(deck) > 0:
            river.append(deck.pop(0))
        
        # Check if player has earned any tiles
        self._check_tile_eligibility(player_index)
        
        return True
    
    def take_tokens(self, player_index, colors):
        """Process a player taking tokens.
        
        Args:
            player_index: Index of the player taking tokens
            colors: List of colors to take one token of each
            
        Returns:
            Boolean indicating success or failure
        """
        # Check for valid player index
        if player_index < 0 or player_index >= len(self.players):
            print(f"Invalid player index: {player_index}")
            return False
            
        player = self.players[player_index]
        
        # Verify this is a valid token action (1-3 different colors)
        if not colors or len(colors) > 3:
            print(f"Invalid token selection: must take 1-3 tokens of different colors")
            return False
        
        # Check for duplicate colors
        if len(colors) != len(set(colors)):
            print(f"Invalid token selection: must take tokens of different colors")
            return False
        
        # Check if these tokens are available
        for color in colors:
            if self.tokens.get(color, 0) <= 0:
                print(f"No {color.name} tokens available")
                return False
        
        # Take the tokens
        for color in colors:
            player.tokens[color] = player.tokens.get(color, 0) + 1
            self.tokens[color] -= 1
        
        return True
    
    def reserve_card(self, player_index, card_index, level):
        """Process a player reserving a card.
        
        Args:
            player_index: Index of the player reserving the card
            card_index: Index of the card to reserve
            level: Level of the river (1, 2, or 3) to reserve from
            
        Returns:
            Boolean indicating success or failure
        """
        # Check for valid player index
        if player_index < 0 or player_index >= len(self.players):
            print(f"Invalid player index: {player_index}")
            return False
            
        player = self.players[player_index]
        
        # Verify the card is in the river
        if level == 1 and card_index in self.level1_river:
            river = self.level1_river
            deck = self.level1_deck
        elif level == 2 and card_index in self.level2_river:
            river = self.level2_river
            deck = self.level2_deck
        elif level == 3 and card_index in self.level3_river:
            river = self.level3_river
            deck = self.level3_deck
        else:
            print(f"Card {card_index} not found in level {level} river")
            return False
        
        # Check if player can reserve more cards (max 3)
        if len(player.reserved_cards) >= 3:
            print(f"Player {player_index + 1} already has 3 reserved cards")
            return False
        
        # Remove card from river and add to player's reserved cards
        river.remove(card_index)
        player.reserved_cards.append(card_index)
        
        # Give player a gold token if available
        if self.tokens.get(Color.GOLD, 0) > 0:
            player.tokens[Color.GOLD] = player.tokens.get(Color.GOLD, 0) + 1
            self.tokens[Color.GOLD] -= 1
        
        # Draw a new card from the deck if available
        if deck and len(deck) > 0:
            river.append(deck.pop(0))
        
        return True
    
    def _check_tile_eligibility(self, player_index):
        """Check if a player is eligible for any of the available tiles.
        
        Args:
            player_index: Index of the player to check
            
        Returns:
            None
        """
        # This is a placeholder implementation
        # In a real implementation, this would check the tile requirements
        # and award tiles when conditions are met
        pass