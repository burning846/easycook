#!/bin/bash

# 设置颜色输出
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
BLUE="\033[0;34m"
RED="\033[0;31m"
NC="\033[0m" # No Color

echo -e "${GREEN}===== EasyCook 数据库恢复脚本 =====${NC}"

# 设置变量
BACKUP_DIR="/var/backups/easycook"
APP_DIR="/var/www/easycook"
DB_FILE="${APP_DIR}/backend/instance/easycook.db"
ENV_FILE="${APP_DIR}/.env"

# 检查备份目录是否存在
if [ ! -d "$BACKUP_DIR" ]; then
    echo -e "${RED}备份目录不存在: $BACKUP_DIR${NC}"
    exit 1
fi

# 检查环境文件是否存在
if [ -f "$ENV_FILE" ]; then
    # 尝试从.env文件中读取数据库配置
    source "$ENV_FILE"
    echo -e "${BLUE}从.env文件加载配置${NC}"
fi

# 列出可用备份
echo -e "${BLUE}可用备份文件:${NC}"
ls -lt "$BACKUP_DIR" | grep "easycook-" | nl

# 询问用户选择哪个备份文件
echo -e "${YELLOW}请输入要恢复的备份文件编号:${NC}"
read -r BACKUP_NUM

# 获取选择的备份文件路径
BACKUP_FILE=$(ls -lt "$BACKUP_DIR" | grep "easycook-" | awk '{print $9}' | sed -n "${BACKUP_NUM}p")
BACKUP_PATH="${BACKUP_DIR}/${BACKUP_FILE}"

if [ ! -f "$BACKUP_PATH" ]; then
    echo -e "${RED}备份文件不存在: $BACKUP_PATH${NC}"
    exit 1
fi

echo -e "${BLUE}选择的备份文件: $BACKUP_PATH${NC}"

# 确认恢复操作
echo -e "${RED}警告: 恢复操作将覆盖当前数据库。此操作不可逆!${NC}"
echo -e "${YELLOW}是否继续? (y/n)${NC}"
read -r CONFIRM

if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
    echo -e "${YELLOW}操作已取消${NC}"
    exit 0
fi

# 检查是否为压缩文件，如果是则解压
if [[ "$BACKUP_PATH" == *.gz ]]; then
    echo -e "${BLUE}解压备份文件...${NC}"
    TEMP_FILE="${BACKUP_PATH%.gz}"
    gunzip -c "$BACKUP_PATH" > "$TEMP_FILE"
    BACKUP_PATH="$TEMP_FILE"
    echo -e "${GREEN}备份文件已解压: $BACKUP_PATH${NC}"
fi

# 根据备份文件类型执行恢复操作
if [[ "$BACKUP_PATH" == *sqlite* ]] || [[ "$BACKUP_PATH" == *.db ]]; then
    echo -e "${BLUE}检测到SQLite备份，开始恢复...${NC}"
    
    # 停止应用服务
    echo -e "${BLUE}停止应用服务...${NC}"
    if [ -f "${APP_DIR}/docker-compose.yml" ]; then
        cd "$APP_DIR" && docker-compose down
    else
        echo -e "${YELLOW}无法自动停止服务，请确保应用已停止${NC}"
    fi
    
    # 备份当前数据库
    if [ -f "$DB_FILE" ]; then
        CURRENT_BACKUP="${DB_FILE}.bak.$(date +"%Y%m%d-%H%M%S")"
        cp "$DB_FILE" "$CURRENT_BACKUP"
        echo -e "${GREEN}当前数据库已备份: $CURRENT_BACKUP${NC}"
    fi
    
    # 恢复数据库
    cp "$BACKUP_PATH" "$DB_FILE"
    
    # 检查恢复是否成功
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}SQLite数据库恢复成功${NC}"
        
        # 启动应用服务
        echo -e "${BLUE}启动应用服务...${NC}"
        if [ -f "${APP_DIR}/docker-compose.yml" ]; then
            cd "$APP_DIR" && docker-compose up -d
        else
            echo -e "${YELLOW}请手动启动应用服务${NC}"
        fi
    else
        echo -e "${RED}SQLite数据库恢复失败${NC}"
        exit 1
    fi
    
elif [[ "$BACKUP_PATH" == *postgres* ]] || [[ "$BACKUP_PATH" == *.sql ]]; then
    echo -e "${BLUE}检测到PostgreSQL备份，开始恢复...${NC}"
    
    # 从DATABASE_URL解析连接信息
    if [ -z "${DATABASE_URL}" ] || [[ "${DATABASE_URL}" != postgres* ]]; then
        echo -e "${RED}未找到有效的PostgreSQL连接信息${NC}"
        exit 1
    fi
    
    DB_USER=$(echo $DATABASE_URL | sed -n 's/.*:\/\/\([^:]*\):.*/\1/p')
    DB_PASS=$(echo $DATABASE_URL | sed -n 's/.*:\/\/[^:]*:\([^@]*\)@.*/\1/p')
    DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
    DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*@[^:]*:\([^\/]*\)\/.*/\1/p')
    DB_NAME=$(echo $DATABASE_URL | sed -n 's/.*\/\([^?]*\).*/\1/p')
    
    # 停止应用服务
    echo -e "${BLUE}停止应用服务...${NC}"
    if [ -f "${APP_DIR}/docker-compose.yml" ]; then
        cd "$APP_DIR" && docker-compose down
    else
        echo -e "${YELLOW}无法自动停止服务，请确保应用已停止${NC}"
    fi
    
    # 设置环境变量以避免在命令行中暴露密码
    export PGPASSWORD="$DB_PASS"
    
    # 执行PostgreSQL恢复
    echo -e "${BLUE}恢复PostgreSQL数据库...${NC}"
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$BACKUP_PATH"
    
    # 检查恢复是否成功
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}PostgreSQL数据库恢复成功${NC}"
        
        # 启动应用服务
        echo -e "${BLUE}启动应用服务...${NC}"
        if [ -f "${APP_DIR}/docker-compose.yml" ]; then
            cd "$APP_DIR" && docker-compose up -d
        else
            echo -e "${YELLOW}请手动启动应用服务${NC}"
        fi
        
        # 清除环境变量
        unset PGPASSWORD
    else
        echo -e "${RED}PostgreSQL数据库恢复失败${NC}"
        unset PGPASSWORD
        exit 1
    fi
else
    echo -e "${RED}未识别的备份文件类型${NC}"
    exit 1
fi

# 清理临时文件
if [[ "$BACKUP_PATH" != "$BACKUP_DIR"* ]]; then
    echo -e "${BLUE}清理临时文件...${NC}"
    rm -f "$BACKUP_PATH"
fi

echo -e "${GREEN}===== 恢复完成 =====${NC}"