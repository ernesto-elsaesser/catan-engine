from __future__ import annotations

TILE_NODES = {
    "A1": ["A1A", "A1B", "A2A", "B2B", "B2A", "B1B"],
    "A2": ["A2A", "A2B", "A3A", "B3B", "B3A", "B2B"],
    "A3": ["A3A", "A3B", "A3C", "B4B", "B4A", "B3B"],

    "B1": ["B1A", "B1B", "B2A", "C2B", "C2A", "C1B"],
    "B2": ["B2A", "B2B", "B3A", "C3B", "C3A", "C2B"],
    "B3": ["B3A", "B3B", "B4A", "C4B", "C4A", "C3B"],
    "B4": ["B4A", "B4B", "B4C", "C5B", "C5A", "C4B"],

    "C1": ["C1A", "C1B", "C2A", "D1B", "D1A", "C1D"],
    "C2": ["C2A", "C2B", "C3A", "D2B", "D2A", "D1B"],
    "C3": ["C3A", "C3B", "C4A", "D3B", "D3A", "D2B"],
    "C4": ["C4A", "C4B", "C5A", "D4B", "D4A", "D3B"],
    "C5": ["C5A", "C5B", "C5C", "C5F", "D4C", "D4B"],

    "D1": ["D1A", "D1B", "D2A", "E1B", "E1A", "D1D"],
    "D2": ["D2A", "D2B", "D3A", "E2B", "E2A", "E1B"],
    "D3": ["D3A", "D3B", "D4A", "E3B", "E3A", "E2B"],
    "D4": ["D4A", "D4B", "D4C", "D4F", "E3C", "E3B"],

    "E1": ["E1A", "E1B", "E2A", "E2D", "E1E", "E1D"],
    "E2": ["E2A", "E2B", "E3A", "E3D", "E2E", "E2D"],
    "E3": ["E3A", "E3B", "E3C", "E3F", "E3E", "E3D"],
}

NODE_EDGES = {
    "A1A": ["A1a", "A1b"],
    "A1B": ["A1b", "A1c"],
    "A2A": ["A2a", "A2b", "A1c"],
    "A2B": ["A2b", "A2c"],
    "A3A": ["A3a", "A3b", "A2c"],
    "A3B": ["A3b", "A3c"],
    "A3C": ["A3c", "A3f"],

    "B1A": ["B1a", "B1b"],
    "B1B": ["B1b", "B1c", "A1a"],
    "B2A": ["B1c", "B2a", "B2b"],
    "B2B": ["B2b", "B2c", "A2a"],
    "B3A": ["B2c", "B3b", "B3a"],
    "B3B": ["B3b", "B3c", "A3a"],
    "B4A": ["B3c", "B4b", "B4a"],
    "B4B": ["B4b", "B4c", "A3f"],
    "B4C": ["B4c", "B4f"],

    "C1A": ["C1a", "C1b"],
    "C1B": ["C1b", "C1c", "B1a"],
    "C2A": ["C1c", "C2b", "C2a"],
    "C2B": ["C2b", "C2c", "B2a"],
    "C3A": ["C2c", "C3b", "C3a"],
    "C3B": ["C3b", "C3c", "B3a"],
    "C4A": ["C3c", "C4b", "C4a"],
    "C4B": ["C4b", "C4c", "B4a"],
    "C5A": ["C4c", "C5b", "C5a"],
    "C5B": ["C5b", "C5c", "B4f"],
    "C5C": ["C5c", "C5f"],

    "C1D": ["C1a", "C1d"],
    "D1A": ["C1d", "D1b", "D1a"],
    "D1B": ["D1b", "D1c", "C2a"],
    "D2A": ["D1c", "D2b", "D2a"],
    "D2B": ["D2b", "D2c", "C3a"],
    "D3A": ["D2c", "D3b", "D3a"],
    "D3B": ["D3b", "D3c", "C4a"],
    "D4A": ["D3c", "D4b", "D4a"],
    "D4B": ["D4b", "D4c", "C5a"],
    "D4C": ["D4c", "C5e", "D4f"],
    "C5F": ["C5e", "C5f"],

    "D1D": ["D1a", "D1d"],
    "E1A": ["D1d", "E1b", "E1a"],
    "E1B": ["E1b", "E1c", "D2a"],
    "E2A": ["E1c", "E2b", "E2a"],
    "E2B": ["E2b", "E2c", "D3a"],
    "E3A": ["E2c", "E3b", "E3a"],
    "E3B": ["E3b", "E3c", "D4a"],
    "E3C": ["E3c", "D4e", "E3f"],
    "D4F": ["D4e", "D4f"],

    "E1D": ["E1a", "E1d"],
    "E1E": ["E1d", "E1e"],
    "E2D": ["E1e", "E2d", "E2a"],
    "E2E": ["E2d", "E2e"],
    "E3D": ["E2e", "E3d", "E3a"],
    "E3E": ["E3d", "E3e"],
    "E3F": ["E3e", "E3f"],
}

NODE_TILES = {
    "A1A": ["A1"],
    "A1B": ["A1"],
    "A2A": ["A1", "A2"],
    "A2B": ["A2"],
    "A3A": ["A2", "A3"],
    "A3B": ["A3"],
    "A3C": ["A3"],

    "B1A": ["B1"],
    "B1B": ["B1", "A1"],
    "B2A": ["B1", "B2", "A1"],
    "B2B": ["B2", "A1", "A2"],
    "B3A": ["B2", "A2", "B3"],
    "B3B": ["A2", "B3", "A3"],
    "B4A": ["B3", "A3", "B4"],
    "B4B": ["A3", "B4"],
    "B4C": ["B4"],

    "C1A": ["C1"],
    "C1B": ["C1", "B1"],
    "C2A": ["C1", "B1", "C2"],
    "C2B": ["B1", "C2", "B2"],
    "C3A": ["C2", "B2", "C3"],
    "C3B": ["B2", "C3", "B3"],
    "C4A": ["C3", "B3", "C4"],
    "C4B": ["B3", "C4", "B4"],
    "C5A": ["C4", "B4", "C5"],
    "C5B": ["B4", "C5"],
    "C5C": ["C5"],

    "C1D": ["C1"],
    "D1A": ["C1", "D1"],
    "D1B": ["C1", "D1", "C2"],
    "D2A": ["D1", "C2", "D2"],
    "D2B": ["C2", "D2", "C3"],
    "D3A": ["D2", "C3", "D3"],
    "D3B": ["C3", "D3", "C4"],
    "D4A": ["D3", "C4", "D4"],
    "D4B": ["C4", "D4", "C5"],
    "D4C": ["D4", "C5"],
    "C5F": ["C5"],

    "D1D": ["D1"],
    "E1A": ["D1", "E1"],
    "E1B": ["D1", "E1", "D2"],
    "E2A": ["E1", "D2", "E2"],
    "E2B": ["D2", "E2", "D3"],
    "E3A": ["E2", "D3", "E3"],
    "E3B": ["D3", "E3", "D4"],
    "E3C": ["E3", "D4"],
    "D4F": ["D4"],

    "E1D": ["E1"],
    "E1E": ["E1"],
    "E2D": ["E1", "E2"],
    "E2E": ["E2"],
    "E3D": ["E2", "E3"],
    "E3E": ["E3"],
    "E3F": ["E3"]
}

EDGE_NODES = {
    "A1b": ["A1A", "A1B"],
    "A1c": ["A2A", "A1B"],
    "A2b": ["A2A", "A2B"],
    "A2c": ["A3A", "A2B"],
    "A3b": ["A3A", "A3B"],
    "A3c": ["A3C", "A3B"],

    "A1a": ["B1B", "A1A"],
    "A2a": ["B2B", "A2A"],
    "A3a": ["B3B", "A3A"],
    "A3f": ["B4B", "A3C"],

    "B1b": ["B1A", "B1B"],
    "B1c": ["B1B", "B2A"],
    "B2b": ["B2A", "B2B"],
    "B2c": ["B2B", "B3A"],
    "B3b": ["B3A", "B3B"],
    "B3c": ["B3B", "B4A"],
    "B4b": ["B4A", "B4B"],
    "B4c": ["B4B", "B4C"],

    "B1a": ["C1B", "B1A"],
    "B2a": ["C2B", "B2A"],
    "B3a": ["C3B", "B3A"],
    "B4a": ["C4B", "B4A"],
    "B4f": ["C5B", "B4C"],

    "C1b": ["C1A", "C1B"],
    "C1c": ["C1B", "C2A"],
    "C2b": ["C2A", "C2B"],
    "C2c": ["C2B", "C3A"],
    "C3b": ["C3A", "C3B"],
    "C3c": ["C3B", "C4A"],
    "C4b": ["C4A", "C4B"],
    "C4c": ["C4B", "C5A"],
    "C5b": ["C5A", "C5B"],
    "C5c": ["C5B", "C5C"],

    "C1a": ["C1D", "C1A"],
    "C2a": ["D1B", "C2A"],
    "C3a": ["D2B", "C3A"],
    "C4a": ["D3B", "C4A"],
    "C5a": ["D4B", "C5A"],
    "C5f": ["C5F", "C5C"],

    "C1d": ["C1D", "D1A"],
    "D1b": ["D1A", "D1B"],
    "D1c": ["D1B", "D2A"],
    "D2b": ["D2A", "D2B"],
    "D2c": ["D2B", "D3A"],
    "D3b": ["D3A", "D3B"],
    "D3c": ["D3B", "D4A"],
    "D4b": ["D4A", "D4B"],
    "D4c": ["D4B", "D4C"],
    "C5e": ["D4C", "C5F"],

    "D1a": ["D1D", "D1A"],
    "D2a": ["E1B", "D2A"],
    "D3a": ["E2B", "D3A"],
    "D4a": ["E3B", "D4A"],
    "D4f": ["D4F", "D4C"],

    "D1d": ["D1D", "E1A"],
    "E1b": ["E1A", "E1B"],
    "E1c": ["E1B", "E2A"],
    "E2b": ["E2A", "E2B"],
    "E2c": ["E2B", "E3A"],
    "E3b": ["E3A", "E3B"],
    "E3c": ["E3B", "E3C"],
    "D4e": ["E3C", "D4F"],

    "E1a": ["E1D", "E1A"],
    "E2a": ["E2D", "E2A"],
    "E3a": ["E3D", "E3A"],
    "E3f": ["E3F", "E3C"],

    "E1d": ["E1D", "E1E"],
    "E1e": ["E1E", "E2D"],
    "E2d": ["E2D", "E2E"],
    "E2e": ["E2E", "E3D"],
    "E3d": ["E3D", "E3E"],
    "E3e": ["E3E", "E3F"],
}

NEIGHBORS = {n: {e: [t for t in EDGE_NODES[e] if t != n][0] for e in es}
             for n, es in NODE_EDGES.items()}

CONNECTIONS = {e: {n: [t for t in NODE_EDGES[n] if t != e] for n in ns}
             for e, ns in EDGE_NODES.items()}

GENERIC_HARBORS = ["A3B", "A3C", "C1A", "C1D", "E2D", "E2E", "E3E", "E3F"]

SPECIFIC_HARBORS = {
    "R0": ["B4C", "C5B"],
    "R1": ["D4C", "D4F"],
    "R2": ["A2A", "A2B"],
    "R3": ["D1D", "E1A"],
    "R4": ["B1A", "B1B"],
}

HARBORS = GENERIC_HARBORS + [n for ns in SPECIFIC_HARBORS.values() for n in ns]


def get_shortest_paths(origin_node_id: str,
                    only_edge_ids: set[str] | None = None,
                    ) -> dict[str, list[str]]:

    if only_edge_ids is None:
        only_edge_ids = set(EDGE_NODES)

    paths: dict[str, list[str]] = {origin_node_id: []}
    frontier: set[str] = {origin_node_id}

    while len(frontier) > 0:

        new_frontier: set[str] = set()
        for node_id in frontier:
            path = paths[node_id]

            for edge_id, next_node_id in NEIGHBORS[node_id].items():
                if edge_id not in only_edge_ids:
                    continue
                if next_node_id in paths:
                    continue
                paths[next_node_id] = path + [edge_id]
                new_frontier.add(next_node_id)

        frontier = new_frontier

    return paths


def get_max_road_length(player_roads: set[str],
                        other_camps: set[str]) -> int:

    waypoints = {n for e in player_roads for n in EDGE_NODES[e]}
    max_length = 0

    for start_node_id in waypoints:
        paths = get_shortest_paths(start_node_id, player_roads)
        for end_node_id in waypoints:
            if end_node_id == start_node_id:
                continue
            path = paths.get(end_node_id)
            if path is None:
                continue
            length = len(path)
            if length <= max_length:
                continue

            interrupted = False
            interim_node_id = start_node_id
            for edge_id in path[:-1]:
                interim_node_id = NEIGHBORS[interim_node_id][edge_id]
                if interim_node_id in other_camps:
                    interrupted = True
                    break

            if not interrupted:
                max_length = length

    return max_length