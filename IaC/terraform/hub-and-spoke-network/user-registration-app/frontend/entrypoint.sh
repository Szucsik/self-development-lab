#!/bin/sh
set -e

# Inject the backend URL (passed as an env var) into a config.js file
# that index.html loads before app.js. This lets the same built image
# point at different backend URLs without rebuilding.
API_URL="${API_BASE_URL:-http://localhost:8000}"

cat > /usr/share/nginx/html/config.js <<EOF
window.API_BASE_URL = "${API_URL}";
EOF

exec nginx -g 'daemon off;'
