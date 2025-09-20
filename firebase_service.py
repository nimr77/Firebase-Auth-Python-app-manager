import firebase_admin
from firebase_admin import credentials, auth
from typing import List, Dict, Optional
import json
import os


class FirebaseUserService:
    """Service class for Firebase user management operations."""
    
    def __init__(self, admin_json_path: str):
        """
        Initialize Firebase admin SDK with service account credentials.
        
        Args:
            admin_json_path: Path to the Firebase admin service account JSON file
        """
        if not os.path.exists(admin_json_path):
            raise FileNotFoundError(f"Firebase admin JSON file not found: {admin_json_path}")
        
        # Initialize Firebase Admin SDK
        try:
            cred = credentials.Certificate(admin_json_path)
            firebase_admin.initialize_app(cred)
        except Exception as e:
            raise Exception(f"Failed to initialize Firebase Admin SDK: {str(e)}")
    
    def get_all_users(self) -> List[Dict]:
        """
        Retrieve all users from Firebase Auth.
        
        Returns:
            List of user dictionaries with uid, email, display_name, etc.
        """
        users = []
        try:
            page = auth.list_users()
            while page:
                for user in page.users:
                    user_data = {
                        'uid': user.uid,
                        'email': user.email or 'No email',
                        'display_name': user.display_name or 'No name',
                        'email_verified': user.email_verified,
                        'disabled': user.disabled,
                        'creation_time': user.user_metadata.creation_timestamp,
                        'last_sign_in': user.user_metadata.last_sign_in_timestamp
                    }
                    users.append(user_data)
                page = page.get_next_page()
        except Exception as e:
            raise Exception(f"Failed to retrieve users: {str(e)}")
        
        return users
    
    def search_users(self, query: str, users: List[Dict]) -> List[Dict]:
        """
        Search users by name or email.
        
        Args:
            query: Search query string
            users: List of users to search through
            
        Returns:
            Filtered list of users matching the query
        """
        if not query.strip():
            return users
        
        query_lower = query.lower()
        filtered_users = []
        
        for user in users:
            email_match = query_lower in (user['email'] or '').lower()
            name_match = query_lower in (user['display_name'] or '').lower()
            
            if email_match or name_match:
                filtered_users.append(user)
        
        return filtered_users
    
    def update_user_password(self, uid: str, new_password: str) -> bool:
        """
        Update user password.
        
        Args:
            uid: User ID
            new_password: New password
            
        Returns:
            True if successful, False otherwise
        """
        try:
            auth.update_user(uid, password=new_password)
            return True
        except Exception as e:
            print(f"Error updating password: {str(e)}")
            return False
    
    def update_user_display_name(self, uid: str, new_name: str) -> bool:
        """
        Update user display name.
        
        Args:
            uid: User ID
            new_name: New display name
            
        Returns:
            True if successful, False otherwise
        """
        try:
            auth.update_user(uid, display_name=new_name)
            return True
        except Exception as e:
            print(f"Error updating display name: {str(e)}")
            return False
    
    def get_user_by_uid(self, uid: str) -> Optional[Dict]:
        """
        Get a specific user by UID.
        
        Args:
            uid: User ID
            
        Returns:
            User dictionary or None if not found
        """
        try:
            user = auth.get_user(uid)
            return {
                'uid': user.uid,
                'email': user.email or 'No email',
                'display_name': user.display_name or 'No name',
                'email_verified': user.email_verified,
                'disabled': user.disabled,
                'creation_time': user.user_metadata.creation_timestamp,
                'last_sign_in': user.user_metadata.last_sign_in_timestamp
            }
        except Exception as e:
            print(f"Error getting user: {str(e)}")
            return None
