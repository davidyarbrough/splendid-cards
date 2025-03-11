from src.common import Color

class Player:
    def __init__(self, name=None):
        self.name = name  # Optional name for the player
        self.tokens = {
            Color.WHITE: 0,
            Color.BLUE: 0,
            Color.BLACK: 0,
            Color.RED: 0,
            Color.GREEN: 0,
            Color.GOLD: 0
        }
        self.cards = {
            Color.WHITE: [],
            Color.BLUE: [],
            Color.BLACK: [],
            Color.RED: [],
            Color.GREEN: []
        }
        self.reserved_cards = []  # List of card indices that are reserved but not yet purchased
        self.tiles = []  # List of tile indices claimed by this player