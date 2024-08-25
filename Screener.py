from flask import Flask, render_template, request
import yfinance as yf
import pandas_ta as ta
import plotly.graph_objs as go
import plotly.io as pio

app = Flask(__name__)

def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1y")
    return hist

def recognize_patterns(data):
    open_price = data['Open']
    high_price = data['High']
    low_price = data['Low']
    close_price = data['Close']

    patterns = {
        'Hammer': ta.cdl_pattern(open_price, high_price, low_price, close_price, name="hammer"),
        'Shooting Star': ta.cdl_pattern(open_price, high_price, low_price, close_price, name="shootingstar"),
        'Engulfing': ta.cdl_pattern(open_price, high_price, low_price, close_price, name="engulfing")
    }

    pattern_results = {}
    for name, pattern in patterns.items():
        if pattern is not None:
            pattern_results[name] = pattern.iloc[-1]
        else:
            pattern_results[name] = "Pattern not detected"

    return pattern_results

def create_candlestick_chart(data):
    fig = go.Figure(data=[go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
    )])

    fig.update_layout(title='Candlestick chart', xaxis_title='Date', yaxis_title='Price')
    
    # Convert the figure to JSON to pass to the template
    graph_json = pio.to_json(fig)
    return graph_json

@app.route("/", methods=["GET", "POST"])
def index():
    chart_data = None
    patterns = None
    ticker = None
    candlestick_chart = None

    if request.method == "POST":
        ticker = request.form.get("ticker")
        if ticker:
            data = get_stock_data(ticker)
            chart_data = data.to_dict(orient="records")
            patterns = recognize_patterns(data)
            candlestick_chart = create_candlestick_chart(data)

    return render_template("index.html", chart_data=chart_data, patterns=patterns, ticker=ticker, candlestick_chart=candlestick_chart)

if __name__ == "__main__":
    app.run(debug=True)
