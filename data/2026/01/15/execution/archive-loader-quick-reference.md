# Archive Loader Quick Reference

**Execution Date**: 2026-01-15
**Status**: COMPLETED
**Duration**: 18 seconds

## Summary

Loaded existing signal database (527 signals) and recent archive reports to build deduplication context for upcoming scan.

## Key Numbers

| Metric | Value |
|--------|-------|
| Total Signals in DB | 527 |
| Emerging/Developing | 487/40 |
| Social/Tech/Econ/Pol/Env | 336/273/130/118/55 |
| Unique URLs in Index | 122 |
| Unique Actors Tracked | 34 |
| Unique Technologies | 24 |
| Unique Policies | 18 |
| Dedup Confidence | High |

## Output Files

All files saved with `-2026-01-15` timestamp:

### Context Files (Ready for Dedup)
- `context/previous-signals.json` - Complete dedup baseline
- `context/archive-summary-2026-01-15.json` - Database statistics
- `context/dedup-index-2026-01-15.json` - URL/title/entity index

### Logs & Reports
- `logs/archive-load-2026-01-15.log` - Detailed execution log
- `data/2026/01/15/execution/archive-loader-summary.md` - Full summary
- `data/2026/01/15/execution/archive-loader-quick-reference.md` - This file

## What Was Done

1. Loaded signal database (527 records from 12 scans)
2. Found 2 archive reports (99 structured + 7 priority-ranked)
3. Built dedup index with 122 URLs
4. Extracted 76 unique entities (actors/tech/policies)
5. Verified 0 URL duplicates, 15 acceptable title variations
6. Generated all context files for next scan cycle

## How to Use

### For Next Scan
1. Use `context/dedup-index-2026-01-15.json` to prevent duplicate URLs
2. Use `context/previous-signals.json` for title similarity matching
3. Monitor 76 tracked entities for repeated coverage

### For Monitoring
- Check `logs/archive-load-2026-01-15.log` for detailed steps
- Review `context/archive-summary-2026-01-15.json` for statistics
- Track priority signals: AI (high volume), Korean politics, employment data

## Quality Checks

- Duplicate detection: PASSED (0 URL duplicates)
- Title normalization: PASSED (15 variations acceptable)
- Database integrity: PASSED (527 signals verified)
- Entity extraction: PASSED (76 entities captured)

## Next Steps

1. Run `/env-scan:run` for new scan with dedup context loaded
2. New signals will be checked against 122 URLs + 527 titles
3. After scan completes, regenerate context files daily
4. Monitor for repeated signals in priority categories

## Files Location

All paths are absolute from project root:

```
/Users/cys/Desktop/ENVscanning-system-main/

├── context/
│   ├── previous-signals.json (MAIN - all in one)
│   ├── archive-summary-2026-01-15.json
│   └── dedup-index-2026-01-15.json
│
├── logs/
│   └── archive-load-2026-01-15.log
│
└── data/2026/01/15/execution/
    ├── archive-loader-summary.md
    └── archive-loader-quick-reference.md (this file)
```

## Performance

- Processing time: 18 seconds
- Records processed: 527
- Indexing rate: ~29 records/second
- All quality checks: PASSED

---

**Ready for next scan cycle!**
