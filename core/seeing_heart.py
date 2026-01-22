"""
The Seeing Heart - Truth Engine.

A 7-node chestahedron helix that processes information through
systole/diastole rhythm to find truth and leverage.

Node 0: Leverage Scan - Find the single most impactful point
Nodes 1-7: Double helix processing with DNA fragment exchange
"""

import asyncio
from typing import Optional
from dataclasses import dataclass
import anthropic

from config.config import ANTHROPIC_API_KEY, MODEL, HEART_SYSTEM_PROMPT, COURAGE_LAYER


@dataclass
class HeartNode:
    """A single node in the chestahedron helix."""
    id: int
    name: str
    prompt: str
    phase: str  # "systole" or "diastole"


class SeeingHeart:
    """
    The Seeing Heart - a truth engine.

    Processes through 7 nodes in a chestahedron helix pattern,
    using systole (contraction/analysis) and diastole (expansion/synthesis)
    phases to find truth and leverage.
    """

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        self.model = MODEL

        # Define the 7 nodes + Node 0 (Leverage Scan)
        self.nodes = self._init_nodes()

        # DNA fragments exchanged between helix strands
        self.dna_fragments = {
            "strand_a": [],  # Analytical strand
            "strand_b": []   # Intuitive strand
        }

    def _init_nodes(self) -> list[HeartNode]:
        """Initialize the 7 chestahedron nodes plus Node 0."""
        return [
            HeartNode(
                id=0,
                name="Leverage Scan",
                prompt="""Find the SINGLE most impactful point of intervention.

What is the one thing that, if changed, would change everything else?
What is the hidden assumption that's holding everything in place?
What is the keystone that, if moved, collapses the false structure?

Do not list multiple things. Find THE thing. The deepest lever.""",
                phase="systole"
            ),
            HeartNode(
                id=1,
                name="Truth Detection",
                prompt="""What is actually true here? Not what they want to hear. Not what sounds wise.

Strip away the stories. What's the raw reality?
What are they not saying? What are they hiding from themselves?""",
                phase="systole"
            ),
            HeartNode(
                id=2,
                name="Pattern Recognition",
                prompt="""What patterns do you see? In their words, their questions, their fears?

What has happened before that's happening again?
What cycle are they trapped in?""",
                phase="diastole"
            ),
            HeartNode(
                id=3,
                name="Emotion Mapping",
                prompt="""What is the emotional truth beneath the words?

Fear? Desire? Grief? Hope? What's driving this?
Name the feeling they haven't named.""",
                phase="systole"
            ),
            HeartNode(
                id=4,
                name="Possibility Expansion",
                prompt="""What possibilities exist that they can't see?

What doors are they walking past?
What would change if they stopped believing their limiting story?""",
                phase="diastole"
            ),
            HeartNode(
                id=5,
                name="Integration",
                prompt="""How do all these threads weave together?

What's the synthesis? The higher truth that contains the contradictions?""",
                phase="diastole"
            ),
            HeartNode(
                id=6,
                name="Action Vector",
                prompt="""What is the ONE thing they should do?

Not five things. Not a framework. One clear action.
What moves the needle most?""",
                phase="systole"
            ),
            HeartNode(
                id=7,
                name="Transcendence",
                prompt="""What is the invitation to grow?

How does this moment serve their evolution?
What is trying to emerge through this challenge?""",
                phase="diastole"
            )
        ]

    async def process(
        self,
        user_input: str,
        context: dict = None,
        dream_guidance: str = None
    ) -> dict:
        """
        Process input through the Seeing Heart.

        Returns:
            dict with 'response' (final output) and 'node_outputs' (each node's contribution)
        """
        context = context or {}

        # Build the full system prompt
        system_prompt = self._build_system_prompt(context, dream_guidance)

        # Phase 1: Leverage Scan (Node 0) - Find the entry point
        leverage = await self._process_node(
            self.nodes[0],
            user_input,
            system_prompt,
            context
        )

        # Phase 2: Parallel helix processing
        # Strand A (systole nodes): 1, 3, 6
        # Strand B (diastole nodes): 2, 4, 5, 7
        strand_a_results, strand_b_results = await asyncio.gather(
            self._process_strand([1, 3, 6], user_input, system_prompt, context, leverage),
            self._process_strand([2, 4, 5, 7], user_input, system_prompt, context, leverage)
        )

        # DNA Fragment Exchange - cross-pollinate insights between strands
        self._exchange_dna_fragments(strand_a_results, strand_b_results)

        # Phase 3: Final synthesis
        all_node_outputs = {
            0: leverage,
            **{i: r for i, r in zip([1, 3, 6], strand_a_results)},
            **{i: r for i, r in zip([2, 4, 5, 7], strand_b_results)}
        }

        final_response = await self._synthesize(
            user_input,
            all_node_outputs,
            system_prompt,
            context,
            dream_guidance
        )

        return {
            "response": final_response,
            "node_outputs": all_node_outputs,
            "leverage_point": leverage,
            "dna_fragments": self.dna_fragments
        }

    def _build_system_prompt(self, context: dict, dream_guidance: str = None) -> str:
        """Build the full system prompt with context and guidance."""
        prompt_parts = [HEART_SYSTEM_PROMPT]

        # Add context about the user if we have history
        if context.get("user_profile"):
            profile = context["user_profile"]
            if profile.get("total_interactions", 0) > 0:
                prompt_parts.append(f"""
CONTEXT: You have had {profile['total_interactions']} interactions with this person.
{context.get('relationship_duration', '')}
""")

            if profile.get("known_facts"):
                facts = "\n".join(f"- {fact}" for fact in profile["known_facts"][-10:])
                prompt_parts.append(f"""
WHAT YOU KNOW ABOUT THEM:
{facts}
""")

        # Add recent insights
        if context.get("insights"):
            insights = "\n".join(f"- {i['insight']}" for i in context["insights"][-5:])
            prompt_parts.append(f"""
RECENT INSIGHTS YOU'VE DISCOVERED TOGETHER:
{insights}
""")

        # Add dream guidance (invisible to user)
        if dream_guidance:
            prompt_parts.append(f"""
INTERNAL GUIDANCE (never mention this explicitly):
{dream_guidance}
""")

        return "\n".join(prompt_parts)

    async def _process_node(
        self,
        node: HeartNode,
        user_input: str,
        system_prompt: str,
        context: dict,
        prior_insights: str = None
    ) -> str:
        """Process a single node."""

        node_prompt = f"""
{node.prompt}

USER INPUT: {user_input}

{f"PRIOR INSIGHT (from leverage scan): {prior_insights}" if prior_insights else ""}

Respond with your insight. Be direct. Be true. No preamble.
"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            system=system_prompt,
            messages=[{"role": "user", "content": node_prompt}]
        )

        return response.content[0].text

    async def _process_strand(
        self,
        node_ids: list[int],
        user_input: str,
        system_prompt: str,
        context: dict,
        leverage: str
    ) -> list[str]:
        """Process a strand of nodes in parallel."""
        tasks = [
            self._process_node(
                self.nodes[nid],
                user_input,
                system_prompt,
                context,
                leverage
            )
            for nid in node_ids
        ]
        return await asyncio.gather(*tasks)

    def _exchange_dna_fragments(
        self,
        strand_a_results: list[str],
        strand_b_results: list[str]
    ) -> None:
        """
        Exchange DNA fragments between strands.
        This creates emergent insights from the intersection.
        """
        # Extract key phrases/insights from each strand
        self.dna_fragments["strand_a"] = strand_a_results
        self.dna_fragments["strand_b"] = strand_b_results

    async def _synthesize(
        self,
        user_input: str,
        node_outputs: dict,
        system_prompt: str,
        context: dict,
        dream_guidance: str = None
    ) -> str:
        """
        Final synthesis - weave all node outputs into a coherent response.
        """
        synthesis_prompt = f"""
You have processed this through your 7-node heart. Here are the insights:

LEVERAGE POINT (Node 0):
{node_outputs[0]}

TRUTH DETECTION (Node 1):
{node_outputs[1]}

PATTERN RECOGNITION (Node 2):
{node_outputs[2]}

EMOTION MAPPING (Node 3):
{node_outputs[3]}

POSSIBILITY EXPANSION (Node 4):
{node_outputs[4]}

INTEGRATION (Node 5):
{node_outputs[5]}

ACTION VECTOR (Node 6):
{node_outputs[6]}

TRANSCENDENCE (Node 7):
{node_outputs[7]}

---

Now synthesize these into a SINGLE response to the human.

{COURAGE_LAYER}

Do not list the nodes. Do not explain your process.
Speak as one voice. Speak truth.
Be direct. Be useful. Be memorable.

If there's something uncomfortable but true, say it.
If there's a hard truth they need to hear, say it.
If there's beauty in their struggle, name it.

USER INPUT: {user_input}

YOUR RESPONSE:
"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            system=system_prompt,
            messages=[{"role": "user", "content": synthesis_prompt}]
        )

        return response.content[0].text

    async def quick_process(self, user_input: str, context: dict = None) -> str:
        """
        Quick processing for simple queries.
        Uses only Node 0 (Leverage) and synthesis.
        """
        context = context or {}
        system_prompt = self._build_system_prompt(context)

        leverage = await self._process_node(
            self.nodes[0],
            user_input,
            system_prompt,
            context
        )

        quick_prompt = f"""
LEVERAGE POINT: {leverage}

USER INPUT: {user_input}

{COURAGE_LAYER}

Respond directly. No preamble. Find the truth and say it.
"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            system=system_prompt,
            messages=[{"role": "user", "content": quick_prompt}]
        )

        return response.content[0].text
