"""
POMABuster CLI & Runner Script
Usage:
    python run.py             # Starts full-stack POMABuster (API + Dashboard at http://127.0.0.1:8000)
    python run.py --test      # Runs test suite verifying all algorithms
    python run.py --port 8000 # Custom port
"""

import sys
import os
import argparse
import subprocess
import uvicorn

def main():
    parser = argparse.ArgumentParser(description="POMABuster - Price Oracle Manipulation Attack Detector")
    parser.add_argument("--host", default="127.0.0.1", help="Host address (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Port (default: 8000)")
    parser.add_argument("--test", action="store_true", help="Run pytest detection engine test suite")
    parser.add_argument("--reload", action="store_true", help="Auto-reload on code changes")
    args = parser.parse_args()

    # Add workspace directory to python path
    workspace_dir = os.path.dirname(os.path.abspath(__file__))
    if workspace_dir not in sys.path:
        sys.path.insert(0, workspace_dir)

    if args.test:
        print("=" * 70)
        print("  Running POMABuster Research Paper Verification Test Suite")
        print("=" * 70)
        import pytest
        exit_code = pytest.main(["-v", "tests"])
        sys.exit(exit_code)

    print("=" * 75)
    print("  POMABuster: Price Oracle Manipulation Attack Detector in DeFi")
    print("  Based on IEEE Symposium on Security and Privacy (S&P) 2024")
    print("=" * 75)
    print(f"  [+] Backend API:       http://{args.host}:{args.port}/api")
    print(f"  [+] Swagger API Docs:  http://{args.host}:{args.port}/docs")
    print(f"  [+] React Dashboard:   http://{args.host}:{args.port}/")
    print("=" * 75)
    print("  Starting unified server... Press Ctrl+C to terminate.")
    print()

    uvicorn.run("backend.api.server:app", host=args.host, port=args.port, reload=args.reload)

if __name__ == "__main__":
    main()
