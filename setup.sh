#!/bin/bash
# Setup script for Vietnamese Token Optimizer
# Tự động cài đặt dependencies và thiết lập môi trường

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HERMES_MODE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --hermes)
            HERMES_MODE=true
            shift
            ;;
        *)
            shift
            ;;
    esac
done

echo "📦 Vietnamese Token Optimizer - Setup Script"
echo "=============================================="
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✓ Python $PYTHON_VERSION found"

# Create virtual environment
if [ "$HERMES_MODE" = false ]; then
    echo ""
    echo "Creating virtual environment..."
    
    if [ -d "$SCRIPT_DIR/venv" ]; then
        echo "  venv already exists, skipping..."
    else
        python3 -m venv "$SCRIPT_DIR/venv"
        echo "✓ Virtual environment created"
    fi
    
    # Activate venv
    source "$SCRIPT_DIR/venv/bin/activate"
    echo "✓ Virtual environment activated"
else
    echo "🔧 Hermes mode: skipping venv (using system Python)"
fi

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r "$SCRIPT_DIR/requirements.txt" > /dev/null 2>&1
echo "✓ Dependencies installed"

# Download pyvi model if needed
echo ""
echo "Setting up pyvi (Vietnamese word segmentation)..."
python3 << 'PYTHON_SCRIPT'
try:
    from pyvi import ViTokenizer
    print("✓ pyvi already configured")
except Exception as e:
    print(f"⚠ pyvi setup warning: {e}")
    print("  This is optional - the optimizer will still work without it")
PYTHON_SCRIPT

# Create config directory
echo ""
echo "Creating configuration files..."
mkdir -p "$SCRIPT_DIR/config"

# Copy template configs if not exists
if [ ! -f "$SCRIPT_DIR/config/config.json" ]; then
    cp "$SCRIPT_DIR/config.json" "$SCRIPT_DIR/config/" 2>/dev/null || true
    echo "✓ Config files created"
else
    echo "  Config already exists, skipping..."
fi

# Run tests if available
echo ""
if [ -f "$SCRIPT_DIR/tests/test_optimizer.py" ]; then
    echo "Running tests..."
    python3 -m pytest "$SCRIPT_DIR/tests/" -v || true
else
    echo "⚠ Tests not found, skipping..."
fi

echo ""
echo "=============================================="
echo "✅ Setup complete!"
echo ""

if [ "$HERMES_MODE" = false ]; then
    echo "📝 Next steps:"
    echo "  1. Activate venv: source venv/bin/activate"
    echo "  2. Run optimizer: python -m optimizer --text 'Xin chào'"
    echo "  3. Or: python -m optimizer --help"
else
    echo "📝 Next steps (Hermes):"
    echo "  1. Add to ~/.hermes/config.yaml:"
    echo "     auxiliary:"
    echo "       vietnamese_optimizer:"
    echo "         enabled: true"
    echo "         module: hermes-vietnamese-token-optimizer"
    echo "  2. Restart Hermes Agent"
fi

echo ""
echo "📚 Documentation: https://github.com/hai-again-bro/hermes-vietnamese-token-optimizer"
