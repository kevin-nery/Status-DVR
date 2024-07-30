from flask import Flask, render_template
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from ping3 import ping
import concurrent.futures
import threading
import time
from collections import OrderedDict

# Inicializar o servidor Flask
server = Flask(__name__)

# Configurar Dash
app = Dash(__name__, server=server, url_base_pathname='/dash/', external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Status dos DVRs"

# Dicionário de dispositivos com IPs/hostnames e seus nomes amigáveis
devices = OrderedDict ({
    "192.168.2.99": "Filial 02",
    "192.168.3.99": "Filial 03",
    "192.168.4.99": "Filial 04",
    "192.168.6.99": "Filial 06",
    "192.168.8.99": "Filial 08",
    "192.168.10.99": "Filial 10",
    "192.168.12.99": "Filial 12",
    "192.168.13.99": "Filial 13",
    "192.168.14.99": "Filial 14",
    "192.168.15.99": "Filial 15",
    "192.168.16.99": "Filial 16",
    "192.168.17.99": "Filial 17",
    "192.168.18.99": "Filial 18",
    "192.168.19.99": "Filial 19",
    "192.168.21.99": "Filial 21",
    "192.168.23.99": "Filial 23",
    "192.168.24.99": "Filial 24",
    "192.168.25.99": "Filial 25",
    "192.168.27.99": "Filial 27",
    "192.168.28.99": "Filial 28",
    "192.168.29.99": "Filial 29",
    "192.168.30.99": "Filial 30",
    "192.168.31.99": "Filial 31",
    "192.168.32.99": "Filial 32",
    "192.168.33.99": "Filial 33",
    "192.168.34.99": "Filial 34",
    "192.168.36.99": "Filial 36",
    "192.168.38.99": "Filial 38",
    "192.168.39.99": "Filial 39",
    "192.168.40.99": "Filial 40",
    "192.168.41.99": "Filial 41",
    "192.168.42.99": "Filial 42",
    "192.168.43.99": "Filial 43",
    "192.168.44.99": "Filial 44",
    "192.168.45.99": "Filial 45",
    "192.168.46.99": "Filial 46",
    "192.168.47.99": "Filial 47",
    "192.168.48.99": "Filial 48",
    "192.168.49.99": "Filial 49",
    "192.168.50.99": "Filial 50",
    "192.168.51.99": "Filial 51",
    "192.168.52.99": "Filial 52",
    "192.168.53.99": "Filial 53 DVR 1",
    "192.168.53.97": "Filial 53 DVR 2",
    "192.168.54.99": "Filial 54 DVR 1",
    "192.168.54.97": "Filial 54 DVR 2",
    "192.168.55.99": "Filial 55",
    "192.168.57.99": "Filial 57",
    "192.168.59.99": "Filial 59",
    "192.168.60.99": "Filial 60",
    "192.168.61.99": "Filial 61",
    "192.168.62.99": "Filial 62",
    "192.168.63.99": "Filial 63",
    "192.168.64.99": "Filial 64",
    "192.168.65.99": "Filial 65",
    "192.168.66.99": "Filial 66",
    "192.168.67.99": "Filial 67",
    "192.168.84.99": "Filial 84",
    "192.168.85.99": "Filial 85",
    "192.168.87.99": "Filial 87",
    "192.168.88.99": "Filial 88",
    "192.168.89.99": "Filial 89",
    "192.168.91.99": "Filial 91",
    "192.168.93.99": "Filial 93",
    "192.168.94.99": "Filial 94",
    "192.168.95.99": "Filial 95",
    "192.168.96.99": "Filial 96",
    "192.168.98.99": "Filial 98 DVR 1",
    "192.168.98.97": "Filial 98 DVR 2",
    "192.168.100.99": "Filial 100",
    "192.168.101.99": "Filial 101",
    "192.168.102.99": "Filial 102",
    "192.168.103.99": "Filial 103",
    "192.168.106.99": "Filial 106",
    "192.168.107.99": "Filial 107",
    "192.168.110.99": "Filial 110",
    "192.168.112.99": "Filial 112",
    "192.168.113.99": "Filial 113",
    "192.168.114.99": "Filial 114",
    "192.168.115.99": "Filial 115",
    "192.168.116.99": "Filial 116",
    "192.168.117.99": "Filial 117",
    "192.168.118.99": "Filial 118",
    "192.168.119.99": "Filial 119",
    "192.168.120.99": "Filial 120",
    "192.168.121.99": "Filial 121",
    "192.168.122.99": "Filial 122",
    "192.168.123.99": "Filial 123",
    "192.168.124.99": "Filial 124",
    "10.0.1.141": "Escritório DVR 1",
    "10.0.1.142": "Escritório DVR 2",
    "10.0.1.143": "Escritório DVR 3",
    "10.86.10.86": "CD DVR 1",
    "10.86.10.88": "CD DVR 2",
    "10.86.10.90": "CD DVR 3",
    "10.86.10.91": "CD DVR 4",

})
device_statuses = OrderedDict({name: "Unknown" for name in devices.values()})

# Função para verificar os aparelhos continuamente em uma thread separada
def check_devices_continuously():
    global device_statuses
    while True:
        statuses = check_devices(devices)
        for name in devices.values():
            device_statuses[name] = statuses.get(name, "Unknown")
        time.sleep(5)

def ping_device(ip, retries=3, timeout=2):
    for _ in range(retries):
        response = ping(ip, timeout=timeout)
        if response:
            return True
        time.sleep(0.5)
    return False

def check_devices(devices, retries=3, timeout=2):
    status = OrderedDict()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(ping_device, ip, retries, timeout): name for ip, name in devices.items()}
        for future in concurrent.futures.as_completed(futures):
            name = futures[future]
            try:
                online = future.result()
                status[name] = "Online" if online else "Offline"
            except Exception as exc:
                status[name] = "Offline"
    return status

# Iniciar a thread de verificação dos aparelhos
threading.Thread(target=check_devices_continuously, daemon=True).start()

# Função para gerar a cor com base no status
def get_color(status):
    return "green" if status == "Online" else "red"

# Layout da aplicação
app.layout = dbc.Container([
    html.H1("Status DVR", style= {"text-align": "center", "margin": "10px","padding": "10px", "font-size": "50px"}),
    dcc.Interval(id='interval-component', interval=5*1000, n_intervals=0),
    html.Div(id='device-status-grid')
], fluid=True)

@app.callback(
    Output('device-status-grid', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_grid(n):
    rows = []
    cols = []
    for i, (ip, name) in enumerate(devices.items()):
        status = device_statuses[name]
        cols.append(
            dbc.Col(
                html.A(
                    html.Div(
                        [
                            html.H4(name, style={"text-align": "center"}),
                            html.Div(
                                status,
                                style={
                                    "background-color": get_color(status),
                                    "color": "white",
                                    "text-align": "center",
                                    "padding": "20px",
                                    "border-radius": "10px",
                                    "font-size": "24px"
                                }
                            )
                        ],
                        style={
                            "border": "1px solid #ddd",
                            "border-radius": "10px",
                            "margin": "10px",
                            "padding": "10px",
                            "width": "150px",
                            "text-align": "center",
                            "display": "inline-block"
                        }
                    ),
                    href=f"http://{ip}",
                    target="_blank",
                    style={"color": "black", "text-decoration": "none"}
                ),
                width=2
            )
        )
        if (i + 1) % 6 == 0:
            rows.append(dbc.Row(cols, justify="center"))
            cols = []
    if cols:
        rows.append(dbc.Row(cols, justify="center"))

    return rows

# Rota principal que serve o HTML
@server.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run_server(debug=True)