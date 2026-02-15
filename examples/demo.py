#!/usr/bin/env python3
"""Demo for Debate Hub."""
import asyncio
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src import ConsensusEngine, Agent

async def main():
    print("Debate Hub Demo")
    ce = ConsensusEngine()
    agents = [Agent(agent_id=f"a{i}", name=f"Agent {i}") for i in range(3)]
    result = await ce.delegate_and_deliberate("Best approach?", agents)
    print(f"Success: {result.success}, Confidence: {result.confidence:.2f}")
    print("Done!")

if __name__ == "__main__": asyncio.run(main())
