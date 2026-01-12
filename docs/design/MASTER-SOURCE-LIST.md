# 환경스캐닝 마스터 소스 리스트 (Master Source List)

**작성일**: 2026-01-12
**버전**: 2.0
**분석 기준**: 2026-01-09 ~ 2026-01-11 전체 스캔 데이터 전수조사 (약 200+ 신호)

---

## 소스 관리 원칙 (Source Management Principles)

### 1. 소스 선정 기준

#### 1.1 품질 기준 (Quality Criteria)
| 등급 | 정의 | 조건 |
|------|------|------|
| **Tier 1** | 최고 신뢰도 | 학술 peer-review, 정부/국제기구 공식 발표, 1차 데이터 |
| **Tier 2** | 고신뢰도 | 주요 언론사, 산업 분석 기관, 기업 공식 뉴스룸 |
| **Tier 3** | 중신뢰도 | 전문 매체, 지역 언론, 산업 블로그 |
| **Tier 4** | 참고용 | 트렌드 사이트, 큐레이션 서비스, 개인 블로그 |

#### 1.2 신호 품질 점수 (Signal Quality Score)
- **5점**: 학술 peer-review, 정부 공식, 1차 데이터 → 직접 인용 허용
- **4점**: 주요 언론, 전문 분석 기관 → 출처 명시 필수
- **3점**: 산업 매체, 지역 언론 → 교차 검증 권장
- **2점**: 블로그, 트렌드 사이트 → 참고용으로만 사용
- **1점**: 검증되지 않은 소스 → 사용 금지

### 2. 소스 관리 원칙

#### 2.1 뉴스 소스 원칙
- **개별 기사가 아닌 메인 사이트를 소스로 등록**
- 특정 섹션(예: /technology, /science)은 별도 등록 가능
- RSS/API 가용 여부 확인 및 기록

#### 2.2 학술 소스 원칙
- **저널/플랫폼 단위로 등록** (개별 논문이 아닌)
- 오픈 액세스 여부 명시
- 주요 카테고리/분야 명시

#### 2.3 정책/보고서 소스 원칙
- **기관 메인 사이트를 소스로 등록**
- 정기 발간 주기 명시
- 언어(영어/한국어/다국어) 명시

### 3. 스캔 일정

| 유형 | 시간 | 대상 | 목적 |
|------|------|------|------|
| **일일 모닝 스캔** | 06:00 KST | Tier 1 + Tier 2 (Core) | 속보, 정책 발표, 주요 뉴스 |
| **주간 심층 스캔** | 매주 월요일 09:00 KST | 전체 Tier | 종합 리뷰, 트렌드 분석 |
| **월간 전략 스캔** | 매월 첫째 월요일 | 특수 소스 포함 | 장기 트렌드, 메타 분석 |

### 4. 소스 검토 주기
- **월간**: 새 소스 추가/기존 소스 활성 여부 확인
- **분기별**: STEEPS 커버리지 밸런스 점검
- **연간**: 전체 소스 리스트 대규모 재검토

---

## STEEPS 카테고리별 마스터 소스 리스트

### S - Social (사회) - 28개 소스

#### Tier 1 (4개)
| 소스명 | URL | 유형 | 언어 | 업데이트 | 비고 |
|--------|-----|------|------|----------|------|
| The Lancet | https://www.thelancet.com | 학술 | EN | Weekly | 글로벌 헬스, 공중보건 |
| PNAS | https://www.pnas.org | 학술 | EN | Weekly | 사회과학 포함 |
| Pew Research Center | https://www.pewresearch.org | 리서치 | EN | Weekly | 인구통계, 여론조사 |
| UN Population Division | https://population.un.org | 정책 | EN | Annual | 인구 데이터 |

#### Tier 2 (12개)
| 소스명 | URL | 유형 | 언어 | 업데이트 |
|--------|-----|------|------|----------|
| Randstad | https://www.randstadusa.com | 리포트 | EN | Quarterly |
| IMD | https://www.imd.org | 리포트 | EN | Monthly |
| Marketing Interactive | https://www.marketing-interactive.com | 뉴스 | EN | Daily |
| Futurist Speakers | https://www.futuristsspeakers.com | 트렌드 | EN | Weekly |
| PR Week | https://www.prweek.com | 뉴스 | EN | Daily |
| Newsweek | https://www.newsweek.com | 뉴스 | EN | Daily |
| Fast Company | https://www.fastcompany.com | 뉴스 | EN | Daily |
| HR Service Inc | https://www.hrserviceinc.com | 리포트 | EN | Monthly |
| Pinterest Trends | https://trends.pinterest.com | 트렌드 | EN | Monthly |
| 경향신문 | https://www.khan.co.kr | 뉴스 | KO | Daily |
| STAT News | https://www.statnews.com | 뉴스 | EN | Daily |
| Qureos | https://www.qureos.com | 리포트 | EN | Quarterly |

#### Tier 3 (12개)
| 소스명 | URL | 유형 | 언어 | 비고 |
|--------|-----|------|------|------|
| Good Housekeeping | https://www.goodhousekeeping.com | 라이프스타일 | EN | 웰빙 |
| Vogue Korea | https://www.vogue.co.kr | 라이프스타일 | KO | 트렌드 |
| Content Grip | https://www.contentgrip.com | 마케팅 | EN | Gen Z |
| Splashtop | https://www.splashtop.com | 리포트 | EN | 원격근무 |
| Influencer Marketing Factory | https://theinfluencermarketingfactory.com | 산업 | EN | 크리에이터 |
| Parade | https://parade.com | 라이프스타일 | EN | 웰니스 |
| Dr. Axe | https://draxe.com | 건강 | EN | 웰니스 |
| Healf | https://healf.com | 건강 | EN | 웰니스 |
| Toward Healthcare | https://www.towardshealthcare.com | 리포트 | EN | 디지털헬스 |
| OhmyNews | https://www.ohmynews.com | 뉴스 | KO | 한국 |
| Focus NJN | https://focusnjn.com | 뉴스 | KO | 한국 교육 |
| NY Korean | https://www.nykorean.net | 뉴스 | KO | 재외동포 |

---

### T - Technological (기술) - 52개 소스

#### Tier 1 - 학술/연구 (15개)
| 소스명 | URL | 유형 | 분야 | 비고 |
|--------|-----|------|------|------|
| Nature | https://www.nature.com | 학술 | 종합과학 | 최고 수준 |
| Science/AAAS | https://www.science.org | 학술 | 종합과학 | |
| arXiv | https://arxiv.org | 프리프린트 | AI/양자/물리 | Daily |
| Cell Press | https://www.cell.com | 학술 | 생명과학 | |
| PNAS | https://www.pnas.org | 학술 | 다학제 | |
| Phys.org | https://phys.org | 학술뉴스 | 물리/공학 | |
| ScienceDaily | https://www.sciencedaily.com | 학술뉴스 | 종합 | |
| ScienceDirect | https://www.sciencedirect.com | 학술DB | Elsevier | |
| Stanford HAI | https://hai.stanford.edu | 연구소 | AI 정책/윤리 | |
| MIT Media Lab | https://www.media.mit.edu | 연구소 | 혁신기술 | |
| Berkeley AI Research | https://bair.berkeley.edu | 연구소 | AI/로보틱스 | |
| Oxford FHI | https://www.fhi.ox.ac.uk | 연구소 | AI 안전 | |
| CAS Insights | https://www.cas.org | 연구 | 화학/바이오 | |
| IEEE Spectrum | https://spectrum.ieee.org | 학술뉴스 | 전기전자 | |
| ZAGENO | https://go.zageno.com | 산업 | 바이오텍 | |

#### Tier 1 - 정부/기관 (8개)
| 소스명 | URL | 유형 | 분야 |
|--------|-----|------|------|
| NASA | https://www.nasa.gov | 정부 | 우주/기후 |
| NIH | https://www.nih.gov | 정부 | 생명과학 |
| NIST | https://www.nist.gov | 정부 | 기술표준/사이버보안 |
| NSF | https://www.nsf.gov | 정부 | 기초과학 |
| ESA | https://www.esa.int | 정부 | 우주 |
| FDA | https://www.fda.gov | 정부 | 의약/의료기기 |
| Space.com | https://www.space.com | 뉴스 | 우주 |
| Payload Space | https://payloadspace.com | 뉴스 | 우주산업 |

#### Tier 2 - 기술 뉴스 (15개)
| 소스명 | URL | 유형 | 분야 |
|--------|-----|------|------|
| MIT Technology Review | https://www.technologyreview.com | 뉴스 | 심층기술 |
| TechCrunch | https://techcrunch.com | 뉴스 | 스타트업/AI |
| Fast Company | https://www.fastcompany.com | 뉴스 | 혁신/비즈니스 |
| Engadget | https://www.engadget.com | 뉴스 | 소비자기술 |
| The Block | https://www.theblock.co | 뉴스 | 크립토/블록체인 |
| DigiTimes | https://www.digitimes.com | 뉴스 | 반도체/IT |
| Interesting Engineering | https://interestingengineering.com | 뉴스 | 공학/로봇 |
| Tom's Guide | https://www.tomsguide.com | 뉴스 | CES/가전 |
| DirectIndustry | https://emag.directindustry.com | 뉴스 | 산업기술 |
| Yahoo Finance Tech | https://finance.yahoo.com/tech | 뉴스 | 기술산업 |
| WildNet Edge | https://www.wildnetedge.com | 트렌드 | 메타버스/VR |
| Business Today | https://www.businesstoday.in | 뉴스 | 인도기술 |
| GlobeNewswire | https://www.globenewswire.com | 보도자료 | 기업발표 |
| The Motley Fool | https://www.fool.com | 분석 | 기술투자 |
| Quartz | https://qz.com | 뉴스 | 기술경제 |

#### Tier 2 - 기업 뉴스룸 (10개)
| 소스명 | URL | 유형 | 분야 |
|--------|-----|------|------|
| NVIDIA Newsroom | https://nvidianews.nvidia.com | 기업 | AI 하드웨어 |
| IBM Newsroom | https://newsroom.ibm.com | 기업 | 양자/엔터프라이즈 |
| Qualcomm News | https://www.qualcomm.com/news | 기업 | 모바일/IoT |
| D-Wave Quantum | https://www.dwavequantum.com | 기업 | 양자컴퓨팅 |
| Hyundai Newsroom | https://www.hyundai.com/newsroom | 기업 | 모빌리티/로보틱스 |
| Mobileye News | https://www.mobileye.com/news | 기업 | 자율주행 |
| Lucid Motors | https://media.lucidmotors.com | 기업 | EV |
| Boston Dynamics | https://bostondynamics.com | 기업 | 로보틱스 |
| OpenAI Blog | https://openai.com/blog | 기업 | AI |
| Google DeepMind | https://deepmind.google | 기업 | AI 연구 |

#### Tier 3 - 섹터 전문 (4개)
| 소스명 | URL | 유형 | 분야 |
|--------|-----|------|------|
| SemiWiki | https://semiwiki.com | 산업 | 반도체 |
| Battery Technology Online | https://www.batterytechonline.com | 산업 | 배터리 |
| BioPharma Dive | https://www.biopharmadive.com | 산업 | 바이오제약 |
| Protein Production Technology | https://www.proteinproductiontechnology.com | 산업 | 대체단백질 |

---

### E - Economic (경제) - 35개 소스

#### Tier 1 - 국제기구/정부 (10개)
| 소스명 | URL | 유형 | 분야 |
|--------|-----|------|------|
| World Bank | https://www.worldbank.org | 기관 | 글로벌 개발 |
| IMF | https://www.imf.org | 기관 | 세계경제 |
| OECD | https://www.oecd.org | 기관 | 정책/데이터 |
| UN News | https://news.un.org | 기관 | 글로벌 |
| UNCTAD | https://unctad.org | 기관 | 무역개발 |
| World Economic Forum | https://www.weforum.org | 기관 | 글로벌 리스크 |
| KDI | https://www.kdi.re.kr | 기관 | 한국경제 |
| Korea.kr | https://www.korea.kr | 정부 | 한국정책 |
| Federal Reserve | https://www.federalreserve.gov | 정부 | 미국통화정책 |
| ECB | https://www.ecb.europa.eu | 정부 | 유럽통화정책 |

#### Tier 2 - 비즈니스 뉴스 (10개)
| 소스명 | URL | 유형 | 분야 |
|--------|-----|------|------|
| Bloomberg | https://www.bloomberg.com | 뉴스 | 금융/경제 |
| CNBC | https://www.cnbc.com | 뉴스 | 비즈니스 |
| Yahoo Finance | https://finance.yahoo.com | 뉴스 | 금융 |
| Nikkei Asia | https://asia.nikkei.com | 뉴스 | 아시아 경제 |
| 매일경제 | https://www.mk.co.kr | 뉴스 | 한국경제 |
| Euronews Business | https://www.euronews.com/business | 뉴스 | 유럽경제 |
| Channel News Asia | https://www.channelnewsasia.com | 뉴스 | 동남아경제 |
| Vietnam Plus | https://en.vietnamplus.vn | 뉴스 | 베트남/ASEAN |
| Korea Biz Review | https://www.koreabizreview.com | 뉴스 | 한국비즈니스 |
| Reuters | https://www.reuters.com | 뉴스 | 글로벌 |

#### Tier 2 - 산업 분석 (9개)
| 소스명 | URL | 유형 | 분야 |
|--------|-----|------|------|
| CB Insights | https://www.cbinsights.com | 리포트 | VC/스타트업 |
| PitchBook | https://pitchbook.com | 리포트 | PE/VC/M&A |
| eMarketer | https://www.emarketer.com | 리포트 | 디지털마케팅 |
| Gartner | https://www.gartner.com | 리포트 | IT전략 |
| McKinsey Global Institute | https://www.mckinsey.com/mgi | 리포트 | 산업/경제 |
| Peterson Institute | https://www.piie.com | 리포트 | 국제경제 |
| Finextra | https://www.finextra.com | 뉴스 | 핀테크 |
| GetStream | https://getstream.io | 리포트 | 라이브커머스 |
| Ad Age | https://adage.com | 산업 | 마케팅/광고 |

#### Tier 3 - 섹터/지역 (6개)
| 소스명 | URL | 유형 | 분야 |
|--------|-----|------|------|
| Retail Dive | https://www.retaildive.com | 뉴스 | 소매업 |
| Supply Chain Dive | https://www.supplychaindive.com | 뉴스 | 공급망 |
| Sourcing Journal | https://sourcingjournal.com | 뉴스 | 공급망 |
| Stimson Center | https://www.stimson.org | 리포트 | 지정학/경제 |
| Everstream Analytics | https://www.everstream.ai | 리포트 | 공급망 리스크 |
| Wood Mackenzie | https://www.woodmac.com | 리포트 | 에너지/자원 |

---

### E - Environmental (환경) - 22개 소스

#### Tier 1 (7개)
| 소스명 | URL | 유형 | 분야 |
|--------|-----|------|------|
| IEA | https://www.iea.org | 기관 | 에너지 |
| Carbon Brief | https://www.carbonbrief.org | 뉴스 | 기후과학/정책 |
| Inside Climate News | https://insideclimatenews.org | 뉴스 | 기후탐사보도 |
| Nature Climate Change | https://www.nature.com/nclimate | 학술 | 기후과학 |
| IPCC | https://www.ipcc.ch | 기관 | 기후변화 |
| UNEP | https://www.unep.org | 기관 | 환경 |
| WRI | https://www.wri.org | 연구소 | 환경/자원 |

#### Tier 2 (10개)
| 소스명 | URL | 유형 | 분야 |
|--------|-----|------|------|
| CleanTechnica | https://cleantechnica.com | 뉴스 | 청정기술/EV |
| ESG Dive | https://www.esgdive.com | 뉴스 | ESG |
| Yale Climate Connections | https://yaleclimateconnections.org | 뉴스 | 기후커뮤니케이션 |
| Energy Storage News | https://www.ess-news.com | 뉴스 | 배터리/그리드 |
| E&E News | https://www.eenews.net | 뉴스 | 에너지/환경정책 |
| Climate Change News | https://www.climatechangenews.com | 뉴스 | 기후정책 |
| Heatmap News | https://heatmap.news | 뉴스 | 기후/에너지 |
| C&EN | https://cen.acs.org | 뉴스 | 화학/환경 |
| Safety4Sea | https://safety4sea.com | 뉴스 | 해양/선박 |
| Aspen Public Radio | https://www.aspenpublicradio.org | 뉴스 | 수자원 |

#### Tier 3 (5개)
| 소스명 | URL | 유형 | 분야 |
|--------|-----|------|------|
| SBTi | https://sciencebasedtargets.org | 기관 | 탄소목표 |
| CDP | https://www.cdp.net | 기관 | 탄소공시 |
| IRENA | https://www.irena.org | 기관 | 재생에너지 |
| EIA | https://www.eia.gov | 정부 | 에너지정보 |
| EPA | https://www.epa.gov | 정부 | 환경규제 |

---

### P - Political (정치) - 28개 소스

#### Tier 1 - 싱크탱크 (10개)
| 소스명 | URL | 유형 | 분야 |
|--------|-----|------|------|
| Brookings Institution | https://www.brookings.edu | 싱크탱크 | 정책 종합 |
| Chatham House | https://www.chathamhouse.org | 싱크탱크 | 지정학 |
| RAND Corporation | https://www.rand.org | 싱크탱크 | 국방/안보 |
| Council on Foreign Relations | https://www.cfr.org | 싱크탱크 | 외교정책 |
| German Marshall Fund | https://www.gmfus.org | 싱크탱크 | 대서양관계 |
| CIDOB Barcelona | https://www.cidob.org | 싱크탱크 | 유럽/지중해 |
| Eurasia Group | https://www.eurasiagroup.net | 리포트 | 지정학리스크 |
| Carnegie Endowment | https://carnegieendowment.org | 싱크탱크 | 국제관계 |
| Center for Strategic Studies | https://www.csis.org | 싱크탱크 | 안보/전략 |
| Atlantic Council | https://www.atlanticcouncil.org | 싱크탱크 | 대서양동맹 |

#### Tier 2 - 뉴스/미디어 (10개)
| 소스명 | URL | 유형 | 분야 |
|--------|-----|------|------|
| Al Jazeera | https://www.aljazeera.com | 뉴스 | 중동/글로벌사우스 |
| Euronews | https://www.euronews.com | 뉴스 | 유럽정치 |
| The Diplomat | https://thediplomat.com | 뉴스 | 아시아정치 |
| TIME | https://time.com | 뉴스 | 글로벌 |
| Foreign Affairs | https://www.foreignaffairs.com | 저널 | 외교 |
| Foreign Policy | https://foreignpolicy.com | 저널 | 외교/안보 |
| Politico | https://www.politico.com | 뉴스 | 미국/EU정치 |
| ETC Journal | https://etcjournal.com | 뉴스 | AI정책 |
| 한겨레 | https://www.hani.co.kr | 뉴스 | 한국정치 |
| 조선일보 | https://www.chosun.com | 뉴스 | 한국정치 |

#### Tier 2 - 정부/법률 (8개)
| 소스명 | URL | 유형 | 분야 |
|--------|-----|------|------|
| EU Official Journal | https://eur-lex.europa.eu | 정부 | EU 법률 |
| EU AI Act Portal | https://artificialintelligenceact.eu | 정책 | AI 규제 |
| White House | https://www.whitehouse.gov | 정부 | 미국정책 |
| US Congress | https://www.congress.gov | 정부 | 미국입법 |
| Sidley Austin | https://datamatters.sidley.com | 법률 | 기술규제 |
| McDermott Will & Emery | https://www.mwe.com | 법률 | 환경규제 |
| National Law Review | https://www.natlawreview.com | 법률 | 규제동향 |
| 대한민국 정책브리핑 | https://www.korea.kr | 정부 | 한국정책 |

---

### S - Spiritual (영성) - 12개 소스

#### Tier 1 (2개)
| 소스명 | URL | 유형 | 분야 |
|--------|-----|------|------|
| Oxford FHI | https://www.fhi.ox.ac.uk | 연구소 | 존재적위험/윤리 |
| Templeton Foundation | https://www.templeton.org | 재단 | 과학/종교 |

#### Tier 2 (5개)
| 소스명 | URL | 유형 | 분야 |
|--------|-----|------|------|
| Religion Unplugged | https://religionunplugged.com | 뉴스 | 종교트렌드 |
| Mindful Leader | https://www.mindfulleader.org | 리포트 | 마음챙김 |
| Travel Tomorrow | https://traveltomorrow.com | 뉴스 | 웰니스여행 |
| Carey Nieuwhof | https://careynieuwhof.com | 블로그 | 종교/교회 |
| CosmicRx | https://cosmicrx.com | 트렌드 | 영성트렌드 |

#### Tier 3 (5개)
| 소스명 | URL | 유형 | 분야 |
|--------|-----|------|------|
| Good Housekeeping | https://www.goodhousekeeping.com | 라이프스타일 | 웰빙 |
| Bharat Bhraman | https://bharatbhraman.life | 블로그 | 영성 |
| NIH/PMC (Mental Health) | https://pmc.ncbi.nlm.nih.gov | 학술 | 정신건강 |
| Psychology Today | https://www.psychologytoday.com | 뉴스 | 심리/웰빙 |
| Greater Good Berkeley | https://greatergood.berkeley.edu | 연구 | 웰빙과학 |

---

## 소스 통계 요약

| 카테고리 | Tier 1 | Tier 2 | Tier 3 | 합계 |
|----------|--------|--------|--------|------|
| Social | 4 | 12 | 12 | **28** |
| Technological | 23 | 25 | 4 | **52** |
| Economic | 10 | 19 | 6 | **35** |
| Environmental | 7 | 10 | 5 | **22** |
| Political | 10 | 18 | 0 | **28** |
| Spiritual | 2 | 5 | 5 | **12** |
| **합계** | **56** | **89** | **32** | **177** |

### STEEPS 커버리지 점수 (5점 만점)
| 카테고리 | 점수 | 상태 |
|----------|------|------|
| Social | 4.0 | 양호 |
| Technological | 5.0 | 최고 |
| Economic | 5.0 | 최고 |
| Environmental | 5.0 | 최고 |
| Political | 5.0 | 최고 |
| Spiritual | 3.5 | 보완 필요 |

---

## 제외 소스 목록 (Excluded Sources)

### 신뢰도 낮음 (Unreliable)
- heypop.kr - 한국 트렌드 블로그
- stupiddope.com - 비공식 사이트
- newneek.co - 큐레이션 서비스
- namu.wiki - 위키 형식 비공식

### 중복 콘텐츠 (Duplicate)
- 라이브 피드 어그리게이터 (tomsguide.com/news/live/*)
- 단순 보도자료 집계 사이트
- 다른 소스 콘텐츠 재게시 사이트

### 접근 제한 (Access Restricted)
- 유료 구독 전용 (분석 예산 내 미포함)
- 지역 제한 콘텐츠

---

## 개선 로드맵

### 단기 (1개월)
1. **Spiritual 카테고리 보강**: Journal of Religion, Ethics & Society 등 학술지 추가
2. **글로벌 사우스 시각 확대**: 아프리카(Africa News), 라틴아메리카(MercoPress) 매체 추가

### 중기 (3개월)
1. **특허 데이터베이스 통합**: USPTO, WIPO, KIPRIS 정기 모니터링
2. **RSS/API 자동화**: 가능한 소스부터 자동 수집 파이프라인 구축

### 장기 (6개월)
1. **다국어 확장**: 일본어(日経), 중국어(财新), 아랍어(알자지라) 원문 소스 추가
2. **실시간 모니터링**: 고우선순위 소스 24시간 모니터링 체계 구축

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| 1.0 | 2026-01-11 | 초기 버전 (85개 소스) |
| 2.0 | 2026-01-12 | 전수조사 기반 확장 (177개 소스) |

---

**작성**: 환경스캐닝 시스템
**다음 검토**: 2026-02-12
