# pSRT Analysis Files (2026-01-12)

## Overview
pSRT (Predicted Signal Reliability Test) is a quantitative framework for scoring and grading environmental signals based on source quality, signal specificity, and analysis rigor.

## Files Generated

### 1. **pSRT-scores-2026-01-12.json** (Primary Output)
**Size**: 51 KB | **Records**: 46 signals

Complete structured data with:
- Individual signal pSRT scores (0-100)
- Component breakdowns (source, signal, analysis scores)
- Letter grade assignments (A+ through F)
- Quality flags (VAGUE_SIGNAL, LOW_SOURCE_QUALITY)
- Summary statistics
- Grade distribution analysis

**Use case**: Data integration, downstream analysis, signal dashboards

**Key fields**:
```json
{
  "signal_id": "SIG-2026-0112-001",
  "overall_pSRT": 53.25,
  "grade": "D",
  "component_scores": {
    "source_score": 100,
    "signal_score": 25,
    "analysis_score": 98
  },
  "flags": []
}
```

---

### 2. **pSRT-summary-report-2026-01-12.txt** (Executive Report)
**Size**: 9.8 KB | **Format**: Plain text

Comprehensive analysis including:
- Executive summary with key findings
- Grade distribution visualization
- Component analysis breakdown
- Top performers (C grade+)
- Flagged signals requiring review
- Improvement recommendations
- Category-by-category performance
- Methodology reference

**Use case**: Executive briefings, management reviews, quality assurance

**Key sections**:
- Overall reliability assessment
- Critical insights (specificity weakness)
- Signals with flags (6 total)
- Improvement roadmap by priority

---

### 3. **pSRT-CALCULATION-SUMMARY.md** (Quick Reference)
**Size**: 8.5 KB | **Format**: Markdown

Quick reference guide including:
- Overview table with statistics
- Complete formula explanation
- Component scoring methodology
- Performance insights by category
- Top/bottom performers
- Grade scale reference
- Technical details

**Use case**: Training, methodology reference, stakeholder education

---

## Key Findings at a Glance

| Metric | Value |
|--------|-------|
| Average pSRT Score | **49.6/100** |
| Highest Score | 60.7 (C grade) |
| Lowest Score | 34.0 (F grade) |
| Grade C or Above | 2 signals (4.3%) |
| Grade D | 23 signals (50.0%) |
| Grade E or Below | 21 signals (45.7%) |

### Main Insights

**Strengths** (Score Components):
- Source Quality: EXCELLENT (78% Tier 1 authoritative sources)
- Analysis Quality: EXCELLENT (89/100 average)
- Classification: Strong across all signals

**Weaknesses** (Score Components):
- Signal Specificity: WEAK (35-40/100 average) ← PRIMARY ISSUE
- Specific dates: Often vague ("2026" vs "Q2 2026")
- Quantified metrics: Many lack numbers ("surge" vs "+45%")
- Named actors: Generic descriptions lacking specifics

### Performance by Category

| Category | Signals | Avg Score | Status |
|----------|---------|-----------|--------|
| Technological | 16 | 54.0 | Best |
| Environmental | 6 | 53.2 | Good |
| Economic | 6 | 49.8 | Average |
| Political | 6 | 49.8 | Average |
| Social | 7 | 44.4 | Weak |
| Spiritual | 5 | 38.0 | Weakest |

---

## Quality Flags Summary

### VAGUE_SIGNAL (4 signals)
Signals lacking specific dates, numbers, or named actors:
1. SIG-2026-0112-040: AgeTech (48.15) - No market size data
2. SIG-2026-0112-013: AI Protein Design (41.50) - Lacks specifics
3. SIG-2026-0112-039: Hybrid Work (36.25) - No adoption metrics
4. SIG-2026-0112-045: Emotional Fitness (36.25) - Trend without data

**Action**: Enhance with quantified metrics, specific timelines, named entities

### LOW_SOURCE_QUALITY (2 signals)
Tier 4 sources with high significance (≥4/5):
1. SIG-2026-0112-034: Trump China Visit (42.50) - Editorial GE (Tier 4)
2. SIG-2026-0112-021: Job Displacement (34.00) - FOX 13 (Tier 4)

**Action**: Seek Tier 1/2 source corroboration or reduce significance rating

---

## pSRT Grade Scale

| Grade | Score | Interpretation | Use Case |
|-------|-------|-----------------|----------|
| A+ | 90-100 | Excellent reliability | Priority action |
| A | 80-89 | Very good reliability | Immediate briefing |
| B | 70-79 | Good reliability | Standard reporting |
| C | 60-69 | Adequate reliability | Include with caveats |
| D | 50-59 | Marginal reliability | Provisional use |
| E | 40-49 | Poor reliability | Research phase |
| F | 0-39 | Very poor reliability | Do not use |

**Current distribution**:
- A+/A/B: 0 signals (0%)
- C: 2 signals (4.3%) ← Highest performing
- D: 23 signals (50.0%) ← Majority of signals
- E/F: 21 signals (45.7%) ← Below threshold

---

## pSRT Calculation Formula

```
Overall pSRT = (Source Score × 0.20) + (Signal Score × 0.35) + (Analysis Score × 0.25)

Where:
- Source Score (20%): Tier rating of source credibility
- Signal Score (35%): Specificity (dates, numbers, actors) + freshness
- Analysis Score (25%): Classification quality + evidence strength
```

### Component Details

**Source Score (20% weight)**:
- Tier 1 (Official): 100 points (78% of signals)
- Tier 2 (Credible): 75 points
- Tier 3 (News): 50 points
- Tier 4 (Other): 25 points (only 2 signals)

**Signal Score (35% weight)** - MAIN WEAKNESS:
- Specific dates: 0-30 points
- Quantified metrics: 0-30 points
- Named entities: 0-20 points
- Freshness: 0-20 points
- **Average: 35-40/100**

**Analysis Score (25% weight)** - MAIN STRENGTH:
- Classification quality: 0-30 points
- Evidence quality: 0-40 points
- Confidence/significance: 0-30 points
- **Average: 89/100**

---

## Top Performers (C Grade & Above)

### #1: TSMC Revenue & AI Chip Demand
- **Score**: 60.7 (C) | **Source**: Bloomberg (Tier 1)
- Why: Specific metrics ($113B revenue, 36% YoY), concrete timeline
- **Use**: High confidence signal for AI infrastructure trends

### #2: Global VC Deployment Forecast
- **Score**: 60.45 (C) | **Source**: Crunchbase (Tier 1)
- Why: Quantified targets ($339.4B→$400B), clear metrics (65.4% AI/ML)
- **Use**: Reliable indicator of investment concentration

---

## Improvement Recommendations

### Priority 1: Enhance Signal Specificity (CRITICAL)
- Add minimum 2-3 specific dates per signal (not just "2026")
- Mandate 2+ quantified metrics (dollars, percentages, volumes)
- Include 3-5 named entities (companies, people, organizations)
- **Expected impact**: +15-20 points average improvement

### Priority 2: Maintain Source Quality (EXCELLENT)
- Continue 78% Tier 1 source target
- Flag Tier 4 sources requiring verification
- Seek corroboration for conflicting signals

### Priority 3: Sustain Analysis Excellence (EXCELLENT)
- Continue current classification practices
- Maintain leading indicator and impact documentation

### Priority 4: Set Minimum Thresholds
- **pSRT ≥ 55**: Include in major reports
- **pSRT 40-54**: Conditional inclusion with flags
- **pSRT < 40**: Research phase only

---

## How to Use These Files

### For Quick Review
→ Start with **pSRT-CALCULATION-SUMMARY.md** for methodology and top performers

### For Executive Briefing
→ Use **pSRT-summary-report-2026-01-12.txt** for findings and recommendations

### For Data Integration
→ Import **pSRT-scores-2026-01-12.json** into dashboards and systems

### For Detailed Analysis
→ Cross-reference all three files for comprehensive view

---

## Next Steps

1. **Immediate**: Review 6 flagged signals and plan corrective actions
2. **This week**: Present C-grade signals to stakeholders
3. **This month**: Implement enhanced signal template requirements
4. **Q1**: Re-score all signals with improved specificity
5. **Q2+**: Track signal maturation and score progression

---

## Technical Information

- **Calculation Date**: 2026-01-12
- **Signals Analyzed**: 46 total
- **Processing Time**: <2 seconds
- **Calculation Engine**: Python 3
- **Framework Version**: pSRT v1.0

---

**Document Generated**: 2026-01-12
**Analyst**: Claude Code Analysis System
**Review Status**: Complete
