from src.netcaprisk.report import dos_sweep


def test_dos_sweep_basic():
    rep = dos_sweep(200, 200, 100, [1, 50], warn_threshold=0.10)
    assert rep["scenario"] == "dos_sweep"
    assert rep["results"][0]["N_flows"] == 1
    assert rep["results"][1]["N_flows"] == 50


def test_dos_sweep_flags():
    rep = dos_sweep(200, 200, 100, [100], warn_threshold=0.10)
    r = rep["results"][0]
    assert "low_headroom" in r["risk"]
