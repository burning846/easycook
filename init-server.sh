#!/bin/bash

# 设置颜色输出
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
BLUE="\033[0;34m"
RED="\033[0;31m"
NC="\033[0m" # No Color

echo -e "${GREEN}===== EasyCook 服务器初始化脚本 =====${NC}"

# 检查是否以root用户运行
if [ "$(id -u)" != "0" ]; then
   echo -e "${RED}此脚本必须以root用户运行${NC}" 1>&2
   exit 1
fi

# 更新系统
echo -e "${BLUE}更新系统...${NC}"
apt update && apt upgrade -y

# 安装基本工具
echo -e "${BLUE}安装基本工具...${NC}"
apt install -y curl wget git vim htop

# 安装Docker
echo -e "${BLUE}安装Docker...${NC}"
apt install -y apt-transport-https ca-certificates gnupg lsb-release
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
apt update
apt install -y docker-ce docker-ce-cli containerd.io

# 安装Docker Compose
echo -e "${BLUE}安装Docker Compose...${NC}"
curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# 安装Nginx
echo -e "${BLUE}安装Nginx...${NC}"
apt install -y nginx

# 安装Certbot
echo -e "${BLUE}安装Certbot...${NC}"
apt install -y certbot python3-certbot-nginx

# 配置防火墙
echo -e "${BLUE}配置防火墙...${NC}"
apt install -y ufw
ufw allow ssh
ufw allow http
ufw allow https
ufw --force enable

# 创建部署用户
echo -e "${BLUE}创建部署用户...${NC}"
adduser --disabled-password --gecos "" easycook
usermod -aG docker easycook
mkdir -p /home/easycook/.ssh
chmod 700 /home/easycook/.ssh

# 设置SSH密钥
echo -e "${YELLOW}请输入部署用户的SSH公钥:${NC}"
read -r SSH_KEY
echo "$SSH_KEY" > /home/easycook/.ssh/authorized_keys
chmod 600 /home/easycook/.ssh/authorized_keys
chown -R easycook:easycook /home/easycook/.ssh

# 创建应用目录
echo -e "${BLUE}创建应用目录...${NC}"
mkdir -p /var/www/easycook
chown -R easycook:easycook /var/www/easycook

# 配置Swap（如果内存小于2GB）
MEM_TOTAL=$(free -m | awk '/^Mem:/{print $2}')
if [ "$MEM_TOTAL" -lt 2048 ]; then
  echo -e "${BLUE}配置Swap空间...${NC}"
  fallocate -l 2G /swapfile
  chmod 600 /swapfile
  mkswap /swapfile
  swapon /swapfile
  echo '/swapfile none swap sw 0 0' >> /etc/fstab
fi

# 设置时区
echo -e "${BLUE}设置时区...${NC}"
timedatectl set-timezone Asia/Shanghai

# 安装Node.js（用于前端构建）
echo -e "${BLUE}安装Node.js...${NC}"
curl -fsSL https://deb.nodesource.com/setup_16.x | bash -
apt install -y nodejs

# 安装Python环境（用于后端）
echo -e "${BLUE}安装Python环境...${NC}"
apt install -y python3 python3-pip python3-venv

echo -e "${GREEN}===== 服务器初始化完成! =====${NC}"
echo -e "现在您可以使用以下命令部署EasyCook应用:"
echo -e "${BLUE}su - easycook${NC}"
echo -e "${BLUE}git clone <repository-url> /var/www/easycook${NC}"
echo -e "${BLUE}cd /var/www/easycook${NC}"
echo -e "${BLUE}./deploy-docker.sh${NC}"