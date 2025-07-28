#!/bin/bash

# 设置颜色输出
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
BLUE="\033[0;34m"
RED="\033[0;31m"
NC="\033[0m" # No Color

echo -e "${GREEN}===== EasyCook 安全检查脚本 =====${NC}"

# 检查文件权限
echo -e "${BLUE}检查文件权限...${NC}"

# 检查.env文件权限
if [ -f ".env" ]; then
    ENV_PERMS=$(stat -c "%a" .env 2>/dev/null || stat -f "%Lp" .env 2>/dev/null)
    if [ "$ENV_PERMS" != "600" ] && [ "$ENV_PERMS" != "400" ]; then
        echo -e "${RED}警告: .env 文件权限过于宽松 ($ENV_PERMS)，建议设置为 600${NC}"
        echo -e "${YELLOW}建议执行: chmod 600 .env${NC}"
    else
        echo -e "${GREEN}.env 文件权限正确${NC}"
    fi
fi

# 检查密钥文件权限
for KEY_FILE in $(find . -name "*.key" -o -name "*.pem" -o -path "*/certbot/conf/live/*/privkey.pem"); do
    KEY_PERMS=$(stat -c "%a" "$KEY_FILE" 2>/dev/null || stat -f "%Lp" "$KEY_FILE" 2>/dev/null)
    if [ "$KEY_PERMS" != "600" ] && [ "$KEY_PERMS" != "400" ]; then
        echo -e "${RED}警告: 密钥文件 $KEY_FILE 权限过于宽松 ($KEY_PERMS)，建议设置为 600${NC}"
        echo -e "${YELLOW}建议执行: chmod 600 $KEY_FILE${NC}"
    else
        echo -e "${GREEN}密钥文件 $KEY_FILE 权限正确${NC}"
    fi
done

# 检查敏感信息泄露
echo -e "${BLUE}检查敏感信息泄露...${NC}"

# 检查是否有硬编码的密钥或密码
SENSITIVE_PATTERNS=("password" "secret" "api_key" "apikey" "api-key" "access_key" "accesskey" "access-key" "private_key" "privatekey" "private-key")

for PATTERN in "${SENSITIVE_PATTERNS[@]}"; do
    FOUND_FILES=$(grep -l -r --include="*.py" --include="*.js" --include="*.jsx" --include="*.ts" --include="*.tsx" --include="*.json" --include="*.yml" --include="*.yaml" --exclude-dir="node_modules" --exclude-dir="venv" "$PATTERN" . 2>/dev/null)
    
    if [ -n "$FOUND_FILES" ]; then
        echo -e "${YELLOW}可能包含 '$PATTERN' 的文件:${NC}"
        for FILE in $FOUND_FILES; do
            echo -e "${YELLOW}- $FILE${NC}"
        done
    fi
done

# 检查Docker安全配置
if [ -f "docker-compose.yml" ]; then
    echo -e "${BLUE}检查Docker安全配置...${NC}"
    
    # 检查是否有容器以root用户运行
    if grep -q "user:" docker-compose.yml; then
        echo -e "${GREEN}已配置容器非root用户运行${NC}"
    else
        echo -e "${YELLOW}警告: 未检测到容器用户配置，容器可能以root用户运行${NC}"
        echo -e "${YELLOW}建议在docker-compose.yml中添加user配置${NC}"
    fi
    
    # 检查是否限制容器资源
    if grep -q -E "(mem_limit|cpus|resources:)" docker-compose.yml; then
        echo -e "${GREEN}已配置容器资源限制${NC}"
    else
        echo -e "${YELLOW}警告: 未检测到容器资源限制配置${NC}"
        echo -e "${YELLOW}建议在docker-compose.yml中添加资源限制配置${NC}"
    fi
fi

# 检查SSL配置
echo -e "${BLUE}检查SSL配置...${NC}"

# 检查Nginx SSL配置
if [ -d "nginx" ]; then
    SSL_CONFIG_FILES=$(grep -l -r "ssl_" nginx/ 2>/dev/null)
    
    if [ -n "$SSL_CONFIG_FILES" ]; then
        echo -e "${GREEN}检测到SSL配置${NC}"
        
        # 检查是否禁用了不安全的SSL协议
        if grep -q "ssl_protocols" $SSL_CONFIG_FILES; then
            if grep -q "SSLv2\|SSLv3" $SSL_CONFIG_FILES; then
                echo -e "${RED}警告: 检测到不安全的SSL协议${NC}"
            else
                echo -e "${GREEN}SSL协议配置安全${NC}"
            fi
        else
            echo -e "${YELLOW}未检测到SSL协议配置${NC}"
        fi
        
        # 检查是否配置了安全的密码套件
        if grep -q "ssl_ciphers" $SSL_CONFIG_FILES; then
            echo -e "${GREEN}已配置SSL密码套件${NC}"
        else
            echo -e "${YELLOW}未检测到SSL密码套件配置${NC}"
        fi
    else
        echo -e "${YELLOW}未检测到SSL配置${NC}"
    fi
fi

# 检查防火墙配置
echo -e "${BLUE}检查防火墙配置...${NC}"
if command -v ufw &> /dev/null; then
    UFW_STATUS=$(ufw status | grep "Status:" | awk '{print $2}')
    if [ "$UFW_STATUS" = "active" ]; then
        echo -e "${GREEN}防火墙已启用${NC}"
        ufw status
    else
        echo -e "${RED}警告: 防火墙未启用${NC}"
        echo -e "${YELLOW}建议执行: sudo ufw enable${NC}"
    fi
else
    echo -e "${YELLOW}未安装ufw防火墙${NC}"
fi

# 检查日志文件权限
echo -e "${BLUE}检查日志文件权限...${NC}"
LOG_FILES=$(find . -name "*.log" 2>/dev/null)
for LOG_FILE in $LOG_FILES; do
    LOG_PERMS=$(stat -c "%a" "$LOG_FILE" 2>/dev/null || stat -f "%Lp" "$LOG_FILE" 2>/dev/null)
    if [ "$LOG_PERMS" != "640" ] && [ "$LOG_PERMS" != "644" ] && [ "$LOG_PERMS" != "600" ]; then
        echo -e "${YELLOW}日志文件 $LOG_FILE 权限为 $LOG_PERMS，建议设置为 640${NC}"
    fi
done

# 检查数据库文件权限
if [ -f "backend/instance/easycook.db" ]; then
    DB_PERMS=$(stat -c "%a" backend/instance/easycook.db 2>/dev/null || stat -f "%Lp" backend/instance/easycook.db 2>/dev/null)
    if [ "$DB_PERMS" != "600" ] && [ "$DB_PERMS" != "640" ]; then
        echo -e "${RED}警告: 数据库文件权限过于宽松 ($DB_PERMS)，建议设置为 600${NC}"
        echo -e "${YELLOW}建议执行: chmod 600 backend/instance/easycook.db${NC}"
    else
        echo -e "${GREEN}数据库文件权限正确${NC}"
    fi
fi

# 检查依赖项安全问题
echo -e "${BLUE}检查依赖项安全问题...${NC}"

# 检查前端依赖
if [ -f "frontend/package.json" ] && command -v npm &> /dev/null; then
    echo -e "${BLUE}检查前端依赖安全问题...${NC}"
    cd frontend && npm audit --json | grep -q '"severity":"high"\|"severity":"critical"' && {
        echo -e "${RED}检测到高危或严重安全问题${NC}"
        echo -e "${YELLOW}建议执行: cd frontend && npm audit fix${NC}"
    } || echo -e "${GREEN}未检测到高危或严重安全问题${NC}"
    cd ..
fi

# 检查后端依赖
if [ -f "backend/requirements.txt" ] && command -v pip &> /dev/null; then
    echo -e "${BLUE}检查后端依赖安全问题...${NC}"
    if command -v safety &> /dev/null; then
        cd backend && safety check -r requirements.txt --json | grep -q '"severity":"high"\|"severity":"critical"' && {
            echo -e "${RED}检测到高危或严重安全问题${NC}"
            echo -e "${YELLOW}请更新有安全问题的依赖${NC}"
        } || echo -e "${GREEN}未检测到高危或严重安全问题${NC}"
        cd ..
    else
        echo -e "${YELLOW}未安装safety工具，无法检查Python依赖安全问题${NC}"
        echo -e "${YELLOW}建议执行: pip install safety${NC}"
    fi
fi

echo -e "${GREEN}===== 安全检查完成 =====${NC}"