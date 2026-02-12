"""
Example usage of the Our Family Wizard Python Client
"""

from ofw_client import OFWClient
import os
from getpass import getpass


def main():
    """Example of how to use the OFW client."""
    
    # Initialize the client
    client = OFWClient()
    
    # Get credentials (in production, use environment variables or secure storage)
    username = input("Enter your OFW username/email: ")
    password = getpass("Enter your OFW password: ")
    
    # Login
    print("\n" + "="*50)
    print("Attempting to login...")
    print("="*50 + "\n")
    
    success = client.login(username, password)
    
    if success:
        print("\n✓ Login successful!")
        
        # Display session information
        print("\nSession Information:")
        print("-" * 50)
        session_info = client.get_session_info()
        for key, value in session_info.items():
            print(f"{key}: {value}")
        
        # Here you can add more functionality:
        # - Read messages
        # - Send messages
        # - Get expenses
        # - Create expenses
        # etc.
        
        # Logout when done
        input("\nPress Enter to logout...")
        client.logout()
        print("✓ Logged out successfully")
    else:
        print("\n✗ Login failed. Please check your credentials and try again.")


if __name__ == "__main__":
    main()
