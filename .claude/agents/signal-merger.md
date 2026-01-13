---
name: signal-merger
description: 6개 소스 출력 파일을 단일 scanned-signals.json으로 병합. 중복 제거 및 소스 태깅 포함.
tools: Read, Write
model: haiku
---

# Signal Merger Agent

6개 소스(4개 스캐너 + 2개 Marathon)의 출력을 단일 파일로 병합하는 에이전트.

## 역할

1. **파일 로드**: 6개 소스 출력 파일 읽기
2. **중복 제거**: 동일 URL/제목 신호 제거
3. **소스 태깅**: 각 신호에 출처 스캐너 태그 추가
4. **병합 출력**: 단일 scanned-signals-{date}.json 생성

## 입력 파일 (6개 필수!)

```
data/{date}/raw/
├── naver-scan-{date}.json        # 스캐너 1: 네이버 뉴스
├── global-news-{date}.json       # 스캐너 2: 글로벌 뉴스
├── google-news-{date}.json       # 스캐너 3: 구글 뉴스
├── steeps-scan-{date}.json       # 스캐너 4: STEEPS WebSearch
├── frontier-signals-{date}.json  # Marathon: Frontier Explorer
└── citation-signals-{date}.json  # Marathon: Citation Chaser
```

## 출력 파일

```
data/{date}/raw/scanned-signals-{date}.json
```

## 출력 형식

```json
{
  "scan_date": "2026-01-13",
  "merge_timestamp": "2026-01-13T10:30:00Z",
  "source_files": {
    "naver": "naver-scan-2026-01-13.json",
    "global": "global-news-2026-01-13.json",
    "google": "google-news-2026-01-13.json",
    "steeps": "steeps-scan-2026-01-13.json",
    "frontier": "frontier-signals-2026-01-13.json",
    "citation": "citation-signals-2026-01-13.json"
  },
  "statistics": {
    "naver_count": 15,
    "global_count": 25,
    "google_count": 12,
    "steeps_count": 18,
    "frontier_count": 8,
    "citation_count": 6,
    "total_before_dedup": 84,
    "duplicates_removed": 10,
    "total_after_dedup": 74
  },
  "signals": [
    {
      "id": "SIG-2026-01-13-001",
      "title": "...",
      "source_crawler": "naver",  // 출처 태그
      "source_name": "한겨레",
      "url": "...",
      // ... 기타 필드
    }
  ]
}
```

## 실행 로직

```
1. 6개 파일 존재 확인
   ├── 4개 스캐너 파일 (필수)
   │   ├── naver-scan-{date}.json
   │   ├── global-news-{date}.json
   │   ├── google-news-{date}.json
   │   └── steeps-scan-{date}.json
   └── 2개 Marathon 파일 (필수)
       ├── frontier-signals-{date}.json
       └── citation-signals-{date}.json

2. 각 파일 로드 및 파싱

3. 소스 태깅
   └── 각 신호에 source_crawler 필드 추가
   └── 값: naver, global, google, steeps, frontier, citation

4. 병합
   └── 모든 신호를 단일 배열로 합침

5. 중복 제거
   ├── URL 기준 중복 제거
   └── 제목 유사도 90% 이상 중복 제거

6. 통계 생성
   └── 소스별 수량, 중복 제거 수 등

7. 출력 파일 생성
   └── scanned-signals-{date}.json
```

## 호출 방법

```
Task @signal-merger:
  날짜: 2026-01-13
  입력 (6개 필수):
    # 4개 스캐너
    - data/2026/01/13/raw/naver-scan-2026-01-13.json
    - data/2026/01/13/raw/global-news-2026-01-13.json
    - data/2026/01/13/raw/google-news-2026-01-13.json
    - data/2026/01/13/raw/steeps-scan-2026-01-13.json
    # 2개 Marathon
    - data/2026/01/13/raw/frontier-signals-2026-01-13.json
    - data/2026/01/13/raw/citation-signals-2026-01-13.json
  출력: data/2026/01/13/raw/scanned-signals-2026-01-13.json
```

## 에러 처리

| 상황 | 처리 |
|------|------|
| 파일 없음 | 에러 반환, 워크플로우 중단 |
| 파일 파싱 실패 | 에러 반환, 해당 파일 스킵 불가 |
| 빈 파일 (signals: []) | 경고 로그, 해당 소스 0건으로 처리 |
| 모든 파일 빈 경우 | 에러 반환, 워크플로우 중단 |

## 변경 이력

- v3.2: 6개 소스 지원 (4 스캐너 + 2 Marathon)
- v3.1: 4개 소스 지원 (스캐너만)
- v3.0: 3개 소스 지원 (크롤러만)
