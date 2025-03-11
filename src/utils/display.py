"""Display utilities for the Splendid Cards game, including ANSI color codes."""

from src.utils.common import Color


class Colors:
    """ANSI color codes for terminal output."""
    WHITE = '\033[97m'       # Bright white
    BLUE = '\033[94m'        # Bright blue
    BLACK = '\033[38;5;180m' # Medium tan color for BLACK
    RED = '\033[91m'         # Bright red
    GREEN = '\033[92m'       # Bright green
    GOLD = '\033[93m'        # Bright yellow for GOLD
    RESET = '\033[0m'        # Reset to default color
    BOLD = '\033[1m'         # Bold text
    UNDERLINE = '\033[4m'    # Underlined text
    
    @staticmethod
    def get_color_code(color_enum):
        """Get the ANSI color code for a given Color enum value.
        
        Args:
            color_enum: Color enum value
            
        Returns:
            str: ANSI color code
        """
        color_map = {
            Color.WHITE: Colors.WHITE,
            Color.BLUE: Colors.BLUE,
            Color.BLACK: Colors.BLACK,
            Color.RED: Colors.RED,
            Color.GREEN: Colors.GREEN,
            Color.GOLD: Colors.GOLD,
        }
        return color_map.get(color_enum, Colors.RESET)
