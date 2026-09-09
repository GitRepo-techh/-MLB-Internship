"""
analytics.py
------------
Turns the stats dict produced by TrafficViolationDetector.get_stats()
into saved artifacts (JSON summary, CSV of violation events) and a
readable console summary.
"""

import csv
import json


def save_stats_json(stats, output_path):
    with open(output_path, "w") as f:
        json.dump(stats, f, indent=2)


def save_events_csv(stats, output_path):
    events = stats.get("violation_events", [])
    fieldnames = ["track_id", "vehicle_type", "violation_type", "frame", "timestamp_sec"]
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for e in events:
            writer.writerow(e)


def print_summary(stats, label=""):
    print("=" * 55)
    print(f"TRAFFIC VIOLATION SUMMARY {('- ' + label) if label else ''}")
    print("=" * 55)
    print(f"Total vehicles tracked : {stats['total_vehicles']}")
    print(f"Total violations       : {stats['total_violations']}")
    print(f"  Wrong-way            : {stats['wrong_way_violations']}")
    print(f"  Restricted zone      : {stats['restricted_zone_violations']}")
    print("Vehicle type counts:")
    for vtype, count in stats["vehicle_type_counts"].items():
        print(f"  {vtype}: {count}")
    print("Violation events:")
    for e in stats["violation_events"]:
        print(f"  ID {e['track_id']:>3} | {e['vehicle_type']:<10} | {e['violation_type']:<16} "
              f"| frame {e['frame']:>5} | t={e['timestamp_sec']}s")
    print("=" * 55)
