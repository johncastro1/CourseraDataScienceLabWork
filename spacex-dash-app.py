# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX launch data into a pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")

max_payload = spacex_df["Payload Mass (kg)"].max()
min_payload = spacex_df["Payload Mass (kg)"].min()

# Create a Dash application
app = dash.Dash(__name__)

# Create the application layout
app.layout = html.Div(
    children=[
        html.H1(
            "SpaceX Launch Records Dashboard",
            style={
                "textAlign": "center",
                "color": "#503D36",
                "font-size": 40,
            },
        ),

        # TASK 1: Launch-site dropdown
        dcc.Dropdown(
            id="site-dropdown",
            options=[
                {"label": "All Sites", "value": "ALL"},
                *[
                    {"label": site, "value": site}
                    for site in sorted(spacex_df["Launch Site"].unique())
                ],
            ],
            value="ALL",
            placeholder="Select a Launch Site here",
            searchable=True,
        ),
        html.Br(),

        # TASK 2: Pie chart
        html.Div(dcc.Graph(id="success-pie-chart")),
        html.Br(),

        html.P("Payload range (Kg):"),

        # TASK 3: Payload range slider
        dcc.RangeSlider(
            id="payload-slider",
            min=0,
            max=10000,
            step=1000,
            marks={value: str(value) for value in range(0, 10001, 2500)},
            value=[min_payload, max_payload],
        ),

        # TASK 4: Payload/success scatter chart
        html.Div(dcc.Graph(id="success-payload-scatter-chart")),
    ]
)


# TASK 2: Render the success pie chart
@app.callback(
    Output(
        component_id="success-pie-chart",
        component_property="figure",
    ),
    Input(
        component_id="site-dropdown",
        component_property="value",
    ),
)
def get_pie_chart(entered_site):
    if entered_site == "ALL":
        # Count successful launches by launch site.
        successful_launches = (
            spacex_df[spacex_df["class"] == 1]
            .groupby("Launch Site")
            .size()
            .reset_index(name="Success Count")
        )

        return px.pie(
            successful_launches,
            values="Success Count",
            names="Launch Site",
            title="Total Success Launches By Site",
        )

    # Show successful versus failed launches for one selected site.
    filtered_df = spacex_df[spacex_df["Launch Site"] == entered_site]

    return px.pie(
        filtered_df,
        names="class",
        title=f"Total Success Launches for site {entered_site}",
        labels={"class": "Launch outcome"},
    )


# TASK 4: Render the payload/success scatter chart
@app.callback(
    Output(
        component_id="success-payload-scatter-chart",
        component_property="figure",
    ),
    [
        Input(
            component_id="site-dropdown",
            component_property="value",
        ),
        Input(
            component_id="payload-slider",
            component_property="value",
        ),
    ],
)
def get_payload_chart(entered_site, payload_range):
    low_payload, high_payload = payload_range

    filtered_df = spacex_df[
        spacex_df["Payload Mass (kg)"].between(
            low_payload,
            high_payload,
            inclusive="both",
        )
    ]

    if entered_site == "ALL":
        title = "Correlation between Payload and Success for all Sites"
    else:
        filtered_df = filtered_df[
            filtered_df["Launch Site"] == entered_site
        ]
        title = (
            "Correlation between Payload and Success "
            f"for site {entered_site}"
        )

    return px.scatter(
        filtered_df,
        x="Payload Mass (kg)",
        y="class",
        color="Booster Version Category",
        title=title,
        hover_data=["Launch Site"],
    )


# Run the app
if __name__ == "__main__":
    app.run(debug=False, port=8050)
