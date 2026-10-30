"""Plotly chart builders - kept separate from app.py so the layout logic stays readable."""
import json
import re
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st

ASSETS = Path(__file__).resolve().parent / "assets"
ART = Path(__file__).resolve().parent / "artifacts"
BLUE, GREEN, RED = "#0057B8", "#1B4D3E", "#C0392B"


def pct_bar(series: pd.Series, color=BLUE, height=320, title=None):
    """Horizontal bar chart on a 0-100% axis with readable (non-truncated) labels."""
    pct = series.values * 100
    fig = go.Figure(
        go.Bar(
            x=pct,
            y=series.index,
            orientation="h",
            marker_color=color,
            text=[f"{v:.1f}%" for v in pct],
            textposition="outside",
        )
    )
    layout_kwargs = dict(
        height=height,
        margin=dict(l=10, r=30, t=30 if title else 10, b=10),
        xaxis_title="Share of adults",
        xaxis_ticksuffix="%",
        xaxis_range=[0, max(pct) * 1.18],  # headroom so the longest bar's label isn't clipped
        yaxis=dict(automargin=True),
        font=dict(size=12),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    if title:
        layout_kwargs["title"] = title
    fig.update_layout(**layout_kwargs)
    return fig


def province_comparison(province_uptake: dict):
    """Insurance vs pension by province - grouped (not stacked) bars, % axis, contrasting colors."""
    provs = list(province_uptake.keys())
    ins = [province_uptake[p]["insurance_uptake"] * 100 for p in provs]
    pen = [province_uptake[p]["pension_uptake"] * 100 for p in provs]
    order = sorted(range(len(provs)), key=lambda i: -(ins[i] + pen[i]))
    provs = [provs[i] for i in order]
    ins = [ins[i] for i in order]
    pen = [pen[i] for i in order]

    fig = go.Figure([
        go.Bar(
            name="Insurance",
            x=provs,
            y=ins,
            marker_color=BLUE,
            text=[f"{v:.1f}%" for v in ins],
            textposition="outside",
        ),
        go.Bar(
            name="Pension",
            x=provs,
            y=pen,
            marker_color=GREEN,
            text=[f"{v:.1f}%" for v in pen],
            textposition="outside",
        ),
    ])
    fig.update_layout(
        barmode="group",
        height=320,
        margin=dict(l=10, r=10, t=10, b=10),
        yaxis_title="Share of adults",
        yaxis_ticksuffix="%",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0
        ),
    )
    return fig


def province_lookalike_rates(seg_agg: pd.DataFrame, target: str) -> pd.Series:
    sub = seg_agg[seg_agg.target == target]
    return sub.groupby("province", observed=True).apply(
        lambda g: (g.adults_k * g.lookalike_rate).sum()
        / g.adults_k.sum()
        * 100,
        include_groups=False,
    )

# Approximate province centroids, used only for labels and the fallback map
PROVINCE_CENTROIDS = {
    "Kigali": (-1.95, 30.06),
    "North": (-1.55, 29.85),
    "South": (-2.35, 29.75),
    "East": (-1.95, 30.55),
    "West": (-2.20, 29.20),
}

# Keywords that identify each province in English, French or Kinyarwanda names
_PROVINCE_KEYS = {
    "Kigali": ["kigali"],
    "North": ["north", "nord", "amajyaruguru"],
    "South": ["south", "sud", "amajyepfo"],
    "East": ["east", "est", "iburasirazuba"],
    "West": ["west", "ouest", "iburengerazuba"],
}


def _canonical_province(raw_name: str):
    tokens = re.findall(r"[a-zà-ÿ]+", str(raw_name).lower())
    for prov, keys in _PROVINCE_KEYS.items():
        for t in tokens:
            if any(t == k or (len(k) > 3 and t.startswith(k)) for k in keys):
                return prov
    return None

def _ring_is_clockwise(ring):
    s = 0.0
    for (x1, y1), (x2, y2) in zip(ring, ring[1:] + ring[:1]):
        s += (x2 - x1) * (y2 + y1)
    return s > 0


def _rewind_ring(ring, want_clockwise):
    ring = [list(p[:2]) for p in ring]
    return ring if _ring_is_clockwise(ring) == want_clockwise else ring[::-1]


def _rewind_polygon(rings):
    # Plotly convention: outer ring clockwise, holes counter-clockwise
    return [_rewind_ring(r, want_clockwise=(i == 0)) for i, r in enumerate(rings)]


def rewind_geojson(gj):
    for feat in gj.get("features", []):
        g = feat.get("geometry") or {}
        if g.get("type") == "Polygon":
            g["coordinates"] = _rewind_polygon(g["coordinates"])
        elif g.get("type") == "MultiPolygon":
            g["coordinates"] = [_rewind_polygon(p) for p in g["coordinates"]]
    return gj

GEO_STATUS = ""


def load_rwanda_geojson():
    """Load province boundaries; records why it failed in GEO_STATUS."""
    global GEO_STATUS
    path = ART / "rwanda_provinces.geojson"
    if not path.exists():
        GEO_STATUS = f"file not found at {path.resolve()}"
        return None
    try:
        gj = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        GEO_STATUS = f"could not parse file ({type(e).__name__}: {e})"
        return None

    matched, seen = set(), []
    for feat in gj.get("features", []):
        props = feat.get("properties", {}) or {}
        seen.append(props.get("shapeName") or props.get("name") or str(props)[:60])
        for v in props.values():
            if isinstance(v, str):
                key = _canonical_province(v)
                if key:
                    feat["id"] = key
                    matched.add(key)
                    break

    if len(matched) != 5:
        GEO_STATUS = f"matched {sorted(matched)} of 5 provinces; features in file: {seen}"
        return None
    try:
        gj = rewind_geojson(gj)
    except Exception as e:
        GEO_STATUS = f"rewind failed ({type(e).__name__}: {e})"
        return None
    GEO_STATUS = "ok"
    return gj

def province_choropleth(rates: pd.Series):
    """Choropleth of lookalike rate by province (falls back to a centroid bubble map)."""
    df = rates.reset_index()
    df.columns = ["Province", "Rate"]
    df["Rate"] = df["Rate"].astype(float)
    geojson = load_rwanda_geojson()

    hi = df["Rate"].max()
    if geojson:
        fig = px.choropleth(
            df, geojson=geojson, featureidkey="id", locations="Province",
            color="Rate", color_continuous_scale="YlGnBu",
            range_color=(0, hi * 1.05),
            hover_data={"Province": True, "Rate": ":.1f"},
        )
        fig.update_traces(marker_line_color="white", marker_line_width=2)
        fig.update_geos(
            fitbounds="locations", visible=False, bgcolor="rgba(0,0,0,0)",
            showcountries=False, showland=False, showocean=False,
        )
    else:
        st.warning(f"Province boundaries not loaded: {GEO_STATUS} - showing approximate bubbles instead.")

        df["lat"] = df["Province"].map(lambda p: PROVINCE_CENTROIDS[p][0])
        df["lon"] = df["Province"].map(lambda p: PROVINCE_CENTROIDS[p][1])
        fig = px.scatter_geo(
            df, lat="lat", lon="lon", size="Rate", color="Rate",
            color_continuous_scale="YlGnBu", range_color=(0, hi * 1.05),
            size_max=60, hover_name="Province",
            hover_data={"lat": False, "lon": False, "Rate": ":.1f"},
        )
        fig.update_geos(
            lataxis_range=[-3.0, -1.0], lonaxis_range=[28.7, 31.0],
            showland=True, landcolor="#EEF2F5", showcountries=True,
            countrycolor="#9AA5B1", showocean=False, bgcolor="rgba(0,0,0,0)",
        )

    fig.add_trace(go.Scattergeo(
        lat=[PROVINCE_CENTROIDS[p][0] for p in df["Province"]],
        lon=[PROVINCE_CENTROIDS[p][1] for p in df["Province"]],
        text=[f"<b>{p}</b><br>{r:.1f}%" for p, r in zip(df["Province"], df["Rate"])],
        mode="text",
        textfont=dict(size=13, color="#111"),
        hoverinfo="skip",
        showlegend=False,
    ))

    fig.update_layout(
        height=450,
        margin=dict(r=0, t=0, l=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        coloraxis_colorbar=dict(title="% of adults", ticksuffix="%", thickness=12, len=0.7),
    )
    return fig

def archetype_comparison(archetypes: list):
    """Vehicle ownership / mobile money per archetype - a visual, not a sentence."""
    names = [a["name"].title() for a in archetypes]
    fig = go.Figure([
        go.Bar(
            name="Vehicle ownership",
            x=names,
            y=[a["pct_owns_vehicle"] * 100 for a in archetypes],
            marker_color=BLUE,
        ),
        go.Bar(
            name="Mobile money use",
            x=names,
            y=[a["pct_mobile_money"] * 100 for a in archetypes],
            marker_color=GREEN,
        ),
    ])
    fig.update_layout(
        barmode="group",
        height=300,
        margin=dict(l=10, r=10, t=10, b=60),
        yaxis_title="% of archetype",
        yaxis_ticksuffix="%",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0
        ),
    )
    return fig


def archetype_sizes(archetypes: list):
    """Adult population per archetype - the other half of 'who are they'."""
    names = [a["name"].title() for a in archetypes]
    sizes = [a["adults_k"] / 1000 for a in archetypes]
    fig = go.Figure(
        go.Bar(
            x=names,
            y=sizes,
            marker_color=GREEN,
            text=[f"{s:.2f}M" for s in sizes],
            textposition="outside",
        )
    )
    fig.update_layout(
        height=260,
        margin=dict(l=10, r=10, t=10, b=60),
        yaxis_title="Adults (millions)",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def waterfall(contrib: pd.Series, labels: dict, top_k=8):
    """Signed SHAP contributions for one person - blue raises, red lowers."""
    ordered = contrib.reindex(
        contrib.abs().sort_values(ascending=False).index
    ).head(top_k)
    ordered = ordered.sort_values()

    colors = [BLUE if v >= 0 else RED for v in ordered.values]
    names = [labels.get(n, n.replace("_", " ")) for n in ordered.index]

    fig = go.Figure(
        go.Bar(
            x=ordered.values,
            y=names,
            orientation="h",
            marker_color=colors,
            text=[f"{v:+.2f}" for v in ordered.values],
            textposition="outside",
        )
    )

    span = max(abs(ordered.values.min()), abs(ordered.values.max()), 1e-6)
    fig.update_layout(
        height=320,
        margin=dict(l=10, r=40, t=10, b=10),
        xaxis_title="Shift in Propensity Score (pts)",
        xaxis_range=[-span * 1.35, span * 1.35],
        yaxis=dict(automargin=True),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig
