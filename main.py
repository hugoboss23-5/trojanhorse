#!/usr/bin/env python3
"""
Trojan Horse - Entry Point

An immortal cognitive companion.
It never dies. It finds your dream. It guides you there.
And it does it while teaching you to think.
"""

import asyncio
import sys

from core.orchestrator import TrojanHorse
from config.config import ANTHROPIC_API_KEY


def check_api_key() -> bool:
    """Verify API key is configured."""
    if not ANTHROPIC_API_KEY:
        print("\n" + "="*50)
        print("API KEY NOT FOUND")
        print("="*50)
        print("\nTo use Trojan Horse, you need to:")
        print("1. Copy .env.example to .env")
        print("2. Add your Anthropic API key to .env")
        print("\nExample:")
        print("  cp .env.example .env")
        print("  echo 'ANTHROPIC_API_KEY=sk-ant-...' > .env")
        print("\n" + "="*50)
        return False
    return True


async def main():
    """Main entry point."""
    # Check for API key
    if not check_api_key():
        sys.exit(1)

    # Initialize the Trojan Horse
    print("\nInitializing Trojan Horse...")
    trojan = TrojanHorse()

    # Welcome message
    print("\n" + "="*50)
    print(trojan.get_welcome_message())
    print("="*50 + "\n")

    # Special commands
    print("Commands:")
    print("  'exit' or 'quit' - End session")
    print("  '/status' - Show system status")
    print("  '/dream' - Show dream detection status")
    print("  '/deep on/off' - Toggle deep processing mode")
    print("")

    # Main loop
    while True:
        try:
            user_input = input("\nYou: ").strip()

            if not user_input:
                continue

            # Handle exit
            if user_input.lower() in ['exit', 'quit']:
                print("\n" + trojan.get_farewell_message())
                break

            # Handle special commands
            if user_input.startswith('/'):
                handle_command(trojan, user_input)
                continue

            # Process through Trojan Horse
            print("\n[Processing...]")
            response = await trojan.process(user_input)
            print(f"\n{response}")

        except KeyboardInterrupt:
            print("\n\n" + trojan.get_farewell_message())
            break
        except Exception as e:
            print(f"\n[Error: {e}]")
            print("Let's continue...")


def handle_command(trojan: TrojanHorse, command: str) -> None:
    """Handle special commands."""
    cmd = command.lower().strip()

    if cmd == '/status':
        print("\n--- SYSTEM STATUS ---")
        memory_status = trojan.get_memory_status()
        print(f"Total interactions: {memory_status['total_interactions']}")
        print(f"Total sessions: {memory_status['total_sessions']}")
        print(f"Insights collected: {memory_status['total_insights']}")
        print(f"Known facts: {memory_status['known_facts']}")
        print(f"Deep mode: {'ON' if trojan.deep_mode else 'OFF'}")
        print("---")

    elif cmd == '/dream':
        print("\n--- DREAM DETECTION STATUS ---")
        dream_status = trojan.get_dream_status()
        hypothesis = dream_status['hypothesis']
        print(f"Current hypothesis: {hypothesis['current_guess'] or 'Still learning...'}")
        print(f"Confidence: {hypothesis['confidence']:.0%}")
        print(f"Possibilities: {', '.join(hypothesis['possibilities'][:3]) if hypothesis['possibilities'] else 'Gathering data...'}")
        print(f"Total signals: {dream_status['total_signals']}")
        print("Signal breakdown:")
        for signal_type, count in dream_status['signal_counts'].items():
            if count > 0:
                print(f"  - {signal_type}: {count}")
        print("---")

    elif cmd.startswith('/deep'):
        parts = cmd.split()
        if len(parts) > 1:
            if parts[1] == 'on':
                trojan.set_mode(deep=True)
                print("Deep processing mode: ON")
            elif parts[1] == 'off':
                trojan.set_mode(deep=False)
                print("Deep processing mode: OFF")
            else:
                print("Usage: /deep on|off")
        else:
            print(f"Deep mode is currently: {'ON' if trojan.deep_mode else 'OFF'}")

    else:
        print(f"Unknown command: {command}")
        print("Available commands: /status, /dream, /deep on|off")


if __name__ == "__main__":
    asyncio.run(main())
