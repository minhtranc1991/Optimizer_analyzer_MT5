"""Interactive charts (Plotly) written to a single self-contained HTML file."""
import math

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from . import commentary as C

HOVER = ["FinalScore", "Trades", "Sharpe Ratio", "Profit Factor", "Equity DD %"]


def _group(full, stable, elite):
    g = pd.Series("Other", index=full.index)
    g[stable.index] = "Stable"
    g[elite.index] = "Elite"
    return g


def _scatter_fwd_back(r):
    df = r["full"].assign(Group=_group(r["full"], r["stable"], r["elite"]))
    hover = [c for c in r["parameters"] + HOVER if c in df.columns]
    fig = px.scatter(
        df, x="Back Result", y="Forward Result", color="Group",
        color_discrete_map={"Other": "#b0b0b0", "Stable": "#1f77b4", "Elite": "#d62728"},
        category_orders={"Group": ["Other", "Stable", "Elite"]},
        hover_data=hover, title="Forward vs Back (on the diagonal = perfectly consistent)",
    )
    top = max(df["Forward Result"].max(), df["Back Result"].max())
    fig.add_shape(type="line", x0=0, y0=0, x1=top, y1=top, line=dict(dash="dash", color="gray"))
    return fig


def _importance(r):
    p, c = r["profit_importance"], r["consistency_importance"]
    m = p.merge(c, on="Parameter", suffixes=("_Profit", "_Consistency"))
    m["Label"] = [f"{x} *" if x in r["parameters"] else x for x in m["Parameter"]]
    long = m.melt(id_vars="Label", value_vars=["Importance_Profit", "Importance_Consistency"],
                  var_name="Target", value_name="Importance")
    return px.bar(long, x="Importance", y="Label", color="Target", barmode="group",
                  orientation="h", title="Parameter importance (* = selected)")


def _parallel(r):
    st, params = r["stable"], r["parameters"]
    dims = params + ["Forward Result", "Back Result", "FinalScore"]
    return px.parallel_coordinates(st, dimensions=dims, color="Cluster",
                                   title="Stable sets: parameters -> results, coloured by cluster")


def _cluster_box(r):
    st = r["stable"].assign(Cluster=lambda d: d["Cluster"].astype(str))
    fig = px.box(st, x="Cluster", y="Forward Result", color="Cluster", points="all",
                 hover_data=r["parameters"], title="Forward Result per cluster")
    best = str(int(r["summary"].iloc[0]["Cluster"]))
    fig.add_annotation(x=best, y=st["Forward Result"].max(), text="recommended",
                       showarrow=True, arrowhead=2)
    return fig


def _pair_map(r):
    a, b = r["parameters"][:2]
    df = r["full"]
    fig = px.scatter(df, x=a, y=b, color="FinalScore", color_continuous_scale="Viridis",
                     hover_data=["Forward Result", "Back Result"],
                     title=f"FinalScore over the two most important parameters ({a}, {b})")
    rg = r["ranges"].set_index("Parameter")
    fig.add_shape(type="rect", x0=rg.loc[a, "Low"], x1=rg.loc[a, "High"],
                  y0=rg.loc[b, "Low"], y1=rg.loc[b, "High"],
                  line=dict(color="red", width=2), fillcolor="rgba(255,0,0,0.08)")
    return fig


def _profiles(r):
    """FinalScore vs each parameter, with the recommended range shaded."""
    params, df = r["parameters"], r["full"]
    rg = r["ranges"].set_index("Parameter")
    cols = min(3, len(params))
    rows = math.ceil(len(params) / cols)
    fig = make_subplots(rows=rows, cols=cols, subplot_titles=params)
    for i, p in enumerate(params):
        row, col = divmod(i, cols)
        fig.add_trace(go.Scatter(x=df[p], y=df["FinalScore"], mode="markers",
                                 marker=dict(size=5, opacity=0.5, color="#1f77b4"),
                                 showlegend=False), row=row + 1, col=col + 1)
        fig.add_vrect(x0=rg.loc[p, "Low"], x1=rg.loc[p, "High"], fillcolor="red",
                      opacity=0.15, line_width=0, row=row + 1, col=col + 1)
        fig.add_vline(x=rg.loc[p, "Center"], line_dash="dash", line_color="red",
                      row=row + 1, col=col + 1)
    fig.update_layout(title="FinalScore vs parameter (red = recommended range)",
                      height=320 * rows)
    return fig


CSS = """
body{font-family:Segoe UI,Arial,sans-serif;max-width:1200px;margin:24px auto;padding:0 16px;color:#222;line-height:1.5}
h1{margin-bottom:0} h2{margin-top:40px;border-bottom:2px solid #ddd;padding-bottom:4px}
.note,.good,.warn{padding:10px 14px;margin:10px 0;border-left:4px solid;border-radius:3px}
.note{background:#eef4fb;border-color:#1f77b4} .good{background:#eaf6ea;border-color:#2ca02c}
.warn{background:#fff4e0;border-color:#ff9800} .note ul,.good ul,.warn ul{margin:6px 0 0 18px;padding:0}
table.t{border-collapse:collapse;font-size:13px;width:100%;margin:10px 0}
table.t th{background:#f0f0f0;text-align:left} table.t td,table.t th{border:1px solid #ddd;padding:5px 8px;vertical-align:top}
"""


def _figure_block(title, help_key, note, fig, first=False):
    return (f"<h3>{title}</h3>" + C._box("Cách đọc", f"<p>{C.FIGURE_HELP[help_key]}</p>") + note
            # plotly.js is embedded once so the file works offline
            + fig.to_html(full_html=False, include_plotlyjs=first))


def write_html_report(result, path, title=""):
    r = result
    charts = [
        _figure_block("Forward vs Back", "fwd_back", C.fwd_back_note(r), _scatter_fwd_back(r), first=True),
        _figure_block("Độ quan trọng của tham số", "importance", C.importance_note(r), _importance(r)),
        _figure_block("Bản đồ hai tham số quan trọng nhất", "pair", C.pair_note(r), _pair_map(r)),
        _figure_block("Điểm số theo từng tham số", "profiles", C.profiles_note(r), _profiles(r)),
        _figure_block("Forward theo cluster", "box", C.box_note(r), _cluster_box(r)),
        _figure_block("Parallel coordinates", "parallel", "", _parallel(r)),
    ]
    body = [
        f"<h1>{title}</h1>",
        C.summary_html(r),
        C.parameters_html(r),
        "<h2>3. Biểu đồ</h2>", *charts,
        C.clusters_html(r),
        C.recommendation_html(r),
        C.top_sets_html(r),
    ]
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(f"<html><head><meta charset='utf-8'><title>{title}</title><style>{CSS}</style></head><body>")
        fh.write("\n".join(body) + "</body></html>")
