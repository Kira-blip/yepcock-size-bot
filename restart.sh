#!/usr/bin/sh
pkill python3
sleep 5
nohup python3 bot.py > logs/nohup.log &
