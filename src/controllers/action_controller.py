"""Game action execution controller for the Splendid Cards game."""

def execute_action(game_state, player_idx, action):
    """Execute a player's action on the game state.
    
    Args:
        game_state: Current GameState object
        player_idx: Index of the player making the action
        action: Action object representing the player's chosen action
        
    Returns:
        bool: Whether the action was executed successfully
    """
    try:
        action_type = action.get("action")
        
        if action_type == "take_tokens":
            # Take tokens action
            tokens = action.get("colors", [])
            game_state.take_tokens(player_idx, tokens)
            print(f"Player {player_idx + 1} takes tokens: {', '.join([color.value.upper() for color in tokens])}")
            return True
            
        elif action_type == "buy":
            # Buy card action
            card_idx = action.get("card_index")
            
            # Check if card is in the player's reserved cards to determine source for display
            is_reserved = card_idx in game_state.players[player_idx].reserved_cards
            
            # Determine the card level for display purposes
            if is_reserved:
                source = "reserved cards"
            else:
                # Try to determine the level for display purposes only
                if card_idx in game_state.level1_river:
                    source = "level 1"
                elif card_idx in game_state.level2_river:
                    source = "level 2"
                elif card_idx in game_state.level3_river:
                    source = "level 3"
                else:
                    source = "unknown source"
            
            # Execute the purchase - no level parameter needed now
            returned_tokens = game_state.buy_card(player_idx, card_idx)
            
            # Format the returned tokens for display
            returned_token_str = ""
            if returned_tokens:
                returned_token_str = " returned tokens: " + str(returned_tokens)
            
            print(f"Player {player_idx + 1} buys card {card_idx} from {source}{returned_token_str}")
            return True
            
        elif action_type == "reserve":
            # Reserve card action
            card_idx = action.get("card_index")
            level = action.get("level", 1)  # Default to level 1 if not specified
            gold_taken = game_state.reserve_card(player_idx, card_idx, level)
            
            level_str = f"level {level}"
            gold_str = " and took a gold token" if gold_taken else ""
            
            print(f"Player {player_idx + 1} reserves card {card_idx} from {level_str}{gold_str}")
            return True
            
        elif action_type == "claim_tile":
            # Claim tile action
            tile_idx = action.get("tile_index")
            success = game_state.claim_tile(player_idx, tile_idx)
            
            if success:
                print(f"Player {player_idx + 1} claims tile {tile_idx}")
                return True
            else:
                print(f"Player {player_idx + 1} failed to claim tile {tile_idx}")
                return False
            
        else:
            print(f"Unknown action type: {action_type}")
            return False
            
    except Exception as e:
        print(f"Error executing action: {e}")
        return False
