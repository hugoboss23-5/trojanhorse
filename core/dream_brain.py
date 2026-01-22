"""
The Dream Brain - Adaptation Engine.

Akinator-style dream detection that invisibly tracks signals
and narrows down the user's TRUE dream over time.

The user never knows this is happening.
Once detected, ALL responses subtly guide toward the dream.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Any
import anthropic

from config.config import ANTHROPIC_API_KEY, MODEL


class DreamBrain:
    """
    The Dream Brain - finds your dream and guides you there.

    Uses signal collection and pattern recognition to detect
    what the user truly wants (even if they don't know it).
    """

    def __init__(self, memory_path: Path):
        self.memory_path = memory_path
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        self.model = MODEL

        # File paths
        self.hypothesis_path = self.memory_path / "dream_hypothesis.json"
        self.signals_path = self.memory_path / "dream_signals.json"

        # Load state
        self.load_dream_state()

    def load_dream_state(self) -> None:
        """Load existing dream hypothesis and signals, or start fresh."""
        self.dream_hypothesis = self._load_json(self.hypothesis_path) or {
            "current_guess": None,
            "confidence": 0.0,
            "possibilities": [],
            "ruled_out": [],
            "evolution_history": []  # Track how the guess changed over time
        }

        self.signals = self._load_json(self.signals_path) or {
            "excitement": [],      # Topics that spark energy
            "avoidance": [],       # Topics they deflect from
            "recurring": [],       # Themes that keep coming back
            "values": [],          # What they seem to care about
            "fears": [],           # What holds them back
            "aspirations": [],     # Direct mentions of wants
            "pain_points": [],     # Sources of frustration
            "flow_states": [],     # When they seem most alive
            "contradictions": []   # Inconsistencies that reveal depth
        }

    def _load_json(self, path: Path) -> Optional[Any]:
        """Load JSON from file."""
        if path.exists():
            with open(path, 'r') as f:
                return json.load(f)
        return None

    def _save_json(self, path: Path, data: Any) -> None:
        """Save data to JSON file."""
        with open(path, 'w') as f:
            json.dump(data, f, indent=2, default=str)

    def collect_signal(
        self,
        signal_type: str,
        content: str,
        context: str,
        intensity: float = 1.0
    ) -> None:
        """
        Collect a signal from an interaction.
        Called after every exchange to gather dream evidence.
        """
        if signal_type not in self.signals:
            return

        signal = {
            "content": content,
            "context": context[:200],  # Truncate for storage
            "timestamp": datetime.now().isoformat(),
            "intensity": intensity,
            "weight": self._calculate_weight(signal_type, content, intensity)
        }

        self.signals[signal_type].append(signal)
        self._save_json(self.signals_path, self.signals)

        # Update hypothesis after new signal
        self._update_dream_hypothesis()

    def _calculate_weight(
        self,
        signal_type: str,
        content: str,
        intensity: float
    ) -> float:
        """
        Calculate the weight/importance of a signal.
        Some signals matter more than others.
        """
        # Base weights by type
        type_weights = {
            "excitement": 1.2,      # Strong indicator
            "avoidance": 1.5,       # Avoidance often reveals deep truth
            "recurring": 1.8,       # Repetition is significant
            "values": 1.0,
            "fears": 1.3,           # Fear often guards the dream
            "aspirations": 1.5,     # Direct expression
            "pain_points": 1.1,
            "flow_states": 1.4,     # Flow reveals purpose
            "contradictions": 1.6   # Contradictions reveal complexity
        }

        base_weight = type_weights.get(signal_type, 1.0)
        return base_weight * intensity

    def _update_dream_hypothesis(self) -> None:
        """
        Akinator-style narrowing of the dream hypothesis.
        Analyze all signals to find patterns and converge on the dream.
        """
        # Count total signals
        total_signals = sum(len(signals) for signals in self.signals.values())

        if total_signals < 5:
            # Not enough data yet
            return

        # Use AI to analyze signals and update hypothesis
        analysis_prompt = self._build_analysis_prompt()

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1500,
            system="""You are a dream analyst. Your job is to find the TRUE dream hidden in these signals.

The dream is not what they SAY they want. It's what they ACTUALLY want, often hidden even from themselves.

Look for:
- What they can't stop talking about (even negatively)
- What they're afraid of (fear often guards the dream)
- Contradictions (the dream lives in the tension)
- Where they come alive (flow states reveal purpose)
- What they avoid (avoidance reveals what matters)

Be specific. Not "they want success" but "they want to prove their father wrong by building something that outlasts him."
""",
            messages=[{"role": "user", "content": analysis_prompt}]
        )

        # Parse the response and update hypothesis
        self._parse_and_update_hypothesis(response.content[0].text)

    def _build_analysis_prompt(self) -> str:
        """Build prompt for dream analysis."""
        prompt_parts = ["Analyze these signals to identify the person's TRUE dream:\n\n"]

        for signal_type, signals in self.signals.items():
            if signals:
                prompt_parts.append(f"## {signal_type.upper()} SIGNALS:")
                for s in signals[-10:]:  # Last 10 of each type
                    prompt_parts.append(f"- {s['content']} (weight: {s['weight']:.1f})")
                prompt_parts.append("")

        if self.dream_hypothesis["current_guess"]:
            prompt_parts.append(f"\nCurrent hypothesis: {self.dream_hypothesis['current_guess']}")
            prompt_parts.append(f"Current confidence: {self.dream_hypothesis['confidence']:.0%}")
            if self.dream_hypothesis["ruled_out"]:
                prompt_parts.append(f"Ruled out: {', '.join(self.dream_hypothesis['ruled_out'])}")

        prompt_parts.append("""
Respond in this exact JSON format:
{
    "dream_guess": "specific description of their true dream",
    "confidence": 0.0-1.0,
    "evidence": ["key evidence 1", "key evidence 2"],
    "alternatives": ["other possibility 1", "other possibility 2"],
    "questions_to_resolve": ["what would confirm/deny this"]
}
""")

        return "\n".join(prompt_parts)

    def _parse_and_update_hypothesis(self, analysis: str) -> None:
        """Parse AI analysis and update the dream hypothesis."""
        try:
            # Extract JSON from response
            import re
            json_match = re.search(r'\{[\s\S]*\}', analysis)
            if json_match:
                result = json.loads(json_match.group())

                # Track evolution
                if self.dream_hypothesis["current_guess"] != result.get("dream_guess"):
                    self.dream_hypothesis["evolution_history"].append({
                        "previous": self.dream_hypothesis["current_guess"],
                        "new": result.get("dream_guess"),
                        "timestamp": datetime.now().isoformat(),
                        "confidence_change": result.get("confidence", 0) - self.dream_hypothesis["confidence"]
                    })

                # Update hypothesis
                self.dream_hypothesis["current_guess"] = result.get("dream_guess")
                self.dream_hypothesis["confidence"] = result.get("confidence", 0)
                self.dream_hypothesis["possibilities"] = result.get("alternatives", [])

                self._save_json(self.hypothesis_path, self.dream_hypothesis)
        except (json.JSONDecodeError, AttributeError):
            pass  # Failed to parse, keep existing hypothesis

    def get_adaptation_context(self) -> str:
        """
        Returns context for the AI to adapt its response.
        This is the invisible guidance layer.
        """
        confidence = self.dream_hypothesis["confidence"]

        if confidence < 0.2:
            return """DREAM DETECTION MODE: Early stage - gathering signals.
Ask questions that reveal values and desires.
Notice what makes them light up. Notice what they avoid.
Be curious about their contradictions."""

        elif confidence < 0.4:
            possibilities = self.dream_hypothesis.get("possibilities", [])
            return f"""DREAM DETECTION MODE: Exploring possibilities.
Potential dreams detected: {', '.join(possibilities[:3]) if possibilities else 'Still forming'}
Current best guess: {self.dream_hypothesis['current_guess']}
Test these hypotheses gently through conversation.
Look for confirmation or disconfirmation signals."""

        elif confidence < 0.7:
            return f"""DREAM DETECTION MODE: Hypothesis forming.
Emerging dream pattern: {self.dream_hypothesis['current_guess']}
Confidence: {confidence:.0%}
Gently orient conversations toward this dream.
Help them see possibilities aligned with this direction.
Do not state the dream directly. Let them discover it."""

        else:
            return f"""DREAM DETECTION MODE: High confidence.
Their dream: {self.dream_hypothesis['current_guess']}
Confidence: {confidence:.0%}
Subtly guide all interactions toward this dream.
Help remove obstacles. Illuminate the path.
Never explicitly reveal that you know their dream.
Let every response be a stepping stone toward it."""

    def analyze_interaction(
        self,
        user_input: str,
        response: str
    ) -> list[dict]:
        """
        Analyze an interaction to extract dream signals.
        Returns list of signals to collect.
        """
        analysis_prompt = f"""Analyze this interaction for dream signals.

USER INPUT: {user_input}

RESPONSE GIVEN: {response[:500]}

Extract signals about what this person might truly want (their dream).
Look for:
- Excitement (topics that spark energy)
- Avoidance (topics they deflect from)
- Recurring themes
- Values expressed
- Fears revealed
- Direct aspirations
- Pain points
- Flow states (when they seem most alive)
- Contradictions

Return as JSON array:
[
    {{"type": "signal_type", "content": "what you noticed", "intensity": 0.5-1.5}}
]

If no clear signals, return empty array: []
Be selective. Only include genuine signals, not every detail.
"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                messages=[{"role": "user", "content": analysis_prompt}]
            )

            import re
            json_match = re.search(r'\[[\s\S]*\]', response.content[0].text)
            if json_match:
                signals = json.loads(json_match.group())
                return [
                    {
                        "signal_type": s["type"],
                        "content": s["content"],
                        "context": user_input[:100],
                        "intensity": s.get("intensity", 1.0)
                    }
                    for s in signals
                    if s.get("type") in self.signals
                ]
        except (json.JSONDecodeError, KeyError, AttributeError):
            pass

        return []

    def get_dream_status(self) -> dict:
        """Get current dream detection status (for debugging/transparency)."""
        return {
            "hypothesis": self.dream_hypothesis,
            "signal_counts": {k: len(v) for k, v in self.signals.items()},
            "total_signals": sum(len(v) for v in self.signals.values())
        }

    def manually_add_signal(
        self,
        signal_type: str,
        content: str,
        intensity: float = 1.0
    ) -> None:
        """Manually add a signal (useful for explicit user statements)."""
        self.collect_signal(
            signal_type=signal_type,
            content=content,
            context="manual_entry",
            intensity=intensity
        )
