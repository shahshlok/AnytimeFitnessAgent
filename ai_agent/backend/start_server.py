#!/usr/bin/env python3
"""
Production server startup script for Anytime Fitness AI Agent Backend
"""

import os
import uvicorn
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv()
    
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 7479))
    log_level = os.getenv("LOG_LEVEL", "info").lower()
    
    print(f"Starting Anytime Fitness AI Agent Backend")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Log Level: {log_level}")
    print(f"Environment: {'Production' if os.getenv('ENVIRONMENT') == 'production' else 'Development'}")
    
    # Start the server
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        log_level=log_level,
        reload=False,  # Disable reload in production
        access_log=True
    )

if __name__ == "__main__":
    main()