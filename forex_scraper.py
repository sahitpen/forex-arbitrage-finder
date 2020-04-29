import json
import urllib.request, urllib.parse, urllib.error
import pandas as pd
import numpy as np

class ForexScraper:

    adjacency_matrix = None
    currency_list = None

    def __init__(self):
        self.currency_list = self.create_currency_list()
        self.create_adjacency_matrix()
        self.create_csv_from_adjacency_matrix()

    #get the initial list of currencies we want to use
    def create_currency_list(self):
        currency_list = []
        url = "http://api.exchangeratesapi.io/2017-07-23?base=USD"
        connection = urllib.request.urlopen(url)
        json_obj = json.loads(connection.read())

        exchange_dict = json_obj["rates"]
        for symbol in exchange_dict:
            currency_list.append(symbol)
        return currency_list

    def create_adjacency_matrix(self):
        # initialize adjacency matrix with 0s with the columns/rows as the currencies in currency_list
        num_currencies = len(self.currency_list)
        self.adjacency_matrix = pd.DataFrame(np.zeros(shape=(num_currencies, num_currencies)),
                                                      columns=self.currency_list, index=self.currency_list)
        # obtain exchange rate between every currency in the matrix and update value in matrix
        # TO-DO: add error handling, try-catch, etc
        for base_symbol in self.currency_list:
            # CREATE A METHOD TO DO API CALLS
            url = "http://api.exchangeratesapi.io/2017-07-23?base=" +base_symbol
            connection = urllib.request.urlopen(url)
            json_obj = json.loads(connection.read())
            exchange_dict = json_obj["rates"]
            for exchange_symbol in exchange_dict:
                try:
                    exchange_rate = exchange_dict[exchange_symbol]
                    self.adjacency_matrix[exchange_symbol][base_symbol] = exchange_rate
                except:
                    print("Couldn't obtain exchange rate for ", exchange_symbol)
        #handle API bug where EUR symbol doesn't return the exchange for itself
        if "EUR" in self.adjacency_matrix:
            if "EUR" in self.adjacency_matrix["EUR"]:
                self.adjacency_matrix["EUR"]["EUR"] = 1

    def create_csv_from_adjacency_matrix(self):
        if  self.adjacency_matrix is not None:
            self.adjacency_matrix.to_csv("forex_exchange_matrix.csv")

    def get_exchange_table_html(self):
        return self.adjacency_matrix.to_html()

    def get_adjacency_matrix(self):
        return self.adjacency_matrix

    def get_currency_list(self):
        return self.currency_list
