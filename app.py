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
    "PBT": 'SELECT * FROM DQA WHERE StationName = "PHILIPS-499QHGT"', 
    "MR4": 'SELECT * FROM DQA WHERE StationName = "PHILIPS-0DIKEI3"',
    "MR6": 'SELECT * FROM DQA WHERE StationName = "AWP176065"',

}


# a bit of tiding up
scanners = {}
for key, value in queries.items():    
    data = pd.read_sql(value,conn)
    data['NSNR'] = data['NSNR'].round(0).astype(int)
    data['NSNR_std'] = data['NSNR_std'].round(0).astype(int)
    data['Noise std'] = (data['noise_std']).astype(float).round(1)
    data['Coil'] = data['Coil'].apply(lambda x: x.replace('WIP_',''))
    # print(f"printing data['Coil']: {data['Coil']}")
    # data['circle'] = (1000*data['noise_std']/data['NSNR']).astype(float).round(1)

    # print(f'without corrections{key} \n{data}\n')

    data.loc[data.StationName  == 'PHILIPS-0DIKEI3', 'Coil'] = data.loc[data.StationName  == 'PHILIPS-0DIKEI3', 'ProtocolName'] # change names for MR4

    data['ReceiveCoilName'] = data['ReceiveCoilName'].replace(['0',0,'None',None],'')


    # print(f'during corrections{key} \n{data}\n')

    if data['ReceiveCoilName'].values[0]:
        print('ReceiveCoilName exists')
        data['Coil'] = data['ReceiveCoilName']
    else:
        print('NO ReceiveCoilName')
        data['Coil'] = data['Coil'].apply(lambda x: x[0:x.find('_DQA')])


    
    data.loc[data.Date  == '2021-02-11 19:00:08.150000', 'Coil'] = 'SPINE' #correct name NV16 to SPINE 
    
    print(f'after corrections {key} \n{data}\n')

    data.sort_values("Date", inplace=True)
    scanners.update({key:data})


# create chart to be shown
charts = []
for scanner in scanners.items():
    print(scanner[0])

    chart = px.scatter( 
        scanner[1], 
        x ="Date",
        # y = 'NSNR',
        # error_y = 'NSNR_std',
        y = scanner[1].NSNR.rolling(1).median(),
        error_y = scanner[1].NSNR_std.rolling(1).median(),
        labels={
                     "y": "NSNR",
                     "x": "Scan datetime",
                     "Date": "Scan datetime"
                 },
        # size = scanner[1]['NSNR_std']/scanner[1]['NSNR'],
        size=  'Noise std',
        # size = 'circle',
        color = "Coil",
        hover_name = "Coil",
        hover_data={'NSNR_std':False,'Coil':False,},
        

        # title = f"{scanner[1].InstitutionName[0].replace('_',' ')}: {scanner[1].ManufacturersModelName[0].replace('_',' ')}",
        title = f"{scanner[0]}: {scanner[1].ManufacturersModelName[0].replace('_',' ')}",
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

        # hovertemplate=
        # "<b>{marker.color}</b><br><br>" +
        # "NSNR: %{y}<br>" +
        # "%{x}<br>" +
        # "<extra></extra>",
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
            children=["The graphs show the normalised signal to noise ratios (NSNR) of different rf-coils, obtained from QC tests performed regularly across the MRI scanners in the Trust."],
            className="header-description"
        ),

    
      

        html.P(
            children=[" You can move and zoom around the desired dates and hide unwanted coils by clicking on their legend.", html.Br()],
            style={"color": 'rgb(97, 197, 97)'}
            # "Rather that the actual NSNR value, we look for any anomaly in the trend of each rf-coil's "
        ),



            
        dcc.Graph(
            id="chart1",
            # config={"displayModeBar": False},
            figure = charts[0],
            className= "card",
            # style={'display': 'inline-block'},
            # config={"displayModeBar": False}
        ),

        dcc.Graph(
            figure = charts[1],
            # style={'display': 'inline-block'},
            # config={"displayModeBar": False},
            className= "card",

        ), 
        dcc.Graph(
            figure = charts[2],
            # style={'display': 'inline-block'},
            # config={"displayModeBar": False},
            className= "card",
        ),

         dcc.Graph(
            figure = charts[3],
            # style={'display': 'inline-block'},
            # config={"displayModeBar": False},
            className= "card",
        ),


        # dcc.Graph(
        #     figure = charts[1],
        #     style={'display': 'inline-block'},
        #     # config={"displayModeBar": False}
        # ),


         html.P(
            children=[dcc.Markdown('''
            ### Reading the graphs
            * The size of the circles is proportional to the standard deviation of the *noise image*.  
            A large circle indicates a sub-optimal image substraction, which can be due to **excessive movement** of the liquid inside the phantom.
            
            * The length of the whiskers represent the standar deviation of the SNR measured.  
            Long whiskers indicate a large variation in the SNR across the imaged volume, and that is okay. It is expected that each coil tested will have different SNR variation (as the coil elements can be closer or further away from the source of the signal, depending on the geometry of the test).
            
            *In order to evaluate the performance of rf-coils over time, it is **critical** that every coil is always tested using the same methodology (**same protocol, same FOV, same phantom position, etc**).*
            '''
            ),

        html.Span(
            children = dcc.Markdown('''
            * In an ideal test, a **well performing** coil should appear as a *flat band* on the graph, with constant NSNR and standar deviation over time. 
            '''
            ),
            style={"color": 'rgb(97, 197, 97)'}),

        html.Span(
            children = dcc.Markdown('''
            * In an ideal test, an **under-performing** coil should appear as a *descending slope*, (if the SNR is gradually worsening) or as a *step reduction* in the event of a sudden loss in SNR.
            '''
            ),
            style={"color": 'rgb(197, 50, 50)'})   
        
        
        ],
            
            className="explanation"
        ),
        
    ],
    className="wrapper",    
)

if __name__ == "__main__":
    app.run_server(debug=True)