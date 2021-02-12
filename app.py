import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sqlite3


# create db connection 
# conn = sqlite3.connect(Path.cwd()/'db'/'app.db')
conn = sqlite3.connect('db/app.db')

# define db queries to separate data into scanners
queries  = {
    "MR2": 'SELECT * FROM DQA WHERE StationName = "MRC25326"',
    "MR4": 'SELECT * FROM DQA WHERE StationName = "PHILIPS-0DIKEI3"',
    "PBT": 'SELECT * FROM DQA WHERE StationName = "PHILIPS-499QHGT"', 
}


# a bit of tiding up
scanners = {}
for key, value in queries.items():    
    data = pd.read_sql(value,conn)
    data['NSNR'] = data['NSNR'].astype(float).round(0)
    data['NSNR_std'] = data['NSNR_std'].astype(float).round(0)
    if data['ReceiveCoilName'][0]:
        data['Coil'] = data['ReceiveCoilName']
    else:
        data['Coil'] = data['Coil'].apply(lambda x: x[0:x.find('_DQA')])
        


    data.loc[data.StationName  == 'PHILIPS-0DIKEI3', 'Coil'] = data.loc[data.StationName  == 'PHILIPS-0DIKEI3', 'ProtocolName'] # change names for MR4
    data.loc[data.Date  == '2021-02-11 19:00:08.150000', 'Coil'] = 'SPINE_DQA' #correct name NV16 to SPINE 


    data.sort_values("Date", inplace=True)
    scanners.update({key:data})
    print(f'\n{data}\n')


# create chart to be shown
charts = []
for scanner in scanners.items():
    print(scanner[0])

    chart = px.scatter( 
        scanner[1], 
        x="Date",
        y = 'NSNR',
        error_y = 'NSNR_std',
        size = 'NSNR_std',
        color = "Coil",
        hover_data={'NSNR_std':False},
        title = f"{scanner[1].InstitutionName[0].replace('_',' ')}: {scanner[1].ManufacturersModelName[0].replace('_',' ')}",
        template = 'simple_white',

        )
    chart.update_traces(
        mode='lines+markers',
        marker=dict(
            # color='LightSkyBlue',
            opacity=1,
            # size=120,
            # line=dict(
            #     color='MediumPurple',
            #     width=12
            ),
        line=dict(dash='dot'), 
        )
    # )

    charts.append(chart)






# define style
external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
                "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]


# define app 
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = "DailyQA: Taking care of your coils!"


app.layout = html.Div(
    children=[
        html.H1(children=" UCLH RF-Coil Performance Monitor",
        style={"fontSize": "48px", "color": "black"},
        # className="header-title"
    
        ),

        html.P(
            children=["The charts show the normalised signal to noise ratios (NSNR) of different rf-coils, obtained from QC tests performed regularly across the MRI scanners in the Trust."],
            className="header-description"
        ),
        
        html.P(
            children=[" Select/Unselect specific rf-coils by clicking on their legend.", html.Br()],
            style={"color": 'rgb(97, 197, 97)'}
            # "Rather that the actual NSNR value, we look for any anomaly in the trend of each rf-coil's "
        ),



            
        dcc.Graph(
            id="chart1",
            # config={"displayModeBar": False},
            figure = charts[0],
            className= "card",
            style={'display': 'inline-block'},
            # config={"displayModeBar": False}
        ),

         dcc.Graph(
            figure = charts[1],
            style={'display': 'inline-block'},
            # config={"displayModeBar": False},
            className= "card",

        ), dcc.Graph(
            figure = charts[2],
            style={'display': 'inline-block'},
            # config={"displayModeBar": False},
            className= "card",
        ),


        # dcc.Graph(
        #     figure = charts[1],
        #     style={'display': 'inline-block'},
        #     # config={"displayModeBar": False}
        # ),
        
    ],
    className="wrapper",    
)

if __name__ == "__main__":
    app.run_server(debug=True)