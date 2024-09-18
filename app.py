from dash import Dash, dcc, html, callback_context, Output, Input
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from sql_utilities import sql_queries

# Dash App
dash_app = Dash(external_stylesheets=[dbc.themes.SLATE], title="MedRentMonitor")
app = dash_app.server

# Configuración de estilos
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "15%",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
    "overflow-y": "scroll",
    "color": "#343a40"  # Color de texto más oscuro
}

CONTENT_STYLE = {
    "margin-left": "15%",  # Ajustado para alinear el contenido con el panel lateral
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa"
}

LANGUAGE_BAR_STYLE = {
    "position": "fixed",
    "top": "10px",
    "right": "1px",
    "padding": "10px",
    "background-color": "#f8f9fa",
    "border": "1px solid #dee2e6",
    "border-radius": "5px",
    "box-shadow": "0 2px 5px rgba(0, 0, 0, 0.1)"
}

# Contenido Eng/Esp
content_text = {
    'es': {
        'title': 'Monitor de precios de arrendamiento del Valle de Aburrá',
        'sidebar_title': 'Datos técnicos',
        'description': """
        Este proyecto tiene como objetivo proporcionar datos de referencia para analizar las dinámicas del mercado inmobiliario en la región
        utilizando técnicas de webscraping de sitios web de anuncios inmobiliarios. El objetivo es identificar el comportamiento de la oferta
        y precios de los arrendamientos en el Valle de Aburrá. Los datos recopilados corresponden a anuncios para apartamentos con al menos
        dos habitaciones y dos baños, utilizando un proceso automatizado que emplea los servicios gratuitos de Azure.

        Los servicios utilizados en este proyecto son:

        - **Azure Functions**: Webscraping automatizado. [Enlace](https://github.com/CloudlessJuan/Rent_Scraper_FR)
        - **Azure DataLake Gen2**: Almacenamiento de datos recopilados mediante webscraping.
        - **Azure SQL Database**: Almacenamiento estructurado de los datos.
        - **Azure App Services**: Dashboard para visualizar los datos almacenados cada semana. [Enlace](https://github.com/CloudlessJuan/DashSQLVisualizer)

        Cabe destacar que las clasificaciones y etiquetas de localización (barrios, comunas) pueden variar en formato, debido a errores en los
        metadatos proporcionados por los creadores de los anuncios. Para más detalles sobre los datos recopilados, puedes contactar al administrador.
        """,
        'fig_titles': {
            'fig_col': 'Precio promedio (COP) por comuna (Medellín)',
            'fig_pie': 'Cantidad de anuncios por municipio',
            'fig_col2': 'Precio promedio (COP) por estrato',
            'fig_line': 'Evolución temporal del precio promedio (COP)'
        }
    },
    'en': {
        'title': 'Housing Rental Price Monitor of the Aburrá Valley',
        'sidebar_title': 'Technical Data',
        'description': """
        This project aims to provide reference data to analyze the dynamics of the real estate market in the region using web scraping techniques
        from real estate listings websites. The goal is to identify the behavior of rental supply and prices in the Aburrá Valley. The collected
        data corresponds to listings for apartments with at least two bedrooms and two bathrooms, using an automated process that employs free
        Azure services.

        The services used in this project are:

        - **Azure Functions**: Automated web scraping. [Link](https://github.com/CloudlessJuan/Rent_Scraper_FR)
        - **Azure DataLake Gen2**: Storage of data collected via web scraping.
        - **Azure SQL Database**: Structured storage of the data.
        - **Azure App Services**: Dashboard for visualizing the stored data on a weekly basis. [Link](https://github.com/CloudlessJuan/DashSQLVisualizer)

        Please note that classifications and location labels (neighborhoods, communes) may vary in format due to errors in the metadata provided
        by the listing creators. For more information about the data, you can contact the administrator.
        """,
        'fig_titles': {
            'fig_col': 'Average Price (COP) by Commune (Medellín)',
            'fig_pie': 'Number of Listings by Municipality',
            'fig_col2': 'Average Price (COP) by Stratum',
            'fig_line': 'Temporal Evolution of Average Price (COP)'
        }
    }
}

# Query con las vistas de la db
df_stratpr, df_citypr, df_commpr, df_tlpr = sql_queries()

def create_figures(titles):
    def style_figure(fig, title):
        fig.update_layout(
            title={'font': {'size': 24, 'family': 'Arial', 'color': 'black'}, 'x': 0.5, 'xanchor': 'center'},
            yaxis_tickformat=','
        )
        return fig

    fig_col = style_figure(px.bar(df_commpr, x="Comuna", y="PrecioPromedio", title=titles['fig_col']), titles['fig_col'])

    fig_pie = px.pie(df_citypr, values="NumeroDeAnuncios", names="Ciudad", title=titles['fig_pie'])
    fig_pie.update_layout(title={'font': {'size': 24, 'family': 'Arial', 'color': 'black'}, 'x': 0.5, 'xanchor': 'center'})

    fig_pie.update_layout(showlegend=True)
    fig_pie = style_figure(fig_pie, titles['fig_pie'])

    fig_col2 = style_figure(px.bar(df_stratpr, x="Estrato", y="PrecioPromedio", title=titles['fig_col2']), titles['fig_col2'])
    fig_line = style_figure(px.line(df_tlpr, x="Fecha", y="PrecioPromedio", title=titles['fig_line']), titles['fig_line'])

    return fig_col, fig_pie, fig_col2, fig_line

# Layout
dash_app.layout = html.Div([
    html.Div([
        html.A(
            [html.Span('🇨🇴', style={'font-size': '24px'}), ' Español'],
            href='#', id='lang-es', style={'margin-right': '10px', 'text-decoration': 'none', 'color': '#343a40'}  # Color de enlace gris oscuro
        ),
        html.A(
            [html.Span('🇬🇧', style={'font-size': '24px'}), ' English'],
            href='#', id='lang-en', style={'text-decoration': 'none', 'color': '#343a40'}  # Color de enlace gris oscuro
        )
    ], style=LANGUAGE_BAR_STYLE),
    
    html.Div(id='sidebar', style=SIDEBAR_STYLE),
    html.Div(id='content', style=CONTENT_STYLE),
])

@dash_app.callback(
    [Output('sidebar', 'children'),
     Output('content', 'children')],
    [Input('lang-es', 'n_clicks'),
     Input('lang-en', 'n_clicks')]
)
def update_language(lang_es, lang_en):
    ctx = callback_context
    if not ctx.triggered:
        button_id = 'lang-es'
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    texts = content_text['es'] if button_id == 'lang-es' else content_text['en']
    
    fig_col, fig_pie, fig_col2, fig_line = create_figures(texts['fig_titles'])
    
    sidebar_content = html.Div([
        html.H2(texts['sidebar_title'], className="display-4", style={'font-size': '25px', 'font-weight': 'bold'}),
        html.Hr(),
        dcc.Markdown(texts['description'], dangerously_allow_html=True, style={'color': '#343a40'})  # Color de texto más oscuro
    ], style=SIDEBAR_STYLE)

    content = html.Div([
        html.H1(texts['title'], style={'textAlign': 'center', 'fontSize': '48px', 'margin-bottom': '30px'}),
        
        # Nueva disposición: pie y gráfico por estratos arriba
        dbc.Row([
            dbc.Col(dcc.Graph(figure=fig_pie), width=6),
            dbc.Col(dcc.Graph(figure=fig_col2), width=6),
        ]),
        html.Br(),
        
        # Gráfico por comunas abajo
        dbc.Row(dbc.Col(dcc.Graph(figure=fig_col), width=12)),
        html.Br(),
        
        # Evolución temporal
        dbc.Row(dbc.Col(dcc.Graph(figure=fig_line), width=12))
    ])

    return sidebar_content, content

if __name__ == '__main__':
    dash_app.run_server(debug=False)
