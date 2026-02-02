#!/bin/bash

# Exit on error
set -e

echo "📦 Installing Capacitor dependencies..."
npm install @capacitor/core @capacitor/cli @capacitor/ios

echo "� Fixing permissions for node_modules binaries..."
chmod -R +x node_modules/.bin/

echo "�📱 Initializing Capacitor..."
if [ -f "capacitor.config.ts" ]; then
    echo "   Config file already exists, skipping init."
else
    npx cap init EcoDrain com.ecodrain.mobile --web-dir dist
fi

echo "🏗️  Building web application..."
npm run build

echo "🍎 Adding iOS platform..."
if [ -d "ios" ]; then
    echo "   iOS platform already added, skipping."
else
    npx cap add ios
fi

echo "🔄 Syncing Capacitor..."
npx cap sync

echo "✅ Setup complete! You can now open the project in Xcode:"
echo "👉 npx cap open ios"
