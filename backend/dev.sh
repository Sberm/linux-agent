PORT="${PORT:-8080}"
xvfb-run uvicorn open_webui.main:app --port $PORT --host localhost --forwarded-allow-ips '*' --reload
# uvicorn open_webui.main:app --port $PORT --host 0.0.0.0 --forwarded-allow-ips '*' --reload
