"""Named, evidence-backed Qyoo rendering geometry profiles.

The names are recovery terminology.  They describe rendering geometry only;
none changes the row-major, MSB-first 36-cell carrier semantics.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class GeometryProfile:
    name: str
    canvas_size: int
    working_scale: int
    carrier_left: float
    carrier_top: float
    carrier_diameter: float
    square_left: float
    square_top: float
    square_right: float
    square_bottom: float
    dot_centers_x: tuple[float, ...]
    dot_centers_y: tuple[float, ...]
    dot_radius: float
    provenance: str

    @property
    def working_canvas_size(self) -> int:
        return self.canvas_size * self.working_scale

    def output_metadata(self) -> dict:
        values = asdict(self)
        scale = self.working_scale
        for key in (
            "carrier_left", "carrier_top", "carrier_diameter", "square_left",
            "square_top", "square_right", "square_bottom", "dot_radius",
        ):
            values[key] /= scale
        values["dot_centers_x"] = [value / scale for value in self.dot_centers_x]
        values["dot_centers_y"] = [value / scale for value in self.dot_centers_y]
        values["working_canvas_size"] = self.working_canvas_size
        return values


LEGACY_PYTHON = GeometryProfile(
    name="legacy_python",
    canvas_size=256,
    working_scale=1,
    carrier_left=0,
    carrier_top=0,
    carrier_diameter=256,
    square_left=128,
    square_top=128,
    square_right=256,
    square_bottom=256,
    dot_centers_x=tuple(48 + 32 * index for index in range(6)),
    dot_centers_y=tuple(48 + 32 * index for index in range(6)),
    dot_radius=12,
    provenance="QyooGenerate-Python behavior before Task 06",
)

HISTORICAL_SVG_204 = GeometryProfile(
    name="historical_svg_204",
    canvas_size=204,
    working_scale=1,
    carrier_left=0,
    carrier_top=0,
    carrier_diameter=204,
    square_left=102,
    square_top=102,
    square_right=204,
    square_bottom=204,
    dot_centers_x=tuple(39 + 25 * index for index in range(6)),
    dot_centers_y=tuple(39 + 25 * index for index in range(6)),
    dot_radius=10,
    provenance="recovered reference/qyoo-us and qyoo-in 204-unit SVG formulas",
)


def _c_profile() -> GeometryProfile:
    canvas = 512
    radius = canvas // 4
    square_size = int(radius * 2 * 0.707)
    dot_radius = square_size // 12
    dot_radius -= (dot_radius + 9) // 10
    center = canvas // 2
    centers = tuple(
        center - square_size // 2 + index * square_size // 6 + dot_radius
        for index in range(6)
    )
    return GeometryProfile(
        name="c_like_512",
        canvas_size=canvas,
        working_scale=1,
        carrier_left=center - radius,
        carrier_top=center - radius,
        carrier_diameter=radius * 2,
        square_left=center,
        square_top=center,
        square_right=center + radius,
        square_bottom=center + radius,
        dot_centers_x=centers,
        dot_centers_y=centers,
        dot_radius=dot_radius,
        provenance="current QyooGenerate-C integer formulas at 512 pixels",
    )


def _php_profile() -> GeometryProfile:
    scale = 4
    canvas = 512
    working = canvas * scale
    radius = working / 4
    square_size = radius * 2 * 0.707
    dot_radius = square_size / 12
    dot_radius -= (dot_radius + 9) / 10
    center = working / 2
    centers = tuple(
        int(center - square_size / 2 + index * square_size / 6 + dot_radius)
        for index in range(6)
    )
    return GeometryProfile(
        name="php_like_512",
        canvas_size=canvas,
        working_scale=scale,
        carrier_left=center - radius,
        carrier_top=center - radius,
        carrier_diameter=radius * 2,
        square_left=center,
        square_top=center,
        square_right=center + radius,
        square_bottom=center + radius,
        dot_centers_x=centers,
        dot_centers_y=centers,
        dot_radius=int(dot_radius),
        provenance="current QyooGenerate-PHP four-times-render/resample formulas",
    )


C_LIKE_512 = _c_profile()
PHP_LIKE_512 = _php_profile()

GEOMETRY_PROFILES = {
    profile.name: profile
    for profile in (LEGACY_PYTHON, HISTORICAL_SVG_204, C_LIKE_512, PHP_LIKE_512)
}

DEFAULT_GEOMETRY_PROFILE = LEGACY_PYTHON.name


def get_geometry_profile(name: str) -> GeometryProfile:
    try:
        return GEOMETRY_PROFILES[name]
    except KeyError as error:
        choices = ", ".join(sorted(GEOMETRY_PROFILES))
        raise ValueError(f"unknown Qyoo geometry profile {name!r}; choose one of: {choices}") from error
