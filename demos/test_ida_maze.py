import time
import sys
from domains import MazeProblem
from heuristics import h_maze_manhattan
from algorithms import a_star, ida_star

def test_ida_maze(size, obstacle_ratio=0.3):
    print("="*50)
    print(f"🧪 正在测试 {size}x{size} 迷宫 (障碍率: {obstacle_ratio})")
    print("="*50)
    
    # 使用固定种子保证每次生成的迷宫相同
    problem = MazeProblem.generate_random_maze(size, size, obstacle_ratio, seed=43)
    
    if not problem.is_solvable():
        print("❌ 当前种子生成的迷宫无解，请更换种子或参数。")
        return

    # --- 1. 运行 A* 算法 ---
    print(f"\n[A* 算法] (图搜索，带全局 Closed 表)")
    print("开始运行...")
    t0 = time.perf_counter()
    path_a, _, exp_a, _, _, _ = a_star(problem, h_maze_manhattan)
    t1 = time.perf_counter()
    print(f"✅ 完成！耗时: {t1-t0:.4f}s | 扩展节点数: {exp_a} | 路径长度: {len(path_a)}")

    # --- 2. 运行 IDA* 算法 ---
    print(f"\n[IDA* 算法] (树搜索，仅带单条路径环路检测)")
    print("开始运行 (如果迷宫大于 10x10，可能需要很久很久，随时可以 Ctrl+C 终止)...")
    
    # 我们为了防止它真的把你的电脑卡死，在外部记录时间，超过 10 秒强制提示
    t0 = time.perf_counter()
    try:
        path_ida, _, exp_ida, _, _, _ = ida_star(problem, h_maze_manhattan)
        t1 = time.perf_counter()
        print(f"✅ 完成！耗时: {t1-t0:.4f}s | 扩展节点数: {exp_ida} | 路径长度: {len(path_ida)}")
    except KeyboardInterrupt:
        print(f"\n🛑 已手动终止 IDA*！当前已耗时: {time.perf_counter()-t0:.2f}s")
        print("💡 思考：为什么 A* 瞬间秒杀，IDA* 却卡死了？")

if __name__ == "__main__":
    print(">>> 实验一：小试牛刀 (5x5) <<<")
    test_ida_maze(5)
    
    print("\n\n>>> 实验二：初见端倪 (8x8) <<<")
    test_ida_maze(8)
    
    print("\n\n>>> 实验三：灾难降临 (20x20) <<<")
    print("⚠️ 警告：这会让你看到 IDA* 的致命弱点，你可以随时按 Ctrl+C 中断。")
    test_ida_maze(20)
