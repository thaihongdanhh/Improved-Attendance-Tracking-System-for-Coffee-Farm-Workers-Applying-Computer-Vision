#!/usr/bin/env python3

import uvicorn
from app.main import app

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=5200,
        reload=True,
        access_log=True
    )