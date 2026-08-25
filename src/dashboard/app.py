"""Stage 5: Plotly Dash dashboard, aggregated by department/topic by default."""
import sqlite3
import sys
from pathlib import Path

import pandas as pd
from dash import Dash, dcc, html, dash_table, Input, Output

sys.path.append(str(Path(__file__).resolve().parents[1]))
from config import DB_PATH  # noqa: E402


def load_data(db_path: str = DB_PATH) -> pd.DataFrame:
    conn = sqlite3.connect(db_path)
    df = pd.read_sql(
        """
        SELECT c.id, c.commitment_text, c.minister, c.department, c.topic_tags, c.date,
               f.status, f.evidence_quote, f.checked_at
        FROM commitments c
        LEFT JOIN follow_ups f ON f.commitment_id = c.id
        """,
        conn,
    )
    conn.close()
    return df


app = Dash(__name__)
df = load_data()

department_summary = (
    df.groupby(["department", "status"]).size().reset_index(name="count")
    if not df.empty else pd.DataFrame(columns=["department", "status", "count"])
)

app.layout = html.Div([
    html.H1("Commitment Ledger"),
    html.P("Parliamentary commitments and their follow-up status, aggregated by department."),

    dcc.Graph(
        id="department-chart",
        figure={
            "data": [
                {"x": department_summary[department_summary.status == s]["department"],
                 "y": department_summary[department_summary.status == s]["count"],
                 "type": "bar", "name": s}
                for s in ("fulfilled", "in_progress", "no_evidence_found")
            ],
            "layout": {"barmode": "stack", "title": "Commitments by department and status"},
        },
    ),

    html.H2("Drilldown"),
    dcc.Dropdown(
        id="department-filter",
        options=[{"label": d, "value": d} for d in sorted(df["department"].dropna().unique())] if not df.empty else [],
        placeholder="Select a department",
    ),
    dash_table.DataTable(
        id="commitment-table",
        columns=[{"name": c, "id": c} for c in ["commitment_text", "minister", "status", "evidence_quote", "date"]],
        page_size=10,
        style_cell={"textAlign": "left", "whiteSpace": "normal"},
    ),
])


@app.callback(Output("commitment-table", "data"), Input("department-filter", "value"))
def update_table(department):
    filtered = df if not department else df[df.department == department]
    return filtered.to_dict("records")


if __name__ == "__main__":
    app.run(debug=True)
