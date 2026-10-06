"""rush-hour-lite: 6x6 高峰时刻滑块解谜 + BFS 求解器。纯标准库。

玩法: 把红色车 X 从第 3 行右边的出口滑出去。车辆只能沿自身方向滑动。
"""
from __future__ import annotations

import argparse
import copy
import random
import sys
from collections import deque

SIZE = 6
EXIT_ROW = 2  # 出口在第 3 行(下标 2)右侧

# 车辆: (编号, 方向 'H'/'V', 长度, 起始行, 起始列)
# 编号 'X' 固定为红色目标车(横向 2 格)
PUZZLES = {
    "easy": [
        ("X", "H", 2, 2, 1),
        ("A", "V", 2, 0, 0),
        ("B", "H", 2, 0, 1),
        ("C", "V", 3, 0, 3),
        ("D", "H", 2, 3, 3),
        ("E", "V", 2, 3, 5),
        ("F", "H", 3, 4, 1),
        ("G", "V", 2, 4, 4),
    ],
    "medium": [
        ("X", "H", 2, 2, 1),
        ("A", "V", 3, 0, 0),
        ("B", "H", 2, 0, 1),
        ("C", "V", 2, 0, 4),
        ("D", "H", 2, 1, 4),
        ("E", "V", 2, 2, 5),
        ("F", "H", 3, 3, 0),
        ("G", "V", 3, 3, 3),
        ("H", "H", 2, 4, 4),
        ("I", "V", 2, 5, 1),
    ],
    "hard": [
        ("X", "H", 2, 2, 1),
        ("A", "V", 3, 1, 3),
        ("B", "V", 3, 2, 5),
        ("C", "V", 3, 3, 2),
        ("D", "V", 2, 3, 0),
        ("E", "H", 3, 0, 1),
        ("F", "V", 2, 3, 4),
        ("G", "V", 2, 4, 1),
        ("H", "H", 2, 5, 3),
        ("I", "H", 2, 0, 4),
        ("J", "V", 2, 1, 0),
        ("K", "H", 2, 1, 4),
    ],
}


class IllegalMove(Exception):
    """非法移动。"""


class RushHour:
    """6x6 高峰时刻棋盘。车辆按固定顺序记录, 状态为每辆车 (行, 列)。"""

    def __init__(self, vehicles):
        self.order = [v[0] for v in vehicles]
        self.orient = {v[0]: v[1] for v in vehicles}
        self.length = {v[0]: v[2] for v in vehicles}
        self.pos = {v[0]: (v[3], v[4]) for v in vehicles}
        if "X" not in self.pos:
            raise ValueError("缺少红色车 X")

    def copy(self):
        return copy.deepcopy(self)

    def occupied(self, ignore=None):
        occ = {}
        for vid, (r, c) in self.pos.items():
            if vid == ignore:
                continue
            for i in range(self.length[vid]):
                cell = (r, c + i) if self.orient[vid] == "H" else (r + i, c)
                occ[cell] = vid
        return occ

    def legal_steps(self, vid):
        """返回车辆 vid 可走的单步方向列表: +1 / -1。"""
        orient = self.orient[vid]
        r, c = self.pos[vid]
        n = self.length[vid]
        occ = self.occupied(ignore=vid)
        steps = []
        if orient == "H":
            if c - 1 >= 0 and (r, c - 1) not in occ:
                steps.append(-1)
            if c + n < SIZE and (r, c + n) not in occ:
                steps.append(+1)
        else:
            if r - 1 >= 0 and (r - 1, c) not in occ:
                steps.append(-1)
            if r + n < SIZE and (r + n, c) not in occ:
                steps.append(+1)
        return steps

    def move(self, vid, step):
        """走一步; 非法抛 IllegalMove。"""
        if vid not in self.pos:
            raise IllegalMove(f"没有这辆车: {vid}")
        if step not in self.legal_steps(vid):
            raise IllegalMove(f"车辆 {vid} 不能向 {'右/下' if step > 0 else '左/上'} 走")
        r, c = self.pos[vid]
        if self.orient[vid] == "H":
            self.pos[vid] = (r, c + step)
        else:
            self.pos[vid] = (r + step, c)

    def is_solved(self):
        r, c = self.pos["X"]
        return r == EXIT_ROW and c + self.length["X"] - 1 == SIZE - 1

    def state_key(self):
        return tuple(self.pos[vid] for vid in self.order)

    def set_state(self, key):
        for vid, p in zip(self.order, key):
            self.pos[vid] = p

    def render(self):
        grid = [["·" for _ in range(SIZE)] for _ in range(SIZE)]
        for vid, (r, c) in self.pos.items():
            ch = "█" if vid == "X" else vid
            for i in range(self.length[vid]):
                cell = (r, c + i) if self.orient[vid] == "H" else (r + i, c)
                grid[cell[0]][cell[1]] = ch
        lines = []
        for i, row in enumerate(grid):
            mark = "▶" if i == EXIT_ROW else " "
            lines.append(mark + " ".join(row) + (" ◀出口" if i == EXIT_ROW else ""))
        return "\n".join(lines)


def solve(game, max_states=400000):
    """BFS 求最短解法。返回 [(车号, 步数), ...], 无解返回 None。"""
    start = game.state_key()
    if game.is_solved():
        return []
    prev = {start: None}
    move_of = {}
    q = deque([start])
    while q:
        key = q.popleft()
        game.set_state(key)
        for vid in game.order:
            for step in game.legal_steps(vid):
                nxt = copy.deepcopy(game)
                nxt.move(vid, step)
                k2 = nxt.state_key()
                if k2 in prev:
                    continue
                prev[k2] = key
                move_of[k2] = (vid, step)
                if nxt.is_solved():
                    path = []
                    k = k2
                    while prev[k] is not None:
                        path.append(move_of[k])
                        k = prev[k]
                    path.reverse()
                    return path
                if len(prev) > max_states:
                    return None
                q.append(k2)
    return None


def load_puzzle(name):
    if name not in PUZZLES:
        raise ValueError(f"未知谜题: {name}, 可选: {', '.join(PUZZLES)}")
    return RushHour(copy.deepcopy(PUZZLES[name]))


def play_auto(puzzle_name="easy", seed=42, verbose=False):
    rng = random.Random(seed)
    game = load_puzzle(puzzle_name)
    sol = solve(game)
    if sol is None:
        print(f"谜题 {puzzle_name}: 无解")
        return None
    print(f"谜题 {puzzle_name}: BFS 找到 {len(sol)} 步解法")
    g = load_puzzle(puzzle_name)
    for vid, step in sol:
        g.move(vid, step)
        if verbose:
            d = "右" if step > 0 and g.orient[vid] == "H" else \
                "下" if step > 0 else "左" if g.orient[vid] == "H" else "上"
            print(f"  {vid} 向{d}")
            print(g.render())
    assert g.is_solved()
    print("已通关 ✓")
    return len(sol)


def play_interactive(puzzle_name="easy"):
    game = load_puzzle(puzzle_name)
    print("高峰时刻: 把红色车 X 从右侧出口滑出去!")
    print("输入如: A +  (A 车向右/下走一格), A - (向左/上), q 退出")
    moves = 0
    while True:
        print()
        print(game.render())
        if game.is_solved():
            print(f"通关! 共用 {moves} 步。")
            return
        s = input("走法> ").strip().upper()
        if s in ("Q", "QUIT", "退出"):
            print("再见!")
            return
        parts = s.split()
        if len(parts) != 2 or parts[0] not in game.pos or parts[1] not in ("+", "-"):
            print("格式不对, 示例: A +")
            continue
        try:
            game.move(parts[0], +1 if parts[1] == "+" else -1)
            moves += 1
        except IllegalMove as e:
            print(f"走不了: {e}")


def main(argv=None):
    ap = argparse.ArgumentParser(description="rush-hour-lite: 高峰时刻滑块解谜")
    ap.add_argument("--puzzle", default="easy", choices=list(PUZZLES),
                    help="谜题: easy/medium/hard")
    ap.add_argument("--solve", action="store_true", help="打印 BFS 最短解法")
    ap.add_argument("--auto", action="store_true", help="自动演示求解")
    ap.add_argument("--games", type=int, default=1, help="自动演示次数")
    ap.add_argument("--seed", type=int, default=42, help="随机种子")
    ap.add_argument("--verbose", action="store_true", help="打印每一步棋盘")
    ap.add_argument("--list", action="store_true", help="列出所有谜题")
    args = ap.parse_args(argv)

    if args.list:
        for name in PUZZLES:
            print(f"{name}: {len(PUZZLES[name])} 辆车")
        return 0
    if args.auto:
        for i in range(args.games):
            r = play_auto(args.puzzle, seed=args.seed + i, verbose=args.verbose)
            if r is None:
                return 1
        return 0
    if args.solve:
        game = load_puzzle(args.puzzle)
        sol = solve(game)
        if sol is None:
            print("无解")
            return 1
        print(f"{len(sol)} 步解法:")
        for vid, step in sol:
            print(f"  {vid} {'+' if step > 0 else '-'}")
        return 0
    if not sys.stdin.isatty():
        print("交互模式需要终端; 请用 --auto 或 --solve", file=sys.stderr)
        return 2
    play_interactive(args.puzzle)
    return 0


if __name__ == "__main__":
    sys.exit(main())
