import argparse
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FIXTURE = ROOT / "pipelines" / "fixtures" / "sample_tropomi_observations.json"
DEFAULT_OUTPUT_ROOT = ROOT / "pipelines" / "artifacts"


def fixture_source(args: argparse.Namespace) -> dict:
    return json.loads(args.fixture.read_text())


def real_source(_: argparse.Namespace) -> dict:
    raise NotImplementedError("Real TROPOMI source is not implemented yet. Use --source fixture.")


SOURCE_READERS: dict[str, Callable[[argparse.Namespace], dict]] = {
    "fixture": fixture_source,
    "real": real_source,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fixture-backed TROPOMI ingest smoke job")
    parser.add_argument(
        "--source",
        choices=tuple(SOURCE_READERS.keys()),
        default=os.getenv("INGEST_SOURCE", "fixture"),
        help="Ingest input source adapter",
    )
    parser.add_argument("--aoi", default=os.getenv("INGEST_AOI", "permian"))
    parser.add_argument("--start-date", default=os.getenv("INGEST_START_DATE", "2026-02-10"))
    parser.add_argument("--end-date", default=os.getenv("INGEST_END_DATE", "2026-02-11"))
    parser.add_argument("--qa-threshold", type=float, default=float(os.getenv("INGEST_QA_THRESHOLD", "0.85")))
    parser.add_argument("--fixture", type=Path, default=Path(os.getenv("INGEST_FIXTURE_PATH", DEFAULT_FIXTURE)))
    parser.add_argument("--output-root", type=Path, default=Path(os.getenv("PIPELINE_ARTIFACT_ROOT", DEFAULT_OUTPUT_ROOT)))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = SOURCE_READERS[args.source](args)
    observations = payload["observations"]
    passed = [obs for obs in observations if obs["qa_value"] >= args.qa_threshold]
    dropped = [obs["observation_id"] for obs in observations if obs["qa_value"] < args.qa_threshold]

    run_id = f"{args.start_date}_{args.end_date}_{args.aoi}".replace("/", "-")
    run_dir = args.output_root / "ingest" / run_id
    raw_dir = run_dir / "raw"
    processed_dir = run_dir / "processed"
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    raw_refs = {
        "dataset": payload["dataset"],
        "product": payload["product"],
        "version": payload["version"],
        "source": args.source,
        "source_fixture": str(args.fixture),
        "raw_observation_ids": [obs["observation_id"] for obs in observations],
    }
    processed = {
        "dataset": payload["dataset"],
        "product": payload["product"],
        "version": payload["version"],
        "aoi": args.aoi,
        "start_date": args.start_date,
        "end_date": args.end_date,
        "qa_threshold": args.qa_threshold,
        "source": args.source,
        "observations": passed,
    }
    metadata = {
        "run_id": run_id,
        "stage": "ingest",
        "dataset": payload["dataset"],
        "product": payload["product"],
        "version": payload["version"],
        "aoi": args.aoi,
        "start_date": args.start_date,
        "end_date": args.end_date,
        "qa_threshold": args.qa_threshold,
        "source": args.source,
        "source_fixture": str(args.fixture),
        "raw_count": len(observations),
        "qa_pass_count": len(passed),
        "qa_fail_count": len(dropped),
        "qa_fail_ids": dropped,
        "generated_at": datetime.now(UTC).isoformat(),
        "raw_refs_path": str(raw_dir / "raw_refs.json"),
        "processed_path": str(processed_dir / "observations.json"),
    }

    (raw_dir / "raw_refs.json").write_text(json.dumps(raw_refs, indent=2))
    (processed_dir / "observations.json").write_text(json.dumps(processed, indent=2))
    (run_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))

    print(
        json.dumps(
            {
                "stage": "ingest",
                "run_id": run_id,
                "raw_count": len(observations),
                "qa_pass_count": len(passed),
                "artifact_dir": str(run_dir),
            }
        )
    )


if __name__ == "__main__":
    main()
