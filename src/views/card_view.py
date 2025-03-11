"""Card display formatting functionality for the Splendid Cards game."""

from src.utils.common import Color
from src.utils.display import Colors


def format_card_compact(game_state, card_idx):
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
    
    # Format the card header with ID, color and points (padded to ensure alignment)
    card_header = f"| {card_idx:2d} {color_code}{color_abbr[card_color]}{Colors.RESET} {Colors.BOLD}{card_points}{Colors.RESET} |"
    
    # Format the card costs
    cost_items = []
    for color in [Color.WHITE, Color.BLUE, Color.BLACK, Color.RED, Color.GREEN]:
        count = card_cost.get(color, 0)
        color_code = Colors.get_color_code(color)
        cost_items.append(f"{color_code}{color_abbr_short[color]}{count}{Colors.RESET}")
    
    # Combine everything into a single line
    return f"{card_header} {' '.join(cost_items)} |"


def print_card_details(game_state, card_idx, verbose):
    """Print details of a card in a compact format with colors.
    
    Args:
        game_state: Current GameState object
        card_idx: Index of the card
        verbose: Whether to print detailed information
    """
    # For reserved cards or other detailed views, use the compact single-line format
    card_display = format_card_compact(game_state, card_idx)
    print("  " + card_display)


def print_card_row(game_state, river, verbose):
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
        card_displays.append(format_card_compact(game_state, card_idx))
    
    print("  " + "  ".join(card_displays))
