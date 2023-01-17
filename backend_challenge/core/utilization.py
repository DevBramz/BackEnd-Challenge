from ortools.linear_solver import pywraplp
from .exceptions import RoutingException


class Packing:
    deliveries = []
    bin_capacity = 0
    drivers = []

    def __init__(self, de, d):
        self.deliveries, self.drivers = de, d

    def create_data_model(self):
        """Create the data for the example."""
        data = {}
        drivers_dict = self.drivers.values()
        # print(drivers_dict)
        # weights = list(self.deliveries.values_list("weight", flat=True))
        weights = list(self.deliveries.values_list("weight", flat=True))
        print(weights)
        data["weights"] = weights

        data["items"] = list(range(len(weights)))
        capacities = [driver["capacity"] for driver in drivers_dict]
        data["bins"] = list(range(len(capacities)))  # data['items']
        data["bin_capacities"] = capacities
        # data['bins'] = data['items']
        # data['bin_capacity'] = [100, 30,]
        # print(data['bin_capacity'])

        return data

    def main(self):
        data = self.create_data_model()

        # Create the mip solver with the SCIP backend.
        solver = pywraplp.Solver.CreateSolver("SCIP")

        if not solver:
            return

        # Variables
        # x[i, j] = 1 if item i is packed in bin j.
        x = {}
        for i in data["items"]:
            for j in data["bins"]:
                x[(i, j)] = solver.IntVar(0, 1, "x_%i_%i" % (i, j))

        # y[j] = 1 if bin j is used.
        y = {}
        for j in data["bins"]:
            y[j] = solver.IntVar(0, 1, "y[%i]" % j)

        # Constraints
        # Each item must be in exactly one bin.
        for i in data["items"]:
            solver.Add(sum(x[i, j] for j in data["bins"]) == 1)

        # The amount packed in each bin cannot exceed its capacity.
        for j in data["bins"]:
            solver.Add(
                sum(x[(i, j)] * data["weights"][i] for i in data["items"])
                <= y[j] * data["bin_capacities"][j]
            )

        # Objective: minimize the number of bins used.
        solver.Minimize(solver.Sum([y[j] for j in data["bins"]]))

        status = solver.Solve()

        if status == pywraplp.Solver.OPTIMAL:
            drivers_dict = self.drivers.values()
            num_bins = 0
            bins_used = []
            for j in data["bins"]:
                if y[j].solution_value() == 1:
                    # self.drivers.objects.get(id=)
                    driver_id=drivers_dict[j]["id"]
                    bins_used.append(driver_id)
                    
                    bin_items = []
                    bin_weight = 0
                    for i in data["items"]:
                        if x[i, j].solution_value() > 0:
                            bin_items.append(i)
                            bin_weight += data["weights"][i]
                    if bin_items:
                        num_bins += 1
                        print("Bin number", j)
                        # print("  Items packed:", bin_items)
                        # print("  Total weight:", bin_weight)
                        # print()
            print(bins_used)
            print("Number of bins used:", num_bins)
            # print("Time = ", solver.WallTime(), " milliseconds")
            
            return bins_used
        else:
            raise RoutingException
