#!/bin/bash
# Start both backend and frontend for development

# Start backend in the background
python -m code_pattern_analyzer web serve &
BACKEND_PID=$!

# If frontend exists, start it too
if [ -d "web_ui/frontend" ]; then
    cd web_ui/frontend
    npm start &
    FRONTEND_PID=$!
fi

# Handle Ctrl+C to stop both processes
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT

# Wait
wait

