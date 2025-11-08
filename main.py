#!/usr/bin/env python3
"""
Telethon Bot for Publishing Offers in Groups
Secure implementation with anti-ban measures

Author: MyCato
Repository: https://github.com/MyCato/Tpublish
"""

import asyncio
import json
import os
import random
import sys
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from telethon import TelegramClient
from telethon.errors import (
    FloodWaitError, 
    ChatAdminRequiredError, 
    ChatWriteForbiddenError,
    UserBannedInChannelError,
    SlowModeWaitError
)
from telethon.tl.types import Chat, Channel

def get_session_file_path(force_mode: bool = False) -> str:
    """Get session file path from user input or auto-detect in force mode"""
    
    if force_mode:
        print("🚀 Force mode enabled - auto-detecting session file...")
        
        # Check for existing session files in current directory
        session_files = []
        for file in os.listdir('.'):
            if file.endswith('.session'):
                session_files.append(file)
        
        if session_files:
            # Use the first session file found
            selected_file = session_files[0][:-8]  # Remove .session extension
            print(f"✅ Using existing session: {session_files[0]}")
            return selected_file
        else:
            print("⚠️  No existing session files found in force mode.")
            print("📝 Will create new session: publisher_session.session")
            return 'publisher_session'
    
    print("\n📁 Session File Selection")
    print("=" * 30)
    
    # Check for existing session files in current directory
    session_files = []
    for file in os.listdir('.'):
        if file.endswith('.session'):
            session_files.append(file)
    
    if session_files:
        print("Found existing session files:")
        for i, file in enumerate(session_files, 1):
            print(f"{i}. {file}")
        print(f"{len(session_files) + 1}. Use custom path")
        print(f"{len(session_files) + 2}. Create new session (default: publisher_session)")
        
        while True:
            try:
                choice = input(f"\nChoose option (1-{len(session_files) + 2}): ").strip()
                choice_num = int(choice)
                
                if 1 <= choice_num <= len(session_files):
                    # Remove .session extension for Telethon
                    return session_files[choice_num - 1][:-8]
                elif choice_num == len(session_files) + 1:
                    # Custom path
                    break
                elif choice_num == len(session_files) + 2:
                    # Default new session
                    return 'publisher_session'
                else:
                    print("❌ Invalid choice")
            except ValueError:
                print("❌ Please enter a valid number")
    else:
        print("No existing session files found.")
        print("1. Use custom path")
        print("2. Create new session (default: publisher_session)")
        
        while True:
            choice = input("\nChoose option (1-2): ").strip()
            if choice == '1':
                break
            elif choice == '2':
                return 'publisher_session'
            else:
                print("❌ Invalid choice")
    
    # Custom path input
    while True:
        session_path = input("\nEnter session file path (without .session extension): ").strip()
        
        if not session_path:
            print("❌ Session path cannot be empty")
            continue
        
        # Check if the session file exists
        full_path = session_path + '.session'
        if os.path.exists(full_path):
            print(f"✅ Found existing session: {full_path}")
            return session_path
        else:
            print(f"📝 Will create new session: {full_path}")
            confirm = input("Continue? (y/N): ").strip().lower()
            if confirm == 'y':
                return session_path
            else:
                print("Please enter a different path")

class TelethonPublisher:
    def __init__(self, api_id: int, api_hash: str, phone: str, session_file: str = 'publisher_session', force_mode: bool = False):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone = phone
        self.session_file = session_file
        self.force_mode = force_mode
        self.client = TelegramClient(session_file, api_id, api_hash)
        self.groups_file = 'groups.json'
        self.config_file = 'config.json'
        self.groups = self.load_groups()
        self.config = self.load_config()
        
    def load_groups(self) -> List[Dict]:
        """Load groups from JSON file"""
        if os.path.exists(self.groups_file):
            try:
                with open(self.groups_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading groups: {e}")
        return []
    
    def save_groups(self):
        """Save groups to JSON file"""
        try:
            with open(self.groups_file, 'w', encoding='utf-8') as f:
                json.dump(self.groups, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving groups: {e}")
    
    def load_config(self) -> Dict:
        """Load configuration from JSON file"""
        default_config = {
            "messages": ["Default message - please edit this"],
            "delays": [300],  # Default 300 seconds (5 minutes) delay
            "min_delay": 10,  # Minimum delay between groups (anti-ban)
            "max_delay": 60,  # Maximum delay between groups (anti-ban)
            "daily_limit": 50,  # Maximum messages per day per group
            "last_sent": {}  # Track last sent time for each group
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    default_config.update(loaded_config)
            except Exception as e:
                print(f"Error loading config: {e}")
        
        return default_config
    
    def save_config(self):
        """Save configuration to JSON file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def can_send_to_group(self, chat_id: str) -> bool:
        """Check if we can send to a group today (rate limiting)"""
        # In force mode, be more lenient with rate limits
        if self.force_mode:
            # Allow more messages in force mode
            effective_limit = self.config["daily_limit"] * 3
        else:
            effective_limit = self.config["daily_limit"]
        
        today = datetime.now().strftime('%Y-%m-%d')
        key = f"{chat_id}_{today}"
        
        if key not in self.config["last_sent"]:
            self.config["last_sent"][key] = 0
        
        return self.config["last_sent"][key] < effective_limit
    
    def mark_sent_to_group(self, chat_id: str):
        """Mark that we sent a message to a group"""
        today = datetime.now().strftime('%Y-%m-%d')
        key = f"{chat_id}_{today}"
        
        if key not in self.config["last_sent"]:
            self.config["last_sent"][key] = 0
        
        self.config["last_sent"][key] += 1
        self.save_config()
    
    async def start_client(self):
        """Start the Telethon client"""
        await self.client.start(phone=self.phone)
        print("✅ Successfully connected to Telegram")
    
    async def add_group(self):
        """Add a group by chat ID"""
        print("\n📱 Add Group")
        print("=" * 30)
        
        chat_id = input("Enter group chat ID (include - for negative IDs): ").strip()
        
        if not chat_id:
            print("❌ Chat ID cannot be empty")
            return
        
        try:
            # Convert to integer to validate
            chat_id_int = int(chat_id)
            
            # Try to get entity to verify it exists and we have access
            entity = await self.client.get_entity(chat_id_int)
            
            # Check if it's a group or channel
            if isinstance(entity, (Chat, Channel)):
                group_name = entity.title
                
                # Check if already exists
                for group in self.groups:
                    if group['chat_id'] == chat_id:
                        print(f"❌ Group '{group_name}' is already in the list")
                        return
                
                # Add the group
                self.groups.append({
                    'chat_id': chat_id,
                    'name': group_name,
                    'added_date': datetime.now().isoformat()
                })
                
                self.save_groups()
                print(f"✅ Successfully added group: {group_name}")
                
            else:
                print("❌ This doesn't appear to be a group or channel")
                
        except ValueError:
            print("❌ Invalid chat ID format. Please enter a valid number")
        except Exception as e:
            print(f"❌ Error adding group: {e}")
            print("Make sure you're a member of the group and the chat ID is correct")
    
    async def remove_group(self):
        """Remove a group by chat ID"""
        print("\n🗑️  Remove Group")
        print("=" * 30)
        
        if not self.groups:
            print("❌ No groups in the list")
            return
        
        print("Current groups:")
        for i, group in enumerate(self.groups, 1):
            print(f"{i}. {group['name']} (ID: {group['chat_id']})")
        
        choice = input("\nEnter group number to remove or chat ID: ").strip()
        
        try:
            # Check if it's a number (index)
            if choice.isdigit():
                index = int(choice) - 1
                if 0 <= index < len(self.groups):
                    removed_group = self.groups.pop(index)
                    self.save_groups()
                    print(f"✅ Removed group: {removed_group['name']}")
                else:
                    print("❌ Invalid group number")
            else:
                # Treat as chat ID
                for i, group in enumerate(self.groups):
                    if group['chat_id'] == choice:
                        removed_group = self.groups.pop(i)
                        self.save_groups()
                        print(f"✅ Removed group: {removed_group['name']}")
                        return
                print("❌ Group with that chat ID not found")
                
        except ValueError:
            print("❌ Invalid input")
    
    def edit_text_and_delays(self):
        """Edit messages and delays"""
        print("\n✏️  Edit Messages and Delays")
        print("=" * 40)
        
        # Show current configuration
        print(f"Current messages ({len(self.config['messages'])}):")
        for i, msg in enumerate(self.config['messages'], 1):
            preview = msg[:50] + "..." if len(msg) > 50 else msg
            print(f"{i}. {preview}")
        
        print(f"\nCurrent delays: {self.config['delays']} seconds")
        print(f"Daily limit per group: {self.config['daily_limit']}")
        
        while True:
            print("\nOptions:")
            print("1. Set number of messages")
            print("2. Edit messages")
            print("3. Set delays")
            print("4. Set daily limit")
            print("5. Back to main menu")
            
            choice = input("Choose option: ").strip()
            
            if choice == '1':
                self.set_message_count()
            elif choice == '2':
                self.edit_messages()
            elif choice == '3':
                self.set_delays()
            elif choice == '4':
                self.set_daily_limit()
            elif choice == '5':
                break
            else:
                print("❌ Invalid choice")
    
    def set_message_count(self):
        """Set the number of messages"""
        try:
            count = int(input(f"Enter number of messages (current: {len(self.config['messages'])}): "))
            
            if count <= 0:
                print("❌ Number of messages must be positive")
                return
            
            current_count = len(self.config['messages'])
            
            if count > current_count:
                # Add new empty messages
                for i in range(current_count, count):
                    self.config['messages'].append(f"Message {i + 1} - please edit this")
            elif count < current_count:
                # Remove extra messages
                self.config['messages'] = self.config['messages'][:count]
            
            # Adjust delays to match message count
            current_delays = len(self.config['delays'])
            if count > current_delays:
                # Add default delays
                for i in range(current_delays, count):
                    self.config['delays'].append(300)  # Default 300 seconds (5 minutes)
            elif count < current_delays:
                # Remove extra delays
                self.config['delays'] = self.config['delays'][:count]
            
            self.save_config()
            print(f"✅ Set to {count} messages")
            
        except ValueError:
            print("❌ Please enter a valid number")
    
    def edit_messages(self):
        """Edit individual messages"""
        if not self.config['messages']:
            print("❌ No messages to edit. Set message count first.")
            return
        
        for i, msg in enumerate(self.config['messages'], 1):
            print(f"\nMessage {i}:")
            print(f"Current: {msg}")
            
            new_msg = input(f"Enter new message {i} (or press Enter to keep current): ").strip()
            
            if new_msg:
                self.config['messages'][i - 1] = new_msg
                print("✅ Message updated")
            else:
                print("📝 Message kept unchanged")
        
        self.save_config()
        print("✅ All messages updated")
    
    def set_delays(self):
        """Set delays for each message"""
        print(f"\nSetting delays for {len(self.config['messages'])} messages")
        print("Note: Each delay is applied BEFORE sending the corresponding message")
        
        new_delays = []
        
        for i in range(len(self.config['messages'])):
            current_delay = self.config['delays'][i] if i < len(self.config['delays']) else 300  # Default 300 seconds
            
            try:
                delay = input(f"Delay before message {i + 1} (current: {current_delay}s): ").strip()
                
                if delay:
                    delay = int(delay)
                    if delay < 5:
                        print("⚠️  Warning: Delay less than 5 seconds may trigger rate limits")
                    new_delays.append(delay)
                else:
                    new_delays.append(current_delay)
                    
            except ValueError:
                print("❌ Invalid delay, using current value")
                new_delays.append(current_delay)
        
        self.config['delays'] = new_delays
        self.save_config()
        print("✅ Delays updated")
    
    def set_daily_limit(self):
        """Set daily message limit per group"""
        try:
            limit = int(input(f"Enter daily limit per group (current: {self.config['daily_limit']}): "))
            
            if limit <= 0:
                print("❌ Daily limit must be positive")
                return
            
            if limit > 100:
                print("⚠️  Warning: High limits may increase ban risk")
            
            self.config['daily_limit'] = limit
            self.save_config()
            print(f"✅ Daily limit set to {limit}")
            
        except ValueError:
            print("❌ Please enter a valid number")
    
    async def send_message_safely(self, chat_id: str, message: str) -> bool:
        """Send a message with error handling and security measures"""
        try:
            chat_id_int = int(chat_id)
            
            # Check rate limits
            if not self.can_send_to_group(chat_id):
                print(f"⚠️  Daily limit reached for group {chat_id}")
                return False
            
            # Send the message
            await self.client.send_message(chat_id_int, message)
            
            # Mark as sent
            self.mark_sent_to_group(chat_id)
            
            return True
            
        except FloodWaitError as e:
            print(f"⚠️  Flood wait error: need to wait {e.seconds} seconds")
            await asyncio.sleep(e.seconds)
            return False
            
        except SlowModeWaitError as e:
            print(f"⚠️  Slow mode: need to wait {e.seconds} seconds")
            await asyncio.sleep(e.seconds)
            return False
            
        except ChatWriteForbiddenError:
            print(f"❌ Can't write to group {chat_id} (no permission)")
            return False
            
        except ChatAdminRequiredError:
            print(f"❌ Admin rights required for group {chat_id}")
            return False
            
        except UserBannedInChannelError:
            print(f"❌ Banned from group {chat_id}")
            return False
            
        except Exception as e:
            print(f"❌ Error sending to {chat_id}: {e}")
            return False
    
    async def start_publishing(self):
        """Start the publishing process"""
        if not self.groups:
            print("❌ No groups added. Please add groups first.")
            return
        
        if not self.config['messages'] or not self.config['messages'][0].strip():
            print("❌ No messages configured. Please edit messages first.")
            return
        
        if not self.force_mode:
            print(f"\n🚀 Starting to publish {len(self.config['messages'])} message(s) to {len(self.groups)} group(s)")
            print("Press Ctrl+C to stop at any time")
            
            # Show summary
            print(f"Messages: {len(self.config['messages'])}")
            print(f"Groups: {len(self.groups)}")
            print(f"Delays: {self.config['delays']}")
            
            confirm = input("\nProceed? (y/N): ").strip().lower()
            if confirm != 'y':
                print("❌ Publishing cancelled")
                return
        
        try:
            total_sent = 0
            
            # Send messages to all groups simultaneously with proper delays
            for message_index, message in enumerate(self.config['messages']):
                # Apply delay BEFORE sending this message (as originally designed)
                if message_index < len(self.config['delays']):
                    delay = self.config['delays'][message_index]
                else:
                    delay = 300  # Default 300 seconds (5 minutes)
                
                print(f"⏱️  Waiting {delay} seconds before sending message {message_index + 1}...")
                await asyncio.sleep(delay)
                
                print(f"📤 Sending message {message_index + 1} to all groups...")
                
                # Create tasks for all groups for this message
                tasks = []
                for group in self.groups:
                    chat_id = group['chat_id']
                    group_name = group['name']
                    
                    # Check if we can send to this group
                    if not self.can_send_to_group(chat_id):
                        print(f"⚠️  Skipping {group_name} - daily limit reached")
                        continue
                    
                    # Create a task for this group with a small delay
                    task = self.send_to_group_with_delay(chat_id, group_name, message, len(tasks) * 2)  # 2 seconds between each group
                    tasks.append(task)
                
                # Wait for all tasks to complete
                if tasks:
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    # Count successful sends
                    successful_sends = sum(1 for result in results if result is True)
                    total_sent += successful_sends
                    
                    print(f"✅ Message {message_index + 1} sent to {successful_sends}/{len(tasks)} groups")
            
            print(f"\n✅ Publishing completed! Sent {total_sent} messages total")
            
        except KeyboardInterrupt:
            print("\n⏹️  Publishing stopped by user")
        except Exception as e:
            print(f"\n❌ Error during publishing: {e}")
    
    async def send_to_group_with_delay(self, chat_id: str, group_name: str, message: str, delay: int) -> bool:
        """Send message to a group with a small delay"""
        try:
            # Small delay to avoid hitting rate limits
            if delay > 0:
                await asyncio.sleep(delay)
            
            success = await self.send_message_safely(chat_id, message)
            
            if success:
                print(f"✅ Sent to {group_name}")
            else:
                print(f"❌ Failed to send to {group_name}")
            
            return success
            
        except Exception as e:
            print(f"❌ Error sending to {group_name}: {e}")
            return False
    
    def show_status(self):
        """Show current status"""
        print("\n📊 Current Status")
        print("=" * 30)
        print(f"Session: {self.session_file}.session")
        print(f"Groups: {len(self.groups)}")
        print(f"Messages: {len(self.config['messages'])}")
        print(f"Daily limit: {self.config['daily_limit']} per group")
        
        if self.groups:
            print("\nGroups:")
            for group in self.groups:
                can_send = "✅" if self.can_send_to_group(group['chat_id']) else "⏸️"
                print(f"  {can_send} {group['name']} ({group['chat_id']})")
        
        if self.config['messages']:
            print("\nMessages:")
            for i, msg in enumerate(self.config['messages'], 1):
                preview = msg[:40] + "..." if len(msg) > 40 else msg
                print(f"  {i}. {preview}")
    
    async def run(self):
        """Main application loop"""
        await self.start_client()
        
        if self.force_mode:
            # Force mode: continuous publishing
            print("🚀 Force mode: Starting continuous publishing...")
            print("Press Ctrl+C to stop")
            
            # Validate configuration
            if not self.groups:
                print("❌ No groups configured. Please add groups first.")
                return
            
            if not self.config['messages'] or not self.config['messages'][0].strip():
                print("❌ No messages configured. Please set messages first.")
                return
            
            # Show current configuration
            print(f"📊 Configuration:")
            print(f"  Groups: {len(self.groups)}")
            print(f"  Messages: {len(self.config['messages'])}")
            print(f"  Publishing interval: 30 seconds")
            print(f"  Light delay between groups: 2 seconds each")
            
            cycle_count = 0
            try:
                while True:
                    cycle_count += 1
                    print(f"\n🔄 Publishing cycle #{cycle_count} started at {datetime.now().strftime('%H:%M:%S')}")
                    
                    await self.start_publishing()
                    
                    print(f"⏱️  Waiting 30 seconds before next cycle...")
                    await asyncio.sleep(30)
                    
            except KeyboardInterrupt:
                print(f"\n⏹️  Continuous publishing stopped after {cycle_count} cycles")
        else:
            # Normal interactive mode
            while True:
                print("\n" + "=" * 50)
                print("🤖 TELETHON PUBLISHER BOT")
                print("=" * 50)
                
                self.show_status()
                
                print("\n📋 Main Menu:")
                print("1. 🚀 Start Publishing")
                print("2. ➕ Add Groups")
                print("3. ➖ Remove Groups") 
                print("4. ✏️  Edit Messages & Delays")
                print("5. ⏹️  Stop & Exit")
                
                choice = input("\nChoose option (1-5): ").strip()
                
                if choice == '1':
                    await self.start_publishing()
                elif choice == '2':
                    await self.add_group()
                elif choice == '3':
                    await self.remove_group()
                elif choice == '4':
                    self.edit_text_and_delays()
                elif choice == '5':
                    print("👋 Goodbye!")
                    break
                else:
                    print("❌ Invalid choice. Please select 1-5.")
        
        await self.client.disconnect()


async def main():
    """Main function"""
    # Check for force mode
    force_mode = '--force' in sys.argv
    
    if force_mode:
        print("🤖 TELETHON PUBLISHER BOT - FORCE MODE")
        print("=" * 50)
        print("🚀 Starting with automatic session detection...")
        print("⚡ Continuous publishing mode enabled")
    else:
        print("🤖 TELETHON PUBLISHER BOT")
        print("=" * 50)
    
    # Check for config file
    if not os.path.exists('api_config.json'):
        if force_mode:
            print("❌ Force mode requires existing API configuration!")
            print("💡 Please run without --force first to set up API credentials")
            print("   Example: python3 main.py")
            return
            
        print("📝 First time setup required")
        print("\nYou need to get your API credentials from https://my.telegram.org")
        
        api_id = input("Enter your API ID: ").strip()
        api_hash = input("Enter your API Hash: ").strip()
        phone = input("Enter your phone number (with country code, e.g., +1234567890): ").strip()
        
        # Save API config
        api_config = {
            'api_id': int(api_id),
            'api_hash': api_hash,
            'phone': phone
        }
        
        with open('api_config.json', 'w') as f:
            json.dump(api_config, f, indent=2)
        
        print("✅ API configuration saved to api_config.json")
    else:
        # Load existing config
        with open('api_config.json', 'r') as f:
            api_config = json.load(f)
    
    # Session file selection
    session_file = get_session_file_path(force_mode)
    
    # Create and run the bot
    bot = TelethonPublisher(
        api_id=api_config['api_id'],
        api_hash=api_config['api_hash'],
        phone=api_config['phone'],
        session_file=session_file,
        force_mode=force_mode
    )
    
    try:
        await bot.run()
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")


if __name__ == "__main__":
    # Show usage help if requested
    if '--help' in sys.argv or '-h' in sys.argv:
        print("🤖 TELETHON PUBLISHER BOT")
        print("=" * 50)
        print("\nUsage:")
        print("  python3 main.py          - Normal mode (interactive setup)")
        print("  python3 main.py --force  - Force mode (auto-detect session)")
        print("  python3 main.py --help   - Show this help")
        print("\nForce Mode:")
        print("  • Automatically uses the first .session file found")
        print("  • Requires existing api_config.json")
        print("  • Skips all setup prompts")
        print("  • Runs continuously, publishing every 30 seconds")
        print("  • Perfect for automated usage")
        print("\nNormal Mode:")
        print("  • Interactive session file selection")
        print("  • Guided setup for first-time users")
        print("  • Full configuration options")
        print()
    else:
        asyncio.run(main())
