"""Search public Sentinel-2 L2A scenes through the Earth Search STAC API.

Catalog search returns metadata and asset links only. A returned scene is not
automatically cloud-free or suitable for analysis; callers must inspect assets
and validate valid-pixel coverage after loading the bands.
"""
from __future__ import annotations

from datetime import date
from typing import Any

STAC_URL = "https://earth-search.aws.element84.com/v1"
COLLECTION = "sentinel-2-l2a"


class CatalogError(RuntimeError):
    """Raised when catalog search cannot be completed or validated."""


def search_sentinel2(
    bbox: tuple[float, float, float, float],
    start_date: date | str,
    end_date: date | str,
    *,
    max_cloud_cover: float = 30.0,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """Search Sentinel-2 L2A by WGS84 bbox and date range.

    bbox is (west, south, east, north) in longitude/latitude degrees.
    Requires the optional `catalog` extra (pystac-client).
    """
    if len(bbox) != 4:
        raise CatalogError("bbox must be (west, south, east, north).")
    west, south, east, north = map(float, bbox)
    if not (-180 <= west < east <= 180 and -90 <= south < north <= 90):
        raise CatalogError("Invalid WGS84 bbox coordinates.")
    if not 0 <= max_cloud_cover <= 100:
        raise CatalogError("max_cloud_cover must be between 0 and 100.")
    if limit < 1 or limit > 100:
        raise CatalogError("limit must be between 1 and 100.")

    try:
        import pystac_client
    except ImportError as exc:
        raise CatalogError(
            "Install the optional catalog dependencies with: pip install -e '.[catalog]'"
        ) from exc

    start = start_date.isoformat() if isinstance(start_date, date) else str(start_date)
    end = end_date.isoformat() if isinstance(end_date, date) else str(end_date)
    interval = f"{start}T00:00:00Z/{end}T23:59:59Z"
    try:
        client = pystac_client.Client.open(STAC_URL)
        search = client.search(
            collections=[COLLECTION],
            bbox=[west, south, east, north],
            datetime=interval,
            query={"eo:cloud_cover": {"lt": max_cloud_cover + 0.000001}},
            max_items=limit,
        )
        items = []
        for item in search.items():
            props = item.properties
            assets = {}
            for key in ("red", "green", "blue", "nir", "visual", "thumbnail", "SCL"):
                asset = item.assets.get(key)
                if asset is not None:
                    assets[key] = {
                        "href": asset.href,
                        "type": asset.media_type,
                        "roles": list(asset.roles or []),
                        "title": asset.title,
                    }
            items.append({
                "id": item.id,
                "collection": item.collection_id,
                "datetime": props.get("datetime"),
                "platform": props.get("platform"),
                "instruments": props.get("instruments"),
                "cloud_cover_percent": props.get("eo:cloud_cover"),
                "bbox": list(item.bbox) if item.bbox else None,
                "geometry": item.geometry,
                "assets": assets,
                "catalog_item_url": item.get_self_href(),
                "license": item.license,
                "provider": "Element 84 Earth Search STAC catalog; Sentinel-2 L2A",
            })
        return items
    except Exception as exc:
        raise CatalogError(f"Sentinel-2 catalog search failed: {exc}") from exc
