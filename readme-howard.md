#### WEBUI

url: http://47.186.55.156:56702/

> already running in 'tmux a -t webui'

## front
npm run dev -- --port 8384 --host 0.0.0.0

## back
normally just to 'sh dev.sh'

PORT="${PORT:-8080}"
uvicorn open_webui.main:app --port $PORT --host 0.0.0.0 --forwarded-allow-ips '*' --reload

## env
# Ollama URL for the backend to connect
# The path '/ollama' will be redirected to the specified backend URL
OLLAMA_BASE_URL='http://localhost:11434'

OPENAI_API_BASE_URL=''
OPENAI_API_KEY=''

# AUTOMATIC1111_BASE_URL="http://localhost:7860"

# DO NOT TRACK
SCARF_NO_ANALYTICS=true
DO_NOT_TRACK=true
ANONYMIZED_TELEMETRY=false

WEBUI_URL='http://47.186.55.156:56702'

PORT=56574
CORS_ALLOW_ORIGIN='http://47.186.55.156:56702'

## ollama
ollama serve

#### Data

Put them in rag-data, before feeding to the vector database

#### Web crawling

In ./web_crawling