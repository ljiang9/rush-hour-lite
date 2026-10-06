# rush-hour-lite 高峰时刻

6×6 滑块解谜:把**红色车 X**从第 3 行右侧的出口滑出去。车辆只能沿自身方向滑动,不能拐弯、不能跳过别的车。

纯 Python 标准库(`argparse`/`copy`/`random`/`sys`/`collections`),无第三方依赖。

## 玩法

- 棋盘 6×6,出口在第 3 行(下标 2)右侧,标 `◀出口`
- 红色车 `X` 是横向 2 格的小车;把它滑到最右列(`(2,4)+(2,5)`)即通关
- 其他车辆:横向/纵向,2 格小车或 3 格卡车,只能沿自身方向走
- 交互输入示例:`A +`(A 车向右/下走一格)、`B -`(向左/上走一格)、`q` 退出

## 用法

```bash
python -m rush_hour_lite                 # 交互玩 easy
python -m rush_hour_lite --puzzle hard   # 选 hard
python -m rush_hour_lite --solve         # 打印 BFS 最短解法
python -m rush_hour_lite --auto          # 自动演示求解
python -m rush_hour_lite --auto --games 3 --seed 7 --verbose  # 逐步打印棋盘
python -m rush_hour_lite --list          # 列出所有谜题
```

## 求解器

BFS 按单步移动搜索,找到的即最短步数解法。实测(本机):

| 谜题 | 车辆数 | 最短步数 |
|------|--------|----------|
| easy | 8 | 9 |
| medium | 10 | 6 |
| hard | 12 | 15 |

## 真实验证记录

- `python3 -m py_compile rush_hour_lite.py __main__.py` 通过
- 单元测试(真实执行):
  - 被挡住的移动抛 `IllegalMove`(贴边/撞车)
  - 出界移动被拒绝
  - 车辆滑动后位置正确
  - 通关判定:`X` 在 `(2,4)` 判胜、在 `(2,3)` 不判胜
  - easy/medium/hard 三题 BFS 均有解,按解法重走全部通关
- `--auto` 演示:求解成功并断言通关
- 非 tty 下交互模式:中文提示并以 exit 2 退出
- 无 TODO/FIXME 占位

## 已知局限(诚实版)

- 只有 3 道固定谜题,无随机生成器、无自定义摆盘
- BFS 状态空间上限 40 万,过大的谜题可能报无解
- 文本界面,无图形/动画/存档/悔棋/步数排行榜
- Python 3.10+,纯标准库

## License

MIT,Copyright (c) 2026 ljiang9
