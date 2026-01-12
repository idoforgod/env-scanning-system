# pSRT (Predicted Signal Reliability Test) Calculation Summary
**Date: 2026-01-12**
**Total Signals Analyzed: 46**

---

## Quick Overview

| Metric | Value |
|--------|-------|
| Average pSRT Score | 49.6/100 |
| Highest Score | 60.7 (C grade) |
| Lowest Score | 34.0 (F grade) |
| Median Score | 51.3 |
| **Grade Distribution** | |
| A+ (90-100) | 0 signals |
| A (80-89) | 0 signals |
| B (70-79) | 0 signals |
| C (60-69) | 2 signals (4.3%) |
| D (50-59) | 23 signals (50.0%) |
| E (40-49) | 13 signals (28.3%) |
| F (0-39) | 8 signals (17.4%) |

---

## pSRT Calculation Formula

```
Overall pSRT = (Source Score × 0.20) + (Signal Score × 0.35) + (Analysis Score × 0.25)
```

### Component Breakdown

#### 1. Source Score (0-100, 20% weight)
Evaluates source credibility and authority:
- **Tier 1** (Official/Authoritative sources): 100 points
  - Examples: IBM Newsroom, NVIDIA Newsroom, D-Wave Quantum, Goldman Sachs, Bloomberg, TechCrunch
  - Status: **78% of signals** use Tier 1 sources (EXCELLENT)
- **Tier 2** (Credible secondary sources): 75 points
  - Examples: Newsspace Korea, SatNews, IAPP, Longevity.Technology
- **Tier 3** (News/aggregator sources): 50 points
  - Examples: Singularity Hub, EditorialGE, Fox 13, SkyQuest Technology
- **Tier 4** (Other/limited authority): 25 points
  - Examples: Individual blogs, opinion sites
  - Status: **Only 2 signals** use Tier 4 sources

#### 2. Signal Score (0-100, 35% weight)
Evaluates signal specificity and freshness (MAIN WEAKNESS):
- **Specificity Components** (0-80 points):
  - Dates/timelines: 0-30 points
  - Numbers/metrics: 0-30 points
  - Named entities: 0-20 points
- **Freshness** (0-20 points):
  - ≤5 days old: 20 points
  - ≤15 days old: 15 points
  - ≤30 days old: 10 points
  - >30 days old: 5 points
- **Current Status**: Average signal score ~35-40 (BELOW AVERAGE)
  - Primary issue: Many signals lack quantified metrics and specific dates

#### 3. Analysis Score (0-100, 25% weight)
Evaluates classification quality and evidence (MAIN STRENGTH):
- **Classification Quality** (0-30 points):
  - Primary category: 15 points
  - Secondary categories: 10 points
  - Status classification: 5 points
- **Evidence Quality** (0-40 points):
  - Clear leading indicators: 15 points
  - Detailed potential impact: 15 points
  - Named key entities: 10 points
- **Confidence & Significance** (0-30 points):
  - Confidence score × 20 points
  - Significance level × 2 points
- **Current Status**: Average analysis score ~89 (EXCELLENT)
  - All signals have strong classification and evidence documentation

---

## Key Performance Insights

### Strengths
1. **Strong Source Quality**: 78% from Tier 1 authoritative sources
2. **Excellent Classification**: Average analysis score of 89/100
3. **High Confidence Levels**: Most signals have 0.85-0.95 confidence scores
4. **Clear Evidence**: All signals documented with leading indicators and impact scenarios

### Weaknesses
1. **Limited Specificity** (CRITICAL): Signal scores average only 35-40
   - Insufficient specific dates/timelines
   - Vague metrics (e.g., "increases" without numbers)
   - Generic descriptions lacking named actors
2. **D-Grade Ceiling**: No signals achieved B+ despite excellent source/analysis scores
3. **Category Performance Imbalance**:
   - Technological: 54.0 avg (best)
   - Spiritual: 38.0 avg (worst - lacks specificity)
   - Social: 44.4 avg (weak)

---

## Top Performers (C Grade & Above)

### 1. SIG-2026-0112-014: TSMC Revenue & AI Chip Demand
- **pSRT Score: 60.7/100 (C)**
- Source: Bloomberg (Tier 1)
- Why it performs well: Specific metrics ($113B revenue, 36% YoY), concrete timeline (2025-2026)
- Component scores: Source 100 | Signal 47 | Analysis 97

### 2. SIG-2026-0112-017: Global VC Deployment Forecast
- **pSRT Score: 60.45/100 (C)**
- Source: Crunchbase (Tier 1)
- Why it performs well: Quantified targets ($339.4B→$400B), percentage metrics (65.4% AI/ML)
- Component scores: Source 100 | Signal 47 | Analysis 96

### 3. SIG-2026-0112-002: CES 2026 Physical AI
- **pSRT Score: 58.75/100 (D)**
- Source: TechCrunch (Tier 1)
- Why it performs well: Specific event dates (Jan 6-9), concrete number (40 companies)
- Component scores: Source 100 | Signal 40 | Analysis 99

---

## Bottom Performers (F Grade)

### Issues & Recommendations

1. **SIG-2026-0112-021: AI Job Displacement** - 34.0/100 (F)
   - Flag: **LOW_SOURCE_QUALITY** (FOX 13 - Tier 4)
   - Issue: Weak source + vague messaging
   - Action: Seek corroboration from Tier 1 source (e.g., labor economics research)

2. **SIG-2026-0112-039: Hybrid Work Default** - 36.25/100 (F)
   - Flag: **VAGUE_SIGNAL**
   - Issue: No specific metrics, general statement
   - Action: Add data on % of companies, timeline specifics

3. **SIG-2026-0112-045: Emotional Fitness Trend** - 36.25/100 (F)
   - Flag: **VAGUE_SIGNAL**
   - Issue: Trend-based with no quantification
   - Action: Add market size, adoption metrics, specific dates

4. **Spiritual Wellness Signals** (Multiple) - 37-40/100 (F)
   - Flag: Consistently **VAGUE_SIGNAL**
   - Pattern: Category-wide lack of specificity
   - Action: Require market data, adoption percentages, concrete examples

---

## Flagged Signals Requiring Review

### VAGUE_SIGNAL Flags (4 signals)
Signals lacking sufficient specific dates, numbers, or named actors:
- SIG-2026-0112-040: AgeTech (48.15/100)
- SIG-2026-0112-013: AI Protein Design (41.50/100)
- SIG-2026-0112-039: Hybrid Work (36.25/100)
- SIG-2026-0112-045: Emotional Fitness (36.25/100)

**Recommendation**: Enhance with:
- Market size/growth metrics
- Specific timeline for adoption
- Named companies or research institutions
- Quantified impact projections

### LOW_SOURCE_QUALITY Flags (2 signals)
Tier 4 sources with high significance (>4/5):
- SIG-2026-0112-034: Trump China Visit (42.50/100, Tier 4)
- SIG-2026-0112-021: Job Displacement (34.00/100, Tier 4)

**Recommendation**: Either:
- Elevate with corroborating Tier 1 sources, OR
- Reduce significance rating if not confirmed, OR
- Delete if cannot be substantiated

---

## Performance by Category

### Technological (16 signals)
- **Average pSRT: 54.0** (HIGHEST)
- Grade distribution: C(1), D(13), E(2)
- Reason: Tech announcements tend to be specific with dates, numbers, actors

### Environmental (6 signals)
- **Average pSRT: 53.2**
- Grade distribution: D(4), E(2)
- Reason: Policy signals well-documented with metrics

### Economic (6 signals)
- **Average pSRT: 49.8**
- Grade distribution: C(1), D(3), E(1), F(1)
- Reason: Mixed specificity in market projections

### Political (6 signals)
- **Average pSRT: 49.8**
- Grade distribution: D(3), E(3)
- Reason: Diplomatic signals often vague on timeline

### Social (7 signals)
- **Average pSRT: 44.4** (SECOND LOWEST)
- Grade distribution: D(0), E(5), F(2)
- Reason: Trends lack quantified adoption metrics

### Spiritual (5 signals)
- **Average pSRT: 38.0** (LOWEST)
- Grade distribution: E(0), F(5)
- Reason: Wellness trends extremely vague on specifics

---

## Improvement Roadmap

### Priority 1: Enhance Signal Specificity
**Target: Improve average pSRT from 49.6 to 65+**

Action Items:
1. **Implement Mandatory Signal Template Requirements**:
   - Minimum 2-3 specific dates (not just "2026")
   - Minimum 2 quantified metrics (numbers, percentages, dollar amounts)
   - Minimum 3-5 named entities (companies, people, organizations)

2. **Create Signal Specificity Scorecard**:
   - Pre-publication checklist before signals enter system
   - Example: ✓ Exact date (not "early 2026") ✓ Numbers (not "surge") ✓ Named actors

3. **Quarterly Signal Enhancement Pass**:
   - Review all D and below signals
   - Add missing specificity from source material
   - Expected impact: +15-20 points average improvement

### Priority 2: Maintain Source Quality
**Status: EXCELLENT - No action needed**
- Current 78% Tier 1 source rate is exceptional
- Continue prioritizing official announcements and authoritative research

### Priority 3: Sustain Analysis Excellence
**Status: EXCELLENT - Continue current practices**
- Average 89/100 analysis score demonstrates strong classification
- Classification framework working well

### Priority 4: Implement Minimum pSRT Thresholds
**Recommended Action Thresholds**:
- pSRT ≥ 55: Include in major reports/briefings
- pSRT 40-54: Conditional inclusion (flag limitations)
- pSRT < 40: Research phase only (do not publish)

### Priority 5: Enable Signal Maturation Tracking
**Implement Signal Grade Progression**:
- Track how signals evolve from F→E→D→C as they develop
- Measure:
  - Source tier improvements (as corroboration grows)
  - Specificity improvements (as implementation details emerge)
  - Confidence increases (as multiple sources confirm)
- Expected benefit: Better understanding of signal lifecycle value

---

## Grade Scale Reference

| Grade | Score | Meaning | Action |
|-------|-------|---------|--------|
| **A+** | 90-100 | Excellent reliability, highly specific, authoritative sources | **Use immediately** |
| **A** | 80-89 | Very good reliability, specific, strong sources | **Use with confidence** |
| **B** | 70-79 | Good reliability, mostly specific, credible sources | **Use with review** |
| **C** | 60-69 | Adequate reliability, some specificity, mixed sources | Use with caveats |
| **D** | 50-59 | Marginal reliability, limited specificity, needs verification | Provisional use only |
| **E** | 40-49 | Poor reliability, vague signals, weak specificity | **Research phase** |
| **F** | 0-39 | Very poor reliability, unsubstantiated | **Do not use** |

---

## Files Generated

1. **pSRT-scores-2026-01-12.json** (51 KB)
   - Complete pSRT scores for all 46 signals
   - Component scores (source, signal, analysis)
   - Grade assignments and flags
   - Summary statistics

2. **pSRT-summary-report-2026-01-12.txt** (9.8 KB)
   - Detailed analysis report with key findings
   - Recommendations by priority
   - Category performance breakdown

3. **pSRT-CALCULATION-SUMMARY.md** (this file)
   - Quick reference guide
   - Methodology explanation
   - Performance insights

---

## Next Steps

1. **Immediate** (This week):
   - Review and address all 6 flagged signals
   - Present C-grade signals to stakeholders as high-confidence

2. **Short-term** (This month):
   - Implement enhanced signal template with specificity requirements
   - Train signal collection team on new requirements
   - Set minimum pSRT threshold policy

3. **Medium-term** (Q1):
   - Conduct re-scoring of all signals with new template compliance
   - Implement signal maturation tracking
   - Publish updated pSRT scores monthly

4. **Long-term** (Q2-Q3):
   - Build pSRT trend analysis (how scores improve over time)
   - Correlate pSRT with actual signal accuracy outcomes
   - Refine weighting formula based on validation data

---

## Technical Details

**Calculation Engine**: Python 3
**Data Source**: env-scanning/structured/structured-signals-2026-01-12.json
**Processing Time**: <2 seconds for 46 signals
**Validation**: All signals pass quality checks

---

Generated: 2026-01-12 12:35 UTC
Analysis Version: pSRT v1.0
