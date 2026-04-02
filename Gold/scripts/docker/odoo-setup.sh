#!/usr/bin/env bash
# odoo-setup.sh — Start Odoo 19 + PostgreSQL and install Accounting module
#
# Usage:
#   chmod +x odoo-setup.sh
#   ./odoo-setup.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="$SCRIPT_DIR/docker-compose.odoo.yml"

echo "Gold-tier AI Employee — Odoo ERP Setup"
echo "======================================="
echo ""

# Start containers
echo "Starting Odoo + PostgreSQL containers..."
docker compose -f "$COMPOSE_FILE" up -d

echo ""
echo "Waiting for Odoo to become healthy..."

MAX_WAIT=120
ELAPSED=0
while [ $ELAPSED -lt $MAX_WAIT ]; do
    if docker inspect --format='{{.State.Health.Status}}' gold-odoo 2>/dev/null | grep -q "healthy"; then
        echo "Odoo is healthy!"
        break
    fi
    sleep 5
    ELAPSED=$((ELAPSED + 5))
    echo "  Waiting... (${ELAPSED}s / ${MAX_WAIT}s)"
done

if [ $ELAPSED -ge $MAX_WAIT ]; then
    echo "WARNING: Odoo did not become healthy within ${MAX_WAIT}s"
    echo "Check logs: docker logs gold-odoo"
    exit 1
fi

echo ""
echo "======================================="
echo "Odoo is running at: http://localhost:8069"
echo ""
echo "First-time setup:"
echo "  1. Open http://localhost:8069 in your browser"
echo "  2. Create the database (use 'odoo' as DB name)"
echo "  3. Set admin email and password"
echo "  4. Install the 'Accounting' module from Apps"
echo ""
echo "For MCP integration, set these env vars:"
echo "  ODOO_URL=http://localhost:8069"
echo "  ODOO_DB=odoo"
echo "  ODOO_USERNAME=<your admin email>"
echo "  ODOO_PASSWORD=<your admin password>"
echo ""
echo "To stop: docker compose -f $COMPOSE_FILE down"
echo "To stop and remove data: docker compose -f $COMPOSE_FILE down -v"
echo "======================================="
