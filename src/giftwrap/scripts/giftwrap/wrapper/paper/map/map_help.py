def _generateRowVertexMappings(vertex_mappings, start_and_end_points):
    rows = []
    in_between_rows = []

    for (start_a, end_a), (start_b, end_b) \
            in zip(start_and_end_points[:-1],
                   start_and_end_points[1:]):
        rows.append(list(range(vertex_mappings[start_a],
                          vertex_mappings[end_a] + 1)))
        in_between_rows.append(
            list(range(vertex_mappings[end_a] + 1,
                  vertex_mappings[start_b])))
    rows.append(
        list(range(vertex_mappings[start_and_end_points[-1][0]],
                   vertex_mappings[start_and_end_points[-1][1]] + 1)))

    return rows, in_between_rows

def _generateVertexMappings(vertex_mappings, fold_point_mappings):
    return {
        fold_id: [vertex_mappings[pt] for pt in points]
        for fold_id, points in fold_point_mappings.items()
    }

