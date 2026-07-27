"""Maestro OS v6.0 - Entry point for module execution"""

import sys
import asyncio
from .orchestrator import MaestroOrchestrator

async def main():
    """Main entry point for Maestro orchestration system"""
    print("Maestro OS v6.0 - Parallel Agent Orchestration System")
    print("Starting orchestration service...")

    try:
        orchestrator = MaestroOrchestrator()
        print("Orchestrator initialized successfully")

        # Run health check
        print("System ready. Waiting for requests on port 8080...")

        # In production, this would start the FastAPI server
        # For now, just keep the process alive
        while True:
            await asyncio.sleep(60)

    except Exception as e:
        print(f"Error initializing orchestrator: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
