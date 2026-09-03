"""Stage 5: Plotly Dash dashboard, aggregated by department/topic by default."""
import sqlite3
import sys
from collections import Counter
from pathlib import Path

import pandas as pd
from dash import Dash, dcc, html, dash_table, Input, Output

sys.path.append(str(Path(__file__).resolve().parents[1]))
from config import DB_PATH  # noqa: E402

# Status colors: validated colorblind-safe pair (good/warning) for the two
# judged outcomes; no_evidence_found stays a deliberately neutral gray since
# it's a statement about the search, not a bad outcome (see STATUS_DEFINITIONS).
STATUS_COLORS = {"fulfilled": "#0ca30c", "in_progress": "#fab219", "no_evidence_found": "#9ca3af"}
STATUS_LABELS = {"fulfilled": "Fulfilled", "in_progress": "In progress", "no_evidence_found": "No evidence found"}


def status_dot(status: str) -> html.Span:
    return html.Span(style={
        "display": "inline-block", "width": "10px", "height": "10px", "borderRadius": "50%",
        "backgroundColor": STATUS_COLORS[status], "marginRight": "8px",
    })
STATUS_DEFINITIONS = {
    "fulfilled": "The later record shows it was met. The evidence is linked.",
    "in_progress": "Movement on record: a consultation, a draft, a date, not yet delivered.",
    "no_evidence_found": "We searched and found nothing. A statement about our search, not the minister.",
}
STATUS_ORDER = ["fulfilled", "in_progress", "no_evidence_found"]

BG = "#0d1117"
CARD_BG = "#1a1f2e"
TEXT = "#e5e7eb"
MUTED = "#9ca3af"
AMBER = "#f5a623"
BORDER = "#2a3141"


def load_data(db_path: str = DB_PATH) -> pd.DataFrame:
    conn = sqlite3.connect(db_path)
    df = pd.read_sql(
        """
        SELECT c.id, c.commitment_text, c.minister, c.department, c.topic_tags, c.date,
               src.url AS source_url, src.title AS source_title,
               f.status, f.evidence_quote, f.checked_at,
               ev.url AS evidence_url
        FROM commitments c
        JOIN documents src ON src.id = c.document_id
        LEFT JOIN follow_ups f ON f.commitment_id = c.id
        LEFT JOIN documents ev ON ev.id = f.document_id
        """,
        conn,
    )
    doc_counts = pd.read_sql("SELECT source, COUNT(*) AS n FROM documents GROUP BY source", conn)
    conn.close()
    df["status"] = df["status"].fillna("no_evidence_found")
    df["department"] = df["department"].fillna("(unspecified)")
    df["source_link"] = "[Source](" + df["source_url"] + ")"
    df["evidence_link"] = df["evidence_url"].apply(lambda u: f"[Evidence]({u})" if pd.notna(u) else "-")
    df["month"] = df["date"].str.slice(0, 7)
    return df, doc_counts


def load_search_candidates(commitment_id: str, db_path: str = DB_PATH) -> pd.DataFrame:
    conn = sqlite3.connect(db_path)
    df = pd.read_sql(
        """
        SELECT sc.rank, sc.similarity_score, d.title, d.date, d.url
        FROM search_candidates sc
        JOIN documents d ON d.id = sc.document_id
        WHERE sc.commitment_id = ?
        ORDER BY sc.rank
        """,
        conn,
        params=(commitment_id,),
    )
    conn.close()
    return df


app = Dash(__name__)
df, doc_counts = load_data()

status_counts = df["status"].value_counts().to_dict()
hansard_n = int(doc_counts.loc[doc_counts.source == "hansard", "n"].sum()) if not doc_counts.empty else 0
written_n = int(doc_counts.loc[doc_counts.source == "written_answer", "n"].sum()) if not doc_counts.empty else 0
total_docs = hansard_n + written_n
total_commitments = len(df)
matched_n = status_counts.get("fulfilled", 0) + status_counts.get("in_progress", 0)

# departments with a single commitment clutter the chart -- fold them into "Other"
# (the dropdown/table below keep the real department name, this only affects the chart)
dept_totals = df["department"].value_counts()
single_depts = set(dept_totals[dept_totals == 1].index)
_chart_department = df["department"].apply(lambda d: "Other" if d in single_depts else d)
department_summary = (
    pd.DataFrame({"department": _chart_department, "status": df["status"]})
    .groupby(["department", "status"]).size().reset_index(name="count")
    if not df.empty else pd.DataFrame(columns=["department", "status", "count"])
)
month_summary = (
    df.groupby(["month", "status"]).size().reset_index(name="count")
    if not df.empty else pd.DataFrame(columns=["month", "status", "count"])
)
topic_counts = Counter(
    t.strip() for tags in df["topic_tags"].dropna() for t in tags.split(",") if t.strip()
)
top_topics = topic_counts.most_common(10)[::-1]  # ascending, so horizontal bar reads largest-on-top

CARD_STYLE = {
    "background": CARD_BG, "border": f"1px solid {BORDER}", "borderRadius": "8px",
    "padding": "16px", "flex": "1",
}


def status_card(status: str) -> html.Div:
    return html.Div([
        html.Div([
            status_dot(status),
            html.Span(STATUS_LABELS[status], style={"color": STATUS_COLORS[status], "fontWeight": "bold"}),
        ]),
        html.Div(str(status_counts.get(status, 0)), style={"color": TEXT, "fontSize": "32px", "fontWeight": "bold", "margin": "8px 0"}),
        html.Div(STATUS_DEFINITIONS[status], style={"color": MUTED, "fontSize": "13px"}),
    ], style=CARD_STYLE)


def _short_dept(name: str) -> str:
    for prefix in ("Department for ", "Department of ", "Ministry of "):
        if name.startswith(prefix):
            return name[len(prefix):]
    return name


# Shared chrome: recessive gridlines/axes, no built-in title (each chart sits in
# a card with its own heading instead), transparent background so the card
# behind it shows through.
_AXIS = {"gridcolor": BORDER, "zerolinecolor": BORDER, "linecolor": BORDER}
CHART_LAYOUT_BASE = {
    "paper_bgcolor": "rgba(0,0,0,0)", "plot_bgcolor": "rgba(0,0,0,0)",
    "font": {"color": TEXT, "family": "system-ui, -apple-system, Segoe UI, sans-serif"},
    "xaxis": dict(_AXIS), "yaxis": dict(_AXIS),
}
# 1px surface-color ring between stacked segments so adjacent statuses don't
# visually bleed into one another.
_SEGMENT_LINE = {"width": 1, "color": CARD_BG}
GRAPH_CONFIG = {"displayModeBar": False}


def bar_figure():
    # horizontal, like the topic chart -- no rotated labels to clean up, and
    # full department names actually fit down the side. Placeholder buckets
    # ("(unspecified)" = missing data, "Other" = singleton departments) go at
    # the bottom regardless of count, since neither is a real named department;
    # real departments are ascending above them so the biggest sits at the top
    # (Plotly renders a category array bottom-to-top).
    PLACEHOLDER_DEPTS = ["(unspecified)", "Other"]
    dept_totals = department_summary.groupby("department")["count"].sum().sort_values(ascending=False)
    named_desc = [d for d in dept_totals.index if d not in PLACEHOLDER_DEPTS]
    placeholders = [d for d in PLACEHOLDER_DEPTS if d in dept_totals.index]
    dept_order = placeholders + list(reversed(named_desc))
    short_dept_order = [_short_dept(d) for d in dept_order]

    # log scale: one department (Health and Social Care) holds ~87% of commitments,
    # a linear axis would flatten every other department to an invisible sliver
    layout = {**CHART_LAYOUT_BASE, "barmode": "stack",
              "xaxis": {**CHART_LAYOUT_BASE["xaxis"], "type": "log"},
              "yaxis": {**CHART_LAYOUT_BASE["yaxis"],
                        "categoryorder": "array", "categoryarray": short_dept_order},
              "margin": {"l": 200, "t": 10}, "legend": {"orientation": "h", "y": -0.2, "x": 0}}
    return {
        "data": [
            {"y": [_short_dept(d) for d in department_summary[department_summary.status == s]["department"]],
             "x": department_summary[department_summary.status == s]["count"],
             "type": "bar", "orientation": "h", "name": STATUS_LABELS[s],
             "marker": {"color": STATUS_COLORS[s], "line": _SEGMENT_LINE}}
            for s in STATUS_ORDER
        ],
        "layout": layout,
    }


def timeline_figure():
    layout = {**CHART_LAYOUT_BASE, "barmode": "stack", "margin": {"t": 10},
              "legend": {"orientation": "h", "y": -0.25, "x": 0}}
    return {
        "data": [
            {"x": month_summary[month_summary.status == s]["month"],
             "y": month_summary[month_summary.status == s]["count"],
             "type": "bar", "name": STATUS_LABELS[s],
             "marker": {"color": STATUS_COLORS[s], "line": _SEGMENT_LINE}}
            for s in STATUS_ORDER
        ],
        "layout": layout,
    }


def topic_figure():
    labels, counts = zip(*top_topics) if top_topics else ([], [])
    layout = {**CHART_LAYOUT_BASE, "margin": {"l": 160, "t": 10}, "showlegend": False}
    return {
        "data": [{"x": list(counts), "y": list(labels), "type": "bar", "orientation": "h",
                   "marker": {"color": STATUS_COLORS["in_progress"], "line": _SEGMENT_LINE}}],
        "layout": layout,
    }


def chart_card(title: str, graph_id: str, figure: dict) -> html.Div:
    return html.Div([
        html.H3(title, style={"color": TEXT, "fontSize": "16px", "marginTop": 0}),
        dcc.Graph(id=graph_id, figure=figure, config=GRAPH_CONFIG),
    ], style={**CARD_STYLE, "marginBottom": "16px"})


app.layout = html.Div([
    html.H1("Commitment Ledger", style={"color": TEXT}),
    html.P(
        "Parliamentary commitments and their follow-up status, aggregated by department.",
        style={"color": MUTED},
    ),

    # Status summary cards (mirrors the deck's "The Solution" slide)
    html.Div([status_card(s) for s in STATUS_ORDER], style={"display": "flex", "gap": "12px", "marginBottom": "16px"}),

    # Honest framing callout
    html.Div(
        f"{total_docs} documents ingested ({hansard_n} Hansard debates + {written_n} written answers) → "
        f"{total_commitments} commitments extracted → {matched_n} have verifiable follow-up evidence so far. "
        f"Most commitments are too recent in this session to have follow-up evidence yet. This tool reports "
        f"what it can verify, not what looks good.",
        style={**CARD_STYLE, "color": TEXT, "marginBottom": "16px", "fontWeight": "bold"},
    ),

    chart_card("Commitments over time", "timeline-chart", timeline_figure()),
    chart_card("Most-tagged topics", "topic-chart", topic_figure()),
    chart_card("Commitments by department and status", "department-chart", bar_figure()),

    html.H2("Drilldown", style={"color": TEXT}),
    dcc.Dropdown(
        id="department-filter",
        className="dash-dropdown",
        options=[{"label": "All departments", "value": ""}] +
                ([{"label": d, "value": d} for d in sorted(df["department"].unique())] if not df.empty else []),
        value="",
        clearable=False,
        style={"marginBottom": "12px"},
    ),
    html.Div([
        html.Span(
            "Select ⚪ next to a commitment to view its search trail below.",
            style={"color": MUTED, "fontSize": "13px"},
        ),
        html.Button(
            "Clear selection", id="clear-selection-btn", n_clicks=0,
            style={
                "marginLeft": "12px", "fontSize": "12px", "background": "transparent",
                "color": STATUS_COLORS["in_progress"], "border": f"1px solid {BORDER}",
                "borderRadius": "4px", "padding": "2px 8px", "cursor": "pointer",
            },
        ),
    ], style={"marginBottom": "4px"}),
    dash_table.DataTable(
        id="commitment-table",
        columns=[
            {"name": "Commitment", "id": "commitment_text"},
            {"name": "Minister", "id": "minister"},
            {"name": "Date", "id": "date"},
            {"name": "Source", "id": "source_link", "presentation": "markdown"},
            {"name": "Status", "id": "status"},
            {"name": "Evidence quote", "id": "evidence_quote"},
            {"name": "Evidence link", "id": "evidence_link", "presentation": "markdown"},
        ],
        markdown_options={"link_target": "_blank"},
        row_selectable="single",
        cell_selectable=False,
        page_size=10,
        style_cell={"textAlign": "left", "whiteSpace": "normal", "backgroundColor": CARD_BG, "color": TEXT},
        style_header={"backgroundColor": BORDER, "color": TEXT, "fontWeight": "bold"},
    ),

    html.H3("Search trail", style={"color": TEXT, "marginTop": "16px"}),
    html.P(
        "Select a row above to see which later documents were actually checked as candidate evidence, "
        "and how close each one was.",
        style={"color": MUTED},
    ),
    html.Div(id="search-trail-panel", style={**CARD_STYLE}),
], style={"background": BG, "padding": "24px", "maxWidth": "1200px", "margin": "0 auto",
          "fontFamily": "system-ui, -apple-system, 'Segoe UI', sans-serif"})


@app.callback(Output("commitment-table", "data"), Input("department-filter", "value"))
def update_table(department):
    filtered = df if not department else df[df.department == department]
    return filtered.to_dict("records")


@app.callback(
    Output("commitment-table", "selected_rows"),
    Input("clear-selection-btn", "n_clicks"),
    prevent_initial_call=True,
)
def clear_selection(_n_clicks):
    return []


@app.callback(
    Output("search-trail-panel", "children"),
    Input("commitment-table", "data"),
    Input("commitment-table", "selected_rows"),
)
def update_search_trail(table_data, selected_rows):
    if not selected_rows or not table_data:
        return html.Span("No commitment selected.", style={"color": MUTED})

    row = table_data[selected_rows[0]]
    candidates = load_search_candidates(row["id"])
    if candidates.empty:
        return html.Span("No candidate documents (nothing dated after this commitment).", style={"color": MUTED})

    rows = [html.P(f"Search trail for: “{row['commitment_text']}”", style={"color": TEXT, "fontWeight": "bold"})]
    for _, c in candidates.iterrows():
        used = row["status"] != "no_evidence_found" and c["url"] == row.get("evidence_url")
        marker = "→ used as evidence" if used else "considered, not sufficient"
        rows.append(html.Div([
            html.A(c["title"] or c["url"], href=c["url"], target="_blank", style={"color": AMBER}),
            html.Span(f"  ({c['date']}, similarity {c['similarity_score']:.2f}): {marker}", style={"color": MUTED}),
        ], style={"marginBottom": "4px"}))
    return rows


if __name__ == "__main__":
    app.run(debug=False)
