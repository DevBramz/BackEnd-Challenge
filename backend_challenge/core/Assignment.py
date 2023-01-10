from ortools.sat.python import cp_model
from geopy.distance import great_circle, geodesic


def main():
    xy_list = [
    (-1.283922, 36.798107),  # Kilimani 0
    (-1.393864, 36.744238),  # RONGAI 1
    (-1.205604, 36.779606),  # RUAKA 2
    (-1.366859, 36.728069),  # langata 3
    (-1.311752, 36.698598),  # karen1  4
    (-1.3362540729230734, 36.71637587249404),  # karen2 5
    (-1.1752106333542798, 36.75964771015464),  # Banana1 6
    (-1.1773237686269944, 36.760334355612045),  # Banana2 7
]  #
    def compute_cost_matrix(self):
        """computes the distance matrix by using geopy"""
      
        waypoints = xy_list
        distance_matrix = [
            [(int(geodesic(p1, p2).miles)) for p2 in waypoints] for p1 in waypoints
        ]
        return distance_matrix 
    
    # def compute_cost_matrix(self, overall_locations):
    #     """ This computes the distance matrix by using GOOGLE MATRIX API """
    #     response = self.gmaps.distance_matrix(
    #         overall_locations[0:], overall_locations[0:], mode="driving"
    #     )
    #     distance_matrix = np.zeros((len(overall_locations), len(overall_locations)))
    #     for index in range(1, len(overall_locations)):
    #         for idx in range(1, len(overall_locations)):
    #             distance_matrix[index, idx] = response["rows"][index - 1]["elements"][
    #                 idx - 1
    #             ]["distance"]["value"]

        return distance_matrix
    # Data
    costs = [
        [15, 15, 15, 15],
        [35, 35, 35, 35],
        [45, 45, 40, 45],
        [110, 110, 110, 110],
        [50, 50, 50, 50],
    ]# distance matrix
    num_workers = len(costs)
    num_tasks = len(costs[0])

    # Model
    model = cp_model.CpModel()

    # Variables
    x = []
    for i in range(num_workers):
        t = []
        for j in range(num_tasks):
            t.append(model.NewBoolVar(f'x[{i},{j}]'))
        x.append(t)

    # Constraints
    # Each worker is assigned to at most one task.
    for i in range(num_workers):
        model.AddAtMostOne(x[i][j] for j in range(num_tasks))

    # Each task is assigned to exactly one worker.
    for j in range(num_tasks):
        model.AddExactlyOne(x[i][j] for i in range(num_workers))

    # Objective
    objective_terms = []
    for i in range(num_workers):
        for j in range(num_tasks):
            objective_terms.append(costs[i][j] * x[i][j])
    model.Minimize(sum(objective_terms))

    # Solve
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # Print solution.
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print(f'Total cost = {solver.ObjectiveValue()}')
        print()
        for i in range(num_workers):
            for j in range(num_tasks):
                if solver.BooleanValue(x[i][j]):
                    print(
                        f'Worker {i} assigned to task {j} Cost = {costs[i][j]}')
    else:
        print('No solution found.')


]