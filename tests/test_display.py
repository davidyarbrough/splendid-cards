import unittest
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.display import Colors
from src.utils.common import Color


class TestColors(unittest.TestCase):
    """Test the Colors class."""
    
    def test_color_code_mapping(self):
        """Test that color codes are correctly mapped to Color enum values."""
        self.assertEqual(Colors.get_color_code(Color.WHITE), Colors.WHITE)
        self.assertEqual(Colors.get_color_code(Color.BLUE), Colors.BLUE)
        self.assertEqual(Colors.get_color_code(Color.BLACK), Colors.BLACK)
        self.assertEqual(Colors.get_color_code(Color.RED), Colors.RED)
        self.assertEqual(Colors.get_color_code(Color.GREEN), Colors.GREEN)
        self.assertEqual(Colors.get_color_code(Color.GOLD), Colors.GOLD)
        
        # Test with a non-existing color (should return RESET)
        # Creating a mock value that's not in the Color enum
        self.assertEqual(Colors.get_color_code(None), Colors.RESET)
        
    def test_color_formatting(self):
        """Test color formatting by checking if the codes match expected ANSI escape sequences."""
        self.assertTrue(Colors.WHITE.startswith('\033['))
        self.assertTrue(Colors.BLUE.startswith('\033['))
        self.assertTrue(Colors.BLACK.startswith('\033['))
        self.assertTrue(Colors.RED.startswith('\033['))
        self.assertTrue(Colors.GREEN.startswith('\033['))
        self.assertTrue(Colors.GOLD.startswith('\033['))
        self.assertTrue(Colors.RESET.startswith('\033['))
        
        # Check specific codes we know
        self.assertEqual(Colors.RESET, '\033[0m')
        self.assertEqual(Colors.BOLD, '\033[1m')
        self.assertEqual(Colors.UNDERLINE, '\033[4m')


if __name__ == '__main__':
    unittest.main()
