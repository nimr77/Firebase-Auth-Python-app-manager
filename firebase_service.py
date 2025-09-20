import firebase_admin
from firebase_admin import credentials, auth
from typing import List, Dict, Optional, Tuple
import json
import os
import requests


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
    
    def test_user_login(self, email: str, password: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Test user login and get authentication token.
        
        Args:
            email: User email
            password: User password
            
        Returns:
            Tuple of (success, token, error_message)
        """
        try:
            # Get Firebase project configuration
            project_id = self._get_project_id()
            if not project_id:
                return False, None, "Could not determine Firebase project ID"
            
            # Firebase Auth REST API endpoint
            auth_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self._get_api_key()}"
            
            # Prepare request data
            data = {
                "email": email,
                "password": password,
                "returnSecureToken": True
            }
            
            # Make the request
            response = requests.post(auth_url, json=data)
            
            if response.status_code == 200:
                result = response.json()
                token = result.get('idToken')
                return True, token, None
            else:
                error_data = response.json()
                error_message = error_data.get('error', {}).get('message', 'Unknown error')
                return False, None, error_message
                
        except Exception as e:
            return False, None, f"Login test failed: {str(e)}"
    
    def _get_project_id(self) -> Optional[str]:
        """Get Firebase project ID from admin credentials."""
        try:
            # Try to get project ID from the app
            app = firebase_admin.get_app()
            return app.project_id
        except:
            return None
    
    def _get_api_key(self) -> Optional[str]:
        """Get Firebase Web API key from admin credentials."""
        try:
            # This is a simplified approach - in production, you'd want to store this securely
            # For now, we'll try to extract it from the credentials
            return None  # This would need to be configured separately
        except:
            return None
    
    def test_login_with_api_key(self, email: str, password: str, api_key: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Test user login with provided API key.
        
        Args:
            email: User email
            password: User password
            api_key: Firebase Web API key
            
        Returns:
            Tuple of (success, token, error_message)
        """
        try:
            # Get Firebase project configuration
            project_id = self._get_project_id()
            if not project_id:
                return False, None, "Could not determine Firebase project ID"
            
            # Firebase Auth REST API endpoint
            auth_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
            
            # Prepare request data
            data = {
                "email": email,
                "password": password,
                "returnSecureToken": True
            }
            
            # Make the request
            response = requests.post(auth_url, json=data)
            
            if response.status_code == 200:
                result = response.json()
                token = result.get('idToken')
                refresh_token = result.get('refreshToken')
                return True, token, None
            else:
                error_data = response.json()
                error_message = error_data.get('error', {}).get('message', 'Unknown error')
                return False, None, error_message
                
        except Exception as e:
            return False, None, f"Login test failed: {str(e)}"
