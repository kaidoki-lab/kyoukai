from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any


class CityDataError(ValueError):
    """Raised when city data cannot be safely rendered."""


ALLOWED_ROUTES = {
    "/",
    "/observation",
    "/observer",
    "/signal",
    "/hyougi",
    "/null",
    "/outside",
    "/archive",
    "/daimyojin",
    "/exit",
    "/gokuraku",
    "/ma",
    "/particles",
    "/ripple",
    "/altar",
}

REQUIRED_LOCATION_FIELDS = {
    "id",
    "slug",
    "name",
    "district",
    "description",
    "images",
    "hotspots",
    "enabled",
}

REQUIRED_COORD_FIELDS = {"x", "y", "width", "height"}


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise CityDataError(f"missing city data file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise CityDataError(f"invalid JSON: {path}") from exc


def _static_path_exists(base_dir: Path, web_path: str) -> bool:
    if not web_path.startswith("/static/"):
        return False
    local_path = base_dir / web_path.lstrip("/")
    try:
        local_path.resolve().relative_to((base_dir / "static").resolve())
    except ValueError:
        return False
    return local_path.exists()


def _valid_coords(coords: Any) -> bool:
    if not isinstance(coords, dict) or not REQUIRED_COORD_FIELDS <= set(coords):
        return False
    for field in REQUIRED_COORD_FIELDS:
        value = coords.get(field)
        if not isinstance(value, (int, float)) or not 0 <= float(value) <= 100:
            return False
    return float(coords["x"]) + float(coords["width"]) <= 100 and float(coords["y"]) + float(coords["height"]) <= 100


def _location_has_images(base_dir: Path, location: dict[str, Any]) -> bool:
    images = location.get("images")
    if not isinstance(images, dict):
        return False
    return all(
        isinstance(images.get(key), str) and _static_path_exists(base_dir, images[key])
        for key in ("pc", "sp")
    )


class CityService:
    def __init__(
        self,
        base_dir: Path,
        *,
        locations_path: Path | None = None,
        districts_path: Path | None = None,
    ) -> None:
        self.base_dir = base_dir
        self.locations_path = locations_path or base_dir / "data" / "city_locations.json"
        self.districts_path = districts_path or base_dir / "data" / "city_districts.json"

    def load_districts(self) -> dict[str, dict[str, Any]]:
        data = _read_json(self.districts_path)
        if not isinstance(data, dict):
            raise CityDataError("city_districts.json must contain an object")
        return {str(key): value for key, value in data.items() if isinstance(value, dict)}

    def load_locations(self, *, include_disabled: bool = False) -> list[dict[str, Any]]:
        data = _read_json(self.locations_path)
        if not isinstance(data, list):
            raise CityDataError("city_locations.json must contain an array")
        locations = []
        for raw in data:
            if not isinstance(raw, dict):
                continue
            location = deepcopy(raw)
            location["_has_images"] = _location_has_images(self.base_dir, location)
            location["_available"] = bool(location.get("enabled")) and bool(location["_has_images"])
            if include_disabled or location["_available"]:
                locations.append(location)
        return locations

    def all_locations_by_slug(self) -> dict[str, dict[str, Any]]:
        return {location["slug"]: location for location in self.load_locations(include_disabled=True)}

    def get_location(self, slug: str) -> dict[str, Any] | None:
        location = self.all_locations_by_slug().get(slug.lower())
        if not location or not location.get("_available"):
            return None
        return self.prepare_location(location)

    def first_location(self) -> dict[str, Any] | None:
        locations = self.load_locations()
        if not locations:
            return None
        return self.prepare_location(locations[0])

    def prepare_location(self, location: dict[str, Any]) -> dict[str, Any]:
        prepared = deepcopy(location)
        all_locations = self.all_locations_by_slug()
        prepared["hotspots"] = [
            self.prepare_hotspot(hotspot, all_locations)
            for hotspot in prepared.get("hotspots", [])
            if self.hotspot_is_renderable(hotspot, all_locations)
        ]
        return prepared

    def prepare_hotspot(
        self,
        hotspot: dict[str, Any],
        all_locations: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        prepared = deepcopy(hotspot)
        hotspot_type = prepared.get("type")
        target = str(prepared.get("target") or "")
        if hotspot_type == "city":
            prepared["href"] = f"/city/{target.lower()}"
        elif hotspot_type == "route":
            prepared["href"] = target
        elif hotspot_type == "external":
            prepared["href"] = target
            prepared["external"] = True
        elif hotspot_type == "action":
            prepared["href"] = "#"
            prepared["action"] = target
        else:
            prepared["href"] = "#"
        return prepared

    def hotspot_is_renderable(
        self,
        hotspot: Any,
        all_locations: dict[str, dict[str, Any]],
    ) -> bool:
        if not isinstance(hotspot, dict) or not hotspot.get("enabled"):
            return False
        if not _valid_coords(hotspot.get("pc")) or not _valid_coords(hotspot.get("sp")):
            return False

        hotspot_type = hotspot.get("type")
        target = str(hotspot.get("target") or "")
        if hotspot_type == "city":
            target_location = all_locations.get(target.lower())
            return bool(target_location and target_location.get("_available"))
        if hotspot_type == "route":
            return target.startswith("/") and target in ALLOWED_ROUTES
        if hotspot_type == "external":
            return target.startswith("https://")
        if hotspot_type == "action":
            return bool(target)
        return False

    def validate(self) -> list[str]:
        errors: list[str] = []
        locations = self.load_locations(include_disabled=True)
        districts = self.load_districts()
        slugs: set[str] = set()
        ids: set[str] = set()
        by_slug = {location.get("slug"): location for location in locations if isinstance(location.get("slug"), str)}

        for location in locations:
            missing = REQUIRED_LOCATION_FIELDS - set(location)
            if missing:
                errors.append(f"{location.get('id', 'UNKNOWN')}: missing fields {sorted(missing)}")

            slug = str(location.get("slug") or "")
            location_id = str(location.get("id") or "")
            if slug in slugs:
                errors.append(f"{location_id}: duplicate slug {slug}")
            if location_id in ids:
                errors.append(f"{location_id}: duplicate id")
            slugs.add(slug)
            ids.add(location_id)

            if slug != slug.lower():
                errors.append(f"{location_id}: slug must be lowercase")
            if location.get("district") not in districts:
                errors.append(f"{location_id}: unknown district {location.get('district')}")

            images = location.get("images")
            if not isinstance(images, dict) or not images.get("pc") or not images.get("sp"):
                errors.append(f"{location_id}: pc/sp images are required")
            elif location.get("enabled"):
                for key in ("pc", "sp"):
                    if not _static_path_exists(self.base_dir, str(images[key])):
                        errors.append(f"{location_id}: missing {key} image {images[key]}")

            for hotspot in location.get("hotspots", []):
                hotspot_id = hotspot.get("id", "UNKNOWN") if isinstance(hotspot, dict) else "UNKNOWN"
                if not isinstance(hotspot, dict):
                    errors.append(f"{location_id}: hotspot must be an object")
                    continue
                if not _valid_coords(hotspot.get("pc")) or not _valid_coords(hotspot.get("sp")):
                    errors.append(f"{location_id}/{hotspot_id}: invalid hotspot coordinates")
                if not hotspot.get("enabled"):
                    continue
                hotspot_type = hotspot.get("type")
                target = str(hotspot.get("target") or "")
                if hotspot_type == "city" and target.lower() not in by_slug:
                    errors.append(f"{location_id}/{hotspot_id}: unknown city target {target}")
                if hotspot_type == "route" and (not target.startswith("/") or target not in ALLOWED_ROUTES):
                    errors.append(f"{location_id}/{hotspot_id}: invalid route target {target}")

        return errors
