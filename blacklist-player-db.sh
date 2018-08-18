#!/bin/bash

read -d '' usage_string <<EOF
$(basename $0) <player>
EOF

if [ -z "$1" ]; then
     echo $usage_string
     exit 0
fi

set -e
player="${1,,}"
sql=$(cat blacklist_player.sql)
printf "%s\n" "${sql//\#NAME\#/$player}" | mysql -ucrawl tournament
echo "Removed entries for player $player from the database."
