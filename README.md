# 视频处理Web应用

这是一个基于FastAPI的视频处理Web应用，支持视频的水平翻转、放大裁剪、旋转以及非关键帧删除等功能。

## 功能特点

- 视频水平翻转
- 视频放大（103%）并裁剪
- 视频旋转（默认2度）并充满画面
- 定期删除非关键帧（可配置间隔）
- 支持MP4格式输出

## 环境要求

- Python 3.9+
- FFmpeg 6.0+
- Conda包管理器

## 安装步骤

1. 克隆项目到本地
2. 使用Conda创建环境：
```bash
conda env create -f environment.yml
```
3. 激活环境：
```bash
conda activate video_processor
```

## 运行应用

1. 启动服务器：
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

2. 打开浏览器访问：`http://localhost:8000`

## 使用说明

1. 在网页界面上传视频文件（支持mp4、mov、avi、mkv格式）
2. 设置处理参数：
   - 旋转角度（默认2度）
   - 非关键帧删除间隔（默认10帧）
3. 点击"处理"按钮
4. 等待处理完成后下载结果文件

## 项目结构

```
.
├── main.py              # FastAPI应用主程序
├── video_processor.py   # 视频处理核心逻辑
├── templates/
│   └── index.html      # 前端页面模板
├── static/
│   └── css/
│       └── style.css   # 样式文件
├── tests/
│   └── test_app.py     # 测试用例
├── environment.yml      # Conda环境配置
└── README.md           # 项目说明文档
```

## 开发说明

- 视频处理使用FFmpeg实现
- 前端使用Bootstrap框架
- 支持异步处理大文件
- 包含基本的错误处理和日志记录

## 测试

运行测试用例：
```bash
pytest tests/
```

## 注意事项

- 上传文件大小限制：500MB
- 支持的视频格式：mp4、mov、avi、mkv
- 处理后的视频统一输出为MP4格式
- 确保系统已正确安装FFmpeg 