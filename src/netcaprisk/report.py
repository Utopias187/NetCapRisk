import json
from pathlib import Path
from typing import Any, Dict, List

from .models import (
    bottleneck_info,
    effective_link_rates,
    end_to_end_throughput,
    per_flow_throughput_shared_backbone,
)


def headroom_ratio(capacity_mbps: float, used_mbps: float) -> float:
    # how much room is left on the link
    if capacity_mbps <= 0:
        return 0.0
    return max(0.0, (capacity_mbps - used_mbps) / capacity_mbps)


def dos_sweep(
    Rs_mbps: float,
    Rc_mbps: float,
    R_backbone_mbps: float,
    N_values: List[int],
    warn_threshold: float = 0.10,
) -> Dict[str, Any]:
    results = []

    for n in N_values:
        per_flow = per_flow_throughput_shared_backbone(Rs_mbps, Rc_mbps, R_backbone_mbps, n)
        total_used = per_flow * n
        headroom = headroom_ratio(R_backbone_mbps, total_used)

        if headroom <= 0.05:
            severity = "CRITICAL"
        elif headroom <= warn_threshold:
            severity = "WARN"
        else:
            severity = "OK"

        risk = []
        if headroom <= warn_threshold:
            risk.append("low_headroom")
        if per_flow <= 0.05 * R_backbone_mbps:
            risk.append("dos_prone")

        results.append(
            {
                "N_flows": n,
                "per_flow_throughput_mbps": per_flow,
                "total_throughput_mbps": total_used,
                "backbone_headroom_ratio": headroom,
                "severity": severity,
                "risk": risk,
            }
        )

    return {
        "scenario": "dos_sweep",
        "Rs_mbps": Rs_mbps,
        "Rc_mbps": Rc_mbps,
        "R_backbone_mbps": R_backbone_mbps,
        "warn_threshold": warn_threshold,
        "results": results,
    }


def load_config(path: str) -> Dict[str, Any]:
    # read the JSON config from disk
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Config not found: {path}")

    with p.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise ValueError("Config root must be a JSON object.")
    return data


def assess_config(config: Dict[str, Any]) -> Dict[str, Any]:
    # run whatever sections exist and return one combined report
    report: Dict[str, Any] = {"meta": config.get("meta", {}), "results": {}}

    sp = config.get("single_path")
    if isinstance(sp, dict):
        rs = float(sp["rs_mbps"])
        links = [float(x) for x in sp["links_mbps"]]
        names = sp.get("link_names")

        if names is not None and len(names) != len(links):
            raise ValueError("single_path.link_names must match links_mbps length")

        t = end_to_end_throughput(rs, links)
        b_rate, b_label = bottleneck_info(rs, links, names)

        report["results"]["single_path"] = {
            "rs_mbps": rs,
            "links_mbps": links,
            "throughput_mbps": t,
            "bottleneck": b_label,
            "bottleneck_rate_mbps": b_rate,
        }

    fs = config.get("fair_share")
    if isinstance(fs, dict):
        rs = float(fs["rs_mbps"])
        rc = float(fs["rc_mbps"])
        backbone = float(fs["backbone_mbps"])
        n_values = [int(n) for n in fs["n_values"]]
        warn_threshold = float(fs.get("warn_threshold", 0.10))

        report["results"]["fair_share"] = dos_sweep(
            Rs_mbps=rs,
            Rc_mbps=rc,
            R_backbone_mbps=backbone,
            N_values=n_values,
            warn_threshold=warn_threshold,
        )

    eff = config.get("effective_links")
    if isinstance(eff, dict):
        links = [float(x) for x in eff["links_mbps"]]
        efficiencies = [float(x) for x in eff["efficiencies"]]
        eff_links = effective_link_rates(links, efficiencies)
        t = min(eff_links) if eff_links else 0.0

        report["results"]["effective_links"] = {
            "base_links_mbps": links,
            "efficiencies": efficiencies,
            "effective_links_mbps": eff_links,
            "throughput_mbps": t,
            "bottleneck_rate_mbps": t,
        }

    return report
