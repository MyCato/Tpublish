#!/bin/bash

# Setup script for Tpublish - Telegram Publisher Bot

echo "🤖 Setting up Tpublish - Telegram Publisher Bot..."
echo "=================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

echo "✅ Python 3 found"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3 first."
    exit 1
fi

echo "✅ pip3 found"

# Install requirements
echo "📦 Installing required packages..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Get your Telegram API credentials from https://my.telegram.org"
echo "2. Run the bot with: python3 main.py"
echo "3. Follow the setup wizard to configure your API credentials"
echo "4. Use 'python3 main.py --force' for automated continuous publishing"
echo ""
echo "📚 For detailed instructions, read the README.md file"
echo "🚀 Default message delay is set to 300 seconds (5 minutes) for safety"
echo ""
