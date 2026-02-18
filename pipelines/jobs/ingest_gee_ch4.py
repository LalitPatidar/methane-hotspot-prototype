import argparse
import json
import os
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_ROOT = ROOT / "pipelines" / "artifacts"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert fetched GEE CH4 samples into ingest observations format")
    parser.add_argument("--aoi", default=os.getenv("INGEST_AOI", "permian"))
    parser.add_argument("--start", default=os.getenv("INGEST_START_DATE", "2026-02-01"))
    parser.add_argument("--end", default=os.getenv("INGEST_END_DATE", "2026-02-07"))
    parser.add_argument("--qa-threshold", type=float, default=float(os.getenv("GEE_QA_THRESHOLD", "0.5")))
    parser.add_argument("--output-root", type=Path, default=Path(os.getenv("PIPELINE_ARTIFACT_ROOT", DEFAULT_OUTPUT_ROOT)))
    return parser.parse_args()


def build_run_id(start_date: str, end_date: str, aoi: str) -> str:
    return f"{start_date}_{end_date}_{aoi}".replace("/", "-")


def load_points(points_path: Path) -> pd.DataFrame:
    if not points_path.exists():
        raise FileNotFoundError(
            f"Missing GEE points artifact at {points_path}. Run `make fetch_gee aoi=<aoi> start=<start> end=<end>` first."
        )
    frame = pd.read_parquet(points_path)
    required = {"lat", "lon", "ch4_ppb", "qa_value", "observed_on"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"GEE points schema missing columns: {sorted(missing)}")
    return frame


def to_observations(frame: pd.DataFrame, qa_threshold: float) -> tuple[list[dict], list[str]]:
    if frame.empty:
        return [], []

    ordered = frame.sort_values(by=["observed_on", "lat", "lon"], ascending=[True, True, True]).reset_index(drop=True)
    observations: list[dict] = []
    dropped_ids: list[str] = []

    for idx, row in ordered.iterrows():
        observation_id = f"GEE-{row['observed_on']}-{idx:06d}"
        qa_value = float(row["qa_value"])
        if qa_value < qa_threshold:
            dropped_ids.append(observation_id)
            continue

        observation = {
            "observation_id": observation_id,
            "observed_on": str(row["observed_on"]),
            "latitude": float(row["lat"]),
            "longitude": float(row["lon"]),
            "lat": float(row["lat"]),
            "lon": float(row["lon"]),
            "ch4_ppb": float(row["ch4_ppb"]),
            "qa_value": qa_value,
        }
        observations.append(observation)

    return observations, dropped_ids


def main() -> None:
    args = parse_args()
    run_id = build_run_id(args.start, args.end, args.aoi)

    source_dir = args.output_root / "source" / "gee" / run_id
    points_path = source_dir / "points.parquet"
    points = load_points(points_path)
    observations, dropped_ids = to_observations(points, args.qa_threshold)

    run_dir = args.output_root / "ingest" / run_id
    raw_dir = run_dir / "raw"
    processed_dir = run_dir / "processed"
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    raw_refs = {
        "dataset": "COPERNICUS/S5P/OFFL/L3_CH4",
        "product": "L3_CH4",
        "version": "gee",
        "source": "gee_parquet",
        "source_paths": [str(points_path)],
        "raw_observation_count": int(len(points)),
    }
    processed_payload = {
        "dataset": "COPERNICUS/S5P/OFFL/L3_CH4",
        "product": "L3_CH4",
        "version": "gee",
        "aoi": args.aoi,
        "start_date": args.start,
        "end_date": args.end,
        "qa_threshold": args.qa_threshold,
        "source": "gee_parquet",
        "observations": observations,
    }
    metadata = {
        "run_id": run_id,
        "stage": "ingest",
        "dataset": "COPERNICUS/S5P/OFFL/L3_CH4",
        "product": "L3_CH4",
        "version": "gee",
        "aoi": args.aoi,
        "start_date": args.start,
        "end_date": args.end,
        "qa_threshold": args.qa_threshold,
        "source": "gee_parquet",
        "raw_count": int(len(points)),
        "qa_pass_count": len(observations),
        "qa_fail_count": len(dropped_ids),
        "qa_fail_ids": dropped_ids,
        "generated_at": datetime.now(UTC).isoformat(),
        "raw_refs_path": str(raw_dir / "raw_refs.json"),
        "processed_path": str(processed_dir / "observations.json"),
    }

    (raw_dir / "raw_refs.json").write_text(json.dumps(raw_refs, indent=2))
    (processed_dir / "observations.json").write_text(json.dumps(processed_payload, indent=2))
    (run_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))

    print(
        json.dumps(
            {
                "stage": "ingest",
                "run_id": run_id,
                "raw_count": len(points),
                "qa_pass_count": len(observations),
                "artifact_dir": str(run_dir),
            }
        )
    )


if __name__ == "__main__":
    main()
