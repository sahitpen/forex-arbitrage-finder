import numpy as np

class ArbitrageAlgorithms:
    """
    This class handles calculations of arbitrage paths using a modified
    bellman ford algorithm.
    """
    digraph = None
    log_digraph = None  # version of digraph with -log(weight) edge weights

    def __init__(self, digraph):
        """
        Class constructor that initializes the digraph and log_digraph variables.
        """
        self.digraph = digraph
        self.log_digraph = self.__convert_currency_weights_to_logs(digraph.copy())

    def __modified_bellman_ford(self, start_vertex):
        """
        This method finds and returns a list of negative cycles in the
        log_digraph from an inputed start vertex.
        """
        distances = dict()
        previous = dict()
        vertices = self.log_digraph.nodes()
        edges = self.log_digraph.edges()
        neg_cycles = []
        discovered = dict()

        for vertex in vertices:
            discovered[vertex] = False

        for vertex in vertices:
            distances[vertex] = float('inf')
            previous[vertex] = None

        distances[start_vertex] = 0

        for vertex in range (len(vertices)-1):
            for (vertex1, vertex2) in edges:
                edge_weight = self.log_digraph[vertex1][vertex2]["weight"]
                if distances[vertex2] > distances[vertex1] + edge_weight:
                    distances[vertex2] = distances[vertex1] + edge_weight
                    previous[vertex2] = vertex1

        for (vertex1, vertex2) in edges:
            edge_weight = self.log_digraph[vertex1][vertex2]["weight"]
            if not discovered[vertex2]:
                if distances[vertex2] > distances[vertex1] + edge_weight:
                    # A negative cycle exists if we get here, now we must trace it back
                    temp = vertex2
                    cycle = []
                    cycle.append(temp)
                    discovered[temp] = True
                    temp = previous[temp]

                    while (temp not in cycle and temp != vertex2):
                        cycle.append(temp)
                        discovered[temp] = True
                        temp = previous[temp]

                    temp_pos = cycle.index(temp)
                    cycle.append(temp)
                    cycle = cycle[temp_pos::]
                    cycle.reverse()
                    neg_cycles.append(cycle)

        return neg_cycles

    def __run_bellman_ford_all_vertices(self):
        """
        This method runs the modified bellman ford algorithm on every vertex in
        the log_digraph, returning a list of all negative cycles in the graph.
        """
        all_neg_cycles = []
        vertices = self.log_digraph.nodes()
        for vertex in vertices:
            neg_cycles = self.__modified_bellman_ford(vertex)
            for cycle in neg_cycles:
                if cycle not in all_neg_cycles:
                    all_neg_cycles.append(cycle)
        return all_neg_cycles

    def __convert_currency_weights_to_logs(self, digraph):
        """
        This is a helper method used to change every edge weight in an
        inputed digraph to -log(original-weight).
        """
        for (node1, node2) in digraph.edges():
            edge_weight = digraph[node1][node2]["weight"]
            try:
                digraph[node1][node2]["weight"] = -np.log(edge_weight)
            except:
                digraph[node1][node2]["weight"] = 0
        return digraph

    def run_arbitrage(self):
        """
        This method iterates through all the negative cycles found and calculates
        the arbitrage profit percentage for each cycle. It returns a list of
        paths which contains tuples (cycle, percentage_gain). It also prints
        out the arbitrage path and profit percentage to the command line.
        """
        paths = []
        # find all negative cycles in the graph
        negative_cycles = self.__run_bellman_ford_all_vertices()
        # calculate arbitrage for each negative cycle
        for cycle in negative_cycles:
            total = 1
            for i in range(len(cycle)-1):
                curr1 = cycle[i]
                curr2 = cycle[i+1]
                exchange_rate = self.digraph[curr1][curr2]["weight"]
                total *= exchange_rate
                print(curr1, "->", curr2, ": exchange rate - ", exchange_rate)
            percentage_gain = (total-1)*100
            paths.append((cycle, percentage_gain))
            print("COMPLETE PATH: ", cycle, ": ", (total-1)*100, "% gain\n");
        return paths

    def get_arbitrage_currencies(self):
        """
        This method returns a list of all currencies involved in one or more
        calculated arbitrage opportunities.
        """
        arbitrage_currencies = set()
        negative_cycles = self.__run_bellman_ford_all_vertices()
        for cycle in negative_cycles:
            for currency in cycle:
                arbitrage_currencies.add(currency)
        return arbitrage_currencies
