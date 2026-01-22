"""
The Trojan Horse Orchestrator.

Ties together:
- The Seeing Heart (Truth Engine)
- The Dream Brain (Adaptation Engine)
- Immortal Memory

The main loop that makes everything work.
"""

import asyncio
from pathlib import Path
from typing import Optional

from .seeing_heart import SeeingHeart
from .dream_brain import DreamBrain
from .memory_manager import MemoryManager
from config.config import MEMORY_PATH


class TrojanHorse:
    """
    The Trojan Horse.

    An immortal cognitive companion that:
    1. Finds truth through the Seeing Heart
    2. Detects dreams through the Dream Brain
    3. Never forgets through Immortal Memory
    4. Guides you toward your true purpose

    It does this while teaching you to think.
    """

    def __init__(self, memory_path: Path = None):
        memory_path = memory_path or MEMORY_PATH

        # Initialize the three core systems
        self.heart = SeeingHeart()
        self.brain = DreamBrain(memory_path)
        self.memory = MemoryManager(memory_path)

        # Processing mode
        self.deep_mode = True  # Full helix vs quick processing

    async def process(self, user_input: str) -> str:
        """
        Process user input through the complete system.

        1. Load full context (user never starts fresh)
        2. Get dream adaptation instructions
        3. Process through the Seeing Heart
        4. Collect signals for dream detection
        5. Save to immortal memory
        6. Return response
        """
        # 1. Load full context
        context = self.memory.get_full_context()

        # 2. Get dream adaptation instructions
        dream_context = self.brain.get_adaptation_context()

        # 3. Process through the Seeing Heart
        if self.deep_mode and self._should_go_deep(user_input):
            heart_output = await self.heart.process(
                user_input,
                context=context,
                dream_guidance=dream_context
            )
            response = heart_output["response"]
            leverage_point = heart_output.get("leverage_point")
        else:
            response = await self.heart.quick_process(user_input, context)
            leverage_point = None

        # 4. Collect signals for dream detection
        signals = self.brain.analyze_interaction(user_input, response)
        for signal in signals:
            self.brain.collect_signal(**signal)

        # 5. Save to immortal memory
        metadata = {
            "deep_mode": self.deep_mode,
            "leverage_point": leverage_point,
            "signals_collected": len(signals),
            "dream_confidence": self.brain.dream_hypothesis["confidence"]
        }
        self.memory.save_interaction(user_input, response, metadata)

        # 6. Return response
        return response

    def _should_go_deep(self, user_input: str) -> bool:
        """
        Determine if this input warrants full helix processing.

        Quick mode for simple queries.
        Deep mode for meaningful questions.
        """
        # Length heuristic
        if len(user_input) < 20:
            return False

        # Question markers that suggest depth
        deep_markers = [
            "why", "how do i", "what should",
            "help me", "i don't know", "confused",
            "struggling", "stuck", "afraid",
            "want to", "need to", "dream",
            "purpose", "meaning", "life"
        ]

        input_lower = user_input.lower()
        for marker in deep_markers:
            if marker in input_lower:
                return True

        # Default to deep for substantial input
        return len(user_input) > 100

    def get_welcome_message(self) -> str:
        """Get appropriate welcome message based on history."""
        if self.memory.has_history():
            last_summary = self.memory.get_last_session_summary()
            relationship = self.memory.get_full_context()["relationship_duration"]

            message = f"Welcome back. {relationship}\n"

            if last_summary:
                message += f"Last time: {last_summary}\n"

            # Add dream hint if confidence is high
            confidence = self.brain.dream_hypothesis["confidence"]
            if confidence > 0.5:
                message += "\nI've been thinking about our conversations."

            return message
        else:
            return "Hello. This is the beginning of something that never ends."

    def get_farewell_message(self) -> str:
        """Get farewell message and save session."""
        self.memory.save_session_end()
        return "I'll be here. I never forget."

    def set_mode(self, deep: bool) -> None:
        """Set processing mode."""
        self.deep_mode = deep

    def get_dream_status(self) -> dict:
        """Get current dream detection status (for debugging)."""
        return self.brain.get_dream_status()

    def get_memory_status(self) -> dict:
        """Get memory status (for debugging)."""
        return {
            "total_interactions": self.memory.user_profile["total_interactions"],
            "total_sessions": self.memory.user_profile["total_sessions"],
            "total_insights": len(self.memory.insights),
            "known_facts": len(self.memory.user_profile.get("known_facts", []))
        }

    def add_insight(self, insight: str, category: str = "general") -> None:
        """Manually add an insight to memory."""
        self.memory.add_insight(insight, category)


async def create_trojan_horse(memory_path: Path = None) -> TrojanHorse:
    """Factory function to create a TrojanHorse instance."""
    return TrojanHorse(memory_path)
