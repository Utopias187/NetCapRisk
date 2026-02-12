import argparse
import json
from typing import List, Optional

from .models import (
    end_to_end_throughput,
    bottleneck_info,
    per_flow_throughput_shared_backbone,
    effective_link_rates,
)
from .report import dos_sweep


def _print(data: dict, as_json: bool) -> None:
    # quick switch between human output and JSON
    if as_json:
        print(json.dumps(data, indent=2))
    else:
        for k, v in data.items():
            print(f"{k}: {v}")


def cmd_single(args: argparse.Namespace) -> None:
    t = end_to_end_throughput(args.rs, args.links)
    b_rate, b_label = bottleneck_info(args.rs, args.links, args.names)

    out = {
        "scenario": "single_path",
        "Rs_mbps": args.rs,
        "links_mbps": args.links,
        "throughput_mbps": t,
        "bottleneck": b_label,
        "bottleneck_rate_mbps": b_rate,
    }
    _print(out, args.json)


def cmd_fair(args: argparse.Namespace) -> None:
    rows = []
    for n in args.N:
        t = per_flow_throughput_shared_backbone(args.rs, args.rc, args.backbone, n)
        rows.append({"N_flows": n, "per_flow_throughput_mbps": t})

    out = {
        "scenario": "fair_share",
        "Rs_mbps": args.rs,
        "Rc_mbps": args.rc,
        "R_backbone_mbps": args.backbone,
        "results": rows,
    }

    if args.json:
        _print(out, True)
        return

    print("N_flows | per-flow throughput (Mbps)")
    print("-----------------------------------")
    for r in rows:
        print(f"{r['N_flows']:>6} | {r['per_flow_throughput_mbps']:>24.4f}")


def cmd_effective(args: argparse.Namespace) -> None:
    eff_links = effective_link_rates(args.links, args.eff)
    t = min(eff_links) if eff_links else 0.0  # sender/receiver not provided here

    out = {
        "scenario": "effective_links",
        "base_links_mbps": args.links,
        "efficiencies": args.eff,
        "effective_links_mbps": eff_links,
        "throughput_mbps": t,
    }
    _print(out, args.json)


def cmd_dos(args: argparse.Namespace) -> None:
    report = dos_sweep(
        Rs_mbps=args.rs,
        Rc_mbps=args.rc,
        R_backbone_mbps=args.backbone,
        N_values=args.N,
        warn_threshold=args.warn_threshold,
    )

    if args.json:
        _print(report, True)
        return

    print("N_flows | per-flow (Mbps) | total (Mbps) | headroom | risk")
    print("--------------------------------------------------------")
    for r in report["results"]:
        risk = ",".join(r["risk"]) if r["risk"] else "-"
        print(
            f"{r['N_flows']:>6} | "
            f"{r['per_flow_throughput_mbps']:>13.4f} | "
            f"{r['total_throughput_mbps']:>11.4f} | "
            f"{r['backbone_headroom_ratio']:>7.3f} | "
            f"{risk}"
        )


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="netcaprisk",
        description="Mini network throughput + risk modeling tool",
    )
    p.add_argument("--json", action="store_true", help="print machine-readable JSON")

    sub = p.add_subparsers(dest="command", required=True)

    s1 = sub.add_parser("single", help="single flow, single path")
    s1.add_argument("--rs", type=float, required=True, help="sender rate (Mbps)")
    s1.add_argument("--links", type=float, nargs="+", required=True, help="link capacities (Mbps)")
    s1.add_argument("--names", type=str, nargs="*", default=None, help="optional link names")
    s1.set_defaults(func=cmd_single)

    s2 = sub.add_parser("fair", help="N flows fairly share a backbone")
    s2.add_argument("--rs", type=float, required=True, help="sender rate (Mbps)")
    s2.add_argument("--rc", type=float, required=True, help="receiver rate (Mbps)")
    s2.add_argument("--backbone", type=float, required=True, help="backbone capacity (Mbps)")
    s2.add_argument("--N", type=int, nargs="+", required=True, help="flow counts to evaluate")
    s2.set_defaults(func=cmd_fair)

    s3 = sub.add_parser("effective", help="apply per-link efficiencies")
    s3.add_argument("--links", type=float, nargs="+", required=True, help="base link capacities (Mbps)")
    s3.add_argument("--eff", type=float, nargs="+", required=True, help="efficiencies in [0,1]")
    s3.set_defaults(func=cmd_effective)

    s4 = sub.add_parser("dos", help="simulate load increase (DoS pressure) on shared backbone")
    s4.add_argument("--rs", type=float, required=True, help="sender rate (Mbps)")
    s4.add_argument("--rc", type=float, required=True, help="receiver rate (Mbps)")
    s4.add_argument("--backbone", type=float, required=True, help="backbone capacity (Mbps)")
    s4.add_argument("--N", type=int, nargs="+", required=True, help="flow counts to sweep")
    s4.add_argument("--warn-threshold", type=float, default=0.10, help="headroom ratio warning threshold")
    s4.set_defaults(func=cmd_dos)

    return p


def main(argv: Optional[List[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "single" and args.names is not None and len(args.names) == 0:
        args.names = None

    args.func(args)
