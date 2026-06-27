"""Generate initial SVG charts for M/M/1 experiment summaries."""

from __future__ import annotations

import argparse
from pathlib import Path

from src.common.csv_utils import read_rows_csv

COLORS = [
    "#1f77b4",
    "#d62728",
    "#2ca02c",
    "#9467bd",
    "#ff7f0e",
    "#17becf",
]

METRIC_LABELS = {
    "average_number_in_system": "Average customers in system",
    "average_number_in_queue": "Average customers in queue",
    "average_time_in_system": "Average time in system",
    "average_time_in_queue": "Average time in queue",
    "server_utilization": "Server utilization",
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot M/M/1 experiment results.")
    parser.add_argument(
        "--input-dir",
        default="results/mm1/experiments",
        help="Directory containing mm1_summary.csv.",
    )
    parser.add_argument(
        "--output-dir",
        default="figures/mm1",
        help="Directory where SVG figures will be written.",
    )
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    summary_rows = read_rows_csv(input_dir / "mm1_summary.csv")
    _plot_infinite_queue_metrics(summary_rows, output_dir)
    _plot_denial_probability(summary_rows, output_dir)

    print("M/M/1 figures generated")
    print(f"  output directory: {output_dir}")


def _plot_infinite_queue_metrics(
    summary_rows: list[dict[str, str]],
    output_dir: Path,
) -> None:
    rows = [
        row
        for row in summary_rows
        if row["queue_capacity"] == "infinite"
        and row["theoretical_status"] == "infinite_capacity_steady_state"
    ]
    rows.sort(key=lambda row: _to_float(row["rho"]) or 0.0)

    for metric, label in METRIC_LABELS.items():
        simulation_points = [
            (_to_float(row["rho"]), _to_float(row[f"{metric}_mean"]))
            for row in rows
        ]
        theory_points = [
            (_to_float(row["rho"]), _to_float(row[f"{metric}_theory"]))
            for row in rows
        ]
        _write_xy_line_chart(
            [
                {
                    "label": "Simulation mean",
                    "points": _valid_points(simulation_points),
                    "color": COLORS[0],
                    "dash": "",
                },
                {
                    "label": "Theory",
                    "points": _valid_points(theory_points),
                    "color": COLORS[1],
                    "dash": "6 4",
                },
            ],
            output_dir / f"mm1_infinite_{metric}.svg",
            title=f"M/M/1 infinite queue - {label}",
            x_label="rho",
            y_label=label,
        )


def _plot_denial_probability(
    summary_rows: list[dict[str, str]],
    output_dir: Path,
) -> None:
    rows = [
        row
        for row in summary_rows
        if row["queue_capacity"] != "infinite"
    ]
    capacities = sorted(
        {
            int(row["queue_capacity"])
            for row in rows
        }
    )
    rhos = sorted({_to_float(row["rho"]) for row in rows})

    series = []
    for index, rho in enumerate(rhos):
        points = []
        for capacity in capacities:
            match = next(
                row
                for row in rows
                if int(row["queue_capacity"]) == capacity
                and _to_float(row["rho"]) == rho
            )
            points.append(
                (
                    str(capacity),
                    _to_float(match["denial_probability_mean"]),
                )
            )
        series.append(
            {
                "label": f"rho={rho:g}",
                "points": _valid_category_points(points),
                "color": COLORS[index % len(COLORS)],
                "dash": "",
            }
        )

    _write_category_line_chart(
        series,
        output_dir / "mm1_denial_probability_by_capacity.svg",
        title="M/M/1/K - Denial probability by queue capacity",
        x_label="Queue capacity",
        y_label="Denial probability",
        categories=[str(capacity) for capacity in capacities],
    )


def _write_xy_line_chart(
    series: list[dict],
    path: Path,
    title: str,
    x_label: str,
    y_label: str,
) -> None:
    all_points = [
        point
        for item in series
        for point in item["points"]
    ]
    if not all_points:
        return

    x_values = [point[0] for point in all_points]
    y_values = [point[1] for point in all_points]
    x_min, x_max = min(x_values), max(x_values)
    y_min, y_max = 0.0, max(y_values)
    if y_max == y_min:
        y_max = y_min + 1.0

    chart = _Chart(path, title, x_label, y_label)
    chart.start()
    chart.axes([f"{value:g}" for value in x_values], y_min, y_max)
    for item in series:
        points = [
            (
                chart.x_scale(point[0], x_min, x_max),
                chart.y_scale(point[1], y_min, y_max),
            )
            for point in item["points"]
        ]
        chart.line(points, item["color"], item["dash"])
        chart.points(points, item["color"])
    chart.legend(series)
    chart.finish()


def _write_category_line_chart(
    series: list[dict],
    path: Path,
    title: str,
    x_label: str,
    y_label: str,
    categories: list[str],
) -> None:
    all_points = [
        point
        for item in series
        for point in item["points"]
    ]
    if not all_points:
        return

    y_values = [point[1] for point in all_points]
    y_min, y_max = 0.0, max(y_values)
    if y_max == y_min:
        y_max = y_min + 1.0

    category_positions = {
        category: index
        for index, category in enumerate(categories)
    }
    chart = _Chart(path, title, x_label, y_label)
    chart.start()
    chart.axes(categories, y_min, y_max)
    for item in series:
        points = [
            (
                chart.x_scale(
                    category_positions[point[0]],
                    0,
                    max(len(categories) - 1, 1),
                ),
                chart.y_scale(point[1], y_min, y_max),
            )
            for point in item["points"]
        ]
        chart.line(points, item["color"], item["dash"])
        chart.points(points, item["color"])
    chart.legend(series)
    chart.finish()


class _Chart:
    width = 960
    height = 560
    left = 86
    right = 230
    top = 70
    bottom = 80

    def __init__(self, path: Path, title: str, x_label: str, y_label: str):
        self.path = path
        self.title = title
        self.x_label = x_label
        self.y_label = y_label
        self._parts: list[str] = []

    @property
    def plot_width(self) -> int:
        return self.width - self.left - self.right

    @property
    def plot_height(self) -> int:
        return self.height - self.top - self.bottom

    def start(self) -> None:
        self._parts.append(
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{self.width}" height="{self.height}" '
            f'viewBox="0 0 {self.width} {self.height}">'
        )
        self._parts.append('<rect width="100%" height="100%" fill="#ffffff"/>')
        self._parts.append(
            f'<text x="{self.width / 2}" y="32" text-anchor="middle" '
            f'font-family="Arial" font-size="22" font-weight="700">'
            f'{_escape(self.title)}</text>'
        )

    def axes(
        self,
        x_labels: list[str],
        y_min: float,
        y_max: float,
    ) -> None:
        left = self.left
        right = self.width - self.right
        top = self.top
        bottom = self.height - self.bottom

        for index in range(6):
            fraction = index / 5
            y = bottom - fraction * self.plot_height
            value = y_min + fraction * (y_max - y_min)
            self._parts.append(
                f'<line x1="{left}" y1="{y:.2f}" x2="{right}" y2="{y:.2f}" '
                f'stroke="#e6e6e6" stroke-width="1"/>'
            )
            self._parts.append(
                f'<text x="{left - 10}" y="{y + 4:.2f}" text-anchor="end" '
                f'font-family="Arial" font-size="12">{value:.3g}</text>'
            )

        self._parts.append(
            f'<line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" '
            f'stroke="#222" stroke-width="1.5"/>'
        )
        self._parts.append(
            f'<line x1="{left}" y1="{top}" x2="{left}" y2="{bottom}" '
            f'stroke="#222" stroke-width="1.5"/>'
        )

        labels = _unique_preserve_order(x_labels)
        for index, label in enumerate(labels):
            denominator = max(len(labels) - 1, 1)
            x = left + index / denominator * self.plot_width
            self._parts.append(
                f'<text x="{x:.2f}" y="{bottom + 24}" text-anchor="middle" '
                f'font-family="Arial" font-size="12">{_escape(label)}</text>'
            )

        self._parts.append(
            f'<text x="{left + self.plot_width / 2}" y="{self.height - 24}" '
            f'text-anchor="middle" font-family="Arial" font-size="14">'
            f'{_escape(self.x_label)}</text>'
        )
        self._parts.append(
            f'<text x="26" y="{top + self.plot_height / 2}" '
            f'text-anchor="middle" font-family="Arial" font-size="14" '
            f'transform="rotate(-90 26 {top + self.plot_height / 2})">'
            f'{_escape(self.y_label)}</text>'
        )

    def x_scale(self, value: float, minimum: float, maximum: float) -> float:
        if maximum == minimum:
            return self.left + self.plot_width / 2
        return self.left + (value - minimum) / (maximum - minimum) * self.plot_width

    def y_scale(self, value: float, minimum: float, maximum: float) -> float:
        return (
            self.height
            - self.bottom
            - (value - minimum) / (maximum - minimum) * self.plot_height
        )

    def line(
        self,
        points: list[tuple[float, float]],
        color: str,
        dash: str,
    ) -> None:
        if len(points) < 2:
            return
        commands = " ".join(f"{x:.2f},{y:.2f}" for x, y in points)
        dash_attribute = f' stroke-dasharray="{dash}"' if dash else ""
        self._parts.append(
            f'<polyline points="{commands}" fill="none" stroke="{color}" '
            f'stroke-width="2.5"{dash_attribute}/>'
        )

    def points(self, points: list[tuple[float, float]], color: str) -> None:
        for x, y in points:
            self._parts.append(
                f'<circle cx="{x:.2f}" cy="{y:.2f}" r="4" '
                f'fill="{color}" stroke="#fff" stroke-width="1"/>'
            )

    def legend(self, series: list[dict]) -> None:
        x = self.width - self.right + 32
        y = self.top + 8
        for index, item in enumerate(series):
            y_pos = y + index * 24
            dash_attribute = (
                f' stroke-dasharray="{item["dash"]}"'
                if item["dash"]
                else ""
            )
            self._parts.append(
                f'<line x1="{x}" y1="{y_pos}" x2="{x + 28}" y2="{y_pos}" '
                f'stroke="{item["color"]}" stroke-width="2.5"{dash_attribute}/>'
            )
            self._parts.append(
                f'<text x="{x + 38}" y="{y_pos + 4}" font-family="Arial" '
                f'font-size="13">{_escape(item["label"])}</text>'
            )

    def finish(self) -> None:
        self._parts.append("</svg>")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_bytes(("\n".join(self._parts) + "\n").encode("utf-8"))


def _to_float(value: str) -> float | None:
    if value is None or value == "":
        return None
    return float(value)


def _valid_points(
    points: list[tuple[float | None, float | None]],
) -> list[tuple[float, float]]:
    return [
        (x, y)
        for x, y in points
        if x is not None and y is not None
    ]


def _valid_category_points(
    points: list[tuple[str, float | None]],
) -> list[tuple[str, float]]:
    return [
        (x, y)
        for x, y in points
        if y is not None
    ]


def _unique_preserve_order(values: list[str]) -> list[str]:
    seen = set()
    output = []
    for value in values:
        if value not in seen:
            seen.add(value)
            output.append(value)
    return output


def _escape(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


if __name__ == "__main__":
    main()
