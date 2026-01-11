# 환경스캐닝 정기 소스 분석 및 선정

**분석 일자**: 2026-01-11
**분석 기준**: 오늘 수행한 3회 스캔 (7day, rescan, ALT) 총 148개 신호

---

## 1. 소스 현황 요약

| 구분 | 소스 수 | 신호 수 | 평균 품질 |
|------|---------|---------|-----------|
| 7day 스캔 | 38 | 58 | 4.2 |
| rescan 스캔 | 25 | 42 | 4.0 |
| ALT 스캔 | 33 | 48 | 4.5 |
| **총 고유 소스** | **85** | **148** | **4.2** |

---

## 2. Tier별 소스 분류

### Tier 1: 최고 신뢰도 (1차 출처) - 일일 스캔
| 카테고리 | 소스 수 | 주요 소스 |
|----------|---------|-----------|
| 학술 저널 | 9 | Nature, Science, arXiv, Cell, Lancet, PNAS, Phys.org, ScienceDaily, ScienceDirect |
| 싱크탱크 | 8 | Brookings, Chatham House, McKinsey, PIIE, RAND, CFR, GMF, CIDOB |
| 국제기구 | 7 | World Bank, IMF, OECD, IEA, UN, UNCTAD, WEF |
| 정부기관 | 6 | NASA, NIH, NIST, NSF, Korea.kr, ESA |
| 대학연구소 | 4 | Stanford HAI, MIT Media Lab, Berkeley AI, Oxford FHI |

### Tier 2: 고신뢰도 (주요 언론/산업 분석) - 일일 스캔
| 카테고리 | 소스 수 | 주요 소스 |
|----------|---------|-----------|
| 기술 언론 | 6 | MIT Tech Review, CNBC, Bloomberg, Fast Company, Engadget, The Block |
| 지역 매체 | 4 | Nikkei Asia, Al Jazeera, Euronews, Channel News Asia |
| 산업 분석 | 4 | CB Insights, PitchBook, eMarketer, Gartner |
| 섹터 전문 | 5 | STAT News, Finextra, SemiWiki, ESS News, Battery Tech |
| 환경/기후 | 5 | Carbon Brief, Inside Climate News, CleanTechnica, ESG Dive, Yale Climate |
| 한국 | 5 | 경향신문, 매일경제, KDI, Korea Biz Review, Vogue Korea |
| 기업 뉴스룸 | 4 | NVIDIA, IBM, Qualcomm, Hyundai |

### Tier 3: 중신뢰도 (전문 매체) - 주간 스캔
| 카테고리 | 소스 수 | 주요 소스 |
|----------|---------|-----------|
| 트렌드 리포트 | 4 | Randstad, IMD, Ad Age, Retail Dive |
| 영성/웰니스 | 4 | Religion Unplugged, Mindful Leader, Travel Tomorrow, Good Housekeeping |

---

## 3. STEEPS별 커버리지

| 카테고리 | 커버리지 | 핵심 소스 | 보완 필요 |
|----------|----------|-----------|-----------|
| **Social** | ★★★★☆ | Lancet, Randstad, STAT News | 인구통계 전문 |
| **Technological** | ★★★★★ | Nature, arXiv, Stanford HAI, NVIDIA | - |
| **Economic** | ★★★★★ | World Bank, IMF, Bloomberg, CB Insights | - |
| **Environmental** | ★★★★★ | IEA, Carbon Brief, Inside Climate News | - |
| **Political** | ★★★★★ | Brookings, CFR, Chatham House, OECD | - |
| **Spiritual** | ★★★☆☆ | Religion Unplugged, Oxford FHI | 종교/윤리 학술지 추가 필요 |

---

## 4. 정기 스캔 일정

### 일일 스캔 (06:00 KST)
- **대상**: Tier 1 + Tier 2 전체 (68개 소스)
- **집중**: 속보, 정책 발표, 연구 출판

### 주간 심층 스캔 (매주 월요일 09:00 KST)
- **대상**: 전체 Tier (85개 소스)
- **집중**: 종합 리뷰, 트렌드 리포트, 산업 분석

### 월간 전략 스캔 (매월 첫째 월요일)
- **집중**: 장기 트렌드, 메타 신호, 시나리오 시사점

---

## 5. 제외된 소스

### 신뢰도 낮음
- heypop.kr (한국 트렌드 블로그)
- stupiddope.com (비공식 사이트)
- newneek.co (큐레이션 서비스)
- namu.wiki (위키 형식 비공식)

### 중복 콘텐츠
- 라이브 피드 어그리게이터 (tomsguide.com/news/live/*)
- 단순 보도자료 집계 사이트

---

## 6. 품질 기준

| 품질 점수 | 정의 | 인용 방식 |
|-----------|------|-----------|
| 5 | 학술 peer-review, 정부 공식, 1차 데이터 | 직접 인용 허용 |
| 4 | 주요 언론, 전문 분석 기관 | 출처 명시 필수 |
| 3 | 산업 매체, 지역 언론 | 교차 검증 권장 |
| 2 | 블로그, 트렌드 사이트 | 참고용으로만 |
| 1 | 검증되지 않은 소스 | 사용 금지 |

**보고서 포함 최소 품질**: 3점 이상

---

## 7. 개선 권장사항

### 단기 (1개월 내)
1. **Spiritual 카테고리 보강**: 종교학/윤리학 학술지 추가 (Journal of Religion, Ethics 등)
2. **글로벌 사우스 시각 확대**: 아프리카, 라틴아메리카 매체 추가

### 중기 (3개월 내)
1. **특허 데이터베이스 통합**: USPTO, WIPO 정기 모니터링
2. **오픈소스/탈중앙화 시각**: 대안 기술 커뮤니티 소스 추가

### 장기 (6개월 내)
1. **자동화 파이프라인**: RSS/API 기반 자동 수집 구현
2. **다국어 확장**: 일본어, 중국어, 아랍어 소스 추가

---

## 8. 파일 위치

```
env-scanning/config/
├── regular-sources.json     # 정기 스캔 소스 마스터 설정
└── SOURCE-ANALYSIS.md       # 본 분석 문서
```

---

**작성**: 환경스캐닝 시스템
**버전**: 1.0
**다음 검토**: 2026-02-11
