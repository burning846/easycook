#!/bin/bash

# 设置颜色输出
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
BLUE="\033[0;34m"
RED="\033[0;31m"
NC="\033[0m" # No Color

echo -e "${GREEN}===== EasyCook Conda环境管理脚本 =====${NC}"

# 设置变量
CONDA_ENV_FRONTEND="easycook_frontend"
CONDA_ENV_BACKEND="easycook_backend"
APP_DIR="/var/www/easycook"
FRONTEND_DIR="${APP_DIR}/frontend"
BACKEND_DIR="${APP_DIR}/backend"

# 检查是否安装了conda
if ! command -v conda &> /dev/null; then
    echo -e "${RED}未安装conda，请先安装Miniconda或Anaconda${NC}"
    exit 1
fi

# 显示帮助信息
show_help() {
    echo -e "${BLUE}用法: $0 [选项]${NC}"
    echo -e "管理EasyCook应用的Conda环境"
    echo -e ""
    echo -e "选项:"
    echo -e "  update-frontend  更新前端环境依赖"
    echo -e "  update-backend   更新后端环境依赖"
    echo -e "  update-all       更新所有环境依赖"
    echo -e "  rebuild-frontend 重建前端环境"
    echo -e "  rebuild-backend  重建后端环境"
    echo -e "  rebuild-all      重建所有环境"
    echo -e "  status           显示环境状态"
    echo -e "  list             列出所有环境"
    echo -e "  help             显示此帮助信息"
}

# 更新前端环境
update_frontend() {
    echo -e "${BLUE}更新前端环境依赖...${NC}"
    conda activate "$CONDA_ENV_FRONTEND"
    cd "$FRONTEND_DIR"
    npm install
    npm update
    echo -e "${GREEN}前端环境依赖已更新${NC}"
}

# 更新后端环境
update_backend() {
    echo -e "${BLUE}更新后端环境依赖...${NC}"
    conda activate "$CONDA_ENV_BACKEND"
    cd "$BACKEND_DIR"
    pip install --upgrade -r requirements.txt
    echo -e "${GREEN}后端环境依赖已更新${NC}"
}

# 重建前端环境
rebuild_frontend() {
    echo -e "${BLUE}重建前端环境...${NC}"
    conda deactivate
    conda env remove -n "$CONDA_ENV_FRONTEND"
    conda create -y -n "$CONDA_ENV_FRONTEND" nodejs=16
    conda activate "$CONDA_ENV_FRONTEND"
    cd "$FRONTEND_DIR"
    npm install
    echo -e "${GREEN}前端环境已重建${NC}"
}

# 重建后端环境
rebuild_backend() {
    echo -e "${BLUE}重建后端环境...${NC}"
    conda deactivate
    conda env remove -n "$CONDA_ENV_BACKEND"
    conda create -y -n "$CONDA_ENV_BACKEND" python=3.9
    conda activate "$CONDA_ENV_BACKEND"
    cd "$BACKEND_DIR"
    pip install -r requirements.txt
    pip install gunicorn
    echo -e "${GREEN}后端环境已重建${NC}"
}

# 显示环境状态
show_status() {
    echo -e "${BLUE}Conda环境状态:${NC}"
    
    # 检查前端环境
    if conda env list | grep -q "$CONDA_ENV_FRONTEND"; then
        echo -e "${GREEN}前端环境 ($CONDA_ENV_FRONTEND) 已安装${NC}"
        conda activate "$CONDA_ENV_FRONTEND"
        echo -e "Node.js版本: $(node -v)"
        echo -e "npm版本: $(npm -v)"
        conda deactivate
    else
        echo -e "${RED}前端环境 ($CONDA_ENV_FRONTEND) 未安装${NC}"
    fi
    
    # 检查后端环境
    if conda env list | grep -q "$CONDA_ENV_BACKEND"; then
        echo -e "${GREEN}后端环境 ($CONDA_ENV_BACKEND) 已安装${NC}"
        conda activate "$CONDA_ENV_BACKEND"
        echo -e "Python版本: $(python --version)"
        echo -e "pip版本: $(pip --version)"
        conda deactivate
    else
        echo -e "${RED}后端环境 ($CONDA_ENV_BACKEND) 未安装${NC}"
    fi
}

# 列出所有环境
list_envs() {
    echo -e "${BLUE}所有Conda环境:${NC}"
    conda env list
}

# 主函数
main() {
    case "$1" in
        update-frontend)
            update_frontend
            ;;
        update-backend)
            update_backend
            ;;
        update-all)
            update_frontend
            update_backend
            ;;
        rebuild-frontend)
            rebuild_frontend
            ;;
        rebuild-backend)
            rebuild_backend
            ;;
        rebuild-all)
            rebuild_frontend
            rebuild_backend
            ;;
        status)
            show_status
            ;;
        list)
            list_envs
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