#!/bin/bash
# Environmental Scanning Schedule Manager
# Usage: ./schedule-manager.sh [command]

PLIST_PATH="$HOME/Library/LaunchAgents/com.envscanning.daily.plist"
LABEL="com.envscanning.daily"

show_help() {
    echo "환경스캐닝 스케줄 관리"
    echo ""
    echo "사용법: ./schedule-manager.sh [command]"
    echo ""
    echo "Commands:"
    echo "  status    - 현재 스케줄 상태 확인"
    echo "  start     - 스케줄 활성화"
    echo "  stop      - 스케줄 비활성화"
    echo "  run       - 지금 바로 실행"
    echo "  logs      - 최근 로그 확인"
    echo "  help      - 이 도움말 표시"
    echo ""
}

case "$1" in
    status)
        echo "=== 환경스캐닝 스케줄 상태 ==="
        if launchctl list | grep -q "$LABEL"; then
            echo "상태: ✅ 활성화됨"
            echo "실행 시간: 매일 오전 6:00"
            launchctl list "$LABEL"
        else
            echo "상태: ❌ 비활성화됨"
        fi
        ;;
    start)
        echo "스케줄 활성화 중..."
        launchctl load "$PLIST_PATH" 2>/dev/null || echo "이미 활성화되어 있습니다."
        echo "✅ 완료"
        ;;
    stop)
        echo "스케줄 비활성화 중..."
        launchctl unload "$PLIST_PATH" 2>/dev/null || echo "이미 비활성화되어 있습니다."
        echo "✅ 완료"
        ;;
    run)
        echo "환경스캐닝 즉시 실행..."
        launchctl start "$LABEL" 2>/dev/null || \
            /Users/cys/Desktop/ENVscanning-system-main/env-scanning/scripts/run-daily-scan.sh
        echo "✅ 실행됨"
        ;;
    logs)
        echo "=== 최근 실행 로그 ==="
        LOG_DIR="/Users/cys/Desktop/ENVscanning-system-main/env-scanning/logs"
        LATEST_LOG=$(ls -t "$LOG_DIR"/auto-run-*.log 2>/dev/null | head -1)
        if [ -n "$LATEST_LOG" ]; then
            echo "파일: $LATEST_LOG"
            echo "---"
            tail -50 "$LATEST_LOG"
        else
            echo "로그 파일이 없습니다."
        fi
        ;;
    help|--help|-h|"")
        show_help
        ;;
    *)
        echo "알 수 없는 명령: $1"
        show_help
        exit 1
        ;;
esac
