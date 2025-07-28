#!/bin/bash

# 设置颜色输出
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
BLUE="\033[0;34m"
RED="\033[0;31m"
NC="\033[0m" # No Color

echo -e "${GREEN}===== EasyCook Conda环境升级脚本 =====${NC}"

# 设置变量
CONDA_ENV_FRONTEND="easycook_frontend"
CONDA_ENV_BACKEND="easycook_backend"
APP_DIR="/var/www/easycook"
FRONTEND_DIR="${APP_DIR}/frontend"
BACKEND_DIR="${APP_DIR}/backend"
BACKUP_DIR="${APP_DIR}/backups"
LOG_DIR="${APP_DIR}/logs"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="${LOG_DIR}/upgrade_${TIMESTAMP}.log"

# 确保日志目录存在
mkdir -p "$LOG_DIR"
mkdir -p "$BACKUP_DIR"

# 记录日志函数
log() {
    echo -e "$1" | tee -a "$LOG_FILE"
}

# 检查是否安装了conda
if ! command -v conda &> /dev/null; then
    log "${RED}未安装conda，请先安装Miniconda或Anaconda${NC}"
    exit 1
fi

# 检查环境是否存在
if ! conda env list | grep -q "$CONDA_ENV_FRONTEND"; then
    log "${RED}前端环境 ($CONDA_ENV_FRONTEND) 未安装，请先运行deploy-conda.sh${NC}"
    exit 1
fi

if ! conda env list | grep -q "$CONDA_ENV_BACKEND"; then
    log "${RED}后端环境 ($CONDA_ENV_BACKEND) 未安装，请先运行deploy-conda.sh${NC}"
    exit 1
fi

# 备份代码和数据库
backup_code_and_db() {
    log "${BLUE}备份代码和数据库...${NC}"
    
    # 备份代码
    tar -czf "${BACKUP_DIR}/code_backup_${TIMESTAMP}.tar.gz" -C "$(dirname $APP_DIR)" "$(basename $APP_DIR)" --exclude="${APP_DIR}/backups" --exclude="${APP_DIR}/logs" 2>> "$LOG_FILE"
    
    # 备份数据库
    if [ -f "${BACKEND_DIR}/app.db" ]; then
        # SQLite数据库
        cp "${BACKEND_DIR}/app.db" "${BACKUP_DIR}/app_db_backup_${TIMESTAMP}.db"
        log "${GREEN}SQLite数据库已备份${NC}"
    elif [ -f "${APP_DIR}/.env" ] && grep -q "DATABASE_URL=postgresql" "${APP_DIR}/.env"; then
        # PostgreSQL数据库
        source "${APP_DIR}/.env"
        DB_NAME=$(echo $DATABASE_URL | sed -E 's/.*\/([^\/]+)$/\1/')
        DB_USER=$(echo $DATABASE_URL | sed -E 's/.*:\/\/([^:]+):.*/\1/')
        
        if command -v pg_dump &> /dev/null; then
            pg_dump -U "$DB_USER" "$DB_NAME" > "${BACKUP_DIR}/pg_db_backup_${TIMESTAMP}.sql" 2>> "$LOG_FILE"
            log "${GREEN}PostgreSQL数据库已备份${NC}"
        else
            log "${RED}未找到pg_dump命令，无法备份PostgreSQL数据库${NC}"
        fi
    else
        log "${YELLOW}未找到数据库文件，跳过数据库备份${NC}"
    fi
    
    log "${GREEN}备份完成${NC}"
}

# 停止服务
stop_services() {
    log "${BLUE}停止服务...${NC}"
    ./start-conda.sh stop
    log "${GREEN}服务已停止${NC}"
}

# 拉取最新代码
pull_latest_code() {
    log "${BLUE}拉取最新代码...${NC}"
    
    # 检查是否有未提交的更改
    if [ -d "${APP_DIR}/.git" ]; then
        cd "$APP_DIR"
        if [ -n "$(git status --porcelain)" ]; then
            log "${YELLOW}存在未提交的更改，创建本地更改的补丁${NC}"
            git diff > "${BACKUP_DIR}/local_changes_${TIMESTAMP}.patch"
            git stash
        fi
        
        # 拉取最新代码
        git pull
        
        # 如果有本地更改的补丁，尝试应用
        if [ -f "${BACKUP_DIR}/local_changes_${TIMESTAMP}.patch" ]; then
            log "${YELLOW}尝试应用本地更改...${NC}"
            if git apply "${BACKUP_DIR}/local_changes_${TIMESTAMP}.patch"; then
                log "${GREEN}本地更改已应用${NC}"
            else
                log "${RED}无法应用本地更改，补丁文件保存在 ${BACKUP_DIR}/local_changes_${TIMESTAMP}.patch${NC}"
            fi
        fi
    else
        log "${RED}不是Git仓库，无法拉取最新代码${NC}"
        exit 1
    fi
    
    log "${GREEN}代码已更新${NC}"
}

# 更新前端
update_frontend() {
    log "${BLUE}更新前端...${NC}"
    
    # 激活conda环境
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate "$CONDA_ENV_FRONTEND"
    
    cd "$FRONTEND_DIR"
    
    # 安装依赖
    npm install
    
    # 构建前端
    npm run build
    
    log "${GREEN}前端已更新${NC}"
}

# 更新后端
update_backend() {
    log "${BLUE}更新后端...${NC}"
    
    # 激活conda环境
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate "$CONDA_ENV_BACKEND"
    
    cd "$BACKEND_DIR"
    
    # 安装依赖
    pip install --upgrade -r requirements.txt
    
    # 运行数据库迁移
    if [ -f "migrations/env.py" ]; then
        log "${BLUE}运行数据库迁移...${NC}"
        flask db upgrade
    fi
    
    log "${GREEN}后端已更新${NC}"
}

# 启动服务
start_services() {
    log "${BLUE}启动服务...${NC}"
    ./start-conda.sh start
    log "${GREEN}服务已启动${NC}"
}

# 检查服务状态
check_status() {
    log "${BLUE}检查服务状态...${NC}"
    ./start-conda.sh status
}

# 主函数
main() {
    log "${GREEN}开始升级 EasyCook 应用 (Conda环境)...${NC}"
    
    # 备份
    backup_code_and_db
    
    # 停止服务
    stop_services
    
    # 拉取最新代码
    pull_latest_code
    
    # 更新前端和后端
    update_frontend
    update_backend
    
    # 启动服务
    start_services
    
    # 检查状态
    check_status
    
    log "${GREEN}EasyCook 应用升级完成${NC}"
}

# 执行主函数
main