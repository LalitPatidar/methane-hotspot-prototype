import argparse
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Callable

from tropomi_real_adapter import load_real_tropomi_payload

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FIXTURE = ROOT / "pipelines" / "fixtures" / "sample_tropomi_observations.json"
DEFAULT_AOI_PRESETS = ROOT / "pipelines" / "fixtures" / "aoi.geojson"
DEFAULT_OUTPUT_ROOT = ROOT / "pipelines" / "artifacts"


def fixture_source(args: argparse.Namespace) -> dict:
    return json.loads(args.fixture.read_text())


def real_source(args: argparse.Namespace) -> dict:
    if not args.real_source_url:
        raise ValueError("--real-source-url (or INGEST_REAL_SOURCE_URL) is required when --source=real")

    return load_real_tropomi_payload(
        args.real_source_url,
        start_date=args.start_date,
        end_date=args.end_date,
        aoi=getattr(args, "query_aoi", args.aoi),
        timeout_seconds=args.real_source_timeout_seconds,
    )


SOURCE_READERS: dict[str, Callable[[argparse.Namespace], dict]] = {
    "fixture": fixture_source,
    "real": real_source,
}


def _validate_bbox(min_lon: float, min_lat: float, max_lon: float, max_lat: float) -> tuple[float, float, float, float]:
    if not -180 <= min_lon <= 180 or not -180 <= max_lon <= 180:
        raise ValueError("AOI longitude values must be within [-180, 180]")
    if not -90 <= min_lat <= 90 or not -90 <= max_lat <= 90:
        raise ValueError("AOI latitude values must be within [-90, 90]")
    if min_lon >= max_lon:
        raise ValueError("AOI bbox min_lon must be less than max_lon")
    if min_lat >= max_lat:
        raise ValueError("AOI bbox min_lat must be less than max_lat")

    return min_lon, min_lat, max_lon, max_lat


def _parse_bbox(aoi_value: str) -> tuple[float, float, float, float] | None:
    parts = [part.strip() for part in aoi_value.split(",")]
    if len(parts) != 4:
        return None

    try:
        min_lon, min_lat, max_lon, max_lat = (float(part) for part in parts)
    except ValueError as exc:
        raise ValueError("AOI bbox must contain numeric values: min_lon,min_lat,max_lon,max_lat") from exc

    return _validate_bbox(min_lon, min_lat, max_lon, max_lat)


def _load_named_aois() -> dict[str, tuple[float, float, float, float]]:
    feature_collection = json.loads(DEFAULT_AOI_PRESETS.read_text())
    named_aois: dict[str, tuple[float, float, float, float]] = {}
    for feature in feature_collection.get("features", []):
        name = feature.get("properties", {}).get("name")
        coordinates = feature.get("geometry", {}).get("coordinates", [])
        if not name or not coordinates:
            continue

        ring = coordinates[0]
        longitudes = [point[0] for point in ring]
        latitudes = [point[1] for point in ring]
        named_aois[name] = _validate_bbox(min(longitudes), min(latitudes), max(longitudes), max(latitudes))

    return named_aois


def resolve_aoi(aoi_input: str) -> dict[str, str | list[float]]:
    named_aois = _load_named_aois()
    if aoi_input in named_aois:
        bbox = named_aois[aoi_input]
        return {"aoi": aoi_input, "aoi_bbox": list(bbox), "query_aoi": aoi_input}

    parsed_bbox = _parse_bbox(aoi_input)
    if parsed_bbox:
        canonical_bbox = ",".join(f"{value:.6f}" for value in parsed_bbox)
        return {
            "aoi": f"bbox:{canonical_bbox}",
            "aoi_bbox": list(parsed_bbox),
            "query_aoi": canonical_bbox,
        }

    named = ", ".join(sorted(named_aois))
    raise ValueError(
        "Invalid --aoi. Use one of the named presets "
        f"({named}) or a bbox in the format min_lon,min_lat,max_lon,max_lat"
    )


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
    parser.add_argument("--real-source-url", default=os.getenv("INGEST_REAL_SOURCE_URL"))
    parser.add_argument(
        "--real-source-timeout-seconds",
        type=float,
        default=float(os.getenv("INGEST_REAL_SOURCE_TIMEOUT_SECONDS", "30")),
    )
    parser.add_argument("--output-root", type=Path, default=Path(os.getenv("PIPELINE_ARTIFACT_ROOT", DEFAULT_OUTPUT_ROOT)))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    resolved_aoi = resolve_aoi(args.aoi)
    aoi = str(resolved_aoi["aoi"])
    aoi_bbox = resolved_aoi["aoi_bbox"]
    args.query_aoi = resolved_aoi["query_aoi"]
    payload = SOURCE_READERS[args.source](args)
    observations = payload["observations"]
    passed = [obs for obs in observations if obs["qa_value"] >= args.qa_threshold]
    dropped = [obs["observation_id"] for obs in observations if obs["qa_value"] < args.qa_threshold]

    run_id = f"{args.start_date}_{args.end_date}_{aoi}".replace("/", "-")
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
        "source_fixture": str(args.fixture) if args.source == "fixture" else None,
        "source_urls": payload.get("source_urls", []),
        "raw_observation_ids": [obs["observation_id"] for obs in observations],
    }
    processed = {
        "dataset": payload["dataset"],
        "product": payload["product"],
        "version": payload["version"],
        "aoi": aoi,
        "aoi_bbox": aoi_bbox,
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
        "aoi": aoi,
        "aoi_bbox": aoi_bbox,
        "start_date": args.start_date,
        "end_date": args.end_date,
        "qa_threshold": args.qa_threshold,
        "source": args.source,
        "source_fixture": str(args.fixture) if args.source == "fixture" else None,
        "source_urls": payload.get("source_urls", []),
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
