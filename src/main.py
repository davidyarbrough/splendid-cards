"""Main entry point for Splendid Cards game simulation."""

import argparse
import sys
import os

# Add the project root directory to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from src.models.gamestate import GameState
from src.agents.greedy_buyer import GreedyBuyer
from src.agents.stingy_buyer import StingyBuyer
from src.utils.common import Color

# Import refactored modules
from src.utils.logging import game_logger
from src.utils.display import Colors
from src.views.game_view import print_game_state, print_end_game_summary
from src.controllers.action_controller import execute_action


def main():
    """Main entry point for the game simulation."""
    parser = argparse.ArgumentParser(description="Splendid Cards Game Simulation")
    parser.add_argument("--players", type=int, default=4, choices=[2, 3, 4],
                        help="Number of players in the game (2-4)")
    parser.add_argument("--agents", type=str, nargs="*", default=["greedy"],
                        help="Agent types to use (greedy, stingy)")
    parser.add_argument("--seed", type=int, default=None,
                        help="Random seed for reproducible games")
    parser.add_argument("--verbose", action="store_true",
                        help="Print detailed game state information")
    parser.add_argument("--rounds", type=int, default=100,
                        help="Maximum number of rounds to play. Values < 1 mean unlimited rounds")
    
    args = parser.parse_args()
    
    # Setup game logging
    log_filename = game_logger.setup()
    print(f"Game log will be saved to: {log_filename}")
    
    # Initialize the game state
    game_state = GameState(players=args.players, seed=args.seed)
    
    # Map agent type names to agent classes
    agent_types = {
        "greedy": GreedyBuyer,
        "stingy": StingyBuyer,
    }
    
    # Create agents based on specified types
    agents = []
    agent_names = args.agents[:] if len(args.agents) >= args.players else [args.agents[0]] * args.players
    
    # Ensure we have enough agent types (repeat the last one if needed)
    while len(agent_names) < args.players:
        agent_names.append(agent_names[-1])
    
    # Create the agent instances
    for i in range(args.players):
        agent_type = agent_names[i].lower()
        if agent_type not in agent_types:
            print(f"Warning: Unknown agent type '{agent_type}'. Using 'greedy' instead.")
            agent_type = "greedy"
        
        agent_class = agent_types[agent_type]
        agent_name = f"{agent_class.__name__}-{i+1}"
        agents.append(agent_class(agent_name))
    
    # Print initial game state
    if args.verbose:
        print("Initial Game State:")
        print_game_state(game_state, agents=agents, verbose=args.verbose)
    else:
        print(f"Starting game with {args.players} players")
        if args.seed is not None:
            print(f"Using seed: {args.seed}")
    
    # Main game loop
    current_player = 0
    turn_count = 0
    round_number = 1
    final_round = False
    winning_player = None
    game_over = False
    
    # Track the starting player of the game (always Player 1 for now)
    starting_player = 0
    
    # Determine max rounds (< 1 means unlimited)
    unlimited_rounds = args.rounds < 1
    max_rounds = None if unlimited_rounds else args.rounds
    
    while not game_over:
        turn_count += 1
        print(f"\nTurn {turn_count} - Round {round_number} - Player {current_player + 1}'s turn ({agents[current_player].name})")
        
        # Get action from current agent and execute it
        action = agents[current_player].take_turn(game_state, current_player)
        success = execute_action(game_state, current_player, action)
        
        if not success:
            print(f"Invalid action from Player {current_player + 1}. Skipping turn.")
        
        # Check if any player has reached the victory point threshold (only if we're not already in the final round)
        # Official victory threshold is 15 points
        VICTORY_POINTS = 15
        if not final_round:
            for i, player in enumerate(game_state.players):
                points = game_state.calculate_player_points(i)
                if points >= VICTORY_POINTS:
                    print(f"\nPlayer {i + 1} ({agents[i].name}) has reached {points} points!")
                    print(f"Final round triggered - all players will get one more turn.")
                    final_round = True
                    winning_player = i  # Track the first player to reach the victory point threshold
                    break
        
        # Move to next player
        current_player = (current_player + 1) % args.players
        
        # If we've completed a round (all players have taken a turn), update round counter
        if current_player == starting_player:
            round_number += 1
            
            # If we're in the final round and have completed it, end the game
            if final_round:
                game_over = True
                print(f"\nGame over! Round complete after player reached {VICTORY_POINTS}+ points.")
                
            # Check if we've hit the maximum round limit
            if not unlimited_rounds and round_number > max_rounds:
                game_over = True
                print(f"\nGame over! Reached maximum round limit of {max_rounds} rounds.")
        
        # Print game state after the turn if verbose
        if args.verbose:
            print_game_state(game_state, current_player, agents, args.verbose)
    
    # Final game state
    print("\nFinal Game State:")
    print_game_state(game_state, agents=agents, verbose=True)
    
    # Print final scores and determine winner
    print_end_game_summary(game_state, agents)
    
    # Print round limit message if applicable
    if not unlimited_rounds and round_number > max_rounds:
        print(f"\nGame ended due to reaching maximum round limit of {max_rounds} rounds.")
    
    # Close game logging
    game_logger.close()
    print("Game log saved successfully")


if __name__ == "__main__":
    main()
