"""Reads a .osm.pbf file with osmium and yields sport/recreation elements.

Requires the optional `osmium` package (see requirements-ingestion.txt).
Only imported when build_dataset.py actually runs against a PBF file, so
the web service itself never needs osmium installed.
"""

from typing import Iterator

from ingestion.osm_filters import is_sport_feature


def iter_sport_elements(pbf_path: str) -> Iterator[dict]:
    import osmium

    class SportHandler(osmium.SimpleHandler):
        def __init__(self):
            super().__init__()
            self.elements: list[dict] = []

        def node(self, n):
            tags = {tag.k: tag.v for tag in n.tags}
            if is_sport_feature(tags) and n.location.valid():
                self.elements.append(
                    {
                        "type": "node",
                        "id": n.id,
                        "tags": tags,
                        "lat": n.location.lat,
                        "lon": n.location.lon,
                    }
                )

        def area(self, a):
            tags = {tag.k: tag.v for tag in a.tags}
            if not is_sport_feature(tags):
                return
            try:
                centroid = osmium.geom.WKBFactory().create_point(a)
            except Exception:
                return
            self.elements.append(
                {
                    "type": "way" if a.from_way() else "relation",
                    "id": a.orig_id(),
                    "tags": tags,
                    "wkb_point": centroid,
                }
            )

    handler = SportHandler()
    handler.apply_file(pbf_path, locations=True, idx="flex_mem")
    yield from handler.elements
