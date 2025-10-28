#!/usr/bin/env python3
"""
Backend startup script
Adds project root to Python path and starts FastAPI
"""

import sys
from pathlib import Path

# Add project root to Python path
root = Path(__file__).parent
sys.path.insert(0, str(root))

# Now import and run
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

