# Splendid Cards

A sophisticated simulation framework for analyzing optimal strategies in a certain gem-collecting, card-development tableau game that shall remain nameless (but is certainly *splendid*).

## About

Splendid Cards is a research tool designed to evaluate optimal playstyles in a famous renaissance-themed card acquisition game through simulation. By modeling various agent strategies and running large numbers of simulated games, this project aims to identify effective approaches and analyze the impact of different tactics.

## Game Overview

In this *jewel* of a tableau-building game, players:

- Collect tokens of five different colors (white, blue, black, red, and green)
- Purchase development cards using these tokens
- Earn prestige points from cards and tiles
- Build an economic engine through card discounts
- Claim tiles by meeting color requirements with owned cards
- Race to be the first to reach 15 prestige points

The simulation faithfully recreates the elegant balance of resource management, strategic planning, and tactical decision-making that makes the original game a *gem* among tabletop enthusiasts.

## Project Structure

```
splendid-cards/
├── data/           # Game configuration data
├── src/            # Source code
│   ├── agents/     # AI agent implementations
│   ├── models/     # Game models and logic
│   ├── common.py   # Common game objects and enums
│   └── main.py     # Entry point for simulations
└── docs/           # Documentation
```

## Features

- Complete implementation of the game rules
- Modular agent framework for implementing different AI strategies
- Extensive metrics and analytics for evaluating agent performance
- Configurable game parameters for experimentation
- Batch simulation capabilities for statistical analysis

## Usage

```bash
# Run a basic simulation
python3 src/main.py

# Run simulation with specific agents
python3 src/main.py --agents random greedy value

# Run with a specific number of rounds (useful for comparing strategies)
python3 src/main.py --rounds 30

# Run in single-player time trial mode
python3 src/main.py --single-player --agents value

# Compare all agent types in single-player mode
python3 src/main.py --single-player --compare-all --seed 123
```

## Agent Types

Use these names with the `--agents` parameter to specify which agents to use in your game:

- **Greedy** (`greedy`): Always buys the most expensive card it can afford. This agent prioritizes cards with the highest total cost. When eligible for tiles, it selects the tile with the highest combined card requirement cost.

- **Stingy** (`stingy`): Buys the cheapest card it can afford. This agent prioritizes cards with the lowest total cost, breaking ties by preferring cards with more diverse color requirements and higher points. When eligible for tiles, it selects the tile with the lowest combined card requirement cost.

- **Random** (`random`): Makes random decisions from available legal moves. If any cards can be purchased immediately, it randomly selects one to buy. Otherwise, it takes 3 tokens of randomly selected colors (never GOLD tokens). When eligible for tiles, it randomly selects one of the available qualifying tiles.

- **Value-Based** (`value`): Evaluates moves based on a heuristic value function. This agent computes a value score for each possible action (buying cards, reserving cards, collecting tokens) and selects the highest-valued action. It prioritizes cards that help complete tile requirements and collects tokens needed for reserved cards.

- **MCTS** (`mcts`): Uses Monte Carlo Tree Search to look ahead. (Not yet implemented)

### Examples

```bash
# Use all GreedyBuyer agents
python3 src/main.py --agents greedy

# Use all StingyBuyer agents
python3 src/main.py --agents stingy

# Specify different agents for each player (in a 4-player game)
python3 src/main.py --agents greedy stingy greedy stingy

# For a 2-player game with specific agents
python3 src/main.py --players 2 --agents greedy stingy
```

## Single-Player Time Trial Mode

Splendid Cards now supports a single-player mode where agents try to reach 15 points as quickly as possible. This is ideal for benchmarking different agent strategies in isolation.

### Usage

```bash
# Run a single agent in time trial mode
python3 src/main.py --single-player --agents value

# Compare all agent types in a single run
python3 src/main.py --single-player --compare-all --seed 123

# Set a maximum round limit
python3 src/main.py --single-player --compare-all --rounds 50
```

### Features

- Each agent starts with a fresh game state (identical setup when using the same seed)
- In single-player mode, each turn counts as a round
- The game ends when the agent reaches 15 points or hits the round limit
- When comparing all agents, a performance table is displayed showing:
  - Points achieved by each agent
  - Number of rounds taken to reach 15 points (or DNF if unable to reach it)

## Benchmark Mode

The benchmark mode allows you to evaluate an agent's performance across multiple seeds, providing detailed statistical analysis.

### Usage

```bash
# Run benchmark with default settings (agent tested on seeds 0-99)
python3 src/main.py --benchmark --agents value

# Specify a different range of seeds
python3 src/main.py --benchmark --agents greedy --min-seed 100 --max-seed 199

# Set a maximum round limit 
python3 src/main.py --benchmark --agents value --rounds 50 --min-seed 0 --max-seed 19
```

### Features

- Tests a single agent against multiple seeds (default: seeds 0-99)
- Provides comprehensive statistical analysis:
  - Success rate (percentage of seeds where agent reached 15+ points)
  - Best and worst performing seeds
  - Average, median, and standard deviation of rounds to 15 points
  - Detailed listing of top 5 best and worst seeds
- Progress indicators show completion percentage during longer benchmark runs

- **Custom**: Define your own agent strategies

## Development

### Prerequisites

- Python 3.8+
- Required packages (detailed in requirements.txt)

### Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-strategy`)
3. Commit your changes (`git commit -m 'Add new agent strategy'`)
4. Push to the branch (`git push origin feature/amazing-strategy`)
5. Open a Pull Request

## Acknowledgements

- Thanks to all the *noble* strategy game designers whose *precious* work has *enriched* the tabletop gaming world
- This project is for academic and research purposes only
- No association with any commercially available game is implied or intended
