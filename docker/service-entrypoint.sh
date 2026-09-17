#!/usr/bin/env bash
set -Eeuo pipefail
: "${AI_TOOLKIT_AUTH:?Set a nonempty AI_TOOLKIT_AUTH for the training service}"
cd /app/ai-toolkit/ui
# Requires an existing mounted /state directory; initializes new DBs without resetting old data.
npx --no-install prisma db push --skip-generate
exec npm run start
