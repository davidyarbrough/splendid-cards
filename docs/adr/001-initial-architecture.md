# ADR 001: Initial Architecture for Splendid Cards

## Date: 2025-03-11

## Status

Accepted

## Context

Splendid Cards is a simulation framework designed to evaluate optimal strategies in a gem-collecting card acquisition game. The framework needs to support multiple agent implementations, maintain game state, enforce rules, and facilitate analysis of different play styles.

Key requirements include:
- A game engine that implements the complete ruleset
- Support for various AI agent implementations with different strategies
- Process isolation to ensure fair play and prevent cross-agent interference
- Efficient communication of game state to agents
- Reproducible results for research purposes

## Decision

We will implement the following architectural approach:

### 1. Game Engine Architecture

The game engine will follow a Model-View-Controller pattern:

- **Models Layer**: Core game objects and state
  - `common.py`: Contains fundamental game entities (Colors, Tokens, Cards, Tiles)
  - `models/gamestate.py`: Maintains the central game state including decks, rivers, tokens, and tiles
  - `models/player.py`: Tracks player state including tokens, cards, and tiles

- **Controller Layer**: Game logic and rule enforcement
  - `engine.py`: Orchestrates game flow, validates moves, and updates state
  - `rules.py`: Encapsulates game rules and victory conditions

- **Simulation Layer**: Coordinates agent interactions
  - `simulator.py`: Manages game sessions, collects metrics, and presents game state to agents
  - `reporter.py`: Generates analysis reports of game outcomes and agent performance

### 2. Game State Communication

Game state will be communicated to agents through a standardized JSON protocol:

- Each agent receives a complete but tailored view of the game state that includes:
  - Public information (available cards, token pool, opponent information)
  - Private information (agent's hand, reserved cards)
  - Game history (previous moves, significant events)

- The communication will be implemented using:
  - Standard input/output streams for process-based agents
  - API endpoints for network-based agents
  - Direct function calls for in-process agents during development

- State snapshots will be:
  - Serializable for persistence and reproduction
  - Immutable to prevent accidental state modification
  - Versioned to allow forward compatibility

### 3. Agent Architecture

Our implemented architecture uses a class-based approach for agents, with a common interface enabling simple additions of new agent types:

- **Base Agent Class**: An abstract class that defines the interface all agents must implement
  - Provides a standard `take_turn` method signature that agents must override
  - Allows for consistent interaction with the game state

- **Agent Implementation**: Currently implemented agents include:
  - `GreedyBuyer`: An agent that prioritizes purchasing the most expensive affordable cards
    - Has fallback strategies for token collection and card reservation
    - Implements decision-making logic for all legal game actions

- **Agent-Game Interface**:
  - Agents receive a comprehensive game state through their `take_turn` method
  - Agents return a standardized action dictionary describing their chosen move
  - Actions are executed by the main game loop through the `execute_action` function

The action protocol includes:

```python
# Game state passed to agent
game_state = {
  "seed": 42,
  "tokens": {"WHITE": 4, "BLUE": 4, ...},
  "level1_river": [12, 7, 3, 22],
  "level2_river": [34, 41, 27, 33],
  "level3_river": [56, 61, 59, 64],
  "available_tiles": [2, 5, 7],
  "players": [
    {
      "tokens": {"WHITE": 2, "BLUE": 1, ...},
      "cards": {"WHITE": [4, 9], "RED": [17]},
      "reserved_cards": [23],
      "tiles": [],
      "points": 3
    },
    # Other players...
  ]
}

# Action returned by agent
action = {
  "action": "buy",
  "card_index": 34,
  "level": 2
}
# OR
action = {
  "action": "take_tokens",
  "colors": [Color.RED, Color.GREEN, Color.BLUE]
}
# OR
action = {
  "action": "reserve",
  "card_index": 56,
  "level": 3
}
```

This in-process agent architecture provides:
- **Simplicity**: Direct function calls without process overhead
- **Debugging**: Easier to trace and debug agent behavior
- **Development Speed**: Faster iteration during initial development

## Consequences

### Positive

- **Modularity**: Clean separation of concerns with distinct classes for game state, agents, and the main game loop
- **Extensibility**: Abstract Agent base class enables easy addition of new agent types
- **Reproducibility**: Seed-based game initialization ensures reproducible results for analysis
- **Game Logic**: Comprehensive implementation of game rules including buying, reserving cards, and token management
- **Configurability**: Command-line options for number of players, seed, and verbosity

### Current Implementation Status

- **Completed Components**:
  - GameState class with methods for all player actions (buy_card, take_tokens, reserve_card)
  - Player class with token, card, and tile tracking
  - Abstract Agent class defining the agent interface
  - GreedyBuyer agent implementing a complete card acquisition strategy
  - Main game loop with turn management and win condition detection
  - Token logic that ensures proper token return to the shared pool

- **In Progress**:
  - Card and tile data loading from CSV files
  - More sophisticated agent implementations
  - Comprehensive game state visualization

### Challenges and Mitigations

- **Challenge**: Ensuring proper resource tracking (tokens, cards) between players and the game state
  - **Mitigation**: Implemented rigorous token logic in the buy_card method that correctly returns tokens to the pool

- **Challenge**: Creating meaningful agent strategies with limited visibility
  - **Mitigation**: Implemented a GreedyBuyer agent with fallback strategies for multiple situations

- **Challenge**: Balancing code complexity with feature completeness
  - **Mitigation**: Used a phased approach, starting with core game logic before adding advanced features

## Alternatives Considered

### 1. In-Process Agents

- **Pros**: Lower overhead, simpler implementation
- **Cons**: Less security, potential for cheating, cross-agent interference
- **Why Rejected**: Would compromise research integrity and limit future extensions

### 2. Network-Based Communication

- **Pros**: Greater flexibility, support for distributed agents
- **Cons**: Higher complexity and overhead, more points of failure
- **Why Partially Adopted**: Will be supported as an option but not the primary method

### 3. Shared Memory

- **Pros**: Performance benefits, reduced serialization overhead
- **Cons**: More complex synchronization, higher risk of bugs
- **Why Rejected**: Process isolation benefits outweigh the performance gains

## Implementation Notes

Initial implementation will focus on:

1. Core models and game state representation
2. Basic rule enforcement
3. Simple process-based agent communication
4. Minimal set of agent strategies for testing

Future extensions will include:

1. Advanced agent strategies (MCTS, reinforcement learning)
2. Distributed simulation capabilities
3. Enhanced analytics and visualization
4. Optional network-based agent communication
