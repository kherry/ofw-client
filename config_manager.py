"""
Secure configuration management for OFW credentials
"""

import os
from pathlib import Path
from typing import Optional


class OFWConfig:
    """Configuration manager for OFW credentials."""
    
    @staticmethod
    def from_env() -> tuple[Optional[str], Optional[str]]:
        """
        Load credentials from environment variables.
        
        Set these environment variables:
        - OFW_USERNAME or OFW_EMAIL
        - OFW_PASSWORD
        
        Returns:
            Tuple of (username, password)
        """
        username = os.getenv('OFW_USERNAME') or os.getenv('OFW_EMAIL')
        password = os.getenv('OFW_PASSWORD')
        return username, password
    
    @staticmethod
    def from_file(filepath: str = '.env') -> tuple[Optional[str], Optional[str]]:
        """
        Load credentials from a .env file.
        
        File format:
        OFW_USERNAME=your_username
        OFW_PASSWORD=your_password
        
        Args:
            filepath: Path to the .env file
            
        Returns:
            Tuple of (username, password)
        """
        env_path = Path(filepath)
        if not env_path.exists():
            return None, None
        
        credentials = {}
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    credentials[key.strip()] = value.strip()
        
        username = credentials.get('OFW_USERNAME') or credentials.get('OFW_EMAIL')
        password = credentials.get('OFW_PASSWORD')
        return username, password


# Example usage
if __name__ == "__main__":
    from ofw_client import OFWClient
    
    # Try environment variables first
    username, password = OFWConfig.from_env()
    
    # Fall back to .env file
    if not username or not password:
        username, password = OFWConfig.from_file('.env')
    
    # Prompt if neither worked
    if not username or not password:
        from getpass import getpass
        username = input("Enter OFW username: ")
        password = getpass("Enter OFW password: ")
    
    # Login
    client = OFWClient()
    if client.login(username, password):
        print("✓ Logged in successfully!")
        print(f"\nSession info: {client.get_session_info()}")
        
        input("\nPress Enter to logout...")
        client.logout()
    else:
        print("✗ Login failed")
