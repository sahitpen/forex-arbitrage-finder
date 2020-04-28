import json
import urllib.request, urllib.parse, urllib.error
import ssl
import pandas as pd
import numpy as np
from arbitrage_algos import ArbitrageAlgorithms
from visualization import GraphVisualization

class ForexScraper:
    # Ignore SSL certificate errors
    #ctx = ssl.create_default_context()
    #ctx.check_hostname = False
    #ctx.verify_mode = ssl.CERT_NONE

    # startSymbolsParam = "USD"
    # convertSymbolsParam = "ETH,DASH,EUR,BNB,BTC,SOL,LINK,XMR,XTZ,XRP,WTC,ENJ,LTC"
    # apiKeyParam = "6fb8973a560906b569b9cc10a7af360d2a61279a5d692368d61a977d334bf9de"
    # cryptocompareUrl = 'https://min-api.cryptocompare.com/data/pricemulti?'+'fsyms=' +startSymbolsParam +'&tsyms=' +convertSymbolsParam+'&api_key=' +apiKeyParam

    # USE THIS API INSTEAD
    # https://exchangeratesapi.io/

    # PROGRAM DESIGN
    # CLASS W CONSTRUCTOR AND FUNCS THAT HANDLES RETRIEVING FOREX DATA FROM API AND FORMATTING INTO A 2D MATRIX
    # CLASS W CONSTRUCTOR AND FUNCS THAT TAKES IN MATRIX AND CREATES VISUAL GRAPH
    # CLASS W CONSTRUCTOR AND FUNCS THAT HANDLES ALL ARBITRAGE FINDING ALGORITHMS
    # CLASS WITH MAIN METHOD THAT RUNS ALL ABOVE 3 CLASSES WITH USER INPUT

    # CREATE A METHOD TO HANDLE THIS PART
    #get the initial list of currencies we want to use
    currencyList = []
    url = "http://api.exchangeratesapi.io/2017-07-23?base=USD"
    connection = urllib.request.urlopen(url)#, context=ctx)
    jsonObj = json.loads(connection.read())

    exchangeDict = jsonObj["rates"]
    for symbol in exchangeDict:
        currencyList.append(symbol)

    # CREATE A METHOD TO HANDLE THIS PART
    #create an matrix initially filled with 0s with the columns/rows as the currencies in currencyList
    numCurrencies = len(currencyList)
    adjacencyMatrix = pd.DataFrame(np.zeros(shape=(numCurrencies,numCurrencies)),
                      columns=currencyList, index=currencyList)
    # obtain exchange rate between every currency in the matrix and update value in matrix
    # TO-DO: add error handling, try-catch, etc
    for baseSymbol in currencyList:
        # CREATE A METHOD TO DO API CALLS
        url = "http://api.exchangeratesapi.io/2017-07-23?base=" +baseSymbol
        connection = urllib.request.urlopen(url)#, context=ctx)
        jsonObj = json.loads(connection.read())
        exchangeDict = jsonObj["rates"]
        for exchangeSymbol in exchangeDict:
            try:
                exchangeRate = exchangeDict[exchangeSymbol]
                adjacencyMatrix[exchangeSymbol][baseSymbol] = exchangeRate
            except:
                print("Couldn't obtain exchange rate for ", exchangeSymbol)

    #handle API bug where EUR symbol doesn't return the exchange for itself
    #TO-DO: add error handling
    adjacencyMatrix["EUR"]["EUR"] = 1

    # CREATE A METHOD TO HANDLE THIS PART
    #create a CSV file from this adjacencyMatrix for reference later
    adjacencyMatrix.to_csv("forex_exchange_matrix.csv")

    # CREATE A METHOD TO HANDLE THIS PART
    #plot adjacencyMatrix as a digraph
    visualization = GraphVisualization()
    digraph = visualization.create_graph_from_dataframe(adjacencyMatrix)
    visualization.draw_graph(digraph, output_file="all_vertices_digraph.png", size="small", edge_weights=False)

    arbitrage = ArbitrageAlgorithms(digraph)
    arbitrage.run_arbitrage()

    # get a list of all currencies involved in one or more arbitrage opportunities
    arbitrage_currencies = arbitrage.get_arbitrage_currencies()
    # create a list of all currencies NOT involved any arbitrage opportunities
    currencySet = set(currencyList)
    no_arbitrage_currencies = currencySet.difference(arbitrage_currencies)
    # create a new adjancey matrix with only the currencies involved in one or more arbitrage opportunities
    filtered_adj_matrix = adjacencyMatrix.copy()
    filtered_adj_matrix = filtered_adj_matrix.drop(index=no_arbitrage_currencies, columns=no_arbitrage_currencies)

    #filtered_digraph = visualization.create_graph_from_dataframe(filtered_adj_matrix)
    #visualization.draw_graph(filtered_digraph, output_file="filtered_digraph.png", size="large", edge_weights=True)

    def getExchangeTableHTML(self):
        return self.adjacencyMatrix.to_html()
