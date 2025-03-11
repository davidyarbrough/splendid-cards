"""Main entry point for Splendid Cards game simulation."""

import argparse
import sys
import os
import statistics
from collections import defaultdict

# Add the project root directory to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from src.models.gamestate import GameState
from src.agents.greedy_buyer import GreedyBuyer
from src.agents.random_buyer import RandomBuyer
from src.agents.stingy_buyer import StingyBuyer
from src.agents.value_buyer import ValueBuyer
from src.utils.common import Color

# Import refactored modules
from src.utils.logging import game_logger
from src.utils.display import Colors
from src.views.game_view import print_game_state, print_end_game_summary
from src.controllers.action_controller import execute_action


def main():
    """Main entry point for the game simulation."""
    parser = argparse.ArgumentParser(description="Splendid Cards Game Simulation")
    parser.add_argument("--players", type=int, default=4, choices=[1, 2, 3, 4],
                        help="Number of players in the game (1-4). Use 1 for single-player mode")
    parser.add_argument("--agents", type=str, nargs="*", default=["greedy"],
                        help="Agent types to use (greedy, random, stingy, value)")
    parser.add_argument("--seed", type=int, default=None,
                        help="Random seed for reproducible games")
    parser.add_argument("--verbose", action="store_true",
                        help="Print detailed game state information")
    parser.add_argument("--rounds", type=int, default=100,
                        help="Maximum number of rounds to play. Values < 1 mean unlimited rounds")
    parser.add_argument("--single-player", action="store_true",
                        help="Run in single-player mode where the agent tries to reach 15 points as quickly as possible")
    parser.add_argument("--compare-all", action="store_true",
                        help="In single-player mode, compare all agent types by running them in sequence")
    parser.add_argument("--benchmark", action="store_true",
                        help="Run benchmark tests across multiple seeds for a single agent type")
    parser.add_argument("--min-seed", type=int, default=0,
                        help="Starting seed for benchmark mode (default: 0)")
    parser.add_argument("--max-seed", type=int, default=99,
                        help="Ending seed for benchmark mode (inclusive, default: 99)")
    
    args = parser.parse_args()
    
    # Setup game logging
    log_filename = game_logger.setup()
    print(f"Game log will be saved to: {log_filename}")
    
    # If single-player mode or benchmark mode is enabled, force players to 1
    if args.single_player or args.benchmark:
        mode_name = "single-player time trial mode" if args.single_player else "benchmark mode"
        print(f"Running in {mode_name}")
        args.players = 1
    
    # Initialize the game state
    game_state = GameState(players=args.players, seed=args.seed)
    
    # Map agent type names to agent classes
    agent_types = {
        "greedy": GreedyBuyer,
        "random": RandomBuyer,
        "stingy": StingyBuyer,
        "value": ValueBuyer,
    }
    
    # Different agent creation based on mode
    agents = []
    
    # For benchmark mode, we're testing just one agent type
    if args.benchmark:
        if len(args.agents) > 1:
            print(f"Warning: Multiple agents specified for benchmark. Using only the first one: {args.agents[0]}")
        
        agent_type = args.agents[0].lower()
        if agent_type not in agent_types:
            print(f"Warning: Unknown agent type '{agent_type}'. Using 'greedy' instead.")
            agent_type = "greedy"
            
        agent_class = agent_types[agent_type]
        print(f"Will benchmark {agent_class.__name__} across seeds {args.min_seed} to {args.max_seed}")
        agents.append(agent_class(f"{agent_class.__name__}"))
    # For compare-all mode, we'll run each agent type sequentially
    elif args.single_player and args.compare_all:
        agent_types_to_run = list(agent_types.keys())
        print(f"Will compare all agent types: {', '.join(agent_types_to_run)}")
        # We'll create the first agent now and create others as we go
        agent_type = agent_types_to_run[0].lower()
        agent_class = agent_types[agent_type]
        agents.append(agent_class(f"{agent_class.__name__}"))
        # Track current agent for compare-all mode
        current_agent_idx = 0
    else:
        # Normal agent creation
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
    
    # Track performance results for compare-all mode or benchmark mode
    performance_results = []
    benchmark_results = defaultdict(list) if args.benchmark else None
    
    # Function to run a single game
    def run_single_game(game_state, agents, agent_idx=0):
        # Main game loop variables
        current_player = 0  # Always 0 in single player mode
        turn_count = 0
        round_number = 1
        game_over = False
        success_round = None
        
        # Determine max rounds (< 1 means unlimited)
        unlimited_rounds = args.rounds < 1
        max_rounds = None if unlimited_rounds else args.rounds
        
        # Official victory threshold is 15 points
        VICTORY_POINTS = 15
        
        # Print game start info
        agent_name = agents[agent_idx].name
        print(f"\nStarting game with agent: {agent_name}")
        
        while not game_over:
            turn_count += 1
            print(f"\nTurn {turn_count} - Round {round_number} - {agent_name}'s turn")
            
            # Get action from agent and execute it
            action = agents[agent_idx].take_turn(game_state, current_player)
            success = execute_action(game_state, current_player, action)
            
            if not success:
                print(f"Invalid action from {agent_name}. Skipping turn.")
            
            # Check if player has reached the victory point threshold
            points = game_state.calculate_player_points(current_player)
            if points >= VICTORY_POINTS:
                print(f"\n{agent_name} has reached {points} points in {round_number} rounds!")
                game_over = True
                success_round = round_number
                
            # Update round counter (in single-player mode, each turn is a round)
            round_number += 1
                
            # Check if we've hit the maximum round limit
            if not unlimited_rounds and round_number > max_rounds:
                game_over = True
                print(f"\nGame over! Reached maximum round limit of {max_rounds} rounds.")
            
            # Print game state after the turn if verbose
            if args.verbose:
                print_game_state(game_state, current_player, agents, args.verbose)
        
        # Return the number of rounds it took to reach 15 points, or None if time limit reached
        return success_round, points
    
    # Single player mode with compare-all
    if args.single_player and args.compare_all:
        # Run each agent type in sequence
        for agent_type in agent_types.keys():
            # Reset the game state with the same seed
            game_state = GameState(players=1, seed=args.seed)
            
            # Create the agent
            agent_class = agent_types[agent_type]
            agent_name = f"{agent_class.__name__}"
            agents = [agent_class(agent_name)]
            
            # Run the game
            success_round, points = run_single_game(game_state, agents)
            
            # Record results
            performance_results.append({
                "agent_type": agent_type,
                "agent_name": agent_name,
                "points": points,
                "rounds": success_round
            })
            
            print(f"\n{agent_name} finished with {points} points in {success_round or 'DNF'} rounds")
            print("-" * 60)
    
    # Normal single player mode or regular multiplayer mode
    else:
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
        
        # Special case for benchmark mode
        if args.benchmark:
            # Run agent across the specified range of seeds
            agent_type = args.agents[0].lower() if args.agents[0].lower() in agent_types else "greedy"
            agent_class = agent_types[agent_type]
            agent_name = f"{agent_class.__name__}"
            
            print(f"Benchmarking {agent_name} across {args.max_seed - args.min_seed + 1} seeds...")
            
            for seed in range(args.min_seed, args.max_seed + 1):
                # Reset the game state with the current seed
                game_state = GameState(players=1, seed=seed)
                
                # Create fresh agent for each seed
                agents = [agent_class(agent_name)]
                
                # Run the game with this seed
                success_round, points = run_single_game(game_state, agents)
                
                # Store the results for this seed
                benchmark_results[seed] = {
                    "rounds": success_round if success_round is not None else float('inf'),
                    "points": points
                }
                
                # Print progress indicator for every 10 seeds
                if (seed - args.min_seed + 1) % 10 == 0 or seed == args.max_seed:
                    print(f"Processed {seed - args.min_seed + 1}/{args.max_seed - args.min_seed + 1} seeds")
        # Special case for single player mode
        elif args.single_player and args.players == 1:
            success_round, points = run_single_game(game_state, agents)
        else:
            # Regular multiplayer game loop
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
    
    # Handle the compare-all results
    if args.single_player and args.compare_all and performance_results:
        # Display summary table
        print("\n=== AGENT PERFORMANCE COMPARISON ===\n")
        print("{:<20} {:<15} {:<15}".format("Agent Type", "Points", "Rounds to 15"))
        print("-" * 50)
        
        # Sort by rounds (fastest to slowest), then by points (highest to lowest)
        sorted_results = sorted(
            performance_results, 
            key=lambda x: (float('inf') if x['rounds'] is None else x['rounds'], -x['points'])
        )
        
        for result in sorted_results:
            rounds_display = result['rounds'] if result['rounds'] is not None else "DNF"
            print("{:<20} {:<15} {:<15}".format(
                result['agent_name'],
                result['points'], 
                rounds_display
            ))
    # Handle benchmark results
    elif args.benchmark and benchmark_results:
        # Calculate statistics
        rounds_data = [data['rounds'] for data in benchmark_results.values() 
                      if data['rounds'] != float('inf')]  # Filter out DNFs for calculations
        points_data = [data['points'] for data in benchmark_results.values()]
        
        # Find best and worst seeds
        if rounds_data:  # Only if we have any successful runs
            best_seed = min(benchmark_results.items(), key=lambda x: x[1]['rounds'])[0]
            worst_seed = max(benchmark_results.items(), key=lambda x: x[1]['rounds'])[0]
            
            # Calculate statistics only if we have successful runs
            avg_rounds = statistics.mean(rounds_data)
            median_rounds = statistics.median(rounds_data)
            std_dev_rounds = statistics.stdev(rounds_data) if len(rounds_data) > 1 else 0
            
            # Count successful runs (where 15+ points were reached)
            success_rate = len(rounds_data) / len(benchmark_results) * 100
            
            # Display overall statistics
            agent_name = agents[0].name
            print(f"\n=== BENCHMARK RESULTS FOR {agent_name.upper()} ===\n")
            print(f"Seeds tested: {args.min_seed} to {args.max_seed} ({len(benchmark_results)} total)")
            print(f"Success rate: {success_rate:.1f}% ({len(rounds_data)}/{len(benchmark_results)})")
            print(f"\nStatistics for successful runs (reached 15+ points):")
            print(f"Best performance: Seed {best_seed} - {benchmark_results[best_seed]['rounds']} rounds")
            print(f"Worst performance: Seed {worst_seed} - {benchmark_results[worst_seed]['rounds']} rounds")
            print(f"Average rounds to 15 points: {avg_rounds:.2f}")
            print(f"Median rounds to 15 points: {median_rounds:.2f}")
            print(f"Standard deviation: {std_dev_rounds:.2f}")
            
            # Display top 5 best and worst seeds
            print("\nTop 5 Best Seeds:")
            best_seeds = sorted(benchmark_results.items(), key=lambda x: x[1]['rounds'])[:5]
            for seed, data in best_seeds:
                points = data['points']
                rounds = data['rounds']
                if rounds == float('inf'):
                    rounds_display = "DNF"
                else:
                    rounds_display = rounds
                print(f"  Seed {seed}: {points} points in {rounds_display} rounds")
            
            print("\nTop 5 Worst Seeds:")
            worst_seeds = sorted(benchmark_results.items(), key=lambda x: x[1]['rounds'], reverse=True)[:5]
            for seed, data in worst_seeds:
                points = data['points']
                rounds = data['rounds']
                if rounds == float('inf'):
                    rounds_display = "DNF"
                else:
                    rounds_display = rounds
                print(f"  Seed {seed}: {points} points in {rounds_display} rounds")
        else:
            print(f"\n=== BENCHMARK RESULTS ===\n")
            print("No successful runs found. The agent did not reach 15 points in any seed.")
    else:
        # Final game state for a single game
        print("\nFinal Game State:")
        print_game_state(game_state, agents=agents, verbose=True)
        
        # Print final scores and determine winner with efficiency stats for a regular game
        if not args.single_player or args.players > 1:
            print_end_game_summary(game_state, agents, round_number)
        
        # Print round limit message if applicable for a regular game
        if not args.single_player and not unlimited_rounds and round_number > max_rounds:
            print(f"\nGame ended due to reaching maximum round limit of {max_rounds} rounds.")
    
    # Close game logging
    game_logger.close()
    print("Game log saved successfully")


if __name__ == "__main__":
    main()
