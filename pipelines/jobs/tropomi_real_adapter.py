import json
from typing import Any
from urllib.parse import urlencode, urlparse
from urllib.request import urlopen

REQUIRED_FIELDS = (
    "observation_id",
    "observed_on",
    "latitude",
    "longitude",
    "ch4_ppb",
    "qa_value",
)


class RealSourceError(ValueError):
    """Raised when the configured real source payload cannot be normalized."""


def _first_present(record: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in record and record[key] is not None:
            return record[key]
    return None


def normalize_observation(record: dict[str, Any]) -> dict[str, Any]:
    normalized = {
        "observation_id": _first_present(record, "observation_id", "id", "observationId"),
        "observed_on": _first_present(record, "observed_on", "date", "observedOn"),
        "latitude": _first_present(record, "latitude", "lat"),
        "longitude": _first_present(record, "longitude", "lon", "lng"),
        "ch4_ppb": _first_present(record, "ch4_ppb", "methane_mixing_ratio_bias_corrected", "xch4"),
        "qa_value": _first_present(record, "qa_value", "qa", "quality"),
    }

    missing = [field for field in REQUIRED_FIELDS if normalized[field] is None]
    if missing:
        raise RealSourceError(f"Record is missing required field(s): {', '.join(missing)}")

    normalized["latitude"] = float(normalized["latitude"])
    normalized["longitude"] = float(normalized["longitude"])
    normalized["ch4_ppb"] = float(normalized["ch4_ppb"])
    normalized["qa_value"] = float(normalized["qa_value"])
    normalized["observation_id"] = str(normalized["observation_id"])
    normalized["observed_on"] = str(normalized["observed_on"])

    return normalized


def load_real_tropomi_payload(source_url: str, *, start_date: str, end_date: str, aoi: str, timeout_seconds: float) -> dict[str, Any]:
    query = urlencode({"start_date": start_date, "end_date": end_date, "aoi": aoi})
    parsed = urlparse(source_url)
    if parsed.scheme == "file":
        request_url = source_url
        source_reference = f"{source_url}?{query}"
    else:
        separator = "&" if "?" in source_url else "?"
        request_url = f"{source_url}{separator}{query}"
        source_reference = request_url

    with urlopen(request_url, timeout=timeout_seconds) as response:
        payload = json.loads(response.read().decode("utf-8"))

    observations = payload.get("observations")
    if not isinstance(observations, list):
        raise RealSourceError("Real source payload must include an observations list")

    normalized_observations = sorted(
        (normalize_observation(record) for record in observations),
        key=lambda record: (record["observed_on"], record["observation_id"]),
    )

    return {
        "dataset": payload.get("dataset", "Sentinel-5P"),
        "product": payload.get("product", "TROPOMI-CH4"),
        "version": payload.get("version", "unknown"),
        "source_urls": [source_reference],
        "observations": normalized_observations,
    }
