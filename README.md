# 指尖魔鼠

[![GitHub license](https://img.shields.io/github/license/GDNDZZK/FingertipMagicMouse.svg)](https://github.com/GDNDZZK/FingertipMagicMouse/blob/master/LICENSE) ![Python版本](https://img.shields.io/badge/python-3.7+-yellow)

在吃烧烤炸鸡等时戴着手套不方便操作,摘下手套又麻烦,直接操作怕弄脏,怎么办呢?指尖魔鼠它来了!隔空操作你的电脑!

[演示视频...还没做](https://www.bilibili.com/video/BV)

## 功能特点

- **手势控制**: 利用摄像头识别手势隔空操作鼠标，无需直接接触。
- **自定义手势**: 可自定义操作手势，适应不同用户习惯，例如单指点击、双指滚动等。
- **跨平台支持**: 支持 Windows、macOS 和 Linux 系统，方便不同用户使用。

## 使用方法

#### 1.使用Relese版本

1. 下载并解压7z压缩包
2. 运行程序:

   ```
   FingertipMagicMouse.exe
   ```
3. 开始使用键盘控制鼠标

#### 2.从源代码构建

1. 克隆或下载此仓库到本地
2. 确保你的Python版本在3.7及以上
3. 安装必要的Python库：

   ```shell
   pip install -r requirements.txt
   ```
4. 运行程序：

   ```
   app.py
   ```
5. 开始使用

## 默认手势

懒得写了,去看[配置文件](./config/config.ini)吧~

## 注意事项

- pynput在Linux Wayland下可能无法正常工作,如果你正在用Linux请使用X11
- Linux下运行如果出现报错 `ModuleNotFoundError: No module named 'tkinter'`请手动安装 `python3-tk`软件包,例如deb系使用 `sudo apt-get install python3-tk`

## 自定义设置

1. 在 `config.ini` 文件中，可以自定义触摸手势和设置参数
2. 每个设置项的功能请看注释

## 使用到的库

- [filterpy](https://github.com/rlabbe/filterpy): 卡尔曼滤波
- [mediapipe](https://github.com/google-ai-edge/mediapipe): 手势识别
- [numpy](https://github.com/numpy/numpy): 快速计算
- [opencv-python](https://github.com/opencv/opencv-python): 加载并简单处理摄像头画面
- [Pillow](https://github.com/python-pillow): 加载托盘图标的图像
- [pynput](https://github.com/moses-palmer/pynput): 控制鼠标
- [pystray](https://github.com/moses-palmer/pystray): 创建托盘图标

## 开发者

由 [GDNDZZK](https://github.com/GDNDZZK) 开发和维护

## 许可证

本项目使用 MIT 许可证，详情请参阅 [LICENSE](https://github.com/GDNDZZK/FingertipMagicMouse/blob/master/LICENSE) 文件
