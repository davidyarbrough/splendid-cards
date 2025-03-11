# this file defines common objects that are used by the model
from enum import Enum
import random
import time
import csv
import os

class Color(Enum):
    WHITE = 'wht'
    BLUE = 'blu'
    BLACK = 'blk'
    RED = 'red'
    GREEN = 'grn'
    GOLD = 'gld'

class Token():
    color: Color

class CardCost():
    cost: dict = {Color: int}

class Card():
    color: Color
    cost: CardCost
    points: int

class Tile():
    cost: dict = {Color: int}
    points: int

def shuffleDecks(seed=None):
    """Create and shuffle the three decks of cards according to the seed provided.
    
    Args:
        seed: Optional integer to seed the random number generator. If None, uses current time.
        
    Returns:
        A tuple of three lists (level1_deck, level2_deck, level3_deck), each containing indices
        of cards from cards.csv, shuffled according to the seed.
    """
    if seed is None:
        seed = int(time.time())
    rng = random.Random(seed)
    
    # Initialize empty decks for each level
    level1_deck = []
    level2_deck = []
    level3_deck = []
    
    # Read cards from CSV file
    # Calculate the project root directory and find cards.csv
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))  # Go up two levels from utils to project root
    csv_path = os.path.join(project_root, 'data', 'cards.csv')
    
    with open(csv_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            card_index = int(row['index'])
            deck_level = int(row['deck'])
            
            # Add card index to the appropriate deck
            if deck_level == 1:
                level1_deck.append(card_index)
            elif deck_level == 2:
                level2_deck.append(card_index)
            elif deck_level == 3:
                level3_deck.append(card_index)
    
    # Shuffle the decks using the seeded random generator
    rng.shuffle(level1_deck)
    rng.shuffle(level2_deck)
    rng.shuffle(level3_deck)
    
    return (level1_deck, level2_deck, level3_deck)

def shuffleTiles(seed=None):
    """Create and shuffle the tiles according to the seed provided.
    
    Args:
        seed: Optional integer to seed the random number generator. If None, uses current time. 
        
    Returns:
        A list of tile indices, shuffled according to the seed."""
    if seed is None:
        seed = int(time.time())
    rng = random.Random(seed)
    
    # Read tiles from CSV file
    # Calculate the project root directory and find tiles.csv
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))  # Go up two levels from utils to project root
    csv_path = os.path.join(project_root, 'data', 'tiles.csv')
    
    with open(csv_path, 'r') as file:
        reader = csv.DictReader(file)
        tiles = [int(row['index']) for row in reader]
    
    # Shuffle the tiles using the seeded random generator
    rng.shuffle(tiles)
    
    return tiles
