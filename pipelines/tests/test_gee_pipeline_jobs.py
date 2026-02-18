import json
import subprocess
import sys
from pathlib import Path

import os

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[2]
FETCH_JOB = ROOT / "pipelines" / "jobs" / "fetch_gee_ch4.py"
INGEST_GEE_JOB = ROOT / "pipelines" / "jobs" / "ingest_gee_ch4.py"
GEE_FIXTURE = ROOT / "pipelines" / "fixtures" / "gee_points.json"

sys.path.append(str(ROOT / "pipelines" / "jobs"))
import fetch_gee_ch4  # noqa: E402


def test_build_run_id() -> None:
    assert fetch_gee_ch4.build_run_id("2026-02-01", "2026-02-07", "permian") == "2026-02-01_2026-02-07_permian"


def test_write_artifacts_with_empty_points_creates_stable_parquet_schema(tmp_path: Path) -> None:
    run_dir = fetch_gee_ch4.write_artifacts(
        output_root=tmp_path,
        run_id="2026-02-01_2026-02-07_permian",
        rows=[],
        aoi="permian",
        start_date="2026-02-01",
        end_date="2026-02-07",
        scale_meters=10000,
        qa_threshold=0.5,
        max_points=50000,
    )
    points = pd.read_parquet(run_dir / "points.parquet")
    metadata = json.loads((run_dir / "metadata.json").read_text())

    assert list(points.columns) == ["lat", "lon", "ch4_ppb", "qa_value", "observed_on", "source"]
    assert points.empty
    assert metadata["point_count"] == 0


def test_ingest_gee_converts_parquet_to_observations(tmp_path: Path) -> None:
    run_id = "2026-02-01_2026-02-07_permian"
    source_dir = tmp_path / "source" / "gee" / run_id
    source_dir.mkdir(parents=True)
    source_fixture_payload = json.loads(GEE_FIXTURE.read_text())
    source_fixture = pd.DataFrame(source_fixture_payload["points"])
    source_fixture.to_parquet(source_dir / "points.parquet", index=False)

    result = subprocess.run(
        [
            sys.executable,
            str(INGEST_GEE_JOB),
            "--aoi",
            "permian",
            "--start",
            "2026-02-01",
            "--end",
            "2026-02-07",
            "--qa-threshold",
            "0.5",
            "--output-root",
            str(tmp_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout.strip())
    assert payload["run_id"] == run_id

    processed = json.loads((tmp_path / "ingest" / run_id / "processed" / "observations.json").read_text())
    metadata = json.loads((tmp_path / "ingest" / run_id / "metadata.json").read_text())

    assert len(processed["observations"]) == 2
    assert processed["observations"][0]["observation_id"].startswith("GEE-")
    assert metadata["qa_fail_count"] == 1


@pytest.mark.skipif(os.getenv("GEE_RUN_INTEGRATION") != "1", reason="GEE integration requires explicit env opt-in and credentials")
def test_fetch_gee_job_integration_smoke(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(FETCH_JOB),
            "--aoi",
            "permian",
            "--start",
            "2026-02-01",
            "--end",
            "2026-02-02",
            "--max-points",
            "50",
            "--output-root",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
