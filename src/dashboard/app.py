"""Stage 5: Plotly Dash dashboard, aggregated by department/topic by default."""
import sqlite3
import sys
from collections import Counter
from pathlib import Path

import pandas as pd
from dash import Dash, dcc, html, dash_table, Input, Output

sys.path.append(str(Path(__file__).resolve().parents[1]))
from config import DB_PATH  # noqa: E402

# Colors and status wording matched to the pitch deck's "The Solution" slide,
# so the live dashboard and the deck read as one coherent product.
STATUS_COLORS = {"fulfilled": "#22c55e", "in_progress": "#f59e0b", "no_evidence_found": "#9ca3af"}
STATUS_DOTS = {"fulfilled": "\U0001f7e2", "in_progress": "\U0001f7e1", "no_evidence_found": "⚪"}
STATUS_LABELS = {"fulfilled": "Fulfilled", "in_progress": "In progress", "no_evidence_found": "No evidence found"}
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
    df["evidence_link"] = df["evidence_url"].apply(lambda u: f"[Evidence]({u})" if pd.notna(u) else "—")
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

department_summary = (
    df.groupby(["department", "status"]).size().reset_index(name="count")
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
            html.Span(STATUS_DOTS[status], style={"marginRight": "8px"}),
            html.Span(STATUS_LABELS[status], style={"color": STATUS_COLORS[status], "fontWeight": "bold"}),
        ]),
        html.Div(str(status_counts.get(status, 0)), style={"fontSize": "32px", "fontWeight": "bold", "margin": "8px 0"}),
        html.Div(STATUS_DEFINITIONS[status], style={"color": MUTED, "fontSize": "13px"}),
    ], style=CARD_STYLE)


def bar_figure():
    return {
        "data": [
            {"x": department_summary[department_summary.status == s]["department"],
             "y": department_summary[department_summary.status == s]["count"],
             "type": "bar", "name": STATUS_LABELS[s], "marker": {"color": STATUS_COLORS[s]}}
            for s in STATUS_ORDER
        ],
        "layout": {
            "barmode": "stack", "title": "Commitments by department and status",
            "paper_bgcolor": BG, "plot_bgcolor": BG, "font": {"color": TEXT},
            "legend": {"orientation": "h"},
        },
    }


def timeline_figure():
    return {
        "data": [
            {"x": month_summary[month_summary.status == s]["month"],
             "y": month_summary[month_summary.status == s]["count"],
             "type": "bar", "name": STATUS_LABELS[s], "marker": {"color": STATUS_COLORS[s]}}
            for s in STATUS_ORDER
        ],
        "layout": {
            "barmode": "stack", "title": "Commitments over time",
            "paper_bgcolor": BG, "plot_bgcolor": BG, "font": {"color": TEXT},
            "legend": {"orientation": "h"},
        },
    }


def topic_figure():
    labels, counts = zip(*top_topics) if top_topics else ([], [])
    return {
        "data": [{"x": list(counts), "y": list(labels), "type": "bar", "orientation": "h",
                   "marker": {"color": AMBER}}],
        "layout": {
            "title": "Most-tagged topics",
            "paper_bgcolor": BG, "plot_bgcolor": BG, "font": {"color": TEXT},
            "margin": {"l": 160},
        },
    }


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
        f"Most commitments are too recent in this session to have follow-up evidence yet — this tool reports "
        f"what it can verify, not what looks good.",
        style={**CARD_STYLE, "marginBottom": "16px", "fontWeight": "bold"},
    ),

    dcc.Graph(id="department-chart", figure=bar_figure()),
    dcc.Graph(id="timeline-chart", figure=timeline_figure()),
    dcc.Graph(id="topic-chart", figure=topic_figure()),

    html.H2("Drilldown", style={"color": TEXT}),
    dcc.Dropdown(
        id="department-filter",
        options=[{"label": d, "value": d} for d in sorted(df["department"].unique())] if not df.empty else [],
        placeholder="Select a department",
    ),
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

    html.Hr(style={"borderColor": BORDER, "margin": "32px 0"}),

    html.Div([
        html.Div("⚠ ILLUSTRATIVE EXAMPLE — NOT REAL DATA", style={"color": AMBER, "fontWeight": "bold", "marginBottom": "8px"}),
        html.P(
            "The example below is a fictional mockup, not a real commitment or minister. It shows what this "
            "ledger looks like once a commitment has had enough time to accumulate real follow-up evidence — "
            "most of today's real dataset is too recent in the session for that to have happened yet.",
            style={"color": MUTED, "fontSize": "13px"},
        ),
        html.Div([
            html.Div([
                html.Span(STATUS_DOTS["fulfilled"], style={"marginRight": "8px"}),
                html.Span("Fulfilled", style={"color": STATUS_COLORS["fulfilled"], "fontWeight": "bold"}),
            ]),
            html.P(
                "“We will publish a review of NHS dental access by March 2027.” "
                "— [Illustrative] Minister for Example Affairs, [Illustrative] Department of Example, 2026-06-01",
                style={"fontStyle": "italic", "marginTop": "8px"},
            ),
            html.P(
                "Evidence (illustrative, not a real quote): “The review was published on 2027-03-14, "
                "confirming revised access targets for NHS dental services.”",
                style={"color": MUTED},
            ),
        ], style={"background": BG, "border": f"1px dashed {AMBER}", "borderRadius": "6px", "padding": "12px", "marginTop": "8px"}),
    ], style={**CARD_STYLE, "border": f"1px dashed {AMBER}"}),
], style={"background": BG, "padding": "24px", "fontFamily": "sans-serif"})


@app.callback(Output("commitment-table", "data"), Input("department-filter", "value"))
def update_table(department):
    filtered = df if not department else df[df.department == department]
    return filtered.to_dict("records")


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

    rows = [html.P(f"Search trail for: “{row['commitment_text']}”", style={"fontWeight": "bold"})]
    for _, c in candidates.iterrows():
        used = row["status"] != "no_evidence_found" and c["url"] == row.get("evidence_url")
        marker = "→ used as evidence" if used else "considered, not sufficient"
        rows.append(html.Div([
            html.A(c["title"] or c["url"], href=c["url"], target="_blank", style={"color": AMBER}),
            html.Span(f"  ({c['date']}, similarity {c['similarity_score']:.2f}) — {marker}", style={"color": MUTED}),
        ], style={"marginBottom": "4px"}))
    return rows


if __name__ == "__main__":
    app.run(debug=True)
