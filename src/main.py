#!/usr/bin/env python3

"""Main entry point for Splendid Cards game simulation."""

import argparse
import sys
import os
import time
import io
import re
from datetime import datetime

# Add the project root directory to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from src.models.gamestate import GameState
from src.agents.greedy_buyer import GreedyBuyer
from src.common import Color


# Game logging functionality
class GameLogger:
    """Logger class to write game output to both console and a file."""
    
    def __init__(self):
        self.log_file = None
        self.buffer = io.StringIO()
        self.original_print = print
        
    def setup(self):
        """Set up logging to a timestamped file in gamelogs directory."""
        # Create gamelogs directory if it doesn't exist
        project_root = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        logs_dir = os.path.join(project_root, 'gamelogs')
        
        # Create timestamped filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_filename = os.path.join(logs_dir, f'game_{timestamp}.log')
        
        # Open log file
        self.log_file = open(log_filename, 'w')
        
        # Override print function to log to both console and file
        def custom_print(*args, **kwargs):
            # Call the original print function for stdout output
            self.original_print(*args, **kwargs)
            
            # Capture for log file
            if self.log_file and not self.log_file.closed:
                # Get the string representation of the print arguments
                if 'file' not in kwargs:
                    # Clone the kwargs and remove 'flush' if it exists
                    log_kwargs = kwargs.copy()
                    log_kwargs.pop('flush', None)
                    
                    # Write to our StringIO buffer
                    self.buffer.truncate(0)
                    self.buffer.seek(0)
                    self.original_print(*args, file=self.buffer, **log_kwargs)
                    
                    # Get the content and write to the log file
                    log_line = self.buffer.getvalue()
                    
                    # Strip ANSI escape sequences (color codes) for the log file
                    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
                    log_line = ansi_escape.sub('', log_line)
                    
                    self.log_file.write(log_line)
                    self.log_file.flush()
        
        # Replace the built-in print function
        import builtins
        builtins.print = custom_print
        
        return log_filename
    
    def close(self):
        """Close log file and restore original print function."""
        if self.log_file and not self.log_file.closed:
            # Restore original print function
            import builtins
            builtins.print = self.original_print
            
            # Close the log file
            self.log_file.close()

# Create global logger instance
game_logger = GameLogger()


# ANSI color codes for terminal output
class Colors:
    WHITE = '\033[97m'       # Bright white
    BLUE = '\033[94m'        # Bright blue
    BLACK = '\033[38;5;180m' # Medium tan color for BLACK
    RED = '\033[91m'         # Bright red
    GREEN = '\033[92m'       # Bright green
    GOLD = '\033[93m'        # Bright yellow for GOLD
    RESET = '\033[0m'        # Reset to default color
    BOLD = '\033[1m'         # Bold text
    UNDERLINE = '\033[4m'    # Underlined text
    
    @staticmethod
    def get_color_code(color_enum):
        """Get the ANSI color code for a given Color enum value."""
        from src.common import Color
        color_map = {
            Color.WHITE: Colors.WHITE,
            Color.BLUE: Colors.BLUE,
            Color.BLACK: Colors.BLACK,
            Color.RED: Colors.RED,
            Color.GREEN: Colors.GREEN,
            Color.GOLD: Colors.GOLD
        }
        return color_map.get(color_enum, Colors.RESET)


def print_game_state(game_state, current_player=None, verbose=False):
    """Print the current state of the game in a compact format with colors.
    
    Args:
        game_state: Current GameState object
        current_player: Index of the current player (optional)
        verbose: Whether to print detailed information
    """
    print("\n" + Colors.BOLD + "=" * 60 + Colors.RESET)
    print(Colors.BOLD + f"Game State (Seed: {game_state.seed})" + Colors.RESET)
    print(Colors.BOLD + "=" * 60 + Colors.RESET)
    
    # Print token pool on a single line with colors
    token_parts = []
    for color, count in game_state.tokens.items():
        if count > 0:
            color_code = Colors.get_color_code(color)
            token_parts.append(f"{color_code}{color.name}{Colors.RESET}:{count}")
    
    token_str = "Tokens: " + ", ".join(token_parts)
    print(token_str)
    
    # Print tiles on a single line
    tile_str = "Tiles: " + ", ".join([f"{i}" for i in game_state.available_tiles])
    print(tile_str)
    
    # Print all card rivers in compact horizontal rows
    print("\n" + Colors.BOLD + "Card Rivers:" + Colors.RESET)
    print(Colors.BOLD + "Level 3:" + Colors.RESET)
    _print_card_row(game_state, game_state.level3_river, verbose)
    
    print(Colors.BOLD + "Level 2:" + Colors.RESET)
    _print_card_row(game_state, game_state.level2_river, verbose)
    
    print(Colors.BOLD + "Level 1:" + Colors.RESET)
    _print_card_row(game_state, game_state.level1_river, verbose)
    
    # Print player information
    print("\n" + Colors.BOLD + "Players:" + Colors.RESET)
    for idx, player in enumerate(game_state.players):
        # Format player header with current turn indicator
        player_header = f"Player {idx+1}" + (f"{Colors.BOLD} (Current Turn){Colors.RESET}" if current_player == idx else "")
        print("\n" + Colors.UNDERLINE + player_header + Colors.RESET)
        
        # Print player tokens on a single line with colors
        token_parts = []
        for color, count in player.tokens.items():
            if count > 0:
                color_code = Colors.get_color_code(color)
                token_parts.append(f"{color_code}{color.name}{Colors.RESET}:{count}")
        
        player_tokens = ", ".join(token_parts)
        print(f"Tokens: {player_tokens}")
        
        # Print player tiles if any
        if player.tiles:
            player_tiles = ", ".join([f"{Colors.GOLD}{i}{Colors.RESET}" for i in player.tiles])
            print(f"Tiles: {player_tiles}")
        
        # Print reserved cards if any
        if player.reserved_cards:
            print(Colors.UNDERLINE + "Reserved cards:" + Colors.RESET)
            for card_idx in player.reserved_cards:
                _print_card_details(game_state, card_idx, verbose)
        
        # Print owned cards by color with colors
        card_parts = []
        for color, cards in player.cards.items():
            if cards:
                color_code = Colors.get_color_code(color)
                card_parts.append(f"{color_code}{color.name}{Colors.RESET}:{len(cards)}")
        
        if card_parts:
            print(f"Cards: {', '.join(card_parts)}")
        else:
            print("Cards: None")
        
        # Print total prestige points in bold
        prestige_points = game_state.calculate_player_points(idx)
        print(f"Points: {Colors.BOLD}{prestige_points}{Colors.RESET}")


def _print_card_row(game_state, river, verbose):
    """Print a row of cards in a compact, single-line format with colors.
    
    Args:
        game_state: Current GameState object
        river: List of card indices in the river
        verbose: Whether to print detailed information
    """
    if not river:
        print("  (Empty)")
        return
    
    # Print all cards in a single line
    card_displays = []
    for card_idx in river:
        card_displays.append(_format_card_compact(game_state, card_idx))
    
    print("  " + "  ".join(card_displays))


def _format_card_compact(game_state, card_idx):
    """Format a card in a compact, single-line representation.
    
    Args:
        game_state: Current GameState object
        card_idx: Index of the card
        
    Returns:
        A string representing the card in the format '| ID COLOR PTS | W# U# B# R# G# |'
    """
    # Get card data
    card_color = game_state.get_card_color(card_idx)
    card_points = game_state.get_card_points(card_idx)
    card_cost = game_state.get_card_cost(card_idx)
    
    # Get color code for the card's color
    color_code = Colors.get_color_code(card_color)
    
    # Color abbreviation map (3-letter)
    color_abbr = {
        Color.WHITE: "WHT",
        Color.BLUE: "BLU",
        Color.GREEN: "GRN",
        Color.RED: "RED",
        Color.BLACK: "BLK",
        Color.GOLD: "GLD"  # Shouldn't be used for card colors
    }
    
    # Single letter abbreviation map
    color_abbr_short = {
        Color.WHITE: "W",
        Color.BLUE: "U",  # Using U for blue as in Magic: The Gathering
        Color.GREEN: "G",
        Color.RED: "R",
        Color.BLACK: "B"
    }
    
    # Format the card header with ID, color and points
    card_header = f"| {card_idx} {color_code}{color_abbr[card_color]}{Colors.RESET} {Colors.BOLD}{card_points}{Colors.RESET} |"
    
    # Format the card costs
    cost_items = []
    for color in [Color.WHITE, Color.BLUE, Color.BLACK, Color.RED, Color.GREEN]:
        count = card_cost.get(color, 0)
        color_code = Colors.get_color_code(color)
        cost_items.append(f"{color_code}{color_abbr_short[color]}{count}{Colors.RESET}")
    
    # Combine everything into a single line
    return f"{card_header} {' '.join(cost_items)} |"


def _print_card_details(game_state, card_idx, verbose):
    """Print details of a card in a compact format with colors.
    
    Args:
        game_state: Current GameState object
        card_idx: Index of the card
        verbose: Whether to print detailed information
    """
    # For reserved cards or other detailed views, use the compact single-line format
    card_display = _format_card_compact(game_state, card_idx)
    print("  " + card_display)


def execute_action(game_state, player_index, action):
    """Execute a player's action on the game state.
    
    Args:
        game_state: Current state of the game
        player_index: Index of the player taking the action
        action: Dictionary describing the action to take
        
    Returns:
        True if the action was executed successfully, False otherwise
    """
    action_type = action.get("action")
    
    if action_type == "buy":
        card_index = action.get("card_index")
        level = action.get("level")
        return game_state.buy_card(player_index, card_index, level)
    
    elif action_type == "take_tokens":
        colors = action.get("colors")
        return game_state.take_tokens(player_index, colors)
    
    elif action_type == "reserve":
        card_index = action.get("card_index")
        level = action.get("level")
        return game_state.reserve_card(player_index, card_index, level)
    
    elif action_type == "pass":
        # Passing is always valid
        return True
    
    else:
        print(f"Unknown action type: {action_type}")
        return False


def main():
    """Main entry point for the game simulation."""
    parser = argparse.ArgumentParser(description="Splendid Cards Game Simulation")
    parser.add_argument("--players", type=int, default=4, choices=[2, 3, 4],
                        help="Number of players in the game (2-4)")
    parser.add_argument("--seed", type=int, default=None,
                        help="Random seed for reproducible games")
    parser.add_argument("--verbose", action="store_true",
                        help="Print detailed game state information")
    
    args = parser.parse_args()
    
    # Setup game logging
    log_filename = game_logger.setup()
    print(f"Game log will be saved to: {log_filename}")
    
    # Initialize the game state
    game_state = GameState(players=args.players, seed=args.seed)
    
    # Create agents (all GreedyBuyer for now)
    agents = [GreedyBuyer(f"GreedyBuyer-{i+1}") for i in range(args.players)]
    
    # Print initial game state
    if args.verbose:
        print("Initial Game State:")
        print_game_state(game_state, verbose=args.verbose)
    else:
        print(f"Starting game with {args.players} players")
        if args.seed is not None:
            print(f"Using seed: {args.seed}")
    
    # Main game loop
    current_player = 0
    max_turns = 100  # Safety limit to prevent infinite loops
    turn_count = 0
    game_over = False
    
    while not game_over and turn_count < max_turns:
        turn_count += 1
        print(f"\nTurn {turn_count} - Player {current_player + 1}'s turn ({agents[current_player].name})")
        
        # Get action from current agent
        action = agents[current_player].take_turn(game_state, current_player)
        
        # Print the action
        action_type = action.get("action")
        if action_type == "buy":
            print(f"Player {current_player + 1} buys card {action.get('card_index')} from level {action.get('level')}")
        elif action_type == "take_tokens":
            color_names = [color.name for color in action.get("colors", [])]
            print(f"Player {current_player + 1} takes tokens: {', '.join(color_names)}")
        elif action_type == "reserve":
            print(f"Player {current_player + 1} reserves card {action.get('card_index')} from level {action.get('level')}")
        elif action_type == "pass":
            print(f"Player {current_player + 1} passes their turn")
        
        # Execute the action
        success = execute_action(game_state, current_player, action)
        
        if not success:
            print(f"Invalid action from Player {current_player + 1}. Skipping turn.")
        
        # Check if any player has reached 15 points
        for i, player in enumerate(game_state.players):
            points = game_state.calculate_player_points(i)
            if points >= 15:
                print(f"\nGame over! Player {i + 1} ({agents[i].name}) has won with {points} points!")
                game_over = True
                break
        
        # Move to next player
        current_player = (current_player + 1) % args.players
        
        # Print game state after the turn if verbose
        if args.verbose:
            print_game_state(game_state, current_player, args.verbose)
    
    # Final game state
    print("\nFinal Game State:")
    print_game_state(game_state, verbose=True)
    
    # Print final scores
    print("\nFinal Scores:")
    for i, player in enumerate(game_state.players):
        points = game_state.calculate_player_points(i)
        print(f"Player {i + 1} ({agents[i].name}): {points} points")
    
    if turn_count >= max_turns:
        print("\nGame ended due to reaching maximum turn limit.")
    
    # Close game logging
    game_logger.close()
    print("Game log saved successfully")


if __name__ == "__main__":
    main()