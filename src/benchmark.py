import time
import csv
import os
import unicodedata
from domains import PuzzleProblem, MazeProblem
from heuristics import h_zero, h_misplaced, h_manhattan, h_linear_conflict, h_maze_manhattan
from algorithms import bfs, dijkstra, a_star, ida_star

# ==========================================
# 测试用例配置 (Test Cases)
# ==========================================
# 准备测试用例：8 数码的三个难度等级
# 难度划分依据是最优步数，步数越多，搜索空间爆炸越严重
TEST_CASES = {
    "8-Puzzle (简单)": {
        "type": "puzzle",
        "start": (1, 2, 3, 4, 0, 5, 7, 8, 6),
        "goal":  (1, 2, 3, 4, 5, 6, 7, 8, 0),
        "dim": 3
    },
    "8-Puzzle (中等)": {
        "type": "puzzle",
        "start": (2, 8, 3, 1, 6, 4, 7, 0, 5),
        "goal":  (1, 2, 3, 8, 0, 4, 7, 6, 5),
        "dim": 3
    },
    "8-Puzzle (困难)": {
        "type": "puzzle",
        # 最优解为 31 步的真正困难状态
        "start": (8, 6, 7, 2, 5, 4, 3, 0, 1),
        "goal":  (1, 2, 3, 4, 5, 6, 7, 8, 0),
        "dim": 3
    },
    "15-Puzzle (简单)": {
        "type": "puzzle",
        "start": (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 0, 15),
        "goal":  (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 0),
        "dim": 4
    },
    "15-Puzzle (中等)": {
        "type": "puzzle",
        "start": (1, 0, 2, 4, 5, 7, 3, 8, 9, 6, 10, 12, 13, 14, 11, 15),
        "goal":  (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 0),
        "dim": 4
    },
    "15-Puzzle (困难)": {
        "type": "puzzle",
        # 这是一个需要较多步数才能解开的困难状态
        "start": (2, 3, 4, 8, 1, 6, 0, 12, 5, 10, 7, 11, 9, 13, 14, 15),
        "goal":  (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 0),
        "dim": 4
    },
    "Maze (5x5 简单迷宫)": {
        "type": "maze_random",
        "rows": 5,
        "cols": 5,
        "obstacle_ratio": 0.2,
        "seed": 42
    },
    "Maze (10x10 中等迷宫)": {
        "type": "maze_random",
        "rows": 10,
        "cols": 10,
        "obstacle_ratio": 0.3,
        "seed": 1
    },
    "Maze (20x20 复杂迷宫)": {
        "type": "maze_random",
        "rows": 20,
        "cols": 20,
        "obstacle_ratio": 0.3,
        "max_weight": 1,
        "seed": 1
    },
    "Maze (20x20 变长边权/泥潭)": {
        "type": "maze_random",
        "rows": 20,
        "cols": 20,
        "obstacle_ratio": 0.2, # 稍微减少墙壁，让路多一点，体现不同边权的绕路选择
        "max_weight": 5,       # 空地上可能出现代价高达 5 的泥潭
        "seed": 42
    },
    "Maze (贪心陷阱 - 验证加权A*次优性)": {
        "type": "maze",
        "grid": [
            # 一条直达终点但包含剧毒泥潭(代价8)的路 vs 一条绕路但全是平地(代价1)的路
            [0, 0, 0, 8, 0],
            [0, 1, 1, 1, 0],
            [0, 0, 0, 0, 0],
            [1, 1, 1, 1, 1],
            [0, 0, 0, 0, 0]
        ],
        "start": (0, 0),
        "goal":  (0, 4)
    }
}

# ==========================================
# 辅助函数 (Helpers)
# ==========================================
def get_display_width(s):
    """计算中英文字符显示宽度的辅助函数"""
    return sum(2 if unicodedata.east_asian_width(c) in 'WF' else 1 for c in s)

def pad_string(s, width):
    """填充字符串至指定显示宽度"""
    w = get_display_width(s)
    if w < width:
        return s + ' ' * (width - w)
    return s

def print_table_header(scenario_name):
    """打印表格表头"""
    print(f"\n{'='*95}")
    print(f"[SCENARIO] {scenario_name}")
    print(f"{'-'*95}")
    # 这里为了对齐，考虑到中文字符宽度，手动调整部分列宽
    print(f"{'Algorithm':<28} | {'Status':<7} | {'Time (s)':<10} | {'Expanded':<10} | {'Max Open':<10} | {'Steps':<7} | {'Cost':<7}")
    print(f"{'-'*95}")

# ==========================================
# 主函数 (Main Benchmark Runner)
# ==========================================
def run_benchmark():
    """
    性能跑批脚本。
    遍历不同的算法、启发函数，并将测试结果导出为 CSV 报表。
    """
    print("-" * 60)
    print("\n[SYSTEM] Starting Algorithm Performance Benchmark")
    print("-" * 60)
    
    results = []

    for case_name, case_data in TEST_CASES.items():
        if case_data["type"] == "puzzle":
            problem = PuzzleProblem(case_data["dim"], case_data["start"], case_data["goal"])
            algorithms_config = [
                ("BFS (盲搜)", bfs, None, False, 1.0),
                ("Dijkstra (代价搜)", dijkstra, None, False, 1.0),
                ("A* (错位棋子数)", a_star, h_misplaced, True, 1.0),
                ("A* (曼哈顿距离)", a_star, h_manhattan, True, 1.0),
                ("A* (线性冲突)", a_star, h_linear_conflict, True, 1.0),
                ("加权 A* (曼哈顿 W=2)", a_star, h_manhattan, True, 2.0),
                ("IDA* (曼哈顿距离)", ida_star, h_manhattan, True, 1.0)
            ]
        elif case_data["type"] == "maze_random":
            problem = MazeProblem.generate_random_maze(
                rows=case_data["rows"], 
                cols=case_data["cols"], 
                obstacle_ratio=case_data.get("obstacle_ratio", 0.3),
                max_weight=case_data.get("max_weight", 1),
                seed=case_data.get("seed", None)
            )
            algorithms_config = [
                ("BFS (盲搜)", bfs, None, False, 1.0),
                ("Dijkstra (代价搜)", dijkstra, None, False, 1.0),
                ("A* (迷宫曼哈顿)", a_star, h_maze_manhattan, True, 1.0),
                ("A* (加权迷宫曼哈顿)", a_star, h_maze_manhattan, True, 2.0),
                ("IDA* (迷宫曼哈顿)", ida_star, h_maze_manhattan, True, 1.0)
            ]
        elif case_data["type"] == "maze":
            problem = MazeProblem(case_data["grid"], case_data["start"], case_data["goal"])
            algorithms_config = [
                ("BFS (盲搜)", bfs, None, False, 1.0),
                ("Dijkstra (代价搜)", dijkstra, None, False, 1.0),
                ("A* (迷宫曼哈顿)", a_star, h_maze_manhattan, True, 1.0),
                ("A* (加权迷宫曼哈顿)", a_star, h_maze_manhattan, True, 2.0),
                ("IDA* (迷宫曼哈顿)", ida_star, h_maze_manhattan, True, 1.0)
            ]
        
        if not problem.is_solvable():
            print_table_header(case_name)
            print(f"{pad_string('[ALL ALGORITHMS]', 28)} | {'SKIPPED':<7} | State is unsolvable.")
            print(f"{'='*95}")
            continue
            
        print_table_header(case_name)
        for algo_name, algo_func, heuristic, uses_heuristic, weight in algorithms_config:
                 
            # 20x20 复杂迷宫下，IDA* 会因为树搜索无全局记忆而导致天文数字般的重复扩展，直接跳过
            if case_name == "Maze (20x20 复杂迷宫)" and algo_name == "IDA* (迷宫曼哈顿)":
                 print(f"{pad_string(algo_name, 28)} | {'SKIPPED':<7} | Tree Search takes too long on large open grids.")
                 continue
                 
            # 处理字符串以便动态显示
            display_name = algo_name
            if get_display_width(display_name) > 28:
                display_name = display_name[:20] + "..."
                
            print(f"{pad_string(display_name, 28)} | ", end="", flush=True)
            
            try:
                # 调用统一接口
                if uses_heuristic:
                    if algo_func == ida_star:
                        # IDA* 签名没有 weight 参数
                        path_actions, _, expanded, max_open, t_cost, total_cost = algo_func(problem, heuristic)
                    else:
                        path_actions, _, expanded, max_open, t_cost, total_cost = algo_func(problem, heuristic, weight)
                else:
                    path_actions, _, expanded, max_open, t_cost, total_cost = algo_func(problem)
                    
                # 计算步数
                path_length = len(path_actions)
                
                print(f"{'SUCCESS':<7} | {t_cost:<10.4f} | {expanded:<10} | {max_open:<10} | {path_length:<7} | {total_cost:<7}")
                
                # 收集数据
                results.append({
                    "场景": case_name,
                    "算法配置": algo_name,
                    "耗时(秒)": round(t_cost, 4),
                    "扩展节点数(Closed)": expanded,
                    "内存峰值(Open)": max_open,
                    "步数(Steps)": path_length,
                    "总代价(Cost)": total_cost
                })
                
            except Exception as e:
                print(f"{'ERROR':<7} | {str(e)}")
        
        print(f"{'='*95}")
                
    # --- 导出 CSV 报表 ---
    csv_filename = "report_data.csv"
    print(f"\n[SYSTEM] All tests completed, exporting report to {csv_filename} ...")
    
    if results:
        keys = results[0].keys()
        with open(csv_filename, 'w', newline='', encoding='utf-8-sig') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(results)
        print("\n[SUCCESS] Report exported successfully.")
    else:
        print("\n[WARNING] No data was collected.")

if __name__ == "__main__":
    run_benchmark()
