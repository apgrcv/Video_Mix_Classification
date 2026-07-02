# 视频分类工具

将视频文件按“开头键”进行分组，确保每个目标文件夹内开头键不重复，并支持限制每个文件夹最多文件数。

## 功能特性

- 自动识别”剧名开头编号”或”开头编号”两种命名格式
- 预览与执行分离，先看结果再移动
- 每个文件夹文件数上限可配置，默认 25
- **剧名严格分离模式（v1.4 新增）**：可选启用，确保同一文件夹内剧名也互不相同
- 同时提供命令行与 Tkinter 可视化界面
- 跨平台支持 Windows / macOS

## 快速开始

### 方式一：可视化界面（推荐）

- Windows 双击：`启动GUI.bat`
- macOS 双击：`启动GUI.command`

进入界面后可直接选择目录、设置参数、预览和执行。

### 方式二：命令行

```bash
# 预览（默认模式）
python 视频分类脚本.py "目录路径" -m 25

# 预览（剧名严格分离模式）
python 视频分类脚本.py "目录路径" -m 25 --strict-drama-separation

# 执行
python 视频分类脚本.py "目录路径" -e -m 25
```

## 文件说明

| 文件 | 说明 |
|------|------|
| `视频分类脚本.py` | 核心逻辑与命令行入口 |
| `视频分类GUI.py` | Tkinter 可视化工具 |
| `video_classifier_cli.py` | Windows 兼容命令行包装入口（避免中文文件名编码问题） |
| `video_classifier_gui.py` | Windows 兼容 GUI 包装入口（避免中文文件名编码问题） |
| `启动GUI.bat` | Windows GUI 启动脚本 |
| `启动GUI.command` | macOS GUI 启动脚本 |
| `预览.bat` / `执行.bat` | Windows 命令行快速启动脚本 |
| `预览.command` / `执行.command` | macOS 命令行快速启动脚本 |
| `使用说明.md` | 详细使用文档 |
| `项目全景上下文.md` | 项目背景与演进文档 |

## 环境要求

- Python 3.6+
- Tkinter（大多数 Python 发行版已内置）

## Windows 兼容性说明

部分 Windows 电脑在 `cmd` 中会对中文批处理或中文脚本文件名出现编码兼容问题，表现为双击 `.bat` 后提示“不是内部或外部命令”或把中文文件名显示成乱码。

当前项目已提供英文包装入口：

- `video_classifier_gui.py`
- `video_classifier_cli.py`

Windows 下的 `.bat` 已默认改为调用这两个英文入口，以提高兼容性。

## 许可证

MIT
