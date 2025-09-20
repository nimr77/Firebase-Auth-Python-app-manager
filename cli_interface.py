import os
from typing import List, Dict, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich.layout import Layout
from rich.live import Live
from rich import box
from firebase_service import FirebaseUserService


class FirebaseAdminCLI:
    """CLI interface for Firebase user management."""
    
    def __init__(self, firebase_service: FirebaseUserService):
        self.firebase_service = firebase_service
        self.console = Console()
        self.users: List[Dict] = []
        self.filtered_users: List[Dict] = []
        
    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_header(self):
        """Display the application header."""
        header_text = Text("🔥 Firebase Admin Console", style="bold blue")
        subtitle = Text("User Management System", style="italic green")
        
        header_panel = Panel(
            f"{header_text}\n{subtitle}",
            box=box.DOUBLE,
            style="blue"
        )
        self.console.print(header_panel)
        self.console.print()
    
    def display_users_table(self, users: List[Dict], title: str = "Users"):
        """Display users in a formatted table."""
        if not users:
            self.console.print("[yellow]No users found.[/yellow]")
            return
        
        table = Table(title=title, box=box.ROUNDED)
        table.add_column("UID", style="cyan", width=20)
        table.add_column("Email", style="green", width=30)
        table.add_column("Display Name", style="magenta", width=25)
        table.add_column("Verified", style="yellow", width=10)
        table.add_column("Status", style="red", width=10)
        
        for user in users:
            verified_status = "✅ Yes" if user['email_verified'] else "❌ No"
            account_status = "🔒 Disabled" if user['disabled'] else "✅ Active"
            
            table.add_row(
                user['uid'][:20] + "..." if len(user['uid']) > 20 else user['uid'],
                user['email'][:30] + "..." if len(user['email']) > 30 else user['email'],
                user['display_name'][:25] + "..." if len(user['display_name']) > 25 else user['display_name'],
                verified_status,
                account_status
            )
        
        self.console.print(table)
        self.console.print(f"\n[dim]Total users: {len(users)}[/dim]")
    
    def load_users(self):
        """Load all users from Firebase."""
        try:
            self.console.print("[blue]Loading users from Firebase...[/blue]")
            self.users = self.firebase_service.get_all_users()
            self.filtered_users = self.users.copy()
            self.console.print(f"[green]✅ Loaded {len(self.users)} users successfully![/green]")
        except Exception as e:
            self.console.print(f"[red]❌ Error loading users: {str(e)}[/red]")
            self.users = []
            self.filtered_users = []
    
    def search_users(self):
        """Search users by name or email."""
        query = Prompt.ask("\n[cyan]Enter search query (name or email)")
        
        if not query.strip():
            self.filtered_users = self.users.copy()
        else:
            self.filtered_users = self.firebase_service.search_users(query, self.users)
        
        self.clear_screen()
        self.display_header()
        self.display_users_table(self.filtered_users, f"Search Results for: '{query}'")
    
    def show_user_details(self, user: Dict):
        """Show detailed information about a specific user."""
        details_panel = Panel(
            f"""
[bold cyan]UID:[/bold cyan] {user['uid']}
[bold green]Email:[/bold green] {user['email']}
[bold magenta]Display Name:[/bold magenta] {user['display_name']}
[bold yellow]Email Verified:[/bold yellow] {'Yes' if user['email_verified'] else 'No'}
[bold red]Account Status:[/bold red] {'Disabled' if user['disabled'] else 'Active'}
[bold blue]Created:[/bold blue] {user['creation_time']}
[bold blue]Last Sign In:[/bold blue] {user['last_sign_in'] or 'Never'}
            """,
            title="User Details",
            box=box.DOUBLE,
            style="blue"
        )
        self.console.print(details_panel)
    
    def update_user_password(self):
        """Update user password."""
        uid = Prompt.ask("\n[cyan]Enter user UID")
        
        # Find user
        user = None
        for u in self.users:
            if u['uid'] == uid:
                user = u
                break
        
        if not user:
            self.console.print("[red]❌ User not found![/red]")
            return
        
        self.show_user_details(user)
        
        if not Confirm.ask("\n[yellow]Do you want to update this user's password?"):
            return
        
        new_password = Prompt.ask("[cyan]Enter new password", password=True)
        confirm_password = Prompt.ask("[cyan]Confirm new password", password=True)
        
        if new_password != confirm_password:
            self.console.print("[red]❌ Passwords don't match![/red]")
            return
        
        if self.firebase_service.update_user_password(uid, new_password):
            self.console.print("[green]✅ Password updated successfully![/green]")
        else:
            self.console.print("[red]❌ Failed to update password![/red]")
    
    def update_user_name(self):
        """Update user display name."""
        uid = Prompt.ask("\n[cyan]Enter user UID")
        
        # Find user
        user = None
        for u in self.users:
            if u['uid'] == uid:
                user = u
                break
        
        if not user:
            self.console.print("[red]❌ User not found![/red]")
            return
        
        self.show_user_details(user)
        
        if not Confirm.ask("\n[yellow]Do you want to update this user's display name?"):
            return
        
        new_name = Prompt.ask("[cyan]Enter new display name")
        
        if self.firebase_service.update_user_display_name(uid, new_name):
            self.console.print("[green]✅ Display name updated successfully![/green]")
            # Refresh users to get updated data
            self.load_users()
        else:
            self.console.print("[red]❌ Failed to update display name![/red]")
    
    def show_main_menu(self):
        """Display the main menu."""
        menu_panel = Panel(
            """
[bold cyan]1.[/bold cyan] 🔍 Search Users
[bold cyan]2.[/bold cyan] 🔄 Refresh Users
[bold cyan]3.[/bold cyan] 🔑 Update User Password
[bold cyan]4.[/bold cyan] 👤 Update User Display Name
[bold cyan]5.[/bold cyan] 📋 Show All Users
[bold cyan]6.[/bold cyan] ❌ Exit
            """,
            title="Main Menu",
            box=box.ROUNDED,
            style="green"
        )
        self.console.print(menu_panel)
    
    def run(self):
        """Main application loop."""
        self.clear_screen()
        self.display_header()
        
        # Load users initially
        self.load_users()
        
        while True:
            self.clear_screen()
            self.display_header()
            
            if self.filtered_users:
                self.display_users_table(self.filtered_users)
            
            self.show_main_menu()
            
            choice = Prompt.ask(
                "\n[bold cyan]Select an option",
                choices=["1", "2", "3", "4", "5", "6"],
                default="1"
            )
            
            if choice == "1":
                self.search_users()
            elif choice == "2":
                self.load_users()
            elif choice == "3":
                self.update_user_password()
            elif choice == "4":
                self.update_user_name()
            elif choice == "5":
                self.filtered_users = self.users.copy()
                self.clear_screen()
                self.display_header()
                self.display_users_table(self.filtered_users)
            elif choice == "6":
                self.console.print("\n[green]👋 Goodbye![/green]")
                break
            
            if choice != "6":
                Prompt.ask("\n[dim]Press Enter to continue...[/dim]")
