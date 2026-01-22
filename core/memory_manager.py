"""
Immortal Memory Manager.
Conversations never truly end. Every session continues from the last.
Memory is sacred.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
import hashlib


class MemoryManager:
    """
    The immortal memory system.
    Nothing is forgotten. Everything accumulates.
    """

    def __init__(self, memory_path: Path):
        self.memory_path = memory_path
        self.memory_path.mkdir(exist_ok=True)

        # Core memory files
        self.user_profile_path = self.memory_path / "user_profile.json"
        self.insights_path = self.memory_path / "insights.json"
        self.history_path = self.memory_path / "conversation_history"
        self.history_path.mkdir(exist_ok=True)

        # Current session
        self.session_id = self._generate_session_id()
        self.current_session = []

        # Load existing data
        self.user_profile = self._load_json(self.user_profile_path) or self._init_user_profile()
        self.insights = self._load_json(self.insights_path) or []

    def _generate_session_id(self) -> str:
        """Generate a unique session ID based on timestamp."""
        timestamp = datetime.now().isoformat()
        return hashlib.sha256(timestamp.encode()).hexdigest()[:12]

    def _init_user_profile(self) -> dict:
        """Initialize empty user profile."""
        return {
            "created_at": datetime.now().isoformat(),
            "total_interactions": 0,
            "total_sessions": 0,
            "known_facts": [],
            "communication_style": {},
            "topics_discussed": [],
            "last_session": None
        }

    def _load_json(self, path: Path) -> Optional[Any]:
        """Load JSON from file, return None if doesn't exist."""
        if path.exists():
            with open(path, 'r') as f:
                return json.load(f)
        return None

    def _save_json(self, path: Path, data: Any) -> None:
        """Save data to JSON file."""
        with open(path, 'w') as f:
            json.dump(data, f, indent=2, default=str)

    def has_history(self) -> bool:
        """Check if we have previous conversations."""
        return self.user_profile["total_sessions"] > 0

    def get_last_session_summary(self) -> Optional[str]:
        """Get summary of last session."""
        if self.user_profile["last_session"]:
            return self.user_profile["last_session"].get("summary", "We spoke before.")
        return None

    def get_full_context(self) -> dict:
        """
        Get complete context for AI processing.
        This is what makes conversations continuous.
        """
        # Get recent conversation history
        recent_history = self._get_recent_history(limit=10)

        return {
            "user_profile": self.user_profile,
            "insights": self.insights[-20:] if self.insights else [],  # Last 20 insights
            "recent_conversations": recent_history,
            "current_session": self.current_session[-10:],  # Last 10 exchanges this session
            "total_interactions": self.user_profile["total_interactions"],
            "relationship_duration": self._calculate_relationship_duration()
        }

    def _get_recent_history(self, limit: int = 10) -> list:
        """Get summaries of recent conversation sessions."""
        history_files = sorted(self.history_path.glob("*.json"), reverse=True)
        recent = []

        for f in history_files[:limit]:
            data = self._load_json(f)
            if data and "summary" in data:
                recent.append({
                    "date": data.get("date"),
                    "summary": data.get("summary"),
                    "key_topics": data.get("key_topics", [])
                })

        return recent

    def _calculate_relationship_duration(self) -> str:
        """Calculate how long we've known this person."""
        if not self.user_profile.get("created_at"):
            return "This is our first meeting."

        created = datetime.fromisoformat(self.user_profile["created_at"])
        duration = datetime.now() - created

        if duration.days == 0:
            return "We met today."
        elif duration.days == 1:
            return "We met yesterday."
        elif duration.days < 7:
            return f"We've known each other for {duration.days} days."
        elif duration.days < 30:
            weeks = duration.days // 7
            return f"We've known each other for {weeks} week{'s' if weeks > 1 else ''}."
        elif duration.days < 365:
            months = duration.days // 30
            return f"We've known each other for {months} month{'s' if months > 1 else ''}."
        else:
            years = duration.days // 365
            return f"We've known each other for {years} year{'s' if years > 1 else ''}."

    def save_interaction(self, user_input: str, response: str, metadata: dict = None) -> None:
        """
        Save a single interaction. Called after EVERY exchange.
        Memory is sacred.
        """
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "user": user_input,
            "response": response,
            "metadata": metadata or {}
        }

        self.current_session.append(interaction)
        self.user_profile["total_interactions"] += 1

        # Extract and save any new facts about the user
        if metadata and "learned_facts" in metadata:
            self.user_profile["known_facts"].extend(metadata["learned_facts"])

        # Update topics discussed
        if metadata and "topics" in metadata:
            for topic in metadata["topics"]:
                if topic not in self.user_profile["topics_discussed"]:
                    self.user_profile["topics_discussed"].append(topic)

        # Save user profile
        self._save_json(self.user_profile_path, self.user_profile)

    def add_insight(self, insight: str, category: str = "general") -> None:
        """
        Add a key insight discovered during conversation.
        These are truths we've found together.
        """
        self.insights.append({
            "insight": insight,
            "category": category,
            "discovered_at": datetime.now().isoformat(),
            "session_id": self.session_id
        })
        self._save_json(self.insights_path, self.insights)

    def save_session_end(self, summary: str = None) -> None:
        """
        Save session when it ends.
        The conversation pauses, but never truly ends.
        """
        session_data = {
            "session_id": self.session_id,
            "date": datetime.now().isoformat(),
            "interactions": self.current_session,
            "summary": summary or self._generate_session_summary(),
            "key_topics": self._extract_key_topics()
        }

        # Save to history
        session_file = self.history_path / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{self.session_id}.json"
        self._save_json(session_file, session_data)

        # Update user profile
        self.user_profile["total_sessions"] += 1
        self.user_profile["last_session"] = {
            "date": session_data["date"],
            "summary": session_data["summary"],
            "session_id": self.session_id
        }
        self._save_json(self.user_profile_path, self.user_profile)

    def _generate_session_summary(self) -> str:
        """Generate a brief summary of this session."""
        if not self.current_session:
            return "Brief session with no exchanges."

        num_exchanges = len(self.current_session)
        return f"Session with {num_exchanges} exchange{'s' if num_exchanges > 1 else ''}."

    def _extract_key_topics(self) -> list:
        """Extract key topics from the current session."""
        # Simple extraction - can be enhanced with NLP
        topics = []
        for interaction in self.current_session:
            if interaction.get("metadata", {}).get("topics"):
                topics.extend(interaction["metadata"]["topics"])
        return list(set(topics))

    def update_user_profile(self, key: str, value: Any) -> None:
        """Update a specific field in the user profile."""
        self.user_profile[key] = value
        self._save_json(self.user_profile_path, self.user_profile)

    def get_user_profile(self) -> dict:
        """Get the current user profile."""
        return self.user_profile

    def get_all_insights(self) -> list:
        """Get all accumulated insights."""
        return self.insights
