import argparse
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_ROOT = ROOT / "pipelines" / "artifacts"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fixture-backed hotspot detect smoke job")
    parser.add_argument("--ingest-run-id", default=os.getenv("DETECT_INGEST_RUN_ID"))
    parser.add_argument(
        "--anomaly-threshold-ppb",
        type=float,
        default=float(os.getenv("DETECT_ANOMALY_THRESHOLD_PPB", "40")),
    )
    parser.add_argument("--output-root", type=Path, default=Path(os.getenv("PIPELINE_ARTIFACT_ROOT", DEFAULT_OUTPUT_ROOT)))
    return parser.parse_args()


def resolve_ingest_run_id(output_root: Path, ingest_run_id: str | None) -> str:
    if ingest_run_id:
        return ingest_run_id

    ingest_root = output_root / "ingest"
    runs = sorted(path.name for path in ingest_root.iterdir() if path.is_dir())
    if not runs:
        raise FileNotFoundError("No ingest artifacts found. Run make ingest first.")
    return runs[-1]


def main() -> None:
    args = parse_args()
    ingest_run_id = resolve_ingest_run_id(args.output_root, args.ingest_run_id)

    ingest_payload_path = args.output_root / "ingest" / ingest_run_id / "processed" / "observations.json"
    ingest_metadata_path = args.output_root / "ingest" / ingest_run_id / "metadata.json"
    ingest_payload = json.loads(ingest_payload_path.read_text())
    ingest_metadata = json.loads(ingest_metadata_path.read_text())

    observations = ingest_payload["observations"]
    if not observations:
        baseline = 0.0
        qa_pass_ratio = 0.0
    else:
        baseline = median(obs["ch4_ppb"] for obs in observations)
        qa_pass_ratio = ingest_metadata["qa_pass_count"] / max(1, ingest_metadata["raw_count"])

    hotspots = []
    for obs in observations:
        anomaly = round(obs["ch4_ppb"] - baseline, 3)
        if anomaly >= args.anomaly_threshold_ppb:
            hotspot_id = f"hs-{obs['observation_id']}"
            hotspots.append(
                {
                    "id": hotspot_id,
                    "source_observation_id": obs["observation_id"],
                    "observed_on": obs["observed_on"],
                    "anomaly_score": anomaly,
                    "threshold": args.anomaly_threshold_ppb,
                    "qa_pass_ratio": round(qa_pass_ratio, 3),
                    "pixel_count": 1,
                    "area_km2": 7.0,
                    "centroid_latitude": obs["latitude"],
                    "centroid_longitude": obs["longitude"],
                }
            )

    run_id = ingest_run_id
    run_dir = args.output_root / "detect" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    detection_payload = {
        "ingest_run_id": ingest_run_id,
        "baseline_ppb": baseline,
        "anomaly_threshold_ppb": args.anomaly_threshold_ppb,
        "hotspots": hotspots,
    }
    metadata = {
        "run_id": run_id,
        "stage": "detect",
        "input_ingest_run_id": ingest_run_id,
        "baseline_ppb": baseline,
        "anomaly_threshold_ppb": args.anomaly_threshold_ppb,
        "candidate_count": len(hotspots),
        "source_observation_count": len(observations),
        "generated_at": datetime.now(UTC).isoformat(),
        "hotspots_path": str(run_dir / "hotspots.json"),
    }

    (run_dir / "hotspots.json").write_text(json.dumps(detection_payload, indent=2))
    (run_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))

    print(
        json.dumps(
            {
                "stage": "detect",
                "run_id": run_id,
                "candidate_count": len(hotspots),
                "artifact_dir": str(run_dir),
            }
        )
    )


if __name__ == "__main__":
    main()
