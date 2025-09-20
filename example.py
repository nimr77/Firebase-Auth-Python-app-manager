#!/usr/bin/env python3
"""
Example usage of Firebase Admin Console

This script demonstrates how to use the Firebase Admin Console
with a sample Firebase admin JSON file.
"""

import os
import sys
from firebase_service import FirebaseUserService
from cli_interface import FirebaseAdminCLI


def main():
    """Example usage of the Firebase Admin Console."""
    
    # Example Firebase admin JSON path
    admin_json_path = "firebase-admin-key.json"
    
    # Check if the admin JSON file exists
    if not os.path.exists(admin_json_path):
        print("❌ Firebase admin JSON file not found!")
        print("Please create a file named 'firebase-admin-key.json' with your Firebase admin credentials.")
        print("\nTo get your Firebase admin key:")
        print("1. Go to Firebase Console")
        print("2. Navigate to Project Settings > Service Accounts")
        print("3. Click 'Generate new private key'")
        print("4. Save the downloaded JSON file as 'firebase-admin-key.json'")
        sys.exit(1)
    
    try:
        # Initialize Firebase service
        print("🔗 Initializing Firebase connection...")
        firebase_service = FirebaseUserService(admin_json_path)
        print("✅ Connected to Firebase successfully!")
        
        # Initialize CLI
        cli = FirebaseAdminCLI(firebase_service)
        
        # Run the CLI
        cli.run()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
