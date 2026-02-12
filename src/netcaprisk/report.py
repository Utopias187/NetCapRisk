from typing import Dict, List

from .models import per_flow_throughput_shared_backbone


def headroom_ratio(capacity_mbps: float, used_mbps: float) -> float:
    # how much breathing room is left (0.2 = 20% free)
    if capacity_mbps <= 0:
        return 0.0
    return max(0.0, (capacity_mbps - used_mbps) / capacity_mbps)


def dos_sweep(
    Rs_mbps: float,
    Rc_mbps: float,
    R_backbone_mbps: float,
    N_values: List[int],
    warn_threshold: float = 0.10,
) -> Dict:
    results = []

    for n in N_values:
        per_flow = per_flow_throughput_shared_backbone(Rs_mbps, Rc_mbps, R_backbone_mbps, n)
        total_used = per_flow * n
        headroom = headroom_ratio(R_backbone_mbps, total_used)

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

