import numpy as np

class ArbitrageAlgorithms:

    digraph = None
    log_digraph = None #version of digraph with -log(weight) edge-weights

    def __init__(self, digraph):
        self.digraph = digraph
        self.log_digraph = self.__convert_currency_weights_to_logs(digraph.copy())

    def __modified_bellman_ford(self, start_vertex):
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
        all_neg_cycles = []
        vertices = self.log_digraph.nodes()
        for vertex in vertices:
            neg_cycles = self.__modified_bellman_ford(vertex)
            for cycle in neg_cycles:
                if cycle not in all_neg_cycles:
                    all_neg_cycles.append(cycle)
        return all_neg_cycles

    def __convert_currency_weights_to_logs(self, digraph):
        for (node1, node2) in digraph.edges():
            edge_weight = digraph[node1][node2]["weight"]
            try:
                digraph[node1][node2]["weight"] = -np.log(edge_weight)
            except:
                digraph[node1][node2]["weight"] = 0
        return digraph

    def run_arbitrage(self):
        paths = []
        #find all negative cycles in the graph
        negative_cycles = self.__run_bellman_ford_all_vertices()
        #calculate arbitrage for each negative cycle
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
        arbitrage_currencies = set()
        negative_cycles = self.__run_bellman_ford_all_vertices()
        for cycle in negative_cycles:
            for currency in cycle:
                arbitrage_currencies.add(currency)
        return arbitrage_currencies
