#!/bin/bash

cd "$(dirname "$0")"
python3 视频分类脚本.py "." -m 25

echo ""
echo "按回车键退出..."
read
