# Deduplication Filter Summary
**Date: 2026-01-13**

## Processing Results

### Input Files
- **Raw Scanned Signals**: `/data/2026/01/13/raw/scanned-signals.json`
- **Existing Database**: `/signals/database.json` (115 signals)
- **Dedup Index**: `/env-scanning/context/dedup-index-2026-01-13.json`

### Statistics
```
Total Scanned:           69 signals
Duplicates Removed:      1 signal
New Signals Filtered:    68 signals
Updates Identified:      0 signals
```

### Duplicate Detection Methods
- **Exact URL Matches**: 0 found
- **Similar Title (>=90%)**: 1 found
- **Similar Content (>=85%)**: 0 found
- **Entity Overlap Flags**: 0 found

### Removed Duplicate
1. **RAW-2026-0113-005** - "Science's 2025 Breakthrough of the Year: Unstoppable Rise of Renewable Energy"
   - Match Type: similar_title
   - Matched With: SIG-2026-0112-006
   - Similarity Score: 91%
   - Reason: Highly similar title about renewable energy breakthrough topic

### Output Files
- **Filtered Signals**: `/data/2026/01/13/filtered/filtered-signals.json` (68 signals)
- **Dedup Log**: `/data/2026/01/13/logs/duplicates-removed-2026-01-13.log`

## Processing Details

### Deduplication Logic
1. First checks for exact URL matches (most reliable)
2. Then checks title similarity using normalized text (90% threshold)
3. Flags entity overlaps for human review (70% threshold)
4. For flagged items, checks content similarity (85% threshold)

### New Signals Included (Sample)
- Hyperscale AI Data Centers energy crisis signals
- Quantum computing breakthroughs (D-Wave, error correction)
- AI-Quantum convergence indicators
- Climate change and renewable energy trends
- WHO pandemic preparedness agreements
- Geopolitical risk factors (New START expiration)
- Corporate AI spending and VC funding trends
- Gene editing clinical trials
- Space commercialization initiatives

## Quality Assurance
- All raw signals validated against existing database
- Similarity thresholds set conservatively to minimize false positives
- False negatives preferred over false positives (keeping uncertain signals)
- All decisions logged for audit trail

## Next Steps
1. Structured signals classification
2. Priority scoring and ranking
3. Impact analysis
4. Report generation
