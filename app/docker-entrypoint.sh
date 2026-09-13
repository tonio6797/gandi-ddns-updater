#!/usr/bin/env sh
set -e

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " Starting gandi-ddns..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

UPDATE_SCHEDULE=$(printf '%s' "${UPDATE_SCHEDULE:-*/5 * * * *}" | tr -d '"')

echo "    [+] Schedule: ${UPDATE_SCHEDULE}"
echo "    [+] Creating CRON entry..."
echo "${UPDATE_SCHEDULE} python /gandi-ddns.py" > /etc/crontabs/root
chmod 600 /etc/crontabs/root

echo "    [+] Running..."
echo ""
exec "$@"
