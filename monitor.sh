#!/bin/bash

# 设置颜色输出
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
BLUE="\033[0;34m"
RED="\033[0;31m"
NC="\033[0m" # No Color

echo -e "${GREEN}===== EasyCook 应用监控脚本 =====${NC}"

# 检查Docker是否运行
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker未安装${NC}"
    exit 1
fi

if ! systemctl is-active --quiet docker; then
    echo -e "${RED}Docker服务未运行${NC}"
    exit 1
fi

echo -e "${GREEN}Docker服务正常运行${NC}"

# 检查Docker Compose是否可用
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Docker Compose未安装${NC}"
    exit 1
fi

echo -e "${GREEN}Docker Compose可用${NC}"

# 检查容器状态
echo -e "${BLUE}检查容器状态...${NC}"
docker-compose ps

# 检查前端服务
echo -e "${BLUE}检查前端服务...${NC}"
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:80)
if [ "$FRONTEND_STATUS" -eq 200 ] || [ "$FRONTEND_STATUS" -eq 301 ] || [ "$FRONTEND_STATUS" -eq 302 ]; then
    echo -e "${GREEN}前端服务正常运行 (HTTP状态码: $FRONTEND_STATUS)${NC}"
else
    echo -e "${RED}前端服务异常 (HTTP状态码: $FRONTEND_STATUS)${NC}"
fi

# 检查后端API服务
echo -e "${BLUE}检查后端API服务...${NC}"
API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/api/recipes?per_page=1)
if [ "$API_STATUS" -eq 200 ]; then
    echo -e "${GREEN}后端API服务正常运行 (HTTP状态码: $API_STATUS)${NC}"
else
    echo -e "${RED}后端API服务异常 (HTTP状态码: $API_STATUS)${NC}"
fi

# 检查系统资源
echo -e "${BLUE}系统资源使用情况:${NC}"
echo -e "${YELLOW}CPU使用率:${NC}"
top -bn1 | grep "Cpu(s)" | awk '{print $2 + $4}' | awk '{print $1"%"}'

echo -e "${YELLOW}内存使用情况:${NC}"
free -h

echo -e "${YELLOW}磁盘使用情况:${NC}"
df -h

# 检查Docker容器资源使用情况
echo -e "${BLUE}Docker容器资源使用情况:${NC}"
docker stats --no-stream

# 检查日志文件大小
echo -e "${BLUE}检查日志文件大小...${NC}"
du -sh logs/* 2>/dev/null || echo "日志目录不存在"

# 检查SSL证书有效期
echo -e "${BLUE}检查SSL证书有效期...${NC}"
if [ -d "certbot/conf/live" ]; then
    for domain in certbot/conf/live/*; do
        if [ -d "$domain" ]; then
            domain_name=$(basename "$domain")
            if [ -f "$domain/cert.pem" ]; then
                expiry_date=$(openssl x509 -enddate -noout -in "$domain/cert.pem" | cut -d= -f2)
                expiry_epoch=$(date -d "$expiry_date" +%s)
                current_epoch=$(date +%s)
                days_left=$(( (expiry_epoch - current_epoch) / 86400 ))
                
                if [ "$days_left" -lt 30 ]; then
                    echo -e "${RED}域名 $domain_name 的SSL证书将在 $days_left 天后过期${NC}"
                else
                    echo -e "${GREEN}域名 $domain_name 的SSL证书有效期还剩 $days_left 天${NC}"
                fi
            fi
        fi
    done
else
    echo -e "${YELLOW}未找到SSL证书目录${NC}"
fi

echo -e "${GREEN}===== 监控完成 =====${NC}"