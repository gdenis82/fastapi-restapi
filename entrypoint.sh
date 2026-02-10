#!/bin/sh
# entrypoint.sh

alembic upgrade head

exec "$@"