#!/bin/bash
# HELSSA Agents Workspace Cleanup Script
# This script cleans up the old directories and keeps only the unified structure

echo "🧹 Cleaning up HELSSA workspace..."

# Backup important files from old structure if needed
echo "📋 Creating backup of important files..."
mkdir -p /workspace/HELSSA_AGENTS/BACKUP_OLD

# Move any additional files from agent/ that might be useful
if [ -d "/workspace/agent" ]; then
    echo "📁 Found old agent directory"
    # Any specific files to preserve can be copied here
fi

if [ -d "/workspace/HELSSA-MAIN" ]; then
    echo "📁 Found old HELSSA-MAIN directory"
    # README or other root files
    if [ -f "/workspace/HELSSA-MAIN/README.md" ]; then
        cp "/workspace/HELSSA-MAIN/README.md" "/workspace/HELSSA_AGENTS/BACKUP_OLD/HELSSA_MAIN_README.md"
    fi
fi

echo "✅ Backup completed"

# Confirm the unified structure is ready
echo "🔍 Validating unified structure..."
if [ -f "/workspace/HELSSA_AGENTS/README_AGENTS.md" ] && \
   [ -f "/workspace/HELSSA_AGENTS/PROJECT_TREE_COMPLETE.md" ] && \
   [ -d "/workspace/HELSSA_AGENTS/HELSSA_DOCS" ] && \
   [ -d "/workspace/HELSSA_AGENTS/TEMPLATES" ]; then
    echo "✅ Unified structure validated"
else
    echo "❌ Unified structure incomplete - aborting cleanup"
    exit 1
fi

# Optional: Remove old directories (commented out for safety)
echo "⚠️  To complete cleanup, run:"
echo "   rm -rf /workspace/agent"
echo "   rm -rf /workspace/HELSSA-MAIN"
echo ""
echo "   Or keep them as backup and only use /workspace/HELSSA_AGENTS"

echo "🎯 Cleanup script completed!"
echo "📁 Unified structure location: /workspace/HELSSA_AGENTS"
echo "📖 Start with: cat /workspace/HELSSA_AGENTS/README_AGENTS.md"