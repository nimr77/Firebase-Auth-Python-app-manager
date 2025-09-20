#!/usr/bin/env python3
"""
Firebase Admin Console - User Management System

A beautiful CLI application for managing Firebase users.
Supports searching, password resets, and display name updates.

Usage:
    python app.py <path_to_firebase_admin_json>

Example:
    python app.py ./firebase-admin-key.json
"""

import sys
import os
import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box
from firebase_service import FirebaseUserService
from cli_interface import FirebaseAdminCLI


def validate_firebase_json(json_path: str) -> bool:
    """Validate that the Firebase admin JSON file exists and is readable."""
    if not os.path.exists(json_path):
        return False
    
    try:
        import json
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        # Check for required Firebase admin fields
        required_fields = ['type', 'project_id', 'private_key', 'client_email']
        return all(field in data for field in required_fields)
    except (json.JSONDecodeError, IOError):
        return False


def show_readme(console: Console):
    """Display README documentation."""
    readme_path = "README.md"
    
    if not os.path.exists(readme_path):
        console.print("[red]❌ README.md not found![/red]")
        return
    
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            readme_content = f.read()
        
        # Display README in a panel
        readme_panel = Panel(
            readme_content,
            title="📖 Firebase Admin Console - Documentation",
            box=box.DOUBLE,
            style="blue"
        )
        console.print(readme_panel)
        
    except Exception as e:
        console.print(f"[red]❌ Error reading README: {str(e)}[/red]")


@click.command()
@click.argument('admin_json_path', type=click.Path(exists=True))
@click.option('--readme', is_flag=True, help='Show README documentation and exit')
def main(admin_json_path: str, readme: bool):
    """
    Firebase Admin Console - User Management System
    
    ADMIN_JSON_PATH: Path to your Firebase admin service account JSON file
    """
    console = Console()
    
    # Show README if requested
    if readme:
        show_readme(console)
        return
    
    # Display welcome message
    welcome_text = Text("🔥 Firebase Admin Console", style="bold blue")
    subtitle = Text("User Management System", style="italic green")
    
    welcome_panel = Panel(
        f"{welcome_text}\n{subtitle}\n\n[dim]Initializing Firebase connection...[/dim]",
        box=box.DOUBLE,
        style="blue"
    )
    console.print(welcome_panel)
    
    try:
        # Validate Firebase admin JSON
        if not validate_firebase_json(admin_json_path):
            console.print("[red]❌ Invalid Firebase admin JSON file![/red]")
            console.print("[yellow]Please ensure the file contains all required fields:[/yellow]")
            console.print("[dim]  - type, project_id, private_key, client_email[/dim]")
            sys.exit(1)
        
        # Initialize Firebase service
        console.print("[blue]🔗 Connecting to Firebase...[/blue]")
        firebase_service = FirebaseUserService(admin_json_path)
        console.print("[green]✅ Connected to Firebase successfully![/green]")
        
        # Initialize and run CLI
        cli = FirebaseAdminCLI(firebase_service)
        cli.run()
        
    except FileNotFoundError as e:
        console.print(f"[red]❌ File not found: {str(e)}[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]❌ Error initializing Firebase: {str(e)}[/red]")
        console.print("[yellow]Please check your Firebase admin JSON file and try again.[/yellow]")
        sys.exit(1)


if __name__ == "__main__":
    main()
