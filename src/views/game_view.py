"""Game state display functionality for the Splendid Cards game."""

from src.utils.common import Color
from src.utils.display import Colors
from src.views.card_view import print_card_row, print_card_details


def print_game_state(game_state, current_player=None, agents=None, verbose=False):
    """Print the current state of the game in a human-readable format.
    
    Args:
        game_state: The current GameState object
        current_player: Index of the current player (for highlighting)
        agents: List of agent objects (for displaying names)
        verbose: Whether to print detailed information
    """
    print("\n" + "=" * 60)
    print(f"Game State (Seed: {game_state.seed})")
    print("=" * 60)
    
    # Print available tokens
    token_strs = []
    for color in [Color.WHITE, Color.BLUE, Color.BLACK, Color.RED, Color.GREEN, Color.GOLD]:
        count = game_state.tokens[color]
        color_code = Colors.get_color_code(color)
        color_name = color.value.upper()
        token_strs.append(f"{color_code}{color_name}{Colors.RESET}:{count}")
    print("Tokens: " + ", ".join(token_strs))
    
    # Print tiles
    tile_strs = []
    for tile_idx in game_state.available_tiles:
        tile_strs.append(str(tile_idx))
    print("Tiles: " + ", ".join(tile_strs))
    
    # Print card rivers
    print("\nCard Rivers:")
    
    # Level 3 cards (most valuable)
    print("Level 3:")
    print_card_row(game_state, game_state.level3_river, verbose)
    
    # Level 2 cards (medium value)
    print("Level 2:")
    print_card_row(game_state, game_state.level2_river, verbose)
    
    # Level 1 cards (least valuable)
    print("Level 1:")
    print_card_row(game_state, game_state.level1_river, verbose)
    
    # Print player info
    print("\nPlayers:\n")
    for player_idx, player in enumerate(game_state.players):
        # Determine if this is the current player
        is_current = (player_idx == current_player)
        player_name = f" ({agents[player_idx].name})" if agents and player_idx < len(agents) else ""
        
        # Print player header with optional current marker
        if is_current:
            print(f"Player {player_idx + 1}{player_name} (Current Turn)")
        else:
            print(f"Player {player_idx + 1}{player_name}")
        
        # Print player tokens
        token_strs = []
        for color in [Color.WHITE, Color.BLUE, Color.BLACK, Color.RED, Color.GREEN, Color.GOLD]:
            count = player.tokens[color]
            if count > 0:  # Only show tokens the player has
                color_code = Colors.get_color_code(color)
                color_name = color.value.upper()
                token_strs.append(f"{color_code}{color_name}{Colors.RESET}:{count}")
        
        if token_strs:
            print("Tokens: " + ", ".join(token_strs))
        else:
            print("Tokens: ")
        
        # Print player's owned tiles if they have any
        if hasattr(player, 'tiles') and player.tiles:
            print("Owned tiles:")
            tile_strs = []
            for tile_idx in player.tiles:
                tile_strs.append(str(tile_idx))
            print("  " + ", ".join(tile_strs))
            
        # Print player's owned cards
        print("Owned cards:")
        if not any(len(cards) > 0 for cards in player.cards.values()):
            print("  None")
        else:
            # Cards are already grouped by color in the player object
            # Print cards grouped by color in a format similar to river cards
            for color, cards in player.cards.items():
                if len(cards) > 0:  # Only print colors that have cards
                    color_code = Colors.get_color_code(color)
                    color_name = color.value.upper()
                    print(f"  {color_code}{color_name}{Colors.RESET}:")
                    
                    # Print cards in rows of 3
                    row = []
                    for card_index, card_idx in enumerate(cards):
                        row.append(card_idx)
                        if (card_index + 1) % 3 == 0 or card_index == len(cards) - 1:
                            card_strs = []
                            for c in row:
                                # Pad card indexes < 10 with a space
                                padded_idx = f" {c}" if c < 10 else f"{c}"
                                points = game_state.get_card_points(c)
                                color_code = Colors.get_color_code(color)
                                color_str = color.value.upper()
                                # Apply color highlighting to the color name
                                card_strs.append(f"| {padded_idx} {color_code}{color_str}{Colors.RESET} {points} |")
                            print("    " + "  ".join(card_strs))
                            row = []
        
        # Print player's reserved cards
        if player.reserved_cards:
            print("Reserved cards:")
            for card_idx in player.reserved_cards:
                print_card_details(game_state, card_idx, verbose)
        
        # Print player points
        points = game_state.calculate_player_points(player_idx)
        print(f"Points: {points}\n")


def print_end_game_summary(game_state, agents, round_number=None):
    """Print a summary of the game results.
    
    Args:
        game_state: The current GameState object
        agents: List of agent objects
        round_number: The final round number reached in the game
    """
    # Get the round number from game log if not provided
    if round_number is None:
        # Try to infer round number from the latest game log
        from src.utils.logging import game_logger
        round_number = game_logger.get_current_round() or 1
    
    # Calculate player points and efficiency
    player_stats = []
    for i in range(len(game_state.players)):
        points = game_state.calculate_player_points(i)
        # Calculate points per round (efficiency)
        efficiency = points / round_number if round_number > 0 else 0
        player_stats.append((i, points, efficiency))
    
    # Sort by points (descending)
    player_stats.sort(key=lambda x: x[1], reverse=True)
    
    # Print final scores
    print("\nFinal Scores (after {} rounds):".format(round_number))
    print("{:<10} {:<25} {:<10} {:<15}".format("Player", "Agent", "Points", "Points/Round"))
    print("-" * 60)
    for player_idx, points, efficiency in player_stats:
        player_name = agents[player_idx].name if agents else f"Player {player_idx + 1}"
        print("{:<10} {:<25} {:<10} {:<15.2f}".format(
            f"Player {player_idx + 1}", 
            player_name, 
            points, 
            efficiency
        ))
    
    # Determine winner(s)
    max_points = player_stats[0][1]
    winners = [(idx, agents[idx]) for idx, points, _ in player_stats if points == max_points]
    
    # Print winner message
    if len(winners) == 1:
        idx, _ = winners[0]
        points = player_stats[0][1]
        print(f"\nPlayer {idx + 1} ({agents[idx].name}) wins with {points} points!")
    else:
        # It's a tie
        winner_strings = [f"Player {idx + 1} ({agent.name})" for idx, agent in winners]
        print(f"\nTie game! {', '.join(winner_strings)} tied with {max_points} points each!")
