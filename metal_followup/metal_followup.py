#!/usr/bin/env python3
"""
Daily metal follow-up test bench -- entry point.

    python metal_followup.py --metal copper \\
        --bo SuiviCuivre_2026.xls \\
        --book Suivi_Cuivre_202607.xlsx \\
        --price 11727.13

See README.md for setup and usage. See metalfollowup/ for the actual logic.
"""

import sys

from metalfollowup.cli import main

if __name__ == "__main__":
    sys.exit(main())
