#!/bin/bash
# Environmental Scanning Daily Runner
# Runs at 06:00 AM daily via launchd

# Configuration
SCAN_DIR="/Users/cys/Desktop/ENVscanning-system-main"
LOG_DIR="$SCAN_DIR/logs"
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

# Run Claude Code in non-interactive mode
# --print: 비대화형 모드
# --permission-mode bypassPermissions: 권한 확인 건너뛰기
# --dangerously-skip-permissions: 모든 권한 체크 건너뛰기 (필요 시)
claude --print \
    --permission-mode bypassPermissions \
    "/env-scan:run --skip-human" >> "$LOG_FILE" 2>&1

EXIT_CODE=$?

# Log completion
echo "" >> "$LOG_FILE"
echo "Exit Code: $EXIT_CODE" >> "$LOG_FILE"
echo "Completed: $(date)" >> "$LOG_FILE"
echo "======================================" >> "$LOG_FILE"

# Send notification based on result
if [ $EXIT_CODE -eq 0 ]; then
    osascript -e 'display notification "환경스캐닝 완료. 보고서를 확인하세요." with title "Environmental Scanning" sound name "Glass"' 2>/dev/null
else
    osascript -e 'display notification "환경스캐닝 실패. 로그를 확인하세요." with title "Environmental Scanning Error" sound name "Basso"' 2>/dev/null
fi

exit $EXIT_CODE
