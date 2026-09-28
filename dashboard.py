import os
import base64

import pandas as pd
import dash_leaflet as dl
import plotly.express as px
from dash import Dash, dcc, html, dash_table, ctx
from dash.dependencies import Input, Output

from CRUD_Python_Module import AnimalShelter


# -------------------------------------------------------------------
# Data / MongoDB connection
# -------------------------------------------------------------------

username = os.getenv("AAC_MONGO_USER", "aacuser")
password = os.getenv("AAC_MONGO_PASSWORD")

if not password:
    raise RuntimeError(
        "AAC_MONGO_PASSWORD is not set. "
        "Set it in the PyCharm run configuration or terminal before starting the app."
    )

db = AnimalShelter(username, password)

# Return the MongoDB query associated with the selected rescue type
def get_rescue_query(filter_type):
    if filter_type == "water":
        return {
            "animal_type": "Dog",
            "breed": {
                "$in": [
                    "Labrador Retriever Mix",
                    "Chesapeake Bay Retriever",
                    "Newfoundland"
                ]
            },
            "sex_upon_outcome": "Intact Female",
            "age_upon_outcome_in_weeks": {
                "$gte": 26,
                "$lte": 156
            }
        }

    if filter_type == "mountain":
        return {
            "animal_type": "Dog",
            "breed": {
                "$in": [
                    "German Shepherd",
                    "Alaskan Malamute",
                    "Old English Sheepdog",
                    "Siberian Husky",
                    "Rottweiler"
                ]
            },
            "sex_upon_outcome": "Intact Male",
            "age_upon_outcome_in_weeks": {
                "$gte": 26,
                "$lte": 156
            }
        }

    if filter_type == "disaster":
        return {
            "animal_type": "Dog",
            "breed": {
                "$in": [
                    "Doberman Pinscher",
                    "German Shepherd",
                    "Golden Retriever",
                    "Bloodhound",
                    "Rottweiler"
                ]
            },
            "sex_upon_outcome": "Intact Male",
            "age_upon_outcome_in_weeks": {
                "$gte": 20,
                "$lte": 300
            }
        }

    return {}

# Load only the first page for the initial table structure
initial_results = db.read_paginated(
    query={},
    page=1,
    page_size=10
)

df = pd.DataFrame.from_records(initial_results)

# MongoDB ObjectId values are not JSON serializable for Dash
if "_id" in df.columns:
    df.drop(columns=["_id"], inplace=True)


# -------------------------------------------------------------------
# Dashboard layout
# -------------------------------------------------------------------

app = Dash(__name__)

image_filename = "Grazioso_Salvare_Logo.png"
encoded_image = base64.b64encode(
    open(image_filename, "rb").read()
).decode()

app.layout = html.Div([
    html.Center(
        html.Div([
            html.H1("CS340 Dashboard", style={"marginBottom": "0px"}),

            html.P(
                "Roger Fisher • AAC Outcomes Explorer",
                style={
                    "marginTop": "4px",
                    "fontStyle": "italic",
                    "opacity": "0.85",
                },
            ),

            html.Div(
                html.A(
                    html.Img(
                        src=f"data:image/png;base64,{encoded_image}",
                        style={
                            "height": "85px",
                            "marginTop": "12px",
                            "marginBottom": "8px",
                        },
                    ),
                    href="https://www.snhu.edu",
                    target="_blank",
                )
            ),

            html.Div(
                "Unique Identifier: The Force is strong with this one",
                style={
                    "display": "inline-block",
                    "padding": "6px 14px",
                    "border": "1px solid #ccc",
                    "borderRadius": "20px",
                    "backgroundColor": "#f7f7f7",
                },
            ),
        ])
    ),

    html.Div([
        html.H3("Rescue Type Filter", style={"marginBottom": "6px"}),

        dcc.RadioItems(
            id="filter-type",
            options=[
                {"label": "Water Rescue", "value": "water"},
                {"label": "Mountain / Wilderness Rescue", "value": "mountain"},
                {"label": "Disaster / Individual Tracking", "value": "disaster"},
                {"label": "Reset (All Records)", "value": "reset"},
            ],
            value="reset",
            inline=True,
        ),

        html.P(
            "Tip: Select a rescue type above to filter the table and charts.",
            style={
                "fontSize": "0.95em",
                "opacity": "0.85",
                "marginTop": "8px",
            },
        ),
    ]),

    html.Hr(),

    dash_table.DataTable(
        id="datatable-id",
        columns=[
            {"name": i, "id": i, "deletable": False, "selectable": True}
            for i in df.columns
        ],
        data=df.to_dict("records"),
        page_current=0,
        page_size=10,
        page_count=1,
        page_action="custom",
        sort_action="custom",
        sort_mode="single",
        sort_by=[],
        filter_action="none",
        row_selectable="single",
        selected_rows=[0],
        style_header={"fontWeight": "bold"},
        style_table={
            "overflowX": "auto",
            "border": "1px solid #ddd",
        },
        style_cell={
            "padding": "6px",
            "fontFamily": "Arial",
            "textAlign": "left",
            "whiteSpace": "normal",
        },
    ),

    html.Br(),
    html.Hr(),

    html.Div(
        style={
            "display": "flex",
            "gap": "16px",
            "alignItems": "stretch",
        },
        children=[
            html.Div(
                id="graph-id",
                style={"flex": "1", "minWidth": "0"},
            ),
            html.Div(
                id="map-id",
                style={"flex": "1", "minWidth": "0"},
            ),
        ],
    ),
])


# -------------------------------------------------------------------
# Callbacks
# -------------------------------------------------------------------

@app.callback(
    Output("datatable-id", "data"),
    Output("datatable-id", "selected_rows"),
    Output("datatable-id", "page_count"),
    Output("datatable-id", "page_current"),
    Input("filter-type", "value"),
    Input("datatable-id", "page_current"),
    Input("datatable-id", "page_size"),
    Input("datatable-id", "sort_by"),
)
def update_dashboard(
        filter_type,
        page_current,
        page_size,
        sort_by):

    # Return to the first page when the rescue filter changes
    if ctx.triggered_id == "filter-type":
        page_current = 0

    query = get_rescue_query(filter_type)

    # Count matching records and calculate the number of pages
    total_records = db.count(query)

    page_count = max(
        1,
        (total_records + page_size - 1) // page_size
    )

    sort_field = None
    sort_direction = 1

    if sort_by:
        sort_field = sort_by[0]["column_id"]

        if sort_by[0]["direction"] == "desc":
            sort_direction = -1

    results = db.read_paginated(
        query=query,
        page=page_current + 1,
        page_size=page_size,
        sort_field=sort_field,
        sort_direction=sort_direction
    )

    temp_df = pd.DataFrame.from_records(results)

    if "_id" in temp_df.columns:
        temp_df.drop(columns=["_id"], inplace=True)

    if temp_df.empty:
        return [], [], page_count, page_current

    return temp_df.to_dict("records"), [0], page_count, page_current


@app.callback(
    Output("graph-id", "children"),
    Input("filter-type", "value"),
)
def update_graphs(filter_type):

    query = get_rescue_query(filter_type)

    breed_summary = db.get_breed_summary(
        query,
        limit=10
    )

    if not breed_summary:
        return html.Div("No data to display.")

    breed_counts = pd.DataFrame(breed_summary)

    breed_counts.rename(
        columns={
            "_id": "breed",
            "count": "count"
        },
        inplace=True
    )

    fig = px.pie(
        breed_counts,
        names="breed",
        values="count",
        title="Top 10 Breeds (Current Filter)",
    )

    fig.update_layout(
        margin=dict(l=20, r=20, t=60, b=20)
    )

    return dcc.Graph(figure=fig)


@app.callback(
    Output("datatable-id", "style_data_conditional"),
    Input("datatable-id", "selected_columns"),
)
def update_styles(selected_columns):
    if not selected_columns:
        selected_columns = []

    return [
        {
            "if": {"column_id": column_id},
            "background_color": "#D2F3FF",
        }
        for column_id in selected_columns
    ]


@app.callback(
    Output("map-id", "children"),
    Input("datatable-id", "derived_virtual_data"),
    Input("datatable-id", "derived_virtual_selected_rows"),
)
def update_map(view_data, index):
    if not view_data:
        return [
            dl.Map(
                style={"width": "100%", "height": "500px"},
                center=[30.75, -97.48],
                zoom=10,
                children=[dl.TileLayer(id="base-layer-id")],
            )
        ]

    dff = pd.DataFrame(view_data)

    row = 0 if not index else index[0]

    if row >= len(dff):
        row = 0

    lat = dff.loc[row, "location_lat"]
    lon = dff.loc[row, "location_long"]
    breed = dff.loc[row, "breed"]
    name = dff.loc[row, "name"]
    outcome = dff.loc[row, "outcome_type"]

    return [
        dl.Map(
            style={"width": "100%", "height": "500px"},
            center=[lat, lon],
            zoom=10,
            children=[
                dl.TileLayer(id="base-layer-id"),
                dl.Marker(
                    position=[lat, lon],
                    children=[
                        dl.Tooltip(str(breed)),
                        dl.Popup([
                            html.H4(str(name)),
                            html.P(f"Breed: {breed}"),
                            html.P(f"Outcome: {outcome}"),
                        ]),
                    ],
                ),
            ],
        )
    ]


if __name__ == "__main__":
    app.run(debug=False)
