#!/bin/bash

# 设置颜色输出
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
BLUE="\033[0;34m"
RED="\033[0;31m"
NC="\033[0m" # No Color

echo -e "${GREEN}===== 启动EasyCook应用（Conda环境）=====${NC}"

# 设置变量
CONDA_ENV_FRONTEND="easycook_frontend"
CONDA_ENV_BACKEND="easycook_backend"
APP_DIR="/var/www/easycook"
FRONTEND_DIR="${APP_DIR}/frontend"
BACKEND_DIR="${APP_DIR}/backend"
LOG_DIR="${APP_DIR}/logs"
BACKEND_PORT=8000

# 确保日志目录存在
mkdir -p "$LOG_DIR"

# 检查是否安装了conda
if ! command -v conda &> /dev/null; then
    echo -e "${RED}未安装conda，请先安装Miniconda或Anaconda${NC}"
    exit 1
fi

# 检查环境是否存在
if ! conda env list | grep -q "$CONDA_ENV_FRONTEND"; then
    echo -e "${RED}前端环境 ($CONDA_ENV_FRONTEND) 未安装，请先运行deploy-conda.sh${NC}"
    exit 1
fi

if ! conda env list | grep -q "$CONDA_ENV_BACKEND"; then
    echo -e "${RED}后端环境 ($CONDA_ENV_BACKEND) 未安装，请先运行deploy-conda.sh${NC}"
    exit 1
fi

# 启动后端服务
start_backend() {
    echo -e "${BLUE}启动后端服务...${NC}"
    cd "$BACKEND_DIR"
    
    # 激活conda环境
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate "$CONDA_ENV_BACKEND"
    
    # 使用nohup启动Gunicorn，并将输出重定向到日志文件
    nohup gunicorn --bind 0.0.0.0:$BACKEND_PORT --workers 3 --timeout 120 app:app > "$LOG_DIR/backend.log" 2>&1 &
    
    # 保存PID
    echo $! > "$APP_DIR/backend.pid"
    
    echo -e "${GREEN}后端服务已启动，PID: $(cat "$APP_DIR/backend.pid")${NC}"
}

# 检查服务状态
check_status() {
    echo -e "${BLUE}检查服务状态...${NC}"
    
    # 检查后端PID文件
    if [ -f "$APP_DIR/backend.pid" ]; then
        BACKEND_PID=$(cat "$APP_DIR/backend.pid")
        if ps -p $BACKEND_PID > /dev/null; then
            echo -e "${GREEN}后端服务正在运行，PID: $BACKEND_PID${NC}"
        else
            echo -e "${RED}后端服务未运行，但PID文件存在${NC}"
        fi
    else
        echo -e "${RED}后端服务未运行${NC}"
    fi
    
    # 检查Nginx状态
    if systemctl is-active --quiet nginx; then
        echo -e "${GREEN}Nginx服务正在运行${NC}"
    else
        echo -e "${RED}Nginx服务未运行${NC}"
    fi
}

# 停止服务
stop_services() {
    echo -e "${BLUE}停止服务...${NC}"
    
    # 停止后端服务
    if [ -f "$APP_DIR/backend.pid" ]; then
        BACKEND_PID=$(cat "$APP_DIR/backend.pid")
        if ps -p $BACKEND_PID > /dev/null; then
            echo -e "${YELLOW}停止后端服务，PID: $BACKEND_PID${NC}"
            kill $BACKEND_PID
            sleep 2
            # 如果进程仍在运行，强制终止
            if ps -p $BACKEND_PID > /dev/null; then
                echo -e "${RED}强制终止后端服务${NC}"
                kill -9 $BACKEND_PID
            fi
        else
            echo -e "${YELLOW}后端服务已经停止${NC}"
        fi
        rm -f "$APP_DIR/backend.pid"
    else
        echo -e "${YELLOW}未找到后端服务PID文件${NC}"
    fi
}

# 重启服务
restart_services() {
    echo -e "${BLUE}重启服务...${NC}"
    stop_services
    sleep 2
    start_backend
    echo -e "${GREEN}服务已重启${NC}"
}

# 显示帮助信息
show_help() {
    echo -e "${BLUE}用法: $0 [选项]${NC}"
    echo -e "管理EasyCook应用服务（Conda环境）"
    echo -e ""
    echo -e "选项:"
    echo -e "  start    启动服务"
    echo -e "  stop     停止服务"
    echo -e "  restart  重启服务"
    echo -e "  status   显示服务状态"
    echo -e "  help     显示此帮助信息"
}

# 主函数
main() {
    case "$1" in
        start)
            start_backend
            ;;
        stop)
            stop_services
            ;;
        restart)
            restart_services
            ;;
        status)
            check_status
            ;;
        help)
            show_help
            ;;
        *)
            echo -e "${RED}未知选项: $1${NC}"
            show_help
            exit 1
            ;;
    esac
}

# 如果没有参数，显示帮助信息
if [ $# -eq 0 ]; then
    show_help
    exit 0
fi

# 执行主函数
main "$1"

echo -e "${GREEN}===== 操作完成 =====${NC}"