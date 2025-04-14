#!/bin/bash
# Setup script for the Code Pattern Analyzer Web UI

# Create necessary directories
mkdir -p web_ui/static
mkdir -p web_ui/templates

# Install dependencies
pip install -r requirements.txt

# Check for installation of npm for frontend development
if command -v npm &> /dev/null; then
    echo "npm found, setting up React frontend..."
    
    # Create React app if it doesn't exist
    if [ ! -d "web_ui/frontend" ]; then
        npx create-react-app web_ui/frontend
        
        # Install frontend dependencies
        cd web_ui/frontend
        npm install axios chart.js react-chartjs-2 react-router-dom
        
        # Create a simple proxy configuration for development
        echo '{
  "proxy": "http://localhost:8000"
}' > package.json.tmp
        
        # Merge into the existing package.json
        jq -s '.[0] * .[1]' package.json package.json.tmp > package.json.new
        mv package.json.new package.json
        rm package.json.tmp
        
        cd ../..
    else
        echo "React app already exists, skipping creation"
    fi
else
    echo "npm not found. Frontend setup skipped."
    echo "To set up the frontend, install Node.js and npm, then run this script again."
fi

# Create a simple startup script
echo '#!/bin/bash
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
' > scripts/start_web_ui.sh
chmod +x scripts/start_web_ui.sh

echo "Setup complete!"
echo "Run 'python -m code_pattern_analyzer web serve' to start the API server"
echo "API documentation will be available at http://localhost:8000/docs"

if command -v npm &> /dev/null; then
    echo "To start both backend and frontend in development mode, run 'scripts/start_web_ui.sh'"
else
    echo "Note: Frontend setup was skipped because npm was not found"
fi