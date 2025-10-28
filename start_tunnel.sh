#!/bin/bash
# Start Cloudflare Tunnel

echo "Starting Cloudflare Tunnel..."
echo "Flask server status:"
curl -s http://localhost:5000/health || echo "ERROR: Flask not running!"

echo ""
echo "Starting tunnel..."
/tmp/cloudflared tunnel --url http://localhost:5000 2>&1 | tee /tmp/current-tunnel.log &
TUNNEL_PID=$!

echo "Tunnel PID: $TUNNEL_PID"
echo "Waiting for tunnel URL..."

# Wait and extract URL
for i in {1..20}; do
    sleep 1
    URL=$(grep -oP 'https://[a-z0-9-]+\.trycloudflare\.com' /tmp/current-tunnel.log 2>/dev/null | head -1)
    if [ ! -z "$URL" ]; then
        echo ""
        echo "================================"
        echo "✅ TUNNEL ACTIVE!"
        echo "================================"
        echo ""
        echo "🌐 Public URL: $URL"
        echo ""
        echo "Test it:"
        echo "  curl $URL/health"
        echo ""
        exit 0
    fi
    echo -n "."
done

echo ""
echo "❌ Timeout waiting for tunnel URL"
echo "Check logs: cat /tmp/current-tunnel.log"
