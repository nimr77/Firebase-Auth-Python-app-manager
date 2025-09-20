#!/bin/bash

# Firebase Admin Console - Setup Script
# This script sets up the project environment and handles dependencies

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project variables
PROJECT_NAME="Firebase Admin Console"
VENV_DIR="venv"
CONFIG_DIR="config"
REQUIREMENTS_FILE="requirements.txt"

# Function to show README
show_readme() {
    echo "📖 Firebase Admin Console - README"
    echo "=================================="
    echo
    
    if [ -f "README.md" ]; then
        # Show first part of README (features and quick start)
        head -50 README.md | sed 's/^# /## /' | sed 's/^## /### /'
        echo
        echo "[Press Enter to continue or 'q' to quit]"
        read -r response
        if [ "$response" = "q" ] || [ "$response" = "Q" ]; then
            echo "Setup cancelled."
            exit 0
        fi
    else
        echo "README.md not found. Proceeding with setup..."
    fi
}

# Function to show app information
show_app_info() {
    echo "🔥 Firebase Admin Console"
    echo "========================="
    echo
    echo "This application provides:"
    echo "• 🔍 User search and management"
    echo "• 🔑 Password reset functionality"
    echo "• 👤 Display name updates"
    echo "• 🧪 Token generation (custom & login test)"
    echo "• 📋 Full UID display with copy instructions"
    echo "• 🎨 Beautiful terminal interface"
    echo
    echo "Setup will:"
    echo "• Create virtual environment"
    echo "• Install dependencies"
    echo "• Validate Firebase configuration"
    echo "• Launch the application"
    echo
}

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python version
check_python_version() {
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        print_status "Python version: $PYTHON_VERSION"
        
        # Check if Python version is 3.7 or higher
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 7) else 1)"; then
            print_success "Python version is compatible (3.7+)"
            return 0
        else
            print_error "Python 3.7 or higher is required"
            return 1
        fi
    else
        print_error "Python 3 is not installed"
        return 1
    fi
}

# Function to create virtual environment
create_virtual_environment() {
    print_status "Creating virtual environment..."
    
    if [ -d "$VENV_DIR" ]; then
        print_warning "Virtual environment already exists"
        read -p "Do you want to recreate it? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_status "Removing existing virtual environment..."
            rm -rf "$VENV_DIR"
        else
            print_status "Using existing virtual environment"
            return 0
        fi
    fi
    
    python3 -m venv "$VENV_DIR"
    print_success "Virtual environment created successfully"
}

# Function to activate virtual environment
activate_virtual_environment() {
    print_status "Activating virtual environment..."
    source "$VENV_DIR/bin/activate"
    print_success "Virtual environment activated"
}

# Function to install dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    if [ ! -f "$REQUIREMENTS_FILE" ]; then
        print_error "Requirements file not found: $REQUIREMENTS_FILE"
        return 1
    fi
    
    pip install --upgrade pip
    pip install -r "$REQUIREMENTS_FILE"
    print_success "Dependencies installed successfully"
}

# Function to check Firebase config
check_firebase_config() {
    print_status "Checking Firebase configuration..."
    
    # Check if config directory exists
    if [ ! -d "$CONFIG_DIR" ]; then
        print_status "Creating config directory..."
        mkdir -p "$CONFIG_DIR"
    fi
    
    # Look for Firebase admin key files
    FIREBASE_KEY_FILES=$(find "$CONFIG_DIR" -name "firebase-admin*.json" 2>/dev/null || true)
    
    if [ -z "$FIREBASE_KEY_FILES" ]; then
        print_warning "No Firebase admin key found in config directory"
        echo
        print_status "To get your Firebase admin key:"
        echo "1. Go to Firebase Console (https://console.firebase.google.com/)"
        echo "2. Select your project"
        echo "3. Go to Project Settings > Service Accounts"
        echo "4. Click 'Generate new private key'"
        echo "5. Download the JSON file"
        echo
        read -p "Enter the path to your Firebase admin JSON file: " FIREBASE_KEY_PATH
        
        if [ -z "$FIREBASE_KEY_PATH" ]; then
            print_error "No path provided. Exiting..."
            exit 1
        fi
        
        if [ ! -f "$FIREBASE_KEY_PATH" ]; then
            print_error "File not found: $FIREBASE_KEY_PATH"
            exit 1
        fi
        
        # Copy the file to config directory
        cp "$FIREBASE_KEY_PATH" "$CONFIG_DIR/firebase-admin-key.json"
        print_success "Firebase admin key copied to config directory"
    else
        print_success "Firebase admin key found: $(basename $FIREBASE_KEY_FILES)"
    fi
}

# Function to validate Firebase config
validate_firebase_config() {
    print_status "Validating Firebase configuration..."
    
    FIREBASE_KEY_FILE=$(find "$CONFIG_DIR" -name "firebase-admin*.json" | head -1)
    
    if [ -z "$FIREBASE_KEY_FILE" ]; then
        print_error "No Firebase admin key file found"
        return 1
    fi
    
    # Check if the JSON file is valid
    if python3 -c "import json; json.load(open('$FIREBASE_KEY_FILE'))" 2>/dev/null; then
        print_success "Firebase admin key file is valid JSON"
        
        # Check for required fields
        REQUIRED_FIELDS=("type" "project_id" "private_key" "client_email")
        for field in "${REQUIRED_FIELDS[@]}"; do
            if ! python3 -c "import json; data=json.load(open('$FIREBASE_KEY_FILE')); exit(0 if '$field' in data else 1)" 2>/dev/null; then
                print_error "Missing required field in Firebase admin key: $field"
                return 1
            fi
        done
        
        print_success "Firebase admin key contains all required fields"
        return 0
    else
        print_error "Invalid JSON file: $FIREBASE_KEY_FILE"
        return 1
    fi
}

# Function to run the application
run_application() {
    print_status "Starting Firebase Admin Console..."
    echo
    
    FIREBASE_KEY_FILE=$(find "$CONFIG_DIR" -name "firebase-admin*.json" | head -1)
    
    if [ -z "$FIREBASE_KEY_FILE" ]; then
        print_error "No Firebase admin key file found"
        exit 1
    fi
    
    print_success "Using Firebase admin key: $(basename $FIREBASE_KEY_FILE)"
    echo
    
    # Run the application
    python app.py "$FIREBASE_KEY_FILE"
}

# Function to show help
show_help() {
    echo "Firebase Admin Console - Setup Script"
    echo
    echo "Usage: $0 [OPTIONS]"
    echo
    echo "Options:"
    echo "  --help, -h          Show this help message"
    echo "  --setup-only        Only setup environment, don't run the app"
    echo "  --run-only          Skip setup and run the app directly"
    echo "  --recreate-venv     Force recreate virtual environment"
    echo "  --readme            Show README documentation and exit"
    echo
    echo "This script will:"
    echo "  1. Show app information and optional README"
    echo "  2. Check Python version compatibility"
    echo "  3. Create/activate virtual environment"
    echo "  4. Install dependencies"
    echo "  5. Check/validate Firebase configuration"
    echo "  6. Run the Firebase Admin Console"
}

# Main function
main() {
    # Parse command line arguments first
    SETUP_ONLY=false
    RUN_ONLY=false
    RECREATE_VENV=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --help|-h)
                show_help
                exit 0
                ;;
            --setup-only)
                SETUP_ONLY=true
                shift
                ;;
            --run-only)
                RUN_ONLY=true
                shift
                ;;
            --recreate-venv)
                RECREATE_VENV=true
                shift
                ;;
            --readme)
                show_readme
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # Show app information
    show_app_info
    
    # Ask if user wants to see README
    echo "Would you like to see the README documentation?"
    read -p "Press Enter to view README, or 'n' to skip: " -r response
    
    if [ "$response" != "n" ] && [ "$response" != "N" ]; then
        show_readme
    fi
    
    echo "🔥 Firebase Admin Console - Setup Script"
    echo "========================================"
    echo
    
    # Skip setup if run-only mode
    if [ "$RUN_ONLY" = false ]; then
        # Check Python version
        if ! check_python_version; then
            print_error "Python version check failed"
            exit 1
        fi
        
        # Create virtual environment
        if [ "$RECREATE_VENV" = true ]; then
            rm -rf "$VENV_DIR"
        fi
        create_virtual_environment
        
        # Activate virtual environment
        activate_virtual_environment
        
        # Install dependencies
        if ! install_dependencies; then
            print_error "Failed to install dependencies"
            exit 1
        fi
        
        # Check Firebase config
        check_firebase_config
        
        # Validate Firebase config
        if ! validate_firebase_config; then
            print_error "Firebase configuration validation failed"
            exit 1
        fi
        
        print_success "Setup completed successfully!"
        echo
        
        if [ "$SETUP_ONLY" = true ]; then
            print_status "Setup completed. You can now run:"
            echo "  source $VENV_DIR/bin/activate"
            echo "  python app.py config/firebase-admin-key.json"
            exit 0
        fi
    else
        # Activate existing virtual environment
        if [ -d "$VENV_DIR" ]; then
            activate_virtual_environment
        else
            print_error "Virtual environment not found. Run setup first."
            exit 1
        fi
    fi
    
    # Run the application
    run_application
}

# Run main function
main "$@"
