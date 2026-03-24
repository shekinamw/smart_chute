#!/usr/bin/env python3
"""
main.py — AWSS Entry Point
============================
Thin CLI wrapper that parses arguments, patches config, and runs
the AWSSSystem pipeline loop.

Usage:
  python3 main.py
  python3 main.py --delay 0.95 --hold 2.0
  python3 main.py --bin-height 30 --full-at 5
  python3 main.py --focus 5.0
"""

import argparse
import config
from system import AWSSSystem


def parse_args():
    parser = argparse.ArgumentParser(description="AWSS — Automated Waste Sorting System")
    parser.add_argument("--delay", type=float, default=0.95,
                        help="Settle delay (s) after IR trigger. Default: 0.95")
    parser.add_argument("--hold", type=float, default=2.0,
                        help="Flap hold time (s) before returning neutral. Default: 2.0")
    parser.add_argument("--bin-height", type=float, default=30.0,
                        help="Bin height in cm (sensor-to-floor). Default: 30.0")
    parser.add_argument("--full-at", type=float, default=5.0,
                        help="Distance (cm) at which bin is full. Default: 5.0")
    parser.add_argument("--focus", type=float, default=5.0,
                        help="Camera manual focus position (higher=closer). Default: 5.0")
    return parser.parse_args()


def main():
    args = parse_args()

    # Patch config module with CLI overrides
    config.SETTLE_DELAY  = args.delay
    config.HOLD_TIME     = args.hold
    config.BIN_HEIGHT    = args.bin_height
    config.FULL_AT_CM    = args.full_at
    config.LENS_POSITION = args.focus

    system = AWSSSystem(
        settle_delay=args.delay,
        hold_time=args.hold,
    )

    try:
        system.start()
        while True:
            system.process_bag()

    except KeyboardInterrupt:
        print("\n\n[AWSS] Shutdown requested by user")

    finally:
        system.shutdown()


if __name__ == "__main__":
    main()
