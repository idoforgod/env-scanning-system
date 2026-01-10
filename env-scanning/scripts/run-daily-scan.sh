#!/bin/bash
# Environmental Scanning Daily Runner
# Runs at 06:00 AM daily via launchd

# Configuration
SCAN_DIR="/Users/cys/Desktop/ENVscanning-system-main"
LOG_DIR="$SCAN_DIR/env-scanning/logs"
DATE=$(date +%Y-%m-%d)
LOG_FILE="$LOG_DIR/auto-run-$DATE.log"

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Log start
echo "======================================" >> "$LOG_FILE"
echo "Environmental Scanning Started: $(date)" >> "$LOG_FILE"
echo "======================================" >> "$LOG_FILE"

# Change to project directory
cd "$SCAN_DIR" || exit 1

# Run Claude Code with the scan command
# Using --print for non-interactive mode
claude --print "/run-scan --skip-human" >> "$LOG_FILE" 2>&1

# Log completion
echo "" >> "$LOG_FILE"
echo "Completed: $(date)" >> "$LOG_FILE"
echo "======================================" >> "$LOG_FILE"

# Optional: Send notification (macOS)
osascript -e 'display notification "환경스캐닝 완료. 보고서를 확인하세요." with title "Environmental Scanning"' 2>/dev/null

exit 0
