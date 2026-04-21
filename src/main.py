import os
import sys
import time
from domains import PuzzleProblem, MazeProblem
from heuristics import h_misplaced, h_manhattan, h_linear_conflict, h_maze_manhattan
from algorithms import a_star, bfs, dijkstra, ida_star


PUZZLE_PRESETS = {
    3: {
        "1": ("简单", (1, 2, 3, 4, 0, 5, 7, 8, 6), (1, 2, 3, 4, 5, 6, 7, 8, 0)),
        "2": ("中等", (2, 8, 3, 1, 6, 4, 7, 0, 5), (1, 2, 3, 8, 0, 4, 7, 6, 5)),
        "3": ("困难", (8, 6, 7, 2, 5, 4, 3, 0, 1), (1, 2, 3, 4, 5, 6, 7, 8, 0)),
    },
    4: {
        "1": ("简单", (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 0, 15),
              (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 0)),
        "2": ("中等", (1, 0, 2, 4, 5, 7, 3, 8, 9, 6, 10, 12, 13, 14, 11, 15),
              (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 0)),
        "3": ("困难", (2, 3, 4, 8, 1, 6, 0, 12, 5, 10, 7, 11, 9, 13, 14, 15),
              (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 0)),
    },
}

MAZE_PRESET_8X8 = [
    [0, 0, 0, 1, 0, 0, 0, 0],
    [1, 1, 0, 1, 0, 1, 1, 0],
    [0, 0, 0, 0, 0, 0, 1, 0],
    [0, 1, 1, 1, 1, 0, 1, 0],
    [0, 0, 0, 0, 1, 0, 0, 0],
    [0, 1, 1, 0, 1, 1, 1, 0],
    [0, 0, 1, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 1, 1, 1, 0],
]

ALGORITHM_OPTIONS = {
    "1": ("BFS", bfs, False, 1.0),
    "2": ("Dijkstra", dijkstra, False, 1.0),
    "3": ("A*", a_star, True, 1.0),
    "4": ("Weighted A* (W=2)", a_star, True, 2.0),
    "5": ("IDA*", ida_star, True, 1.0),
}

PUZZLE_HEURISTIC_OPTIONS = {
    "1": ("错位棋子数", h_misplaced),
    "2": ("曼哈顿距离", h_manhattan),
    "3": ("线性冲突", h_linear_conflict),
}

BACK = "__BACK__"


def log(tag, message=""):
    print(f"[{tag}] {message}")


def print_separator(char="-", width=72):
    print(char * width)


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def show_screen_title(title, step=None):
    clear_screen()
    print_separator("=")
    if step is not None:
        log("SYSTEM", f"{title} | Step {step}")
    else:
        log("SYSTEM", title)
    print_separator("=")


def prompt_choice(prompt, options):
    while True:
        choice = input(prompt).strip()
        if choice in options:
            return choice
        log("WARNING", f"无效输入：{choice}，请重新输入。")


def prompt_int(prompt, min_value=None, max_value=None, allow_empty=False, default=None, allow_back=False):
    while True:
        raw = input(prompt).strip()
        if allow_back and raw.lower() == "q":
            return BACK
        if allow_empty and raw == "":
            return default

        try:
            value = int(raw)
        except ValueError:
            log("WARNING", "请输入整数。")
            continue

        if min_value is not None and value < min_value:
            log("WARNING", f"输入值不能小于 {min_value}。")
            continue
        if max_value is not None and value > max_value:
            log("WARNING", f"输入值不能大于 {max_value}。")
            continue
        return value


def prompt_float(prompt, min_value=None, max_value=None, allow_empty=False, default=None, allow_back=False):
    while True:
        raw = input(prompt).strip()
        if allow_back and raw.lower() == "q":
            return BACK
        if allow_empty and raw == "":
            return default

        try:
            value = float(raw)
        except ValueError:
            log("WARNING", "请输入数字。")
            continue

        if min_value is not None and value < min_value:
            log("WARNING", f"输入值不能小于 {min_value}。")
            continue
        if max_value is not None and value > max_value:
            log("WARNING", f"输入值不能大于 {max_value}。")
            continue
        return value


def prompt_pair(prompt, min_first=None, max_first=None, min_second=None, max_second=None,
                allow_empty=False, default=None, allow_back=False):
    while True:
        raw = input(prompt).strip()
        if allow_back and raw.lower() == "q":
            return BACK
        if allow_empty and raw == "":
            return default

        tokens = raw.replace(",", " ").split()
        if len(tokens) != 2:
            log("WARNING", "请输入两个整数，例如 5 5。")
            continue

        try:
            first = int(tokens[0])
            second = int(tokens[1])
        except ValueError:
            log("WARNING", "请输入两个整数，例如 5 5。")
            continue

        if min_first is not None and first < min_first:
            log("WARNING", f"第一个值不能小于 {min_first}。")
            continue
        if max_first is not None and first > max_first:
            log("WARNING", f"第一个值不能大于 {max_first}。")
            continue
        if min_second is not None and second < min_second:
            log("WARNING", f"第二个值不能小于 {min_second}。")
            continue
        if max_second is not None and second > max_second:
            log("WARNING", f"第二个值不能大于 {max_second}。")
            continue

        return first, second


def parse_puzzle_state(raw_text, dimension):
    tokens = raw_text.replace(",", " ").split()
    expected_len = dimension * dimension

    if len(tokens) != expected_len:
        raise ValueError(f"需要输入 {expected_len} 个数字。")

    values = tuple(int(token) for token in tokens)
    expected_values = set(range(expected_len))
    if set(values) != expected_values:
        raise ValueError(f"输入必须恰好包含 0 到 {expected_len - 1}。")
    return values


def print_puzzle_board(state, dimension):
    print("+" + "---+" * dimension)
    for row in range(dimension):
        row_values = state[row * dimension:(row + 1) * dimension]
        line = "|"
        for value in row_values:
            cell = " " if value == 0 else str(value)
            line += f" {cell:>2}|"
        print(line)
        print("+" + "---+" * dimension)


def format_position_1_based(pos):
    return f"({pos[0] + 1}, {pos[1] + 1})"


def render_maze(problem, path_prefix=None, current_state=None):
    path_prefix = path_prefix or []
    path_set = set(path_prefix)

    for row in range(problem.rows):
        row_cells = []
        for col in range(problem.cols):
            pos = (row, col)
            cell_value = problem.grid[row][col]

            if pos == problem.start_pos:
                cell = "S"
            elif pos == problem.goal_pos:
                cell = "G"
            elif current_state is not None and pos == current_state:
                cell = "@"
            elif pos in path_set:
                cell = "*"
            elif cell_value == 1:
                cell = "#"
            elif cell_value > 1:
                cell = str(cell_value)
            else:
                cell = "."
            row_cells.append(f"{cell:>2}")
        print(" ".join(row_cells))


def render_editable_puzzle_grid(grid):
    dimension = len(grid)
    header = "    " + " ".join(f"{col + 1:>3}" for col in range(dimension))
    print(header)
    print("   +" + "---+" * dimension)
    for row in range(dimension):
        line = f"{row + 1:>2} |"
        for col in range(dimension):
            value = grid[row][col]
            cell = "." if value is None else str(value)
            line += f" {cell:>2}|"
        print(line)
        print("   +" + "---+" * dimension)


def render_editable_maze_grid(grid):
    cols = len(grid[0])
    header = "    " + " ".join(f"{col + 1:>3}" for col in range(cols))
    print(header)
    print("   +" + "---+" * cols)
    for row, row_values in enumerate(grid, start=1):
        line = f"{row:>2} |"
        for value in row_values:
            if value == 1:
                cell = "#"
            else:
                cell = str(value)
            line += f" {cell:>2}|"
        print(line)
        print("   +" + "---+" * cols)


def build_puzzle_state_by_coordinates(dimension, title):
    expected_values = set(range(dimension * dimension))
    grid = [[None for _ in range(dimension)] for _ in range(dimension)]

    while True:
        show_screen_title(title, step=2)
        render_editable_puzzle_grid(grid)

        used_values = {value for row in grid for value in row if value is not None}
        remaining_values = sorted(expected_values - used_values)
        log("INFO", f"剩余可填数字: {remaining_values if remaining_values else '无'}")
        log("INPUT", "输入格式: 行 列 值，例如 1 2 8")
        log("INPUT", "支持命令: done 完成, clear 清空全部, q 返回上一步, 行 列 x 清空单格")

        command = input("请输入命令: ").strip().lower()
        if command == "q":
            return BACK
        if command == "clear":
            grid = [[None for _ in range(dimension)] for _ in range(dimension)]
            continue
        if command == "done":
            flat_values = [value for row in grid for value in row]
            if any(value is None for value in flat_values):
                log("WARNING", "棋盘尚未填满，不能完成。")
                input("按回车继续...")
                continue
            if set(flat_values) != expected_values:
                log("WARNING", "棋盘必须恰好包含所有合法数字。")
                input("按回车继续...")
                continue
            return tuple(flat_values)

        parts = command.split()
        if len(parts) != 3:
            log("WARNING", "请输入三个字段：行 列 值。")
            input("按回车继续...")
            continue

        try:
            row = int(parts[0]) - 1
            col = int(parts[1]) - 1
        except ValueError:
            log("WARNING", "行列坐标必须是整数。")
            input("按回车继续...")
            continue

        if not (0 <= row < dimension and 0 <= col < dimension):
            log("WARNING", "坐标超出棋盘范围。")
            input("按回车继续...")
            continue

        if parts[2] == "x":
            grid[row][col] = None
            continue

        try:
            value = int(parts[2])
        except ValueError:
            log("WARNING", "格子值必须是整数，或使用 x 清空单格。")
            input("按回车继续...")
            continue

        if value not in expected_values:
            log("WARNING", f"数码值必须在 0 到 {dimension * dimension - 1} 之间。")
            input("按回车继续...")
            continue

        duplicate_pos = None
        for r in range(dimension):
            for c in range(dimension):
                if (r, c) != (row, col) and grid[r][c] == value:
                    duplicate_pos = (r, c)
                    break
            if duplicate_pos is not None:
                break

        if duplicate_pos is not None:
            log("WARNING", f"数字 {value} 已出现在第 {duplicate_pos[0] + 1} 行第 {duplicate_pos[1] + 1} 列。")
            input("按回车继续...")
            continue

        grid[row][col] = value


def build_maze_grid_by_coordinates(rows, cols):
    grid = [[0 for _ in range(cols)] for _ in range(rows)]

    while True:
        show_screen_title("迷宫网格编辑", step=2)
        render_editable_maze_grid(grid)
        log("INPUT", "输入格式: 行 列 值，例如 2 3 1")
        log("INPUT", "值说明: 0=空地, 1=墙, 2及以上=权重")
        log("INPUT", "支持命令: done 完成, clear 清空全部, q 返回上一步")

        command = input("请输入命令: ").strip().lower()
        if command == "q":
            return BACK
        if command == "clear":
            grid = [[0 for _ in range(cols)] for _ in range(rows)]
            continue
        if command == "done":
            return grid

        parts = command.split()
        if len(parts) != 3:
            log("WARNING", "请输入三个字段：行 列 值。")
            input("按回车继续...")
            continue

        try:
            row = int(parts[0]) - 1
            col = int(parts[1]) - 1
            value = int(parts[2])
        except ValueError:
            log("WARNING", "行、列、值都必须是整数。")
            input("按回车继续...")
            continue

        if not (0 <= row < rows and 0 <= col < cols):
            log("WARNING", "坐标超出迷宫范围。")
            input("按回车继续...")
            continue
        if value < 0:
            log("WARNING", "迷宫格子的值不能为负数。")
            input("按回车继续...")
            continue

        grid[row][col] = value


def choose_puzzle_problem(dimension):
    while True:
        show_screen_title(f"{'8' if dimension == 3 else '15'} 数码配置", step=2)
        print("1. 使用预设测试例")
        print("2. 手动输入初始状态")
        print("0. 返回上一步")
        mode = prompt_choice("请输入选项 (0/1/2): ", {"0", "1", "2"})

        if mode == "0":
            return BACK

        if mode == "1":
            while True:
                show_screen_title(f"{'8' if dimension == 3 else '15'} 数码预设选择", step=2)
                print("1. 简单")
                print("2. 中等")
                print("3. 困难")
                print("0. 返回上一步")
                preset_choice = prompt_choice("请选择选项 (0/1/2/3): ", {"0", "1", "2", "3"})
                if preset_choice == "0":
                    break
                difficulty, start, goal = PUZZLE_PRESETS[dimension][preset_choice]
                return PuzzleProblem(dimension, start, goal)

        expected_len = dimension * dimension
        while True:
            start = build_puzzle_state_by_coordinates(
                dimension,
                f"{'8' if dimension == 3 else '15'} 数码初始状态编辑"
            )
            if start == BACK:
                break
            while True:
                show_screen_title(f"{'8' if dimension == 3 else '15'} 数码目标状态", step=2)
                print("1. 使用标准目标态")
                print("2. 手动编辑目标态")
                print("0. 返回上一步")
                goal_mode = prompt_choice("请输入选项 (0/1/2): ", {"0", "1", "2"})
                if goal_mode == "0":
                    break
                if goal_mode == "1":
                    goal = tuple(list(range(1, expected_len)) + [0])
                    return PuzzleProblem(dimension, start, goal)

                goal = build_puzzle_state_by_coordinates(
                    dimension,
                    f"{'8' if dimension == 3 else '15'} 数码目标状态编辑"
                )
                if goal == BACK:
                    continue
                return PuzzleProblem(dimension, start, goal)


def read_maze_grid(rows, cols):
    log("INPUT", "请逐行输入迷宫。0 表示空地，1 表示墙，2 及以上表示权重。")
    log("INPUT", "输入 q 返回上一步。")
    grid = []
    for row in range(rows):
        while True:
            raw = input(f"第 {row + 1} 行: ").strip()
            if raw.lower() == "q":
                return BACK
            tokens = raw.replace(",", " ").split()
            if len(tokens) != cols:
                log("WARNING", f"本行需要输入 {cols} 个数字。")
                continue
            try:
                values = [int(token) for token in tokens]
            except ValueError:
                log("WARNING", "迷宫中的每个格子都必须是整数。")
                continue
            grid.append(values)
            break
    return grid


def choose_maze_problem():
    while True:
        show_screen_title("迷宫配置", step=2)
        print("1. 使用预设 8x8 迷宫")
        print("2. 手动输入迷宫")
        print("3. 随机生成迷宫")
        print("0. 返回上一步")
        mode = prompt_choice("请输入选项 (0/1/2/3): ", {"0", "1", "2", "3"})

        if mode == "0":
            return BACK

        if mode == "1":
            return MazeProblem(MAZE_PRESET_8X8, (0, 0), (7, 7))

        if mode == "2":
            while True:
                show_screen_title("迷宫手动输入", step=2)
                log("INPUT", "输入 q 返回上一步。")
                size = prompt_pair(
                    "请输入迷宫尺寸 (行 列，输入回车默认 8 8): ",
                    min_first=2,
                    min_second=2,
                    allow_empty=True,
                    default=(8, 8),
                    allow_back=True
                )
                if size == BACK:
                    break
                rows, cols = size

                grid = build_maze_grid_by_coordinates(rows, cols)
                if grid == BACK:
                    continue

                while True:
                    show_screen_title("迷宫起点终点设置", step=2)
                    render_editable_maze_grid(grid)
                    log("INPUT", "输入 q 返回上一步。坐标格式示例: 1 1")
                    start_pos_raw = prompt_pair(
                        "请输入起点坐标 (行 列): ",
                        min_first=1,
                        max_first=rows,
                        min_second=1,
                        max_second=cols,
                        allow_back=True
                    )
                    if start_pos_raw == BACK:
                        break
                    goal_pos_raw = prompt_pair(
                        "请输入终点坐标 (行 列): ",
                        min_first=1,
                        max_first=rows,
                        min_second=1,
                        max_second=cols,
                        allow_back=True
                    )
                    if goal_pos_raw == BACK:
                        break

                    start_pos = (start_pos_raw[0] - 1, start_pos_raw[1] - 1)
                    goal_pos = (goal_pos_raw[0] - 1, goal_pos_raw[1] - 1)

                    if grid[start_pos[0]][start_pos[1]] == 1:
                        log("WARNING", "起点不能设置在墙上。")
                        input("按回车继续...")
                        continue
                    if grid[goal_pos[0]][goal_pos[1]] == 1:
                        log("WARNING", "终点不能设置在墙上。")
                        input("按回车继续...")
                        continue

                    return MazeProblem(grid, start_pos, goal_pos)

        while True:
            show_screen_title("迷宫随机生成", step=2)
            log("INPUT", "在任意输入处可输入 q 返回上一步。")
            size = prompt_pair(
                "请输入迷宫尺寸 (行 列): ",
                min_first=2,
                min_second=2,
                allow_back=True
            )
            if size == BACK:
                break
            rows, cols = size
            obstacle_raw = input("请输入障碍率 (0~0.9，输入回车默认 0.2): ").strip()
            if obstacle_raw.lower() == "q":
                break
            weight_raw = input("请输入最大权重 (输入回车默认 1，>1 表示存在泥潭): ").strip()
            if weight_raw.lower() == "q":
                break
            seed_raw = input("请输入随机种子 (直接回车表示纯随机): ").strip()
            if seed_raw.lower() == "q":
                break
            try:
                obstacle_ratio = 0.2 if obstacle_raw == "" else float(obstacle_raw)
                max_weight = 1 if weight_raw == "" else int(weight_raw)
                seed = None if seed_raw == "" else int(seed_raw)
                if not 0.0 <= obstacle_ratio <= 0.9:
                    raise ValueError("障碍率必须在 0.0 到 0.9 之间。")
                if max_weight < 1:
                    raise ValueError("最大权重不能小于 1。")
            except ValueError as exc:
                log("WARNING", str(exc))
                input("按回车继续...")
                continue

            return MazeProblem.generate_random_maze(
                rows=rows,
                cols=cols,
                obstacle_ratio=obstacle_ratio,
                max_weight=max_weight,
                seed=seed,
            )


def choose_problem_type():
    show_screen_title("启发式搜索算法演示系统", step=1)
    print("1. 8 数码问题")
    print("2. 15 数码问题")
    print("3. 迷宫寻路问题")
    print("0. 退出程序")
    return prompt_choice("请选择问题类型 (0/1/2/3): ", {"0", "1", "2", "3"})


def configure_problem(problem_choice):
    if problem_choice == "1":
        return "puzzle", choose_puzzle_problem(3)
    if problem_choice == "2":
        return "puzzle", choose_puzzle_problem(4)
    return "maze", choose_maze_problem()


def choose_algorithm(problem_type, problem):
    while True:
        show_screen_title("算法选择", step=3)
        print("1. BFS")
        print("2. Dijkstra")
        print("3. A*")
        print("4. Weighted A* (W=2)")
        print("5. IDA*")
        print("0. 返回上一步")
        algo_choice = prompt_choice("请输入选项 (0/1/2/3/4/5): ", {"0", *set(ALGORITHM_OPTIONS.keys())})
        if algo_choice == "0":
            return BACK
        algo_name, algo_func, needs_heuristic, weight = ALGORITHM_OPTIONS[algo_choice]

        if problem_type == "maze" and algo_choice == "5" and (problem.rows > 8 or problem.cols > 8):
            show_screen_title("算法选择", step=3)
            log(
                "WARNING",
                f"当前迷宫尺寸为 {problem.rows}x{problem.cols}，超过 8x8，不建议选择 IDA*，否则可能耗时过长甚至看似卡死。"
            )
            retry = prompt_choice("是否重新选择算法？(0=返回上一步, 1=重新选择, 2=继续使用 IDA*): ", {"0", "1", "2"})
            if retry == "0":
                return BACK
            if retry == "1":
                continue

        heuristic_name = None
        heuristic_func = None
        if needs_heuristic:
            if problem_type == "maze":
                heuristic_name = "迷宫曼哈顿距离"
                heuristic_func = h_maze_manhattan
                show_screen_title("算法选择", step=3)
                log("SYSTEM", f"迷宫问题固定使用启发函数：{heuristic_name}")
                input("按回车开始执行...")
            else:
                while True:
                    show_screen_title("启发函数选择", step=4)
                    print("1. 错位棋子数")
                    print("2. 曼哈顿距离")
                    print("3. 线性冲突")
                    print("0. 返回上一步")
                    heuristic_choice = prompt_choice("请输入选项 (0/1/2/3): ", {"0", *set(PUZZLE_HEURISTIC_OPTIONS.keys())})
                    if heuristic_choice == "0":
                        heuristic_name = BACK
                        break
                    heuristic_name, heuristic_func = PUZZLE_HEURISTIC_OPTIONS[heuristic_choice]
                    break
                if heuristic_name == BACK:
                    continue

        return algo_name, algo_func, heuristic_name, heuristic_func, weight


def print_problem_summary(problem_type, problem):
    show_screen_title("问题配置确认", step=3)
    if problem_type == "puzzle":
        log("INFO", f"棋盘维度: {problem.dimension}x{problem.dimension}")
        log("INFO", "初始状态:")
        print_puzzle_board(problem.get_start_state(), problem.dimension)
        log("INFO", "目标状态:")
        print_puzzle_board(problem.get_goal_state(), problem.dimension)
    else:
        log("INFO", f"迷宫尺寸: {problem.rows}x{problem.cols}")
        log("INFO", f"起点: {format_position_1_based(problem.start_pos)} 终点: {format_position_1_based(problem.goal_pos)}")
        render_maze(problem)
    print_separator("=")
    if not problem.is_solvable():
        log("SKIP", "当前问题无解。")
        print("1. 返回上一步重新配置")
        print("0. 退出程序")
        return prompt_choice("请输入选项 (0/1): ", {"0", "1"})
    print("1. 继续选择算法")
    print("0. 返回上一步")
    return prompt_choice("请输入选项 (0/1): ", {"0", "1"})


def run_selected_algorithm(problem, algo_func, heuristic_func, weight):
    if heuristic_func is None:
        return algo_func(problem)
    if algo_func == ida_star:
        return algo_func(problem, heuristic_func)
    return algo_func(problem, heuristic_func, weight)


def print_result_summary(algo_name, heuristic_name, result):
    show_screen_title("求解结果", step=5)
    path_actions, path_states, expanded, max_open, time_cost, total_cost = result
    log("SUCCESS", "搜索完成")
    log("RESULT", f"算法: {algo_name}")
    if heuristic_name is not None:
        log("RESULT", f"启发函数: {heuristic_name}")
    log("RESULT", f"Time: {time_cost:.4f}s | Exp: {expanded} | Open: {max_open} | Steps: {len(path_actions)} | Cost: {total_cost}")
    if path_actions:
        log("RESULT", f"动作序列: {' -> '.join(path_actions)}")
    else:
        log("RESULT", "动作序列: 空")


def show_puzzle_problem_states(problem):
    show_screen_title("问题状态查看", step=5)
    log("INFO", "初始状态:")
    print_puzzle_board(problem.get_start_state(), problem.dimension)
    log("INFO", "目标状态:")
    print_puzzle_board(problem.get_goal_state(), problem.dimension)
    input("查看结束，按回车返回结果页...")


def replay_puzzle_solution(problem, path_actions, path_states):
    for step_idx, state in enumerate(path_states):
        show_screen_title("数码问题回放", step=6)
        if step_idx == 0:
            log("STEP", "Step 0 | 初始状态")
        else:
            log("STEP", f"Step {step_idx} | Action: {path_actions[step_idx - 1]}")
        print_puzzle_board(state, problem.dimension)
        time.sleep(0.4)
    input("回放结束，按回车返回结果页...")


def replay_maze_solution(problem, path_actions, path_states):
    for step_idx, state in enumerate(path_states):
        show_screen_title("迷宫问题回放", step=6)
        if step_idx == 0:
            log("STEP", "Step 0 | 初始位置")
        else:
            log("STEP", f"Step {step_idx} | Action: {path_actions[step_idx - 1]}")
        render_maze(problem, path_states[:step_idx + 1], state)
        print_separator("-")
        time.sleep(0.25)
    input("回放结束，按回车返回结果页...")


def main():
    while True:
        problem_choice = choose_problem_type()
        if problem_choice == "0":
            return

        while True:
            problem_type, problem = configure_problem(problem_choice)
            if problem == BACK:
                break

            summary_choice = print_problem_summary(problem_type, problem)
            if summary_choice == "0":
                continue
            if not problem.is_solvable():
                continue

            while True:
                algo_config = choose_algorithm(problem_type, problem)
                if algo_config == BACK:
                    break
                algo_name, algo_func, heuristic_name, heuristic_func, weight = algo_config

                show_screen_title("算法执行中", step=5)
                log("RUNNING", f"{algo_name} 开始执行...")
                result = run_selected_algorithm(problem, algo_func, heuristic_func, weight)
                path_actions, path_states, expanded, max_open, time_cost, total_cost = result

                if not path_states:
                    show_screen_title("求解结果", step=5)
                    log("ERROR", "算法执行结束，但未找到可行路径。")
                    log("RESULT", f"Time: {time_cost:.4f}s | Exp: {expanded} | Open: {max_open} | Steps: 0 | Cost: {total_cost}")
                    print("1. 返回当前问题配置")
                    print("2. 返回主菜单")
                    print("0. 退出程序")
                    next_choice = prompt_choice("请输入选项 (0/1/2): ", {"0", "1", "2"})
                    if next_choice == "1":
                        break
                    if next_choice == "2":
                        problem = BACK
                        break
                    return

                while True:
                    print_result_summary(algo_name, heuristic_name, result)
                    print("1. 回放求解过程")
                    if problem_type == "puzzle":
                        print("2. 查看初始状态和目标状态")
                        print("3. 返回当前问题配置")
                        print("4. 返回主菜单")
                        print("0. 退出程序")
                        next_choice = prompt_choice("请输入选项 (0/1/2/3/4): ", {"0", "1", "2", "3", "4"})
                    else:
                        print("2. 返回当前问题配置")
                        print("3. 返回主菜单")
                        print("0. 退出程序")
                        next_choice = prompt_choice("请输入选项 (0/1/2/3): ", {"0", "1", "2", "3"})
                    if next_choice == "1":
                        if problem_type == "puzzle":
                            replay_puzzle_solution(problem, path_actions, path_states)
                        else:
                            replay_maze_solution(problem, path_actions, path_states)
                        continue
                    if problem_type == "puzzle" and next_choice == "2":
                        show_puzzle_problem_states(problem)
                        continue
                    if (problem_type == "puzzle" and next_choice == "3") or (problem_type != "puzzle" and next_choice == "2"):
                        break
                    if (problem_type == "puzzle" and next_choice == "4") or (problem_type != "puzzle" and next_choice == "3"):
                        problem = BACK
                        break
                    return

                if problem == BACK:
                    break
                break

            if problem == BACK:
                break


if __name__ == "__main__":
    try:
        main()
    except EOFError:
        print("\n")
        log("SYSTEM", "输入结束，程序退出。")
        sys.exit(0)
    except KeyboardInterrupt:
        print("\n")
        log("SYSTEM", "程序已手动终止。")
        sys.exit(0)
