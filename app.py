from flask import Flask, render_template, request
from arbitrage_algos import ArbitrageAlgorithms
from visualization import GraphVisualization
from forex_scraper import ForexScraper

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route("/", methods=['POST'])
def run_arbitrage_program():
    # RETRIEVE DATE USER INPUT
    date = request.form['date']
    if date is None or date == "" or date == "now" or date == "today":
        date = "latest"
    ## RUN THE FOREX SCRAPER AND CREATE ADJACENCY MATRIX & EXCHANGE TABLE WITH CURRENCIES
    # 2017-07-23 is good test date
    scraper = ForexScraper(date)
    adjacency_matrix = scraper.get_adjacency_matrix()
    exchange_table = scraper.get_exchange_table_html()

    ## CREATE GRAPH VISUALIZATION OF ALL RETRIEVED CURRENCIES/EXCHANGE RATES
    visualization = GraphVisualization()
    digraph = visualization.create_graph_from_dataframe(adjacency_matrix)
    visualization.draw_graph(digraph, output_file="all_vertices_digraph.png", size="small", edge_weights=False)

    ## FIND ARBITRAGE OPPORTUNITIES ON THE GRAPH
    arbitrage = ArbitrageAlgorithms(digraph)
    paths = arbitrage.run_arbitrage()
    path_string, percentage_string = format_paths(paths)

    ## CREATE NEW ADJACENCY MATRIX USING ONLY CURRENCIES INVOLVED IN ARBITRAGE OPPORTUNITIES
    # get a list of all currencies involved in one or more arbitrage opportunities
    arbitrage_currencies = arbitrage.get_arbitrage_currencies()
    # create a list of all currencies NOT involved any arbitrage opportunities
    currency_set = set(scraper.get_currency_list())
    no_arbitrage_currencies = currency_set.difference(arbitrage_currencies)
    # create a new adjancey matrix with only the currencies involved in one or more arbitrage opportunities
    filtered_adj_matrix = adjacency_matrix.copy()
    filtered_adj_matrix = filtered_adj_matrix.drop(index=no_arbitrage_currencies, columns=no_arbitrage_currencies)

    ## CREATE GRAPH VISUALIZATION OF CURRENCIES/EXCHANGE RATES INVOLVED IN ARBITRAGE OPPORTUNITIES
    filtered_digraph = visualization.create_graph_from_dataframe(filtered_adj_matrix)
    visualization.draw_graph(filtered_digraph, output_file="filtered_digraph.png", size="large", edge_weights=True)

    return render_template('index.html', paths=path_string, percentage_gains=percentage_string,
                            exchange_table=exchange_table, date="("+date+")");

# method to format paths into a displayable string with currency emojis
def format_paths(paths):
    path_string = ""
    percentage_string = ""
    for path, percentage in paths:
        percentage_string += "+ " +str(percentage) + "% profit<br/>"
        for currency in path[:-1]:
            path_string += ForexScraper.currency_flags[currency] + " " +currency + " ⟶ "
        path_string += ForexScraper.currency_flags[path[-1]] + " " +path[-1]
        path_string += "<br/>"
    return (path_string, percentage_string)

if  __name__ == "__main__":
    app.run(debug=True)
