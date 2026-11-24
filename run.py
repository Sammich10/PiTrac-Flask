#!/usr/bin/env python3

from app import create_app
import os

if __name__ == '__main__':
    app = create_app()
    # For HTTPS, use ssl_context='adhoc' (requires pyopenssl)
    # app.run(host='0.0.0.0', port=5000, debug=True, ssl_context='adhoc')
    
    # For HTTP only
    app.run(host='0.0.0.0', port=5000, debug=True)