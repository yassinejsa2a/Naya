#!/usr/bin/env python3
"""
NAYA Travel Journal Backend
"""

import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', 5000))
    
    print(f"Starting NAYA API on http://{host}:{port}")
    print(f"Debug mode: {debug_mode}")
    
    # Start the Flask development server
    app.run(
        host=host,
        port=port,
        debug=debug_mode,
        threaded=True
    )