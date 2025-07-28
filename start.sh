#!/bin/bash

# 设置颜色输出
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
BLUE="\033[0;34m"
NC="\033[0m" # No Color

echo -e "${GREEN}===== 启动 EasyCook 应用 =====${NC}"

# 检查是否已安装必要的工具
command -v python3 >/dev/null 2>&1 || { echo -e "${YELLOW}请先安装 Python 3${NC}"; exit 1; }
command -v npm >/dev/null 2>&1 || { echo -e "${YELLOW}请先安装 npm${NC}"; exit 1; }

# 创建虚拟环境（如果不存在）
if [ ! -d "backend/venv" ]; then
  echo -e "${BLUE}创建 Python 虚拟环境...${NC}"
  cd backend
  python3 -m venv venv
  cd ..
fi

# 激活虚拟环境并安装依赖
echo -e "${BLUE}安装后端依赖...${NC}"
cd backend
source venv/bin/activate
pip install -r requirements.txt

# 初始化数据库
echo -e "${BLUE}初始化数据库...${NC}"
python init_db.py

# 启动后端服务
echo -e "${GREEN}启动后端服务...${NC}"
python run.py &
BACKEND_PID=$!
cd ..

# 安装前端依赖
echo -e "${BLUE}安装前端依赖...${NC}"
cd frontend
npm install

# 启动前端服务
echo -e "${GREEN}启动前端服务...${NC}"
npm start &
FRONTEND_PID=$!
cd ..

echo -e "${GREEN}EasyCook 应用已启动!${NC}"
echo -e "${BLUE}后端服务运行在: http://localhost:5000${NC}"
echo -e "${BLUE}前端服务运行在: http://localhost:3000${NC}"
echo -e "${YELLOW}按 Ctrl+C 停止服务${NC}"

# 捕获 SIGINT 信号（Ctrl+C）
trap "echo -e '${YELLOW}正在停止服务...${NC}'; kill $BACKEND_PID $FRONTEND_PID; exit" INT

# 保持脚本运行
wait