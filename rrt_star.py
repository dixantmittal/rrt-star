import numpy as np
import networkx as nx
from utils import *
from commons import *
from tqdm import tqdm

"""performance is deeply affected by granularity, d_threshold and ball radius, so choose the values according to the 
use case > more ball_radius = better path and more computation time > less granularity = finer check for collision 
and more computation time > more the d_threshold, more rapidly it will explore the space, may result in more 
collisions. """


def apply_rrt_star(space_region, starting_state, target_region, obstacle_map, n_samples=1000, granularity=0.1,
                   d_threshold=0.5):
    tree = nx.DiGraph()
    tree.add_node(starting_state)

    space_dim = len(starting_state)

    final_state = None

    # cost for each vertex
    cost = {starting_state: 0}

    # calculate constant factor
    gamma = 1 + np.power(2, space_dim) * (1 + 1.0 / space_dim) * get_free_area(space_region, obstacle_map)

    for i in tqdm(range(n_samples)):

        # select node to expand
        m_g, random_point = select_node_to_expand(tree, space_region)

        # sample a new point
        m_new = sample_new_point_unconstrained(m_g, random_point, d_threshold)

        # check if m_new lies in space_region
        if not lies_in_area(m_new, space_region):
            continue

        # if m_new is not collision free, sample any other point
        if not is_collision_free(m_g, m_new, obstacle_map, granularity):
            continue

        # find k nearest neighbours
        radius = np.minimum(np.power(gamma / volume_of_unit_ball[space_dim] * np.log(i + 1) / (i + 1),
                                     1 / space_dim), d_threshold)
        m_near = nearest_neighbours(list(tree.nodes), m_new, radius=radius)

        min_cost = m_g
        d_min_cost = cartesian_distance(m_g, m_new)

        # look for shortest cost path to m_new
        for m_g in m_near:

            # find the cost for m_new through m_g
            d = cartesian_distance(m_g, m_new)
            c = cost[m_g] + d

            # if cost is less than current lowest cost, that means m_new to m_g could be a potential link
            if c < cost[min_cost] + d_min_cost:

                # check if path between(m_g,m_new) defined by motion-model is collision free
                is_free = is_collision_free(m_g, m_new, obstacle_map, granularity)

                # if path is free, update the minimum distance
                if is_free:
                    min_cost = m_g
                    d_min_cost = d

        tree.add_weighted_edges_from([(min_cost, m_new, d_min_cost)])
        cost[m_new] = cost[min_cost] + d_min_cost

        # update m_new's neighbours for paths through m_new
        for m_g in m_near:

            # find the cost for m_g through m_new
            d = cartesian_distance(m_g, m_new)
            c = cost[m_new] + d

            # if cost is less than current cost, that means m_new to m_g could be a potential link
            if c < cost[m_g]:
                # check if path between(m_g,m_new) is collision free
                is_free = is_collision_free(m_g, m_new, obstacle_map, granularity)

                # if path is free, update the links
                if is_free:
                    tree.remove_edge(list(tree.predecessors(m_g))[0], m_g)
                    tree.add_weighted_edges_from([(m_new, m_g, d)])
                    cost[m_g] = c

        # if target is reached, return the tree and final state
        if lies_in_area(m_new, target_region):
            print('Target reached at i:', i)
            if final_state is None:
                final_state = m_new
            elif cost[m_new] < cost[final_state]:
                final_state = m_new

    if final_state is None:
        print("Target not reached.")
    return tree, final_state
