#!/bin/bash

# 设置颜色输出
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
BLUE="\033[0;34m"
RED="\033[0;31m"
NC="\033[0m" # No Color

echo -e "${GREEN}===== EasyCook 应用升级脚本 =====${NC}"

# 设置变量
APP_DIR="/var/www/easycook"
BACKUP_DIR="/var/backups/easycook"
DATE=$(date +"%Y%m%d-%H%M%S")

# 检查是否在应用目录中运行
if [ "$(pwd)" != "$APP_DIR" ]; then
    echo -e "${YELLOW}当前不在应用目录中，正在切换到 $APP_DIR${NC}"
    cd "$APP_DIR" || {
        echo -e "${RED}无法切换到应用目录 $APP_DIR${NC}"
        exit 1
    }
fi

# 检查git仓库状态
if [ ! -d ".git" ]; then
    echo -e "${RED}当前目录不是git仓库${NC}"
    exit 1
fi

# 备份当前代码
echo -e "${BLUE}备份当前代码...${NC}"
mkdir -p "$BACKUP_DIR/code"
BACKUP_CODE_DIR="$BACKUP_DIR/code/easycook-$DATE"
cp -r "$APP_DIR" "$BACKUP_CODE_DIR"
echo -e "${GREEN}代码已备份到: $BACKUP_CODE_DIR${NC}"

# 备份数据库
echo -e "${BLUE}备份数据库...${NC}"
if [ -f "./backup.sh" ]; then
    ./backup.sh
else
    echo -e "${YELLOW}未找到数据库备份脚本，跳过数据库备份${NC}"
fi

# 获取当前分支
CURRENT_BRANCH=$(git symbolic-ref --short HEAD)
echo -e "${BLUE}当前分支: $CURRENT_BRANCH${NC}"

# 检查是否有未提交的更改
if [ -n "$(git status --porcelain)" ]; then
    echo -e "${YELLOW}警告: 本地有未提交的更改${NC}"
    git status
    echo -e "${YELLOW}是否继续? 这将丢弃所有本地更改 (y/n)${NC}"
    read -r CONTINUE
    if [ "$CONTINUE" != "y" ] && [ "$CONTINUE" != "Y" ]; then
        echo -e "${YELLOW}升级已取消${NC}"
        exit 0
    fi
    
    # 备份本地更改
    echo -e "${BLUE}备份本地更改...${NC}"
    git diff > "$BACKUP_DIR/local_changes-$DATE.patch"
    echo -e "${GREEN}本地更改已备份到: $BACKUP_DIR/local_changes-$DATE.patch${NC}"
    
    # 重置本地更改
    git reset --hard
fi

# 拉取最新代码
echo -e "${BLUE}拉取最新代码...${NC}"
git fetch --all
git pull origin "$CURRENT_BRANCH"

if [ $? -ne 0 ]; then
    echo -e "${RED}拉取代码失败${NC}"
    exit 1
fi

# 检查是否使用Docker部署
if [ -f "docker-compose.yml" ]; then
    echo -e "${BLUE}检测到Docker部署，更新Docker容器...${NC}"
    
    # 检查.env文件
    if [ ! -f ".env" ]; then
        echo -e "${YELLOW}未找到.env文件，将使用.env.example创建${NC}"
        if [ -f ".env.example" ]; then
            cp .env.example .env
            echo -e "${YELLOW}请编辑.env文件设置正确的配置${NC}"
            exit 1
        else
            echo -e "${RED}未找到.env.example文件，无法继续${NC}"
            exit 1
        fi
    fi
    
    # 重新构建并启动容器
    docker-compose build
    docker-compose up -d
    
    # 检查容器状态
    echo -e "${BLUE}检查容器状态...${NC}"
    docker-compose ps
else
    echo -e "${BLUE}检测到传统部署，更新应用...${NC}"
    
    # 更新前端依赖
    if [ -d "frontend" ]; then
        echo -e "${BLUE}更新前端依赖...${NC}"
        cd frontend || exit 1
        npm install
        npm run build
        cd ..
    fi
    
    # 更新后端依赖
    if [ -d "backend" ]; then
        echo -e "${BLUE}更新后端依赖...${NC}"
        cd backend || exit 1
        
        # 检查虚拟环境
        if [ -d "venv" ]; then
            source venv/bin/activate
        else
            python3 -m venv venv
            source venv/bin/activate
        fi
        
        pip install -r requirements.txt
        
        # 重启后端服务
        if command -v supervisorctl &> /dev/null; then
            echo -e "${BLUE}重启后端服务...${NC}"
            supervisorctl restart easycook_backend
        else
            echo -e "${YELLOW}未找到supervisorctl，请手动重启后端服务${NC}"
        fi
        
        cd ..
    fi
    
    # 重启Nginx
    if command -v nginx &> /dev/null; then
        echo -e "${BLUE}重启Nginx...${NC}"
        nginx -t && systemctl restart nginx
    fi
fi

# 运行数据库迁移（如果有）
if [ -f "backend/init_db.py" ]; then
    echo -e "${BLUE}运行数据库迁移...${NC}"
    if [ -f "docker-compose.yml" ]; then
        docker-compose exec backend python init_db.py
    else
        cd backend || exit 1
        source venv/bin/activate
        python init_db.py
        cd ..
    fi
fi

# 检查应用状态
if [ -f "monitor.sh" ]; then
    echo -e "${BLUE}检查应用状态...${NC}"
    ./monitor.sh
fi

echo -e "${GREEN}===== 升级完成 =====${NC}"
echo -e "当前版本: $(git describe --tags --always)"