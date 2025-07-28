#!/bin/bash

# 设置颜色输出
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
BLUE="\033[0;34m"
RED="\033[0;31m"
NC="\033[0m" # No Color

echo -e "${GREEN}===== EasyCook Conda部署脚本 =====${NC}"

# 设置变量
DOMAIN="easyfood.burning233.top"
API_DOMAIN="api.easyfood.burning233.top"
APP_DIR="/var/www/easycook"
FRONTEND_DIR="${APP_DIR}/frontend"
BACKEND_DIR="${APP_DIR}/backend"
CONDA_ENV_FRONTEND="easycook_frontend"
CONDA_ENV_BACKEND="easycook_backend"

# 检查是否安装了conda
if ! command -v conda &> /dev/null; then
    echo -e "${RED}未安装conda，请先安装Miniconda或Anaconda${NC}"
    exit 1
fi

# 检查是否安装了Nginx
if ! command -v nginx &> /dev/null; then
    echo -e "${RED}未安装Nginx，请先安装Nginx${NC}"
    exit 1
fi

# 检查是否安装了Certbot
if ! command -v certbot &> /dev/null; then
    echo -e "${RED}未安装Certbot，请先安装Certbot${NC}"
    exit 1
fi

# 创建应用目录
echo -e "${BLUE}创建应用目录...${NC}"
mkdir -p "$APP_DIR"

# 如果当前目录不是应用目录，则复制文件到应用目录
if [ "$(pwd)" != "$APP_DIR" ]; then
    echo -e "${BLUE}复制文件到应用目录...${NC}"
    cp -r ./* "$APP_DIR"
    cd "$APP_DIR"
fi

# 创建conda环境 - 前端
echo -e "${BLUE}创建前端conda环境...${NC}"
conda create -y -n "$CONDA_ENV_FRONTEND" nodejs=16

# 创建conda环境 - 后端
echo -e "${BLUE}创建后端conda环境...${NC}"
conda create -y -n "$CONDA_ENV_BACKEND" python=3.9

# 部署前端
echo -e "${BLUE}部署前端...${NC}"
cd "$FRONTEND_DIR"

# 激活前端环境并安装依赖
conda activate "$CONDA_ENV_FRONTEND"
npm install

# 创建API配置文件
echo -e "${BLUE}创建API配置文件...${NC}"
cat > src/services/api.config.js << EOL
// API配置文件
let API_BASE_URL;

// 根据环境设置API基础URL
if (process.env.NODE_ENV === 'production') {
  // 生产环境使用API域名
  API_BASE_URL = 'https://${API_DOMAIN}';
} else {
  // 开发环境使用相对路径
  API_BASE_URL = '/api';
}

export default API_BASE_URL;
EOL

# 更新API服务文件
echo -e "${BLUE}更新API服务文件...${NC}"
cat > src/services/api.js << EOL
import axios from 'axios';
import API_BASE_URL from './api.config';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = \`Bearer \${token}\`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default api;
EOL

# 构建前端
echo -e "${BLUE}构建前端...${NC}"
npm run build

# 部署后端
echo -e "${BLUE}部署后端...${NC}"
cd "$BACKEND_DIR"

# 激活后端环境并安装依赖
conda deactivate
conda activate "$CONDA_ENV_BACKEND"
pip install -r requirements.txt
pip install gunicorn

# 初始化数据库
echo -e "${BLUE}初始化数据库...${NC}"
python init_db.py

# 创建Gunicorn服务文件
echo -e "${BLUE}创建Gunicorn服务文件...${NC}"
cat > "$APP_DIR/gunicorn.service" << EOL
[Unit]
Description=Gunicorn instance to serve EasyCook backend
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=${BACKEND_DIR}
Environment="PATH=/home/$(whoami)/miniconda3/envs/${CONDA_ENV_BACKEND}/bin"
ExecStart=/home/$(whoami)/miniconda3/envs/${CONDA_ENV_BACKEND}/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 run:app
Restart=always

[Install]
WantedBy=multi-user.target
EOL

# 配置Nginx - 前端
echo -e "${BLUE}配置Nginx - 前端...${NC}"
cat > "/etc/nginx/sites-available/$DOMAIN" << EOL
server {
    listen 80;
    server_name ${DOMAIN} www.${DOMAIN};

    root ${FRONTEND_DIR}/build;
    index index.html;

    location / {
        try_files \$uri \$uri/ /index.html;
    }

    location ~* \.(js|css|png|jpg|jpeg|gif|ico)\$ {
        expires max;
        log_not_found off;
    }
}
EOL

# 配置Nginx - 后端API
echo -e "${BLUE}配置Nginx - 后端API...${NC}"
cat > "/etc/nginx/sites-available/$API_DOMAIN" << EOL
server {
    listen 80;
    server_name ${API_DOMAIN};

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOL

# 启用Nginx配置
echo -e "${BLUE}启用Nginx配置...${NC}"
ln -sf "/etc/nginx/sites-available/$DOMAIN" "/etc/nginx/sites-enabled/"
ln -sf "/etc/nginx/sites-available/$API_DOMAIN" "/etc/nginx/sites-enabled/"

# 测试Nginx配置
nginx -t

# 重启Nginx
echo -e "${BLUE}重启Nginx...${NC}"
systemctl restart nginx

# 申请SSL证书
echo -e "${BLUE}申请SSL证书...${NC}"
certbot --nginx -d "$DOMAIN" -d "www.$DOMAIN" -d "$API_DOMAIN"

# 创建启动脚本
echo -e "${BLUE}创建启动脚本...${NC}"
cat > "$APP_DIR/start-conda.sh" << EOL
#!/bin/bash

# 激活后端环境并启动服务
conda activate ${CONDA_ENV_BACKEND}
cd ${BACKEND_DIR}
gunicorn --workers 3 --bind 127.0.0.1:5000 run:app
EOL

chmod +x "$APP_DIR/start-conda.sh"

# 创建systemd服务
echo -e "${BLUE}创建systemd服务...${NC}"
cat > "/etc/systemd/system/easycook.service" << EOL
[Unit]
Description=EasyCook Application
After=network.target

[Service]
User=$(whoami)
WorkingDirectory=${APP_DIR}
ExecStart=${APP_DIR}/start-conda.sh
Restart=always

[Install]
WantedBy=multi-user.target
EOL

# 启动服务
echo -e "${BLUE}启动服务...${NC}"
systemctl daemon-reload
systemctl enable easycook.service
systemctl start easycook.service

echo -e "${GREEN}===== 部署完成 =====${NC}"
echo -e "前端地址: https://${DOMAIN}"
echo -e "后端API地址: https://${API_DOMAIN}"