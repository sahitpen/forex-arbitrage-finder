import json
import urllib.request, urllib.parse, urllib.error
import pandas as pd
import numpy as np
import ssl

class ForexScraper:
    """
    This class is used to pull exchange rate information for a specified date
    from http://api.exchangeratesapi.io/ and store the results in an adjacency
    matrix.
    """
    adjacency_matrix = None
    currency_list = None
    currency_flags = { "CAD": "🇨🇦", "HKD": "🇭🇰", "ISK": "🇮🇸", "PHP": "🇵🇭",
                       "DKK": "🇩🇰", "HUF": "🇭🇺", "CZK": "🇨🇿", "GBP": "🇬🇧",
                       "RON": "🇷🇴", "SEK": "🇸🇪", "IDR": "🇮🇩", "INR": "🇮🇳",
                       "BRL": "🇧🇷", "RUB": "🇷🇺", "HRK": "🇭🇷", "JPY": "🇯🇵",
                       "THB": "🇹🇭", "CHF": "🇨🇭", "EUR": "🇪🇺", "MYR": "🇲🇾",
                       "BGN": "🇧🇬", "TRY": "🇹🇷", "CNY": "🇨🇳", "NOK": "🇳🇴",
                       "NZD": "🇳🇿", "ZAR": "🇿🇦", "USD": "🇺🇸", "MXN": "🇲🇽",
                       "SGD": "🇸🇬", "AUD": "🇦🇺", "ILS": "🇮🇱", "KRW": "🇰🇷",
                       "PLN": "🇵🇱" }

    def __init__(self, date):
        """
        Constructor that, given a date, initializes the list of currencies used,
        creates the adjacency_matrix and creates a CSV file from the matrix.
        """
        self.currency_list = self.create_currency_list(date)
        self.create_adjacency_matrix(date)
        self.create_csv_from_adjacency_matrix()

    def create_currency_list(self, date):
        """
        Method that returns an initial list of currencies we want to use.
        """
        currency_list = []
        json_obj = self.get_exchange_rate_json_from_api(date=date)
        if json_obj is None:
            return currency_list
        exchange_dict = json_obj["rates"]
        for symbol in exchange_dict:
            currency_list.append(symbol)
        return currency_list

    def create_adjacency_matrix(self, date):
        """"
        Method that pulls exchange rates from the API and stores the results
        in an adjacency_matrix.
        """
        # initialize adjacency matrix with 0s with the columns/rows as the currencies in currency_list
        num_currencies = len(self.currency_list)
        self.adjacency_matrix = pd.DataFrame(np.zeros(shape=(num_currencies, num_currencies)),
                                                      columns=self.currency_list, index=self.currency_list)
        # obtain exchange rate between every currency in the matrix and update value in matrix
        for base_symbol in self.currency_list:
            json_obj = self.get_exchange_rate_json_from_api(date=date, base=base_symbol)
            if json_obj is None:
                continue
            exchange_dict = None
            if "rates" in json_obj:
                exchange_dict = json_obj["rates"]
            if exchange_dict is None:
                continue
            for exchange_symbol in exchange_dict:
                try:
                    exchange_rate = exchange_dict[exchange_symbol]
                    self.adjacency_matrix[exchange_symbol][base_symbol] = exchange_rate
                except:
                    print("Couldn't obtain exchange rate for ", exchange_symbol)
        # handle API bug where EUR symbol doesn't return the exchange for itself
        if "EUR" in self.adjacency_matrix:
            if "EUR" in self.adjacency_matrix["EUR"]:
                self.adjacency_matrix["EUR"]["EUR"] = 1

    def get_exchange_rate_json_from_api(self, date, base="USD"):
        """
        This method accesses the API and returns a JSON object for a given
        currency and date.
        """
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        url = "http://api.exchangeratesapi.io/" +date +"?base=" +base
        json_obj = None
        try :
            connection = urllib.request.urlopen(url, context=context)
            json_obj = json.loads(connection.read())
        except:
            print("Error retrieving information from API")
        return json_obj

    def create_csv_from_adjacency_matrix(self):
        """
        This method creates and saves a CSV file from the adjacency_matrix.
        """
        if  self.adjacency_matrix is not None:
            self.adjacency_matrix.to_csv("forex_exchange_matrix.csv")

    def get_exchange_table_html(self):
        """
        This method returns the HTML content for the adjacency_matrix.
        """
        return self.adjacency_matrix.to_html()

    def get_adjacency_matrix(self):
        """
        This method returns the adjacency_matrix.
        """
        return self.adjacency_matrix

    def get_currency_list(self):
        """
        This method returns the currency_list.
        """
        return self.currency_list
