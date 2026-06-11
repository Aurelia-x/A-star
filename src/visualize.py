"""
report_data.csv 可视化脚本 - 多窗口同时展示 + 表格 + 本地保存
"""
import csv
import os
import sys
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = True

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "report_data.csv")
OUT_DIR = os.path.join(BASE_DIR, "figures")
os.makedirs(OUT_DIR, exist_ok=True)

COLORS = [
    "#4C72B0", "#DD8452", "#55A868", "#C44E52",
    "#8172B3", "#937860", "#DA8BC3", "#8C8C8C",
    "#CCB974", "#64B5CD"
]

METRIC_KEYS = ["耗时(秒)", "扩展节点数(Closed)", "内存峰值(Open)", "步数(Steps)", "总代价(Cost)"]
METRIC_SHORT = ["耗时(s)", "扩展节点数", "内存峰值", "步数", "总代价"]

# 需要排除的简单/中等场景
EXCLUDE_SCENARIOS = {
    "8-Puzzle (简单)", "8-Puzzle (中等)",
    "15-Puzzle (简单)",
    "Maze (5x5 简单迷宫)", "Maze (10x10 中等迷宫)",
}


def load_data(path):
    rows = []
    with open(path, "r", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            rows.append(r)
    groups, order = [], []
    for r in rows:
        s = r["场景"]
        if s not in order:
            order.append(s)
            groups.append({"scenario": s, "rows": []})
        groups[order.index(s)]["rows"].append(r)
    return groups


def get_algo_label(raw):
    m = {
        "BFS (盲搜)": "BFS",
        "Dijkstra (代价搜)": "Dijkstra",
        "A* (错位棋子数)": "A*(misplaced)",
        "A* (曼哈顿距离)": "A*(manhattan)",
        "A* (线性冲突)": "A*(linear conflict)",
        "加权 A* (曼哈顿 W=2)": "WA*(W=2)",
        "IDA* (曼哈顿距离)": "IDA*",
        "A* (迷宫曼哈顿)": "A*(maze mh)",
        "A* (加权迷宫曼哈顿)": "WA*(maze)",
        "IDA* (迷宫曼哈顿)": "IDA*(maze)",
    }
    return m.get(raw, raw)


def parse_num(s):
    try:
        return float(s)
    except ValueError:
        return 0


def format_val(v):
    if isinstance(v, float):
        if v < 0.001:
            return f"{v:.2e}"
        elif v < 1:
            return f"{v:.4f}"
        else:
            return f"{v:.2f}"
    return str(v)


def _savefig(fig, path, **kwargs):
    old_stderr = sys.stderr
    sys.stderr = open(os.devnull, "w")
    try:
        fig.savefig(path, **kwargs)
    finally:
        sys.stderr.close()
        sys.stderr = old_stderr


# ==================== 表格 ====================

def make_table_figure(groups, title, filename, figsize=(18, 8)):
    header = ["场景", "算法配置"] + METRIC_SHORT
    table_data = []
    for g in groups:
        first = True
        for r in g["rows"]:
            row = [
                g["scenario"] if first else "",
                r["算法配置"],
                format_val(parse_num(r["耗时(秒)"])),
                r["扩展节点数(Closed)"],
                r["内存峰值(Open)"],
                r["步数(Steps)"],
                r["总代价(Cost)"],
            ]
            table_data.append(row)
            first = False

    fig, ax = plt.subplots(figsize=figsize)
    ax.axis("off")

    col_widths = [0.18, 0.20, 0.12, 0.14, 0.12, 0.10, 0.14]
    table = ax.table(
        cellText=table_data, colLabels=header, cellLoc="center",
        loc="center", colWidths=col_widths,
    )
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1.0, 1.35)

    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor("#CCCCCC")
        cell.set_linewidth(0.5)
        if row == 0:
            cell.set_facecolor("#4472C4")
            cell.set_text_props(color="white", fontweight="bold", fontsize=9)
        else:
            if table_data[row - 1][0]:
                cell.set_facecolor("#D6E4F0")
            else:
                cell.set_facecolor("#F2F2F2" if (row - 1) % 2 == 0 else "white")

    ax.set_title(title, fontsize=13, fontweight="bold", pad=18)
    fig.tight_layout()
    path = os.path.join(OUT_DIR, filename)
    _savefig(fig, path, dpi=150, bbox_inches="tight")
    print(f"  saved: {path}")
    return fig


# ==================== Puzzle / Maze 分类对比 ====================

def make_category_comparison(groups, category_label, filter_key, filename):
    filtered = [g for g in groups if filter_key in g["scenario"]]
    if not filtered:
        return None

    metrics = [
        ("耗时(秒)", "耗时 (s)", False),
        ("扩展节点数(Closed)", "扩展节点数", True),
        ("内存峰值(Open)", "内存峰值", True),
        ("步数(Steps)", "步数", False),
        ("总代价(Cost)", "总代价", False),
    ]

    fig, axes = plt.subplots(2, 3, figsize=(16, 12))
    axes = axes.flatten()

    algo_set = []
    for g in filtered:
        for r in g["rows"]:
            lbl = get_algo_label(r["算法配置"])
            if lbl not in algo_set:
                algo_set.append(lbl)
    n_algos = len(algo_set)
    n_scenes = len(filtered)

    for ax_idx, (key, ylabel, log_scale) in enumerate(metrics):
        ax = axes[ax_idx]
        x = np.arange(n_scenes)
        w = 0.8 / n_algos

        for i, algo in enumerate(algo_set):
            vals = []
            for g in filtered:
                found = 0
                for r in g["rows"]:
                    if get_algo_label(r["算法配置"]) == algo:
                        found = parse_num(r[key])
                        break
                vals.append(found)
            offset = (i - n_algos / 2 + 0.5) * w
            ax.bar(x + offset, vals, w, label=algo, color=COLORS[i % len(COLORS)])

        ax.set_xticks(x)
        ax.set_xticklabels([g["scenario"] for g in filtered], rotation=25, ha="right", fontsize=7)
        ax.set_ylabel(ylabel, fontsize=9)
        ax.set_title(ylabel, fontsize=10, fontweight="bold")
        if log_scale:
            ax.set_yscale("log")
        ax.legend(fontsize=6, ncol=2)

    for i in range(len(metrics), len(axes)):
        axes[i].set_visible(False)

    fig.suptitle(f"{category_label} 类场景算法对比", fontsize=14, fontweight="bold")
    fig.tight_layout()
    path = os.path.join(OUT_DIR, filename)
    _savefig(fig, path, dpi=150, bbox_inches="tight")
    print(f"  saved: {path}")
    return fig


# ==================== 主流程 ====================

def main():
    print(f"读取数据: {CSV_PATH}")
    all_groups = load_data(CSV_PATH)
    print(f"原始共 {len(all_groups)} 个场景")

    # 过滤掉简单/中等难度的场景
    groups = [g for g in all_groups if g["scenario"] not in EXCLUDE_SCENARIOS]
    for g in all_groups:
        if g["scenario"] in EXCLUDE_SCENARIOS:
            print(f"  已排除: {g['scenario']}")
    print(f"保留 {len(groups)} 个场景\n")

    puzzle_groups = [g for g in groups if "Puzzle" in g["scenario"]]
    maze_groups = [g for g in groups if "Maze" in g["scenario"]]

    # ========== 创建所有图形（不立即显示） ==========
    figures = []

    # 1. Puzzle 数据表
    print("[1/4] Puzzle 数据表...")
    f = make_table_figure(puzzle_groups, "Puzzle 类算法性能数据", "table_puzzle.png")
    figures.append(("Puzzle 数据表", f))

    # 2. Maze 数据表
    print("[2/4] Maze 数据表...")
    f = make_table_figure(maze_groups, "Maze 类算法性能数据", "table_maze.png",
                          figsize=(18, 7))
    figures.append(("Maze 数据表", f))

    # 3. Puzzle 分类对比
    print("[3/4] Puzzle 分类对比图...")
    f = make_category_comparison(groups, "Puzzle", "Puzzle", "puzzle_comparison.png")
    if f:
        figures.append(("Puzzle 对比", f))

    # 4. Maze 分类对比
    print("[4/4] Maze 分类对比图...")
    f = make_category_comparison(groups, "Maze", "Maze", "maze_comparison.png")
    if f:
        figures.append(("Maze 对比", f))

    print(f"\n一次性显示 {len(figures)} 个窗口（关闭所有窗口后退出）...")
    # 屏蔽 C 层字体渲染警告
    old_stderr = sys.stderr
    sys.stderr = open(os.devnull, "w")
    try:
        plt.show()
    finally:
        sys.stderr.close()
        sys.stderr = old_stderr


if __name__ == "__main__":
    main()
