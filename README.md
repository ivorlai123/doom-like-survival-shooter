# Doom-like Survival Shooter

这是一个使用 Python + Pygame 实现的 2.5D Doom-like FPS 程序设计大作业。项目采用 raycasting 渲染迷宫场景，包含随机地图、双武器、补给、Imp、Fast Demon、Boss 战、通关出口和结算记录等功能。

## 演示视频

北大网盘链接：TODO: 在这里填写演示视频链接

本地演示文件：`doom_fps_record.mp4`

## 运行方式

进入项目代码目录：

```powershell
cd "DoomLikeProject"
python main.py
```

如果本机缺少 Pygame：

```powershell
pip install pygame
```

## 操作说明

- `WASD`：移动
- 鼠标：视角转动
- 鼠标左键 / `SPACE`：射击
- `1`：切换手枪
- `2`：切换霰弹枪
- `M`：开关小地图
- `ESC`：暂停
- 主菜单 `1 / 2 / 3`：选择 Easy / Normal / Hard 难度

## 主要功能

- 2.5D raycasting 第一人称迷宫渲染
- 多张预设地图随机加载
- 手枪与霰弹枪双武器系统
- 霰弹枪弹药、血包、护甲包等资源管理
- Imp、Fast Demon、Boss 三类敌人
- Boss 二阶段强化和攻击预警
- 小地图、HUD、目标提示、暂停菜单和结算评级
- 击败 3 个 Boss 后开启中心 EXIT，进入后通关
- 最高分、最高波次、击杀数、Boss 击败数和胜利次数记录

## 提交材料

- 作业报告：`report/85-1 作业报告.pdf`
- 源代码地址：`85-1 原代码.txt`
- 程序代码目录：`DoomLikeProject/`
- 演示视频：请将视频上传到北大网盘，并把链接填入本 README 的“演示视频”部分

## 项目结构

- `main.py`：主循环、状态管理、射击、敌人波次、Boss、通关和结算
- `settings.py`：地图、常量、难度和资源路径
- `world.py`：raycasting 世界渲染
- `player.py`：玩家移动、生命、护甲和受击逻辑
- `enemy.py`：Imp、Fast Demon、Boss 和贴图绘制
- `effects.py`：火球、爆炸、补给和屏幕反馈
- `portal.py`：敌人和 Boss 传送门
- `ui.py`：HUD、小地图、菜单、暂停和结算界面
- `assets/`：敌人和传送门贴图素材
