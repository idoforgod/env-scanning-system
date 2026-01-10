# Signal Template

환경스캐닝 신호 표준 템플릿 (STEEPS 6개 카테고리).

## STEEPS Categories
- Social (사회)
- Technological (기술)
- Economic (경제)
- Environmental (환경)
- Political (정치)
- Spiritual (정신/영성)

## JSON Schema

```json
{
  "id": "SIG-{YYYY}-{MMDD}-{NNN}",
  "category": {
    "primary": "Technological",
    "secondary": ["Economic", "Spiritual"]
  },
  "title": "신호 제목 (한 줄 요약)",
  "description": "상세 설명 (2-3 문장)",
  "source": {
    "name": "출처 이름",
    "url": "https://...",
    "type": "news|academic|patent|policy|report",
    "published_date": "2026-01-09"
  },
  "leading_indicator": "이 신호가 선행 지표가 되는 미래 변화",
  "significance": 4,
  "significance_reason": "중요도 평가 근거",
  "potential_impact": {
    "short_term": "1년 내 예상 영향",
    "mid_term": "3년 내 예상 영향",
    "long_term": "10년 내 예상 영향"
  },
  "actors": [
    {
      "name": "행위자 이름",
      "type": "company|government|organization|individual",
      "role": "이 신호에서의 역할"
    }
  ],
  "status": "emerging",
  "first_detected": "2026-01-09",
  "last_updated": "2026-01-09",
  "confidence": 0.85,
  "related_signals": ["SIG-2025-1201-012", "SIG-2025-1215-034"],
  "tags": ["AI", "규제", "유럽"],
  "analyst_notes": "추가 분석 코멘트"
}
```

## Field Descriptions

### ID Format
`SIG-{YYYY}-{MMDD}-{NNN}`
- YYYY: 연도
- MMDD: 월일
- NNN: 당일 순번 (001~999)

### Status Values
| Status | 설명 | 기준 |
|--------|------|------|
| `emerging` | 초기 신호 | 최초 탐지, 단일 출처 |
| `developing` | 발전 중 | 다수 출처 확인, 구체화 |
| `mature` | 성숙 | 트렌드로 정착, 널리 인식 |
| `declining` | 약화 | 관심 감소, 대체 신호 등장 |

### Significance Scale (1-5)
| 점수 | 설명 |
|------|------|
| 1 | 매우 낮음 - 일상적 변화 |
| 2 | 낮음 - 약간의 변화 징후 |
| 3 | 보통 - 주목할 만한 변화 |
| 4 | 높음 - 중요한 변화 신호 |
| 5 | 매우 높음 - 패러다임 전환 가능 |

### Confidence Score (0.0-1.0)
| 범위 | 설명 |
|------|------|
| 0.8-1.0 | 높음 - 다수 신뢰 출처 확인 |
| 0.5-0.8 | 중간 - 단일 출처, 추가 확인 권장 |
| 0.3-0.5 | 낮음 - 미확인, 주의 필요 |
| 0.0-0.3 | 매우 낮음 - 루머 수준 |

## Example Signal

```json
{
  "id": "SIG-2026-0109-001",
  "category": {
    "primary": "Technological",
    "secondary": ["Political"]
  },
  "title": "EU, AI 에이전트 책임 규정 초안 발표",
  "description": "유럽연합이 자율적으로 행동하는 AI 에이전트에 대한 법적 책임 프레임워크 초안을 발표. AI 시스템의 자율적 결정에 대해 개발사와 운영사의 공동 책임을 명시.",
  "source": {
    "name": "European Commission",
    "url": "https://ec.europa.eu/...",
    "type": "policy",
    "published_date": "2026-01-08"
  },
  "leading_indicator": "글로벌 AI 에이전트 규제 표준화",
  "significance": 5,
  "significance_reason": "전 세계 AI 개발 방향에 영향을 미칠 선도적 규제",
  "potential_impact": {
    "short_term": "EU 진출 AI 기업의 컴플라이언스 대응 필요",
    "mid_term": "글로벌 AI 개발 표준에 반영",
    "long_term": "AI 에이전트 산업 구조 재편"
  },
  "actors": [
    {"name": "European Commission", "type": "government", "role": "규제 발의"},
    {"name": "OpenAI", "type": "company", "role": "규제 대상"},
    {"name": "Anthropic", "type": "company", "role": "규제 대상"}
  ],
  "status": "emerging",
  "first_detected": "2026-01-09",
  "last_updated": "2026-01-09",
  "confidence": 0.95,
  "related_signals": [],
  "tags": ["AI 에이전트", "규제", "EU", "법적 책임"],
  "analyst_notes": "미국, 중국의 후속 대응 모니터링 필요"
}
```
