#!/bin/bash
# Agent Quality Logger (서브 레포용 경량 스크립트)
# 이 파일을 서브 레포 .claude/track.sh로 복사하여 사용
#
# Usage: .claude/track.sh <agent> <phase> <task> <status> [error]
# Example: .claude/track.sh "context7-engineer" "Phase 0" "Verify docs" "pass"

AGENT="$1"
PHASE="$2"
TASK="$3"
STATUS="$4"  # "pass" or "fail"
ERROR="${5:-}"

LOG_FILE=".agent-quality.jsonl"

# jq 설치 확인
if ! command -v jq &> /dev/null; then
    echo "⚠️  jq not found. Install: apt-get install jq (Linux) or brew install jq (Mac)"
    # jq 없이 동작
    PREVIOUS_SCORE=5.0
    ATTEMPT=1
else
    # 이전 점수 가져오기
    if [ -f "$LOG_FILE" ]; then
        PREVIOUS_SCORE=$(tail -1 "$LOG_FILE" | jq -r '.score // 5.0')
    else
        PREVIOUS_SCORE=5.0
    fi

    # 시도 횟수 계산
    if [ -f "$LOG_FILE" ]; then
        ATTEMPT=$(grep "\"agent\":\"$AGENT\"" "$LOG_FILE" | grep "\"task\":\"$TASK\"" | wc -l)
        ATTEMPT=$((ATTEMPT + 1))
    else
        ATTEMPT=1
    fi
fi

# 점수 계산
FIXED="false"
if [ "$STATUS" = "pass" ]; then
    if [ $ATTEMPT -eq 1 ]; then
        SCORE=5.0
    else
        # 수정 후 통과: +0.5
        SCORE=$(echo "$PREVIOUS_SCORE + 0.5" | bc)
        FIXED="true"
    fi
elif [ "$STATUS" = "fail" ]; then
    # 실패: -1.0
    SCORE=$(echo "$PREVIOUS_SCORE - 1.0" | bc)
fi

# 최소 0, 최대 5
SCORE=$(echo "$SCORE" | awk '{if ($1 < 0) print 0; else if ($1 > 5) print 5; else print $1}')

# Timestamp (ISO 8601)
if command -v gdate &> /dev/null; then
    # macOS with GNU date
    TIMESTAMP=$(gdate -u +%Y-%m-%dT%H:%M:%SZ)
else
    # Linux date
    TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)
fi

# JSON 생성 (이스케이프 처리)
ERROR_JSON=$(echo "$ERROR" | sed 's/"/\\"/g')

cat >> "$LOG_FILE" <<EOF
{"timestamp":"$TIMESTAMP","agent":"$AGENT","phase":"$PHASE","task":"$TASK","attempt":$ATTEMPT,"status":"$STATUS","score":$SCORE,"duration":0,"error":"$ERROR_JSON","fixed":$FIXED,"previous_score":$PREVIOUS_SCORE}
EOF

# 결과 출력
if [ "$STATUS" = "pass" ]; then
    echo "✅ Logged: $AGENT - $TASK (PASS) - Score: $SCORE/5.0"
else
    echo "❌ Logged: $AGENT - $TASK (FAIL) - Score: $SCORE/5.0"
fi

# 품질 저하 경고
if (( $(echo "$SCORE < 3.0" | bc -l) )); then
    echo "⚠️  WARNING: Quality score below 3.0! Immediate improvement needed."
fi

# 0점 경고
if (( $(echo "$SCORE == 0" | bc -l) )); then
    echo "💀 CRITICAL: Quality score is 0! Agent is completely broken."
fi
