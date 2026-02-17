import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INGEST_JOB = ROOT / "pipelines" / "jobs" / "ingest_tropomi.py"
DETECT_JOB = ROOT / "pipelines" / "jobs" / "detect_hotspots.py"
FIXTURE = ROOT / "pipelines" / "fixtures" / "sample_tropomi_observations.json"


def test_ingest_writes_raw_processed_and_metadata(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(INGEST_JOB),
            "--aoi",
            "permian-test",
            "--start-date",
            "2026-02-10",
            "--end-date",
            "2026-02-11",
            "--qa-threshold",
            "0.9",
            "--fixture",
            str(FIXTURE),
            "--output-root",
            str(tmp_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout.strip())
    run_id = payload["run_id"]

    metadata = json.loads((tmp_path / "ingest" / run_id / "metadata.json").read_text())
    processed = json.loads((tmp_path / "ingest" / run_id / "processed" / "observations.json").read_text())

    assert metadata["qa_threshold"] == 0.9
    assert metadata["qa_pass_count"] == 2
    assert metadata["qa_fail_count"] == 2
    assert len(processed["observations"]) == 2


def test_detect_generates_explainable_hotspots(tmp_path: Path) -> None:
    subprocess.run(
        [
            sys.executable,
            str(INGEST_JOB),
            "--aoi",
            "permian-test",
            "--start-date",
            "2026-02-10",
            "--end-date",
            "2026-02-11",
            "--qa-threshold",
            "0.85",
            "--fixture",
            str(FIXTURE),
            "--output-root",
            str(tmp_path),
        ],
        check=True,
    )

    detect = subprocess.run(
        [
            sys.executable,
            str(DETECT_JOB),
            "--ingest-run-id",
            "2026-02-10_2026-02-11_permian-test",
            "--anomaly-threshold-ppb",
            "40",
            "--output-root",
            str(tmp_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(detect.stdout.strip())
    run_id = payload["run_id"]

    hotspots = json.loads((tmp_path / "detect" / run_id / "hotspots.json").read_text())
    assert hotspots["ingest_run_id"] == "2026-02-10_2026-02-11_permian-test"
    assert len(hotspots["hotspots"]) == 1
    assert hotspots["hotspots"][0]["anomaly_score"] == 47.0
    assert hotspots["hotspots"][0]["qa_pass_ratio"] == 0.75
    assert hotspots["hotspots"][0]["pixel_count"] == 1
