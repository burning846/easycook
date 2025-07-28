#!/bin/bash

# 设置颜色输出
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
BLUE="\033[0;34m"
RED="\033[0;31m"
NC="\033[0m" # No Color

echo -e "${GREEN}===== EasyCook 清理脚本 =====${NC}"

# 设置变量
APP_DIR="/var/www/easycook"
BACKUP_DIR="/var/backups/easycook"
LOG_DIR="/var/log"
RETAIN_DAYS=30

# 检查是否在应用目录中运行
if [ "$(pwd)" != "$APP_DIR" ]; then
    echo -e "${YELLOW}当前不在应用目录中，正在切换到 $APP_DIR${NC}"
    cd "$APP_DIR" || {
        echo -e "${RED}无法切换到应用目录 $APP_DIR${NC}"
        exit 1
    }
fi

# 清理临时文件
echo -e "${BLUE}清理临时文件...${NC}"
find . -type f -name "*.tmp" -delete
find . -type f -name "*.bak" -mtime +7 -delete
find . -type f -name "*.pyc" -delete
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type d -name ".pytest_cache" -exec rm -rf {} +

# 清理前端构建缓存
if [ -d "frontend/node_modules/.cache" ]; then
    echo -e "${BLUE}清理前端构建缓存...${NC}"
    rm -rf frontend/node_modules/.cache
fi

# 清理Docker缓存（如果使用Docker）
if command -v docker &> /dev/null; then
    echo -e "${BLUE}清理未使用的Docker资源...${NC}"
    docker system prune -f
fi

# 清理旧的备份文件
if [ -d "$BACKUP_DIR" ]; then
    echo -e "${BLUE}清理旧的备份文件...${NC}"
    
    # 计算备份总大小
    BACKUP_SIZE_BEFORE=$(du -sh "$BACKUP_DIR" | cut -f1)
    echo -e "${YELLOW}清理前备份总大小: $BACKUP_SIZE_BEFORE${NC}"
    
    # 清理超过保留天数的数据库备份
    find "$BACKUP_DIR" -name "easycook-*.gz" -type f -mtime +$RETAIN_DAYS -delete
    
    # 保留最近10个代码备份，删除其余的
    if [ -d "$BACKUP_DIR/code" ]; then
        cd "$BACKUP_DIR/code" || exit 1
        ls -t | tail -n +11 | xargs rm -rf
        cd "$APP_DIR" || exit 1
    fi
    
    # 计算清理后的备份总大小
    BACKUP_SIZE_AFTER=$(du -sh "$BACKUP_DIR" | cut -f1)
    echo -e "${GREEN}清理后备份总大小: $BACKUP_SIZE_AFTER${NC}"
fi

# 清理日志文件
echo -e "${BLUE}清理旧的日志文件...${NC}"

# 清理应用日志
find "$APP_DIR/logs" -name "*.log.*" -type f -mtime +$RETAIN_DAYS -delete 2>/dev/null

# 清理系统日志
if [ -d "$LOG_DIR" ]; then
    find "$LOG_DIR" -name "easycook-*.log.*" -type f -mtime +$RETAIN_DAYS -delete 2>/dev/null
fi

# 清理会话文件（如果使用Flask）
if [ -d "backend/instance/sessions" ]; then
    echo -e "${BLUE}清理过期会话文件...${NC}"
    find backend/instance/sessions -type f -mtime +7 -delete
fi

# 清理未使用的依赖包
echo -e "${BLUE}清理未使用的依赖包...${NC}"

# 清理Python虚拟环境（可选，谨慎使用）
if [ -d "backend/venv" ] && [ "$1" = "--deep" ]; then
    echo -e "${YELLOW}执行深度清理 - 重建Python虚拟环境${NC}"
    cd backend || exit 1
    rm -rf venv
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
fi

# 清理前端node_modules（可选，谨慎使用）
if [ -d "frontend/node_modules" ] && [ "$1" = "--deep" ]; then
    echo -e "${YELLOW}执行深度清理 - 重建前端依赖${NC}"
    cd frontend || exit 1
    rm -rf node_modules
    npm install
    cd ..
fi

# 显示磁盘使用情况
echo -e "${BLUE}当前磁盘使用情况:${NC}"
df -h

echo -e "${GREEN}===== 清理完成 =====${NC}"