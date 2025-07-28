#!/bin/bash

# 设置颜色输出
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
BLUE="\033[0;34m"
RED="\033[0;31m"
NC="\033[0m" # No Color

echo -e "${GREEN}===== EasyCook 数据库备份脚本 =====${NC}"

# 设置变量
BACKUP_DIR="/var/backups/easycook"
DATE=$(date +"%Y%m%d-%H%M%S")
APP_DIR="/var/www/easycook"
DB_FILE="${APP_DIR}/backend/instance/easycook.db"
ENV_FILE="${APP_DIR}/.env"

# 检查备份目录是否存在，不存在则创建
if [ ! -d "$BACKUP_DIR" ]; then
    mkdir -p "$BACKUP_DIR"
    echo -e "${BLUE}创建备份目录: $BACKUP_DIR${NC}"
fi

# 检查环境文件是否存在
if [ -f "$ENV_FILE" ]; then
    # 尝试从.env文件中读取数据库配置
    source "$ENV_FILE"
    echo -e "${BLUE}从.env文件加载配置${NC}"
fi

# 检查是否使用SQLite数据库
if [ -f "$DB_FILE" ]; then
    echo -e "${BLUE}检测到SQLite数据库，开始备份...${NC}"
    
    # 创建备份文件名
    BACKUP_FILE="${BACKUP_DIR}/easycook-sqlite-${DATE}.db"
    
    # 复制数据库文件
    cp "$DB_FILE" "$BACKUP_FILE"
    
    # 检查备份是否成功
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}SQLite数据库备份成功: $BACKUP_FILE${NC}"
        
        # 压缩备份文件
        gzip "$BACKUP_FILE"
        echo -e "${GREEN}备份文件已压缩: ${BACKUP_FILE}.gz${NC}"
    else
        echo -e "${RED}SQLite数据库备份失败${NC}"
        exit 1
    fi
# 检查是否使用PostgreSQL数据库
elif [ ! -z "${DATABASE_URL}" ] && [[ "${DATABASE_URL}" == postgres* ]]; then
    echo -e "${BLUE}检测到PostgreSQL数据库，开始备份...${NC}"
    
    # 从DATABASE_URL解析连接信息
    DB_USER=$(echo $DATABASE_URL | sed -n 's/.*:\/\/\([^:]*\):.*/\1/p')
    DB_PASS=$(echo $DATABASE_URL | sed -n 's/.*:\/\/[^:]*:\([^@]*\)@.*/\1/p')
    DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
    DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*@[^:]*:\([^\/]*\)\/.*/\1/p')
    DB_NAME=$(echo $DATABASE_URL | sed -n 's/.*\/\([^?]*\).*/\1/p')
    
    # 创建备份文件名
    BACKUP_FILE="${BACKUP_DIR}/easycook-postgres-${DATE}.sql"
    
    # 设置环境变量以避免在命令行中暴露密码
    export PGPASSWORD="$DB_PASS"
    
    # 执行PostgreSQL备份
    pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -F p > "$BACKUP_FILE"
    
    # 检查备份是否成功
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}PostgreSQL数据库备份成功: $BACKUP_FILE${NC}"
        
        # 压缩备份文件
        gzip "$BACKUP_FILE"
        echo -e "${GREEN}备份文件已压缩: ${BACKUP_FILE}.gz${NC}"
        
        # 清除环境变量
        unset PGPASSWORD
    else
        echo -e "${RED}PostgreSQL数据库备份失败${NC}"
        unset PGPASSWORD
        exit 1
    fi
else
    echo -e "${RED}未检测到支持的数据库配置${NC}"
    exit 1
fi

# 清理旧备份（保留最近30天的备份）
echo -e "${BLUE}清理旧备份...${NC}"
find "$BACKUP_DIR" -name "easycook-*.gz" -type f -mtime +30 -delete

# 列出当前备份
echo -e "${BLUE}当前备份文件:${NC}"
ls -lh "$BACKUP_DIR" | grep "easycook-"

# 计算备份总大小
BACKUP_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
echo -e "${GREEN}备份总大小: $BACKUP_SIZE${NC}"

echo -e "${GREEN}===== 备份完成 =====${NC}"

# 提示设置定时任务
echo -e "${YELLOW}提示: 您可以通过crontab设置定时备份任务:${NC}"
echo -e "例如，每天凌晨3点执行备份:"
echo -e "${BLUE}0 3 * * * /var/www/easycook/backup.sh > /var/log/easycook-backup.log 2>&1${NC}"