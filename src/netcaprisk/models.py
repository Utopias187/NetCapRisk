from typing import List, Optional, Tuple


def end_to_end_throughput(Rs_mbps: float, link_rates_mbps: List[float]) -> float:
    if Rs_mbps < 0:
        raise ValueError("Rs_mbps must be non-negative.")
    if any(r < 0 for r in link_rates_mbps):
        raise ValueError("All link rates must be non-negative.")

    if not link_rates_mbps:
        return Rs_mbps

    return min([Rs_mbps] + link_rates_mbps)


def bottleneck_info(
    Rs_mbps: float,
    link_rates_mbps: List[float],
    link_names: Optional[List[str]] = None
) -> Tuple[float, str]:
    if link_names is not None and len(link_names) != len(link_rates_mbps):
        raise ValueError("link_names must be the same length as link_rates_mbps.")

    candidates: List[Tuple[float, str]] = [(Rs_mbps, "sender")]

    for i, r in enumerate(link_rates_mbps):
        name = link_names[i] if link_names is not None else str(i)
        candidates.append((r, f"link {name}"))

    return min(candidates, key=lambda x: x[0])


def per_flow_throughput_shared_backbone(
    Rs_mbps: float,
    Rc_mbps: float,
    R_backbone_mbps: float,
    N_flows: int
) -> float:
    if N_flows <= 0:
        raise ValueError("N_flows must be >= 1.")
    if min(Rs_mbps, Rc_mbps, R_backbone_mbps) < 0:
        raise ValueError("Rates must be non-negative.")

    fair_share = R_backbone_mbps / N_flows
    return min(Rs_mbps, Rc_mbps, fair_share)


def effective_link_rates(link_rates_mbps: List[float], efficiencies: List[float]) -> List[float]:
    if len(link_rates_mbps) != len(efficiencies):
        raise ValueError("link_rates_mbps and efficiencies must have the same length.")
    if any(r < 0 for r in link_rates_mbps):
        raise ValueError("All link rates must be non-negative.")
    if any(e < 0.0 or e > 1.0 for e in efficiencies):
        raise ValueError("All efficiencies must be in the range [0, 1].")

    return [r * e for r, e in zip(link_rates_mbps, efficiencies)]
