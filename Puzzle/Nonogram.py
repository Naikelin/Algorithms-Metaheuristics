import itertools
import time


def get_row_indices(index, width):
    row = index // width
    return [row * width + i for i in range(width)]

def get_col_indices(index, height):
    col = index % height
    return [col + i * height for i in range(height)]

def check_constraint(sequence, clues):
    count = [len(list(g)) for k, g in itertools.groupby(sequence) if k == 1]
    return count == clues

def is_consistent(assignment, index, value, row_clues, col_clues, width, height):
    row_indices = get_row_indices(index, width)
    col_indices = get_col_indices(index, height)
    
    row = [assignment.get(i, None) for i in row_indices]
    col = [assignment.get(i, None) for i in col_indices]
    
    row[index % width] = value
    col[index // width] = value
    
    if None not in row and not check_constraint(row, row_clues[index // width]):
        return False

    if None not in col and not check_constraint(col, col_clues[index % height]):
        return False

    return True

def forward_checking(index, domains, width, height, row_clues, col_clues, node_count, backtrack_count):
    if index == len(domains):
        return domains, node_count, backtrack_count

    node_count += 1

    for value in domains[index]:
        assignment = {i: domains[i][0] for i in range(index)}

        if is_consistent(assignment, index, value, row_clues, col_clues, width, height):
            new_domains = [domain.copy() for domain in domains]
            new_domains[index] = [value]

            for i in range(index + 1, len(domains)):
                new_domains[i] = [v for v in domains[i] if is_consistent(assignment, i, v, row_clues, col_clues, width, height)]

            if all(new_domains[i] for i in range(index + 1, len(domains))):
                result, new_node_count, new_backtrack_count = forward_checking(index + 1, new_domains, width, height, row_clues, col_clues, node_count, backtrack_count)
                if result:
                    return result, new_node_count, new_backtrack_count
        else:
            backtrack_count += 1

    return None, node_count, backtrack_count

def solve_nonogram(row_clues, col_clues):
    height = len(row_clues)
    width = len(col_clues)
    domains = [[0, 1] for _ in range(width * height)]

    new_domains, node_count, backtrack_count = forward_checking(0, domains, width, height, row_clues, col_clues, 0, 0)

    if new_domains:
        assignment = {i: new_domains[i][0] for i in range(len(new_domains))}
        grid = [[assignment[row * width + col] for col in range(width)] for row in range(height)]
        return grid, node_count, backtrack_count
    else:
        print("No solution found")
        return None, node_count, backtrack_count

row_clues = [
    [4],
    [8],
    [10],
    [1, 1, 2, 1, 1],
    [1, 1, 2, 1, 1],
    [1, 6, 1],
    [6],
    [2, 2],
    [4],
    [2]
]

col_clues = [
    [4],
    [2],
    [7],
    [3, 4],
    [7, 2],
    [7, 2],
    [3, 4],
    [7],
    [2],
    [4]
]

start_time = time.perf_counter()
solution, node_count, backtrack_count = solve_nonogram(row_clues, col_clues)
end_time = time.perf_counter()

if solution:
    for row in solution:
        print("".join("#" if cell == 1 else "." for cell in row))

elapsed_time = end_time - start_time
print(f"Tiempo de ejecución: {elapsed_time:.4f} segundos")
print(f"Nodos generados: {node_count}")
print(f"Nodos con backtracking: {backtrack_count}")