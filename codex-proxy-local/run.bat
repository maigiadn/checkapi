@echo off
title Codex Model Proxy
cd /d "d:\ANTIGRAVITY\check_api\codex-proxy-local"
echo Khoi dong Codex Model Proxy...
set PROXY_TARGET=https://apikey.maivangia.com
set PROXY_PORT=18080
node model-proxy.js
pause
