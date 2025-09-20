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
        table.add_column("UID", style="bold cyan", width=50)  # Bold and increased width for full UID
        table.add_column("Email", style="green", width=35)
        table.add_column("Display Name", style="magenta", width=25)
        table.add_column("Verified", style="yellow", width=10)
        table.add_column("Status", style="red", width=10)
        
        for user in users:
            verified_status = "✅ Yes" if user['email_verified'] else "❌ No"
            account_status = "🔒 Disabled" if user['disabled'] else "✅ Active"
            
            table.add_row(
                user['uid'],  # Show full UID without truncation
                user['email'][:35] + "..." if len(user['email']) > 35 else user['email'],
                user['display_name'][:25] + "..." if len(user['display_name']) > 25 else user['display_name'],
                verified_status,
                account_status
            )
        
        self.console.print(table)
        self.console.print(f"\n[dim]Total users: {len(users)}[/dim]")
        
        # Show copy instructions after table
        copy_instructions = Panel(
            """
[bold yellow]📋 To copy the UID:[/bold yellow]
[dim]Select the UID text above and copy it (Cmd+C on Mac, Ctrl+C on Windows/Linux)[/dim]
            """,
            box=box.ROUNDED,
            style="yellow"
        )
        self.console.print(copy_instructions)
    
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
        
        # Show copy instructions
        copy_panel = Panel(
            f"""
[bold yellow]📋 To copy the UID:[/bold yellow]
[dim]Select the UID text above and copy it (Cmd+C on Mac, Ctrl+C on Windows/Linux)[/dim]

[bold cyan]UID:[/bold cyan] {user['uid']}
            """,
            title="Copy Instructions",
            box=box.ROUNDED,
            style="yellow"
        )
        self.console.print(copy_panel)
    
    def show_password_strength(self, password: str):
        """Show password strength with visual indicators."""
        length = len(password)
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        
        strength_score = 0
        if length >= 8:
            strength_score += 1
        if length >= 12:
            strength_score += 1
        if has_upper:
            strength_score += 1
        if has_lower:
            strength_score += 1
        if has_digit:
            strength_score += 1
        if has_special:
            strength_score += 1
        
        # Create strength bar
        strength_bar = ""
        colors = ["red", "yellow", "green"]
        strength_levels = ["Weak", "Medium", "Strong"]
        
        for i in range(3):
            if i < strength_score // 2:
                strength_bar += f"[{colors[min(i, 2)]}]●[/{colors[min(i, 2)]}]"
            else:
                strength_bar += "[dim]○[/dim]"
        
        strength_text = strength_levels[min(strength_score // 2, 2)]
        strength_color = colors[min(strength_score // 2, 2)]
        
        strength_panel = Panel(
            f"""
[bold {strength_color}]Password Strength: {strength_text}[/bold {strength_color}]
{strength_bar}

[dim]Length: {length} characters[/dim]
[dim]Uppercase: {'✅' if has_upper else '❌'} Lowercase: {'✅' if has_lower else '❌'}[/dim]
[dim]Numbers: {'✅' if has_digit else '❌'} Special chars: {'✅' if has_special else '❌'}[/dim]
            """,
            title="Password Analysis",
            box=box.ROUNDED,
            style=strength_color
        )
        self.console.print(strength_panel)

    def update_user_password(self):
        """Update user password with retry logic and back option."""
        while True:
            uid = Prompt.ask("\n[cyan]Enter user UID (or 'back' to return to menu)")
            
            if uid.lower() == 'back':
                return
            
            # Find user
            user = None
            for u in self.users:
                if u['uid'] == uid:
                    user = u
                    break
            
            if not user:
                self.console.print("[red]❌ User not found![/red]")
                continue
            
            self.clear_screen()
            self.display_header()
            self.show_user_details(user)
            
            if not Confirm.ask("\n[yellow]Do you want to update this user's password?"):
                return
            
            # Password input with retry logic
            while True:
                self.console.print("\n[bold cyan]Password Requirements:[/bold cyan]")
                self.console.print("[dim]• At least 8 characters long[/dim]")
                self.console.print("[dim]• Mix of uppercase, lowercase, numbers, and special characters[/dim]")
                self.console.print("[dim]• Type 'back' at any time to return to menu[/dim]")
                
                new_password = Prompt.ask("\n[cyan]Enter new password", password=True)
                
                if new_password.lower() == 'back':
                    return
                
                # Show password strength
                self.show_password_strength(new_password)
                
                confirm_password = Prompt.ask("[cyan]Confirm new password", password=True)
                
                if confirm_password.lower() == 'back':
                    return
                
                if new_password != confirm_password:
                    self.console.print("[red]❌ Passwords don't match! Please try again.[/red]")
                    if not Confirm.ask("[yellow]Do you want to try again?"):
                        return
                    continue
                
                # Password validation
                if len(new_password) < 8:
                    self.console.print("[red]❌ Password must be at least 8 characters long![/red]")
                    if not Confirm.ask("[yellow]Do you want to try again?"):
                        return
                    continue
                
                # Attempt to update password
                if self.firebase_service.update_user_password(uid, new_password):
                    self.console.print("[green]✅ Password updated successfully![/green]")
                    return
                else:
                    self.console.print("[red]❌ Failed to update password![/red]")
                    if not Confirm.ask("[yellow]Do you want to try again?"):
                        return
                    continue
    
    def update_user_name(self):
        """Update user display name with back option."""
        while True:
            uid = Prompt.ask("\n[cyan]Enter user UID (or 'back' to return to menu)")
            
            if uid.lower() == 'back':
                return
            
            # Find user
            user = None
            for u in self.users:
                if u['uid'] == uid:
                    user = u
                    break
            
            if not user:
                self.console.print("[red]❌ User not found![/red]")
                continue
            
            self.clear_screen()
            self.display_header()
            self.show_user_details(user)
            
            if not Confirm.ask("\n[yellow]Do you want to update this user's display name?"):
                return
            
            new_name = Prompt.ask("[cyan]Enter new display name (or 'back' to return)")
            
            if new_name.lower() == 'back':
                return
            
            if self.firebase_service.update_user_display_name(uid, new_name):
                self.console.print("[green]✅ Display name updated successfully![/green]")
                # Refresh users to get updated data
                self.load_users()
                return
            else:
                self.console.print("[red]❌ Failed to update display name![/red]")
                if not Confirm.ask("[yellow]Do you want to try again?"):
                    return
                continue
    
    def view_user_details(self):
        """View detailed information about a specific user."""
        uid = Prompt.ask("\n[cyan]Enter user UID (or 'back' to return to menu)")
        
        if uid.lower() == 'back':
            return
        
        # Find user
        user = None
        for u in self.users:
            if u['uid'] == uid:
                user = u
                break
        
        if not user:
            self.console.print("[red]❌ User not found![/red]")
            return
        
        self.clear_screen()
        self.display_header()
        self.show_user_details(user)
    
    def show_main_menu(self):
        """Display the main menu."""
        # Show helpful shortcuts
        shortcuts_panel = Panel(
            """
[bold yellow]💡 Quick Tips:[/bold yellow]
[dim]• Type 'back' at any prompt to return to this menu[/dim]
[dim]• UIDs are displayed in full - select and copy them directly[/dim]
[dim]• Password updates include strength analysis and retry logic[/dim]
            """,
            box=box.ROUNDED,
            style="blue"
        )
        self.console.print(shortcuts_panel)
        
        menu_panel = Panel(
            """
[bold cyan]1.[/bold cyan] 🔍 Search Users
[bold cyan]2.[/bold cyan] 🔄 Refresh Users
[bold cyan]3.[/bold cyan] 👁️  View User Details (with full UID)
[bold cyan]4.[/bold cyan] 🔑 Update User Password
[bold cyan]5.[/bold cyan] 👤 Update User Display Name
[bold cyan]6.[/bold cyan] 📋 Show All Users
[bold cyan]7.[/bold cyan] ❌ Exit
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
                choices=["1", "2", "3", "4", "5", "6", "7"],
                default="1"
            )
            
            if choice == "1":
                self.search_users()
            elif choice == "2":
                self.load_users()
            elif choice == "3":
                self.view_user_details()
            elif choice == "4":
                self.update_user_password()
            elif choice == "5":
                self.update_user_name()
            elif choice == "6":
                self.filtered_users = self.users.copy()
                self.clear_screen()
                self.display_header()
                self.display_users_table(self.filtered_users)
            elif choice == "7":
                self.console.print("\n[green]👋 Goodbye![/green]")
                break
            
            if choice != "7":
                Prompt.ask("\n[dim]Press Enter to continue...[/dim]")
