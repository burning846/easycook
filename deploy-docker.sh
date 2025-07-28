#!/bin/bash

# 设置颜色输出
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
BLUE="\033[0;34m"
RED="\033[0;31m"
NC="\033[0m" # No Color

echo -e "${GREEN}===== EasyCook Docker部署脚本 =====${NC}"

# 检查是否已安装必要的工具
command -v docker >/dev/null 2>&1 || { echo -e "${RED}请先安装Docker${NC}"; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo -e "${RED}请先安装Docker Compose${NC}"; exit 1; }

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 检查.env文件是否存在
if [ ! -f ".env" ]; then
  echo -e "${YELLOW}未找到.env文件，将使用.env.example创建${NC}"
  if [ -f ".env.example" ]; then
    cp .env.example .env
    echo -e "${YELLOW}已创建.env文件，请编辑该文件并填入正确的配置信息${NC}"
    echo -e "${YELLOW}编辑完成后重新运行此脚本${NC}"
    exit 0
  else
    echo -e "${RED}未找到.env.example文件，无法继续${NC}"
    exit 1
  fi
fi

# 创建必要的目录
echo -e "${BLUE}创建必要的目录...${NC}"
mkdir -p logs/nginx logs/backend logs/frontend
mkdir -p certbot/conf certbot/www

# 确认继续
echo -e "${YELLOW}即将使用Docker部署EasyCook应用${NC}"
read -p "是否继续? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo -e "${YELLOW}部署已取消${NC}"
  exit 0
fi

# 构建并启动容器
echo -e "${BLUE}构建并启动Docker容器...${NC}"
docker-compose up -d --build

# 初始化数据库
echo -e "${BLUE}初始化数据库...${NC}"
docker-compose exec backend python init_db.py

# 获取SSL证书
echo -e "${BLUE}是否现在申请SSL证书? (需要确保域名已正确解析到服务器IP)${NC}"
read -p "申请SSL证书? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
  echo -e "${BLUE}申请SSL证书...${NC}"
  # 停止nginx容器
  docker-compose stop nginx
  
  # 从.env文件获取域名
  source .env
  
  # 运行certbot
  docker-compose run --rm certbot certonly --webroot -w /var/www/certbot \
    -d ${DOMAIN} -d www.${DOMAIN} -d api.${DOMAIN} \
    --email admin@${DOMAIN} --agree-tos --no-eff-email
  
  # 更新nginx配置以使用SSL
  sed -i 's/# listen 443 ssl;/listen 443 ssl;/g' nginx/easycook.conf
  sed -i 's/# ssl_certificate/ssl_certificate/g' nginx/easycook.conf
  sed -i 's/# ssl_certificate_key/ssl_certificate_key/g' nginx/easycook.conf
  sed -i 's/# include \/etc\/letsencrypt/include \/etc\/letsencrypt/g' nginx/easycook.conf
  sed -i 's/# ssl_dhparam/ssl_dhparam/g' nginx/easycook.conf
  
  # 重启nginx容器
  docker-compose start nginx
fi

echo -e "${GREEN}===== EasyCook部署完成! =====${NC}"
echo -e "前端网址: https://${DOMAIN}"
echo -e "API网址: https://api.${DOMAIN}"

echo -e "${BLUE}查看容器状态:${NC}"
docker-compose ps