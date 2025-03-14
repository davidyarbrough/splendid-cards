"""Logging functionality for the Splendid Cards game."""

import os
import time
import datetime
from pathlib import Path


class GameLogger:
    """Logger class for capturing and recording game output to a file."""
    
    def __init__(self):
        """Initialize the logger."""
        self.log_file = None
        self.original_print = print  # Store the original print function
        self.current_log_path = None
    
    def setup(self):
        """Set up the logging system and redirect stdout to the log file.
        
        Returns:
            str: Path to the log file that was created.
        """
        # Ensure the logs directory exists
        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        log_dir = os.path.join(current_dir, 'gamelogs')
        os.makedirs(log_dir, exist_ok=True)
        
        # Create a timestamped log file
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = os.path.join(log_dir, f"game_{timestamp}.log")
        
        # Store the log path for later reference
        self.current_log_path = log_filename
        
        # Open the log file
        self.log_file = open(log_filename, 'w')
        
        # Override the built-in print function
        import builtins
        import re
        
        # Regular expression to match ANSI escape codes
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        
        def custom_print(*args, **kwargs):
            # Call the original print function
            self.original_print(*args, **kwargs)
            
            # Also write to the log file, but remove ANSI color codes
            if 'file' not in kwargs:  # Only log what's printed to stdout
                # Convert args to strings and strip ANSI codes
                clean_args = []
                for arg in args:
                    if isinstance(arg, str):
                        clean_args.append(ansi_escape.sub('', arg))
                    else:
                        clean_args.append(arg)
                
                print(*clean_args, file=self.log_file, **{k: v for k, v in kwargs.items() if k != 'flush'})
                self.log_file.flush()  # Ensure it's written immediately
        
        builtins.print = custom_print
        
        return log_filename
    
    def close(self):
        """Close the log file and restore the original print function."""
        if self.log_file:
            # Restore the original print function
            import builtins
            builtins.print = self.original_print
            
            # Close the log file
            self.log_file.close()
            
    def get_current_round(self):
        """Parse the game log to extract the current round number.
        
        Returns:
            int: The current (or final) round number from the game log, or None if not found.
        """
        import re
        import os
        
        # If we don't have a log file path, return None
        if not self.current_log_path or not os.path.exists(self.current_log_path):
            # Try to find the most recent log file
            current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            log_dir = os.path.join(current_dir, 'gamelogs')
            
            if not os.path.exists(log_dir):
                return None
                
            log_files = sorted(
                [os.path.join(log_dir, f) for f in os.listdir(log_dir) if f.endswith('.log')],
                key=os.path.getmtime,
                reverse=True
            )
            
            if not log_files:
                return None
                
            self.current_log_path = log_files[0]
        
        # Regular expression to match round information
        round_regex = re.compile(r'Turn \d+ - Round (\d+)')
        
        # If the log file is currently open, we need to flush it first
        if self.log_file and not self.log_file.closed:
            self.log_file.flush()
        
        # Parse the log file to find the highest round number
        highest_round = 0
        with open(self.current_log_path, 'r') as f:
            for line in f:
                match = round_regex.search(line)
                if match:
                    round_num = int(match.group(1))
                    highest_round = max(highest_round, round_num)
        
        return highest_round if highest_round > 0 else None

# Create global logger instance
game_logger = GameLogger()
