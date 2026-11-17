"""
Entry point for running POMABuster backend API server.
"""

import uvicorn
import os
import sys

# Ensure backend module can be imported cleanly
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

if __name__ == "__main__":
    uvicorn.run("backend.api.server:app", host="127.0.0.1", port=8000, reload=True)
