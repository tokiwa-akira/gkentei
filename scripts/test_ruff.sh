#!/bin/bash

# Ruff configuration test script

set -e

echo "🔧 Testing Ruff configuration..."

cd backend

echo "📦 Installing dependencies..."
uv sync --dev

echo "🔍 Running Ruff checks..."

# Test linting
echo "  • Lint check..."
uv run ruff check app/ --diff || echo "    ⚠️  Linting issues found (expected for initial run)"

# Test formatting
echo "  • Format check..."
uv run ruff format --check app/ || echo "    ⚠️  Formatting issues found (expected for initial run)"

# Test security rules
echo "  • Security check..."
uv run ruff check app/ --select S || echo "    ⚠️  Security issues found (will be addressed)"

# Test import sorting
echo "  • Import sorting check..."
uv run ruff check app/ --select I || echo "    ⚠️  Import issues found (will be fixed)"

# Show Ruff version and config
echo "📋 Ruff information:"
uv run ruff --version
echo ""
echo "📝 Ruff configuration summary:"
uv run ruff config
echo ""

# Test auto-fix capability (dry run)
echo "🔧 Testing auto-fix (dry run)..."
uv run ruff check app/ --fix --diff --show-fixes || echo "    ✅ Auto-fix test completed"

echo ""
echo "✅ Ruff configuration test completed!"
echo ""
echo "💡 To apply fixes automatically:"
echo "   uv run ruff check app/ --fix"
echo "   uv run ruff format app/"
echo ""
echo "🚀 To run full quality check:"
echo "   uv run ruff check app/ && uv run ruff format --check app/ && uv run mypy app/"