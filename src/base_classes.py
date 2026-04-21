class Node:
    """
    搜索树中的节点类，用于封装状态及其在搜索过程中的代价值。
    """
    def __init__(self, state, parent=None, g=0, h=0, action=None):
        self.state = state      # 当前状态数据 (建议使用可哈希的类型，如 tuple)
        self.parent = parent    # 父节点，用于最终回溯路径
        self.g = g              # 从起点到当前节点的实际代价
        self.h = h              # 启发函数估算代价
        self.f = g + h          # 总评估代价 f = g + h
        self.action = action    # 从父节点到达此状态所执行的动作 (如 "Up", "Down")

    def __lt__(self, other):
        """
        重写小于号方法，以便 heapq 优先队列可以根据 f 值对节点进行自动排序。
        """
        return self.f < other.f

class BaseProblem:
    """
    抽象问题基类，定义了所有搜索问题必须实现的通用接口。
    具体的业务逻辑（如 8数码、15数码、迷宫等）应继承此类并实现这些方法。
    """
    def get_start_state(self):
        """
        返回问题的初始状态。
        """
        raise NotImplementedError("必须在子类中实现此方法")

    def get_goal_state(self):
        """
        返回问题的明确目标状态。
        注意：并非所有问题都有单一明确的目标状态（如迷宫寻路可能有多个出口），
        但在八数码/十五数码中，目标状态是明确的，这是启发式函数计算距离的前提。
        如果不适用，子类可以返回 None。
        """
        return None

    def is_goal(self, state):
        """
        判断给定状态是否为目标状态。
        返回: bool
        """
        raise NotImplementedError("必须在子类中实现此方法")

    def get_successors(self, state):
        """
        获取当前状态的所有合法后继（邻居）状态。
        返回: 一个列表，包含形如 (action, next_state, cost) 的元组
              - action: 到达该后继状态所采取的动作
              - next_state: 后继状态数据
              - cost: 从当前状态到后继状态的单步代价 (通常为 1)
        """
        raise NotImplementedError("必须在子类中实现此方法")

    def is_solvable(self):
        """
        (可选) 判断问题是否有解，用于在搜索前进行快速拦截。
        返回: bool
        """
        return True # 默认返回 True，子类可根据需要重写
