import numpy as np
import networkx as nx
from utils import *
from commons import *
from control_functions import *
from state_generators import *
from tqdm import tqdm


def apply_rrt_nh(space_region, starting_state, target_region, obstacle_map, granularity=0.1, dt=0.5,
                 n_samples=1000, find_optimal=True):
    tree = nx.DiGraph()
    tree.add_node(starting_state)

    final_state = None

    min_cost = None

    # TODO
    # > expand obstacles for car
    # > add padding for velocity


    for i in tqdm(range((n_samples))):
        # select node to expand
        m_g, random_point = select_node_to_expand(tree, space_region)

        # sample a new point
        m_new, controls = sample_new_point_with_control(m_g, dt, velocity_and_steering_angle,
                                                        generate_using_velocity_and_steering_angle)

        # check if m_new lies in space_region
        if not lies_in_area(m_new, space_region):
            continue

        # check if path between(m_g,m_new) defined by motion-model is collision free
        is_free = is_collision_free(m_g, m_new, obstacle_map, granularity)

        # if path is free, add new node to tree
        if is_free:
            tree.add_weighted_edges_from([(m_g, m_new, cartesian_distance(m_g, m_new))])
            if lies_in_area(m_new, target_region):
                print('Target reached at i:', i)
                if min_cost is None:
                    final_state = m_new
                    if not find_optimal:
                        break
                    break
                else:
                    # if new final state has shorter cost, set it as final state
                    cost = nx.shortest_path_length(tree, starting_state, m_new)
                    if cost < min_cost:
                        final_state = m_new
                        min_cost = cost

    if final_state is None:
        print("Target not reached.")
    return tree, final_state
