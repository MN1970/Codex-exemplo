#!/usr/bin/env python3
"""
A/B Test Manager — control vs experimental routing keyword sets.

Operates on maestro_routing_ab_tests (see
supabase/migrations/2026_07_26_add_feedback_tables.sql). Lets the Data Team
create a test, assign a request to a variant deterministically by session,
and report results.

Usage:
    # Create a test: 90% control (current keywords), 10% variant B (candidate keywords)
    python scripts/ab_test_manager.py create \
        --slug saneamento-keyword-v2 \
        --name "Saneamento keyword expansion v2" \
        --variant-a-file keywords/saneamento_v1.json \
        --variant-b-file keywords/saneamento_v2.json \
        --treatment-rate 0.10

    python scripts/ab_test_manager.py assign --slug saneamento-keyword-v2 --session-id abc123
    python scripts/ab_test_manager.py report --slug saneamento-keyword-v2
    python scripts/ab_test_manager.py conclude --slug saneamento-keyword-v2 --promote b
"""

import os
import sys
import json
import hashlib
import argparse

try:
    from supabase import create_client, Client
except ImportError:
    print("Missing dependency. Install with: pip install supabase")
    sys.exit(1)


def get_client() -> Client:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_ANON_KEY")
    if not url or not key:
        print("SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY not set")
        sys.exit(1)
    return create_client(url, key)


def cmd_create(supabase: Client, args):
    with open(args.variant_a_file) as f:
        variant_a = f.read()
    with open(args.variant_b_file) as f:
        variant_b = f.read()

    supabase.table("maestro_routing_ab_tests").insert({
        "test_name": args.name,
        "test_slug": args.slug,
        "description": args.description or "",
        "variant_a_prompt": variant_a,
        "variant_b_prompt": variant_b,
        "control_rate": 1 - args.treatment_rate,
        "treatment_rate": args.treatment_rate,
        "status": "draft",
    }).execute()
    print(f"Created test '{args.slug}' (status=draft). Activate with:")
    print(f"  python scripts/ab_test_manager.py start --slug {args.slug}")


def cmd_start(supabase: Client, args):
    supabase.table("maestro_routing_ab_tests").update({
        "status": "active",
        "started_at": "now()",
    }).eq("test_slug", args.slug).execute()
    print(f"Test '{args.slug}' is now active.")


def cmd_assign(supabase: Client, args):
    """Deterministic bucketing: same session_id always gets the same variant."""
    test = (
        supabase.table("maestro_routing_ab_tests")
        .select("*")
        .eq("test_slug", args.slug)
        .single()
        .execute()
        .data
    )
    if not test or test["status"] != "active":
        print(f"Test '{args.slug}' not active.")
        sys.exit(1)

    digest = hashlib.sha256(f"{args.slug}:{args.session_id}".encode()).hexdigest()
    bucket = (int(digest[:8], 16) % 10_000) / 10_000.0
    variant = "b" if bucket < test["treatment_rate"] else "a"

    print(json.dumps({"session_id": args.session_id, "variant": variant,
                       "keywords": test[f"variant_{variant}_prompt"]}))


def cmd_report(supabase: Client, args):
    test = (
        supabase.table("maestro_routing_ab_tests")
        .select("*")
        .eq("test_slug", args.slug)
        .single()
        .execute()
        .data
    )
    if not test:
        print(f"Test '{args.slug}' not found.")
        sys.exit(1)

    a_n, a_rate = test["variant_a_samples"], test["variant_a_approval_rate"]
    b_n, b_rate = test["variant_b_samples"], test["variant_b_approval_rate"]

    print(f"\nA/B Test: {test['test_name']} ({test['test_slug']})")
    print(f"Status: {test['status']}   Started: {test.get('started_at')}\n")
    print(f"{'variant':10} {'samples':>8} {'approval_rate':>14}")
    print(f"{'A (control)':10} {a_n:>8} {a_rate*100:>13.1f}%")
    print(f"{'B (treatment)':10} {b_n:>8} {b_rate*100:>13.1f}%")

    min_sample = 100
    if a_n < min_sample or b_n < min_sample:
        print(f"\nInsufficient sample size (need >= {min_sample} per variant) — keep collecting data.")
        return

    lift = b_rate - a_rate
    print(f"\nLift (B - A): {lift*100:+.1f} pp")
    if lift > 0.03:
        print("Recommendation: PROMOTE variant B — meaningful positive lift.")
    elif lift < -0.03:
        print("Recommendation: KEEP variant A — B underperforms.")
    else:
        print("Recommendation: INCONCLUSIVE — extend test or increase treatment_rate.")


def cmd_conclude(supabase: Client, args):
    supabase.table("maestro_routing_ab_tests").update({
        "status": "completed",
        "ended_at": "now()",
    }).eq("test_slug", args.slug).execute()
    print(f"Test '{args.slug}' marked completed.")
    if args.promote:
        print(f"Manual step: promote variant '{args.promote}' keywords into "
              f"maestro_routing_keywords (source='feedback_learning') and open a PR "
              f"updating CLAUDE.md routing rules if applicable.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_create = sub.add_parser("create")
    p_create.add_argument("--slug", required=True)
    p_create.add_argument("--name", required=True)
    p_create.add_argument("--description", default="")
    p_create.add_argument("--variant-a-file", required=True)
    p_create.add_argument("--variant-b-file", required=True)
    p_create.add_argument("--treatment-rate", type=float, default=0.10)

    p_start = sub.add_parser("start")
    p_start.add_argument("--slug", required=True)

    p_assign = sub.add_parser("assign")
    p_assign.add_argument("--slug", required=True)
    p_assign.add_argument("--session-id", required=True)

    p_report = sub.add_parser("report")
    p_report.add_argument("--slug", required=True)

    p_conclude = sub.add_parser("conclude")
    p_conclude.add_argument("--slug", required=True)
    p_conclude.add_argument("--promote", choices=["a", "b"], default=None)

    args = parser.parse_args()
    supabase = get_client()

    {
        "create": cmd_create,
        "start": cmd_start,
        "assign": cmd_assign,
        "report": cmd_report,
        "conclude": cmd_conclude,
    }[args.command](supabase, args)


if __name__ == "__main__":
    main()
