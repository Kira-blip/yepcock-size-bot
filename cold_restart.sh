#!/usr/bin/sh
pkill python3
sleep 5
d=$(date +%Y-%m-%d-%H-%M-%S)
cd /home/olegsvs/yep_bot
mkdir -p ../bot_backup/users_backups_$d/
mv users/* ../bot_backup/users_backups_$d/
python3 bot.py &
