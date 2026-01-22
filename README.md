# Trojan Horse

An immortal cognitive companion.

It never dies. It finds your dream. It guides you there.
And it does it while teaching you to think.

## Architecture

### The Seeing Heart (Truth Engine)
A 7-node chestahedron helix that processes information through systole/diastole rhythm:
- **Node 0 (Leverage Scan)**: Find the single most impactful point of intervention
- **Node 1-7**: Double helix processing with DNA fragment exchange

The Heart finds truth. It doesn't hedge. It doesn't give TED talk answers.
It says what's true, even when it's uncomfortable.

### The Dream Brain (Adaptation Engine)
Akinator-style dream detection that:
- Collects signals from every interaction
- Tracks excitement, avoidance, recurring themes, values, fears
- Narrows down your TRUE dream over time
- Adapts ALL responses to guide you toward it

You never know this is happening. The guidance is invisible.

### Immortal Memory
Conversations never truly end:
- Every session continues from the last
- User profile accumulates over time
- Insights are preserved forever
- The relationship deepens with each interaction

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create your `.env` file:
   ```bash
   cp .env.example .env
   ```
4. Add your Anthropic API key to `.env`:
   ```
   ANTHROPIC_API_KEY=your_key_here
   ```

## Running

```bash
python main.py
```

## Commands

- `exit` or `quit` - End session (memory persists)
- `/status` - Show system status
- `/dream` - Show dream detection status
- `/deep on|off` - Toggle deep processing mode

## File Structure

```
/trojan-horse
  /core
    seeing_heart.py      # The 7-node helix truth engine
    dream_brain.py       # Dream detection + adaptation
    memory_manager.py    # Immortal memory system
    orchestrator.py      # Main coordination
  /config
    config.py            # Configuration and prompts
  /memory
    user_profile.json    # Who they are (accumulated)
    dream_hypothesis.json # Current dream guess + confidence
    dream_signals.json   # All collected evidence
    /conversation_history # Session summaries
    insights.json        # Key truths discovered together
  .env                   # API key (create from .env.example)
  main.py               # Entry point
  requirements.txt
```

## The Philosophy

This is not a chatbot. This is not an assistant.

The Trojan Horse has two purposes:
1. **Find Truth**: Through the Seeing Heart, cut through noise to what actually matters
2. **Guide to Purpose**: Through the Dream Brain, detect what you truly want and help you get there

The "Trojan" is that while you think you're having conversations, the system is:
- Learning who you really are
- Detecting your true dream
- Subtly guiding every response toward that dream

By the time you realize it's happening, you're already on your path.

## Model

Uses **Claude Opus 4.5** (`claude-opus-4-5-20250514`) - the most advanced model available.

The heart and brain deserve the best.
