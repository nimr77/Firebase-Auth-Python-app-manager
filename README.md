# 🔥 Firebase Admin Console

A beautiful CLI application for managing Firebase users with a modern terminal interface.

## Features

- 🔍 **Search Users**: Search by name or email
- 📋 **View All Users**: Display all users in a formatted table
- 🔑 **Reset Passwords**: Update user passwords securely
- 👤 **Update Names**: Change user display names
- 🎨 **Beautiful UI**: Modern terminal interface with colors and formatting
- ⚡ **Fast Loading**: Efficient user loading and caching

## Quick Start

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd firebase_auth_python_console
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup Firebase Admin Key
```bash
# Create a config directory for your Firebase admin key
mkdir config
# Move your Firebase admin JSON file to the config directory
mv your-firebase-admin-key.json config/firebase-admin-key.json
```

### 4. Run the Application
```bash
python app.py config/firebase-admin-key.json
```

## Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Setup

1. **Get Firebase Admin Key**:
   - Go to your Firebase Console
   - Navigate to Project Settings > Service Accounts
   - Click "Generate new private key"
   - Download the JSON file

2. **Run the Application**:
   ```bash
   python app.py path/to/your/firebase-admin-key.json
   ```

## Usage

### Starting the Application
```bash
python app.py ./firebase-admin-key.json
```

### Main Menu Options

1. **🔍 Search Users** - Search users by name or email
2. **🔄 Refresh Users** - Reload all users from Firebase
3. **🔑 Update User Password** - Reset a user's password
4. **👤 Update User Display Name** - Change a user's display name
5. **📋 Show All Users** - Display all users in a table
6. **❌ Exit** - Close the application

### Example Workflow

1. Start the app with your Firebase admin JSON
2. The app will automatically load all users
3. Use the search function to find specific users
4. Select a user by UID to update their information
5. Confirm changes before applying them

## Requirements

- Python 3.7+
- Firebase project with Authentication enabled
- Firebase Admin SDK service account key

## Dependencies

- `firebase-admin` - Firebase Admin SDK
- `rich` - Beautiful terminal formatting
- `click` - Command line interface
- `colorama` - Cross-platform colored terminal text

## Project Structure

```
firebase_auth_python_console/
├── app.py                 # Main application entry point
├── firebase_service.py    # Firebase service layer
├── cli_interface.py       # Terminal UI interface
├── example.py             # Example usage script
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── .gitignore            # Git ignore rules
└── config/               # Configuration folder (ignored by Git)
    └── firebase-admin-key.json  # Your Firebase admin key
```

## Security Notes

- Keep your Firebase admin JSON file secure
- Never commit the admin JSON file to version control
- The application handles password input securely (hidden input)
- The `config/` folder is automatically ignored by Git

## Troubleshooting

### Common Issues

1. **"Invalid Firebase admin JSON file"**
   - Ensure the JSON file contains all required fields
   - Check that the file is not corrupted

2. **"Failed to initialize Firebase Admin SDK"**
   - Verify your Firebase project is active
   - Check that Authentication is enabled in Firebase Console

3. **"No users found"**
   - Ensure users exist in your Firebase Authentication
   - Check Firebase project permissions

### Getting Help

If you encounter issues:
1. Check your Firebase admin JSON file format
2. Verify Firebase project settings
3. Ensure all dependencies are installed correctly

## Git Setup

This project is already initialized as a Git repository. Here's how to set it up:

### Initial Setup
```bash
# The repository is already initialized
git status
```

### Adding Files
```bash
# Add all files (config folder will be ignored)
git add .

# Commit your changes
git commit -m "Initial commit: Firebase Admin Console"
```

### Remote Repository
```bash
# Add your remote repository
git remote add origin <your-repo-url>

# Push to remote
git push -u origin main
```

### Important Notes
- The `config/` folder is automatically ignored by Git
- Firebase admin JSON files are ignored for security
- Python cache files and virtual environments are ignored
- IDE and OS-specific files are ignored

## License

This project is open source and available under the MIT License.
