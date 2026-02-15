# Debate Hub

A system for coordinating multiple agent perspectives with structured debate protocols and confidence scoring.

## Features

- **Structured Debate** - Multi-phase debates with opening, argument, rebuttal, synthesis
- **Perspective Collection** - Gather diverse agent perspectives on any question
- **Confidence Scoring** - Calculate confidence levels for consensus results
- **Synthesis Methods** - Weighted average, majority vote, confidence-weighted
- **Dissent Detection** - Identify and track minority opinions

## Quick Start

```python
from debate_hub import ConsensusEngine, Agent

ce = ConsensusEngine()
result = await ce.delegate_and_deliberate("Your question", [agent1, agent2, agent3])
print(result.synthesis, result.confidence)
```

## License

MIT
