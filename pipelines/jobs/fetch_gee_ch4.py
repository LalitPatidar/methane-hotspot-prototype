import argparse
import json
import os
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_ROOT = ROOT / "pipelines" / "artifacts"
DEFAULT_AOI_FIXTURE = ROOT / "pipelines" / "fixtures" / "aoi.geojson"
DATASET_ID = "COPERNICUS/S5P/OFFL/L3_CH4"
SOURCE_NAME = "S5P_OFFL_L3_CH4"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch Sentinel-5P CH4 point samples from Google Earth Engine")
    parser.add_argument("--aoi", default=os.getenv("INGEST_AOI", "permian"))
    parser.add_argument("--start", default=os.getenv("INGEST_START_DATE", "2026-02-01"))
    parser.add_argument("--end", default=os.getenv("INGEST_END_DATE", "2026-02-07"))
    parser.add_argument("--scale-meters", type=int, default=int(os.getenv("GEE_SCALE_METERS", "10000")))
    parser.add_argument("--qa-threshold", type=float, default=float(os.getenv("GEE_QA_THRESHOLD", "0.5")))
    parser.add_argument("--max-points", type=int, default=int(os.getenv("GEE_MAX_POINTS", "50000")))
    parser.add_argument("--tile-scale", type=int, default=int(os.getenv("GEE_TILE_SCALE", "4")))
    parser.add_argument("--aoi-fixture", type=Path, default=Path(os.getenv("INGEST_AOI_FIXTURE", DEFAULT_AOI_FIXTURE)))
    parser.add_argument("--output-root", type=Path, default=Path(os.getenv("PIPELINE_ARTIFACT_ROOT", DEFAULT_OUTPUT_ROOT)))
    return parser.parse_args()


def build_run_id(start_date: str, end_date: str, aoi: str) -> str:
    return f"{start_date}_{end_date}_{aoi}".replace("/", "-")


def load_aoi_geometry(aoi_name: str, fixture_path: Path) -> dict:
    payload = json.loads(fixture_path.read_text())
    for feature in payload.get("features", []):
        if feature.get("properties", {}).get("name") == aoi_name:
            geometry = feature.get("geometry")
            if not geometry:
                break
            return geometry
    raise ValueError(f"AOI '{aoi_name}' was not found in {fixture_path}")


def initialize_ee() -> "object":
    try:
        import ee
    except ModuleNotFoundError as exc:  # pragma: no cover
        raise RuntimeError("earthengine-api is not installed. Run `make setup` and retry.") from exc

    auth_mode = os.getenv("GEE_AUTH_MODE", "user").lower()
    project = os.getenv("GEE_PROJECT")

    try:
        if auth_mode == "service_account":
            service_account_email = os.getenv("GEE_SERVICE_ACCOUNT_EMAIL")
            service_account_key_file = os.getenv("GEE_SERVICE_ACCOUNT_KEY_FILE")
            if not service_account_email or not service_account_key_file:
                raise RuntimeError(
                    "GEE service account auth requires GEE_SERVICE_ACCOUNT_EMAIL and GEE_SERVICE_ACCOUNT_KEY_FILE."
                )
            credentials = ee.ServiceAccountCredentials(service_account_email, service_account_key_file)
            ee.Initialize(credentials=credentials, project=project)
        else:
            ee.Initialize(project=project)
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(
            "Failed to initialize Google Earth Engine. Ensure credentials are configured; see README GEE auth instructions."
        ) from exc

    return ee


def fetch_points(
    ee: "object",
    *,
    aoi_geometry: dict,
    start_date: str,
    end_date: str,
    scale_meters: int,
    qa_threshold: float,
    max_points: int,
    tile_scale: int,
) -> list[dict]:
    region = ee.Geometry(aoi_geometry)
    image = (
        ee.ImageCollection(DATASET_ID)
        .filterDate(start_date, end_date)
        .filterBounds(region)
        .select(["CH4_column_volume_mixing_ratio_dry_air", "qa_value"])
        .median()
    )
    masked = image.updateMask(image.select("qa_value").gte(qa_threshold))
    sampled = masked.sample(
        region=region,
        scale=scale_meters,
        geometries=True,
        numPixels=max_points,
        tileScale=tile_scale,
    )
    info = sampled.getInfo() or {}
    return info.get("features", [])


def features_to_rows(features: list[dict], observed_on: str) -> list[dict]:
    rows: list[dict] = []
    for feature in features:
        geometry = feature.get("geometry") or {}
        coordinates = geometry.get("coordinates")
        properties = feature.get("properties") or {}
        if not coordinates or len(coordinates) != 2:
            continue

        lon, lat = coordinates
        ch4_ppb = properties.get("CH4_column_volume_mixing_ratio_dry_air")
        qa_value = properties.get("qa_value")
        rows.append(
            {
                "lat": float(lat),
                "lon": float(lon),
                "ch4_ppb": float(ch4_ppb) if ch4_ppb is not None else None,
                "qa_value": float(qa_value) if qa_value is not None else None,
                "observed_on": observed_on,
                "source": SOURCE_NAME,
            }
        )
    return rows


def empty_points_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "lat": pd.Series(dtype="float64"),
            "lon": pd.Series(dtype="float64"),
            "ch4_ppb": pd.Series(dtype="float64"),
            "qa_value": pd.Series(dtype="float64"),
            "observed_on": pd.Series(dtype="string"),
            "source": pd.Series(dtype="string"),
        }
    )


def write_artifacts(
    *,
    output_root: Path,
    run_id: str,
    rows: list[dict],
    aoi: str,
    start_date: str,
    end_date: str,
    scale_meters: int,
    qa_threshold: float,
    max_points: int,
) -> Path:
    run_dir = output_root / "source" / "gee" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    points_path = run_dir / "points.parquet"
    frame = pd.DataFrame(rows) if rows else empty_points_frame()
    frame.to_parquet(points_path, index=False)

    metadata = {
        "run_id": run_id,
        "stage": "fetch",
        "dataset": DATASET_ID,
        "source": SOURCE_NAME,
        "aoi": aoi,
        "start_date": start_date,
        "end_date": end_date,
        "scale_meters": scale_meters,
        "qa_threshold": qa_threshold,
        "max_points": max_points,
        "point_count": int(len(frame)),
        "generated_at": datetime.now(UTC).isoformat(),
        "points_path": str(points_path),
    }
    (run_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))
    return run_dir


def main() -> None:
    args = parse_args()
    ee = initialize_ee()
    aoi_geometry = load_aoi_geometry(args.aoi, args.aoi_fixture)
    features = fetch_points(
        ee,
        aoi_geometry=aoi_geometry,
        start_date=args.start,
        end_date=args.end,
        scale_meters=args.scale_meters,
        qa_threshold=args.qa_threshold,
        max_points=args.max_points,
        tile_scale=args.tile_scale,
    )
    rows = features_to_rows(features, observed_on=args.start)

    run_id = build_run_id(args.start, args.end, args.aoi)
    run_dir = write_artifacts(
        output_root=args.output_root,
        run_id=run_id,
        rows=rows,
        aoi=args.aoi,
        start_date=args.start,
        end_date=args.end,
        scale_meters=args.scale_meters,
        qa_threshold=args.qa_threshold,
        max_points=args.max_points,
    )

    print(
        json.dumps(
            {
                "stage": "fetch",
                "run_id": run_id,
                "point_count": len(rows),
                "artifact_dir": str(run_dir),
            }
        )
    )


if __name__ == "__main__":
    main()
