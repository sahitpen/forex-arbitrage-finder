from flask import Flask, render_template, request
from forex_scraper import ForexScraper

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route("/", methods=['POST'])
def run_arbitrage():
    date = request.form['date']
    print(date)
    scraper = ForexScraper()
    exchange_table = scraper.getExchangeTableHTML()
    return render_template('index.html', exchange_table=exchange_table);

if  __name__ == "__main__":
    app.run(debug=True)
