from epypes.graph import Digraph, DirectedCycle, DepthFirstOrder

# Graph example from "Cycles and DAGs" (p. 574), Chapter 4 of
# "Algorithms", 4th Edition by Robert Sedgewick and Kevin Wayne

EDGES_SEDGEWICK = (
    (0, 1),
    (0, 5),
    (0, 6),
    (2, 0),
    (2, 3),
    (3, 5),
    (5, 4),
    (6, 4),
    (6, 9),
    (7, 6),
    (8, 7),
    (9, 10),
    (9, 11),
    (9, 12),
    (11, 12)
)

EDGES_SEDGEWICK_WITH_CYCLE = EDGES_SEDGEWICK + ((4, 0), )

DEPENDECIES_SEDGEWICK = {
    
    0: (2, ),
    1: (0, 2),
    2: tuple(),
    3: (2, ), 
    4: (0, 2, 3, 5, 6, 7, 8),
    5: (0, 2, 3),
    6: (8, 7),
    7: (8, ),
    8: tuple(),
    9: (6, 7, 8),
    10: (6, 7, 8, 9),
    11: (6, 7, 8, 9),
    12: (6, 7, 8, 9, 11),
}


def has_cycle(g):
    cycle_finder = DirectedCycle(g)
    return cycle_finder.has_cycle()


def order_ok(order, dependecies_spec):
    
    for i, entry in enumerate(order):

        set_before = set(order[:i])
        
        for dep in dependecies_spec[entry]:
            if dep not in set_before:
                return False
            
    return True


def test_cycle_detection():

    vertices = list(range(13))
    g = Digraph(vertices, EDGES_SEDGEWICK)
    g_with_cycle = Digraph(vertices, EDGES_SEDGEWICK_WITH_CYCLE)
    
    assert not has_cycle(g)
    assert has_cycle(g_with_cycle)


def test_topological_sort():

    vertices = list(range(13))
    g = Digraph(vertices, EDGES_SEDGEWICK)

    dfo = DepthFirstOrder(g)

    assert order_ok(dfo.topological_order, DEPENDECIES_SEDGEWICK)
