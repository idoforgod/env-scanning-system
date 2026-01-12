#!/usr/bin/env python3

import sys

sys.path.insert(0, "/Users/cys/Desktop/ENVscanning-system-main")

from priority_ranking_final import PriorityRanker

if __name__ == "__main__":
    ranker = PriorityRanker()
    ranker.run()
