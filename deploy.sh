#!/bin/bash

# 设置颜色输出
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
BLUE="\033[0;34m"
RED="\033[0;31m"
NC="\033[0m" # No Color

echo -e "${GREEN}===== EasyCook 生产环境部署脚本 =====${NC}"

# 检查是否已安装必要的工具
command -v python3 >/dev/null 2>&1 || { echo -e "${RED}请先安装 Python 3${NC}"; exit 1; }
command -v npm >/dev/null 2>&1 || { echo -e "${RED}请先安装 npm${NC}"; exit 1; }
command -v nginx >/dev/null 2>&1 || { echo -e "${RED}请先安装 Nginx${NC}"; exit 1; }
command -v certbot >/dev/null 2>&1 || { echo -e "${RED}请先安装 Certbot${NC}"; exit 1; }

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 加载配置
source "$SCRIPT_DIR/deploy.config"

echo -e "${BLUE}使用以下配置:${NC}"
echo -e "域名: ${DOMAIN}"
echo -e "API子域名: ${API_SUBDOMAIN}"
echo -e "前端目录: ${FRONTEND_DIR}"
echo -e "后端目录: ${BACKEND_DIR}"

# 确认继续
read -p "是否继续部署? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo -e "${YELLOW}部署已取消${NC}"
  exit 0
fi

# 创建必要的目录
echo -e "${BLUE}创建必要的目录...${NC}"
sudo mkdir -p /var/www/${DOMAIN}/html
sudo mkdir -p /var/www/${API_SUBDOMAIN}.${DOMAIN}
sudo mkdir -p /var/log/easycook

# 设置目录权限
sudo chown -R $USER:$USER /var/www/${DOMAIN}
sudo chown -R $USER:$USER /var/www/${API_SUBDOMAIN}.${DOMAIN}
sudo chown -R $USER:$USER /var/log/easycook

# 构建前端
echo -e "${BLUE}构建前端应用...${NC}"
cd "$FRONTEND_DIR"
npm install
npm run build

# 复制前端文件到网站目录
echo -e "${BLUE}部署前端文件...${NC}"
cp -r dist/* /var/www/${DOMAIN}/html/

# 创建前端环境变量文件
echo -e "${BLUE}创建前端环境配置...${NC}"
cat > /var/www/${DOMAIN}/html/env-config.js << EOL
window.ENV = {
  API_URL: "https://${API_SUBDOMAIN}.${DOMAIN}"
};
EOL

# 设置后端环境
echo -e "${BLUE}设置后端环境...${NC}"
cd "$BACKEND_DIR"

# 创建虚拟环境（如果不存在）
if [ ! -d "venv" ]; then
  echo -e "${BLUE}创建 Python 虚拟环境...${NC}"
  python3 -m venv venv
fi

# 激活虚拟环境并安装依赖
echo -e "${BLUE}安装后端依赖...${NC}"
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn

# 更新后端环境变量
echo -e "${BLUE}更新后端环境变量...${NC}"
cat > .env << EOL
SECRET_KEY=${SECRET_KEY}
DATABASE_URL=${DATABASE_URL}
GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID}
GOOGLE_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET}
FRONTEND_URL=https://${DOMAIN}
EOL

# 初始化数据库
echo -e "${BLUE}初始化数据库...${NC}"
python init_db.py

# 复制后端文件到网站目录
echo -e "${BLUE}部署后端文件...${NC}"
rsync -av --exclude="venv" --exclude="__pycache__" --exclude=".git" . /var/www/${API_SUBDOMAIN}.${DOMAIN}/

# 创建Gunicorn服务文件
echo -e "${BLUE}创建Gunicorn服务文件...${NC}"
sudo tee /etc/systemd/system/easycook.service > /dev/null << EOL
[Unit]
Description=Gunicorn instance to serve EasyCook backend
After=network.target

[Service]
User=${USER}
Group=www-data
WorkingDirectory=/var/www/${API_SUBDOMAIN}.${DOMAIN}
Environment="PATH=/var/www/${API_SUBDOMAIN}.${DOMAIN}/venv/bin"
ExecStart=/var/www/${API_SUBDOMAIN}.${DOMAIN}/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 --error-logfile /var/log/easycook/error.log --access-logfile /var/log/easycook/access.log run:app

[Install]
WantedBy=multi-user.target
EOL

# 创建Nginx配置文件 - 前端
echo -e "${BLUE}创建Nginx前端配置...${NC}"
sudo tee /etc/nginx/sites-available/${DOMAIN} > /dev/null << EOL
server {
    listen 80;
    server_name ${DOMAIN} www.${DOMAIN};

    root /var/www/${DOMAIN}/html;
    index index.html;

    location / {
        try_files \$uri \$uri/ /index.html;
    }

    location ~* \.(?:css|js|jpg|jpeg|gif|png|ico|svg|woff|woff2|ttf|eot)\$ {
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }

    # 错误日志
    error_log /var/log/nginx/${DOMAIN}_error.log;
    access_log /var/log/nginx/${DOMAIN}_access.log;
}
EOL

# 创建Nginx配置文件 - 后端API
echo -e "${BLUE}创建Nginx后端API配置...${NC}"
sudo tee /etc/nginx/sites-available/${API_SUBDOMAIN}.${DOMAIN} > /dev/null << EOL
server {
    listen 80;
    server_name ${API_SUBDOMAIN}.${DOMAIN};

    location / {
        include proxy_params;
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # 错误日志
    error_log /var/log/nginx/${API_SUBDOMAIN}.${DOMAIN}_error.log;
    access_log /var/log/nginx/${API_SUBDOMAIN}.${DOMAIN}_access.log;
}
EOL

# 启用Nginx配置
echo -e "${BLUE}启用Nginx配置...${NC}"
sudo ln -sf /etc/nginx/sites-available/${DOMAIN} /etc/nginx/sites-enabled/
sudo ln -sf /etc/nginx/sites-available/${API_SUBDOMAIN}.${DOMAIN} /etc/nginx/sites-enabled/

# 测试Nginx配置
echo -e "${BLUE}测试Nginx配置...${NC}"
sudo nginx -t

# 重启Nginx
echo -e "${BLUE}重启Nginx...${NC}"
sudo systemctl restart nginx

# 启动Gunicorn服务
echo -e "${BLUE}启动Gunicorn服务...${NC}"
sudo systemctl start easycook
sudo systemctl enable easycook

# 申请SSL证书
echo -e "${BLUE}申请SSL证书...${NC}"
sudo certbot --nginx -d ${DOMAIN} -d www.${DOMAIN} -d ${API_SUBDOMAIN}.${DOMAIN}

# 设置自动更新证书的定时任务
echo -e "${BLUE}设置证书自动更新...${NC}"
(crontab -l 2>/dev/null; echo "0 3 * * * /usr/bin/certbot renew --quiet") | crontab -

echo -e "${GREEN}===== EasyCook 部署完成! =====${NC}"
echo -e "前端网址: https://${DOMAIN}"
echo -e "API网址: https://${API_SUBDOMAIN}.${DOMAIN}"