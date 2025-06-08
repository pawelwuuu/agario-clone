PORT   = 8765      # port serwera WebSocket
WIDTH  = 800       # szerokość okna klienta
HEIGHT = 600       # wysokość okna klienta
FPS    = 60        # docelowe klatki na sekundę

import os
# WebSocket server configuration
WS_PORT = int(os.environ.get("WS_PORT", 8000))

# HTTP server configuration (for health checks)
HTTP_PORT = int(os.environ.get("PORT", 8080))  # Render uses PORT env var