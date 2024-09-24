import pyodbc, os
import pandas as pd
# import warnings
import struct
from azure.identity import DefaultAzureCredential

# warnings.filterwarnings('ignore')

def sql_queries():
    connection = get_conn()

    if connection is None:
        print("No se pudo establecer la conexión a la base de datos.")
        return None, None, None, None
    
    try:
        sql_query_stratpr = """
        SELECT * FROM SCRP.StratumPrices
        """ 
        df_stratpr = pd.read_sql(sql_query_stratpr, connection) 
        
        sql_query_citypr = """
        SELECT * FROM SCRP.CityPrices
        """ 
        df_citypr = pd.read_sql(sql_query_citypr, connection)
        
        sql_query_commpr = """
        SELECT * FROM SCRP.MedCommunePrices
        """ 
        df_commpr = pd.read_sql(sql_query_commpr, connection)
        
        sql_query_tlpr = """
        SELECT * FROM SCRP.PricesTL
        """ 
        df_tlpr = pd.read_sql(sql_query_tlpr, connection)
        
    except pyodbc.Error as e:
        print(f"Error al ejecutar las queries: {e}")
        return None, None, None, None
    finally:
        connection.close()

    df_tlpr = df_tlpr.sort_values("Fecha")
    return df_stratpr, df_citypr, df_commpr, df_tlpr

def get_conn(): #MS Learn function
    try:
        connection_string = os.environ["SQLAZURECONNSTR_ConMonitor"]
        credential = DefaultAzureCredential(exclude_interactive_browser_credential=False)
        token_bytes = credential.get_token("https://database.windows.net/.default").token.encode("UTF-16-LE")
        token_struct = struct.pack(f'<I{len(token_bytes)}s', len(token_bytes), token_bytes)
        
        SQL_COPT_SS_ACCESS_TOKEN = 1256  # MS Defined
        
        conn = pyodbc.connect(connection_string, attrs_before={SQL_COPT_SS_ACCESS_TOKEN: token_struct})
        return conn

    except pyodbc.Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None
