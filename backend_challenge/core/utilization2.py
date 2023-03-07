import numpy as np
import cvxpy as cvx
from timeit import default_timer as time

# Data
def utilize():
    order_vols = [8, 4, 12, 18, 5, 2, 1, 4]
    order_weights = [5, 3, 2, 5, 3, 4, 5, 6]

    box_vol = 20
    box_weight = 12

    N_ITEMS = len(order_vols)
    max_n_boxes = len(order_vols) # real-world: heuristic?

    """ Optimization """
    M = N_ITEMS + 1

    # VARIABLES
    box_used = cvx.Variable(max_n_boxes, boolean=True)
    box_vol_content = cvx.Variable(max_n_boxes)
    box_weight_content = cvx.Variable(max_n_boxes)
    box_item_map = cvx.Variable((max_n_boxes, N_ITEMS), boolean=True)

    # CONSTRAINTS
    cons = []

    # each item is shipped once
    cons.append(cvx.sum(box_item_map, axis=0) == 1)

    # box is used when >=1 item is using it
    cons.append(box_used * M >= cvx.sum(box_item_map, axis=1))

    # box vol constraints
    cons.append(box_item_map * order_vols <= box_vol)

    # box weight constraints
    cons.append(box_item_map * order_weights <= box_weight)

    problem = cvx.Problem(cvx.Minimize(cvx.sum(box_used)), cons)
    start_t = time()
    problem.solve(solver='CBC', verbose=True)
    end_t = time()
    print('time used (cvxpys reductions & solving): ', end_t - start_t)
    print(problem.status)
    print(problem.value)
    print(box_item_map.value)

    """ Reconstruct solution """
    n_boxes_used = int(np.round(problem.value))
    box_inds_used = np.where(np.isclose(box_used.value, 1.0))[0]

    print('N_BOXES USED: ', n_boxes_used)
    for box in range(n_boxes_used):
        print('Box ', box)
        raw = box_item_map[box_inds_used[box]]
        items = np.where(np.isclose(raw.value, 1.0))[0]
        vol_used = 0
        weight_used = 0
        for item in items:
            print('   item ', item)
            print('       vol: ', order_vols[item])
            print('       weight: ', order_weights[item])
            vol_used += order_vols[item]
            weight_used += order_weights[item]
        print(' total vol: ', vol_used)
        print(' total weight: ', weight_used)
        return weight_used
    
    
    
    # https://groups.google.com/g/or-tools-discuss/c/gMgPBryj1wA
    # https://groups.google.com/g/or-tools-discuss/c/VGeLbk-diWU
    # https://www.vanderwaal.eu/mini-projecten/google-maps-animated-polyline