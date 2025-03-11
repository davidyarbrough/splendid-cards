#!/usr/bin/env python3

"""Main entry point for Splendid Cards game simulation."""

import argparse
import sys
import os
import time

# Add the project root directory to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from src.models.gamestate import GameState
from src.agents.greedy_buyer import GreedyBuyer
from src.common import Color


def print_game_state(game_state, current_player=None, verbose=False):
    """Print the current state of the game.
    
    Args:
        game_state: Current GameState object
        current_player: Index of the current player (optional)
        verbose: Whether to print detailed information
    """
    print("\n" + "=" * 60)
    print(f"Game State (Seed: {game_state.seed})")
    print("=" * 60)
    
    # Print token pool
    print("\nToken Pool:")
    for color, count in game_state.tokens.items():
        print(f"  {color.name}: {count}")
    
    # Print rivers (visible cards)
    print("\nLevel 1 River:")
    for idx, card_idx in enumerate(game_state.level1_river):
        print(f"  Card {idx+1}: Index {card_idx}")
        if verbose:
            # In verbose mode, print card details
            card_cost = game_state.get_card_cost(card_idx)
            card_color = game_state.get_card_color(card_idx)
            card_points = game_state.get_card_points(card_idx)
            print(f"    Color: {card_color.name if card_color else 'Unknown'}")
            print(f"    Points: {card_points}")
            print(f"    Cost: {', '.join([f'{color.name}:{count}' for color, count in card_cost.items() if count > 0])}")
    
    print("\nLevel 2 River:")
    for idx, card_idx in enumerate(game_state.level2_river):
        print(f"  Card {idx+1}: Index {card_idx}")
        if verbose:
            card_cost = game_state.get_card_cost(card_idx)
            card_color = game_state.get_card_color(card_idx)
            card_points = game_state.get_card_points(card_idx)
            print(f"    Color: {card_color.name if card_color else 'Unknown'}")
            print(f"    Points: {card_points}")
            print(f"    Cost: {', '.join([f'{color.name}:{count}' for color, count in card_cost.items() if count > 0])}")
    
    print("\nLevel 3 River:")
    for idx, card_idx in enumerate(game_state.level3_river):
        print(f"  Card {idx+1}: Index {card_idx}")
        if verbose:
            card_cost = game_state.get_card_cost(card_idx)
            card_color = game_state.get_card_color(card_idx)
            card_points = game_state.get_card_points(card_idx)
            print(f"    Color: {card_color.name if card_color else 'Unknown'}")
            print(f"    Points: {card_points}")
            print(f"    Cost: {', '.join([f'{color.name}:{count}' for color, count in card_cost.items() if count > 0])}")
    
    # Print tiles
    print("\nAvailable Tiles:")
    for idx, tile_idx in enumerate(game_state.available_tiles):
        print(f"  Tile {idx+1}: Index {tile_idx}")
        if verbose:
            # Print tile details in verbose mode
            pass  # TODO: Add tile details when implemented
    
    # Print player information
    print("\nPlayers:")
    for idx, player in enumerate(game_state.players):
        if current_player == idx:
            print(f"  Player {idx+1} (Current Turn):")
        else:
            print(f"  Player {idx+1}:")
        
        # Print player tokens
        print("    Tokens:")
        for color, count in player.tokens.items():
            if count > 0:
                print(f"      {color.name}: {count}")
        
        # Print player cards
        print("    Cards:")
        card_count = 0
        for color, cards in player.cards.items():
            if cards:
                print(f"      {color.name}: {len(cards)}")
                card_count += len(cards)
        print(f"      Total: {card_count}")
        
        # Print player prestige points
        prestige_points = game_state.calculate_player_points(idx)
        print(f"    Prestige Points: {prestige_points}")


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


if __name__ == "__main__":
    main()