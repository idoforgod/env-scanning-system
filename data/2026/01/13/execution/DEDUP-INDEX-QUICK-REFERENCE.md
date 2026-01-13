# Deduplication Index Quick Reference

**Generated**: 2026-01-12
**Version**: 2.0
**Status**: READY FOR USE

## Quick Stats

| Metric | Value |
|--------|-------|
| **Total Signals** | 115 |
| **Signal IDs Indexed** | 115 |
| **URLs for Exact Match** | 8 |
| **Titles for Fuzzy Match** | 115 |
| **Total Entities** | 139 |
| **Archive Coverage** | 4 days (2026-01-09 to 2026-01-12) |
| **Confidence Level** | VERY_HIGH |

## How to Use This Index

### 1. Exact URL Matching
Check incoming signals against these 8 known URLs:
```
https://nvidianews.nvidia.com/news/nvidia-releases-new-physical-ai-models-as-global-partners-unveil-next-generation-robots
https://newsroom.ibm.com/2025-11-12-ibm-delivers-new-quantum-processors,-software,-and-algorithm-breakthroughs-on-path-to-advantage-and-fault-tolerance
https://www.dwavequantum.com/company/newsroom/press-release/d-wave-to-acquire-quantum-circuits/
https://techcrunch.com/podcast/ces-2026-was-all-about-physical-ai-and-robots-robots-robots/
https://www.scmp.com/tech/big-tech/article/3338427/deepseek-kicks-2026-paper-signalling-push-train-bigger-models-less
https://www.newsspace.kr/news/article.html?no=11811
https://www.sciencedaily.com/releases/2026/01/260101160855.htm
https://www.pymnts.com/news/wearables/2026/smart-ring-shipments-projected-to-jump-49percent/
```

### 2. Title Similarity Matching
Use fuzzy matching (similarity >= 0.85) against 115 indexed titles.
Reference titles include:
- "NVIDIA Vera Rubin Platform Launch - Next-Gen AI Supercomputer"
- "IBM Declares 2026 as Year of Quantum Advantage"
- "Science's 2025 Breakthrough: Unstoppable Rise of Renewable Energy"
- "Boston Dynamics-Google DeepMind Partnership for Gemini-Powered Atlas Robots"
- And 111 more...

### 3. Entity Matching
Check for keyword overlaps in:

**Actors** (27 keywords):
NVIDIA, IBM, Google, Microsoft, OpenAI, DeepSeek, China, Japan, US, EU, etc.

**Technologies** (96 keywords):
AI, Quantum Computing, CRISPR, Robotics, Renewable Energy, EV, Brain-Computer Interface, etc.

**Policies** (16 keywords):
EU AI Act, CBAM, Carbon Border Adjustment, Export Controls, SBTi, Net-Zero Standards, etc.

## Signal ID Range

All indexed signals use this naming convention: `SIG-YYYY-MMDD-###`

**Indexed ranges**:
- SIG-2026-0109-001 to SIG-2026-0109-024 (24 signals)
- SIG-2026-0111-001 to SIG-2026-0111-020 (20 signals)
- SIG-2026-0112-001 to SIG-2026-0112-046 (46 signals)

**New signals should start at**:
- Next date range: 2026-01-13 onward as SIG-2026-0113-001, SIG-2026-0113-002, etc.

## Top Keywords to Watch

**Critical Keywords** (highest dedup relevance):
1. NVIDIA - 7+ signals
2. Physical AI - 6+ signals
3. Quantum Computing - 5+ signals
4. AI - appears in 44+ signals
5. Renewable Energy - 5+ signals
6. Robotics - 5+ signals
7. Gene Editing/CRISPR - 4+ signals
8. Trade War/Tariffs - 4+ signals
9. EU AI Act - 3+ signals
10. Brain-Computer Interface - 2+ signals

## Matching Thresholds

| Method | Threshold | Strictness |
|--------|-----------|-----------|
| Exact URL Match | 100% | VERY STRICT |
| Title Fuzzy Match | 0.85+ | STRICT |
| Entity Overlap | 0.70+ | MODERATE |
| Keyword Match | 1+ keywords | LOOSE |

## Signal Categories

Distribution of indexed signals:
- **Technological**: 44 (38%) - Highest concentration
- **Economic**: 18 (16%)
- **Social**: 18 (16%)
- **Environmental**: 14 (12%)
- **Political**: 14 (12%)
- **Spiritual**: 7 (6%)

## Signal Status

All indexed signals are:
- **Emerging**: 112 (97.4%)
- **Developing**: 3 (2.6%)

This index is designed to catch duplicates in a high-velocity scanning environment where most new signals will be "emerging" status.

## Common False Positives to Avoid

Words/phrases that appear in multiple signals and shouldn't trigger auto-dedup:
- "AI" (appears in 44+ signals - use with title/URL context)
- "2026" (appears in all 2026 signals - use with entity context)
- "Global", "Technology", "Future" (generic terms)

Always combine keyword matches with title or URL checks for reliability.

## Files Location

- **Index File**: `/context/dedup-index-2026-01-12.json`
- **Log File**: `/logs/archive-load-2026-01-12.log`
- **Script**: `/archive_loader.py`

## Refresh Cycle

This index should be updated:
- **Daily**: After each scanning cycle to add new signals
- **Weekly**: To consolidate emerging signals into developing/mature status
- **Monthly**: To validate and clean up archived signals

Last updated: 2026-01-12 12:00:00Z
Next recommended update: 2026-01-13 after daily scan
