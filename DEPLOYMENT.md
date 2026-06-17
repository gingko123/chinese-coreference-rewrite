# 云服务器 + Nginx + 域名部署流程

本文档说明如何将 Streamlit 应用部署到云服务器，并通过域名访问。

示例目标：

```text
http://your-domain.com
https://your-domain.com
```

## 1. 准备条件

需要准备：

- 一台 Linux 云服务器，推荐 Ubuntu 22.04。
- 一个已备案或可正常解析的域名。
- 服务器公网 IP。
- GitHub 仓库地址。
- 云服务器安全组放行端口：
  - `22`：SSH 登录
  - `80`：HTTP
  - `443`：HTTPS

不建议直接暴露 `8501` 端口给公网。正式方案中，Streamlit 只监听本机 `127.0.0.1:8501`，由 Nginx 对外提供访问。

## 2. 域名解析

在域名服务商后台添加一条 A 记录：

```text
主机记录：@
记录类型：A
记录值：你的服务器公网 IP
```

如果想使用 `www`：

```text
主机记录：www
记录类型：A
记录值：你的服务器公网 IP
```

等待 DNS 生效后，可以在本地测试：

```bash
ping your-domain.com
```

## 3. 登录服务器

```bash
ssh root@你的服务器公网IP
```

如果不是 root 用户，请使用你的云服务器用户名。

## 4. 安装系统依赖

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git nginx
```

检查版本：

```bash
python3 --version
nginx -v
```

## 5. 拉取项目代码

建议放在 `/opt` 目录：

```bash
cd /opt
sudo git clone https://github.com/gingko123/chinese-coreference-rewrite.git
sudo chown -R $USER:$USER chinese-coreference-rewrite
cd chinese-coreference-rewrite
```

如果服务器无法访问 GitHub，可以先在本地打包上传，或给服务器配置代理。

## 6. 创建 Python 虚拟环境

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

测试 Streamlit 是否可启动：

```bash
streamlit run app.py --server.address 127.0.0.1 --server.port 8501
```

看到启动成功后，按 `Ctrl + C` 退出。

## 7. 创建 systemd 服务

创建服务文件：

```bash
sudo nano /etc/systemd/system/coreference-app.service
```

写入以下内容：

```ini
[Unit]
Description=Chinese Coreference Rewrite Streamlit App
After=network.target

[Service]
User=你的Linux用户名
WorkingDirectory=/opt/chinese-coreference-rewrite
Environment="PATH=/opt/chinese-coreference-rewrite/.venv/bin"
ExecStart=/opt/chinese-coreference-rewrite/.venv/bin/streamlit run app.py --server.address 127.0.0.1 --server.port 8501 --server.headless true --browser.gatherUsageStats false
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

注意替换：

```text
User=你的Linux用户名
```

如果你使用 root 部署，则可以写：

```text
User=root
```

加载并启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable coreference-app
sudo systemctl start coreference-app
```

查看状态：

```bash
sudo systemctl status coreference-app
```

查看日志：

```bash
sudo journalctl -u coreference-app -f
```

## 8. 配置 Nginx 反向代理

创建 Nginx 配置：

```bash
sudo nano /etc/nginx/sites-available/coreference-app
```

写入：

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        proxy_read_timeout 86400;
    }
}
```

注意替换：

```text
your-domain.com
www.your-domain.com
```

启用配置：

```bash
sudo ln -s /etc/nginx/sites-available/coreference-app /etc/nginx/sites-enabled/
```

测试 Nginx 配置：

```bash
sudo nginx -t
```

重启 Nginx：

```bash
sudo systemctl reload nginx
```

现在访问：

```text
http://your-domain.com
```

应该可以看到 Streamlit 页面。

## 9. 配置 HTTPS

安装 Certbot：

```bash
sudo apt install -y certbot python3-certbot-nginx
```

申请证书：

```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

按提示选择是否自动跳转 HTTPS。推荐选择自动跳转。

测试自动续期：

```bash
sudo certbot renew --dry-run
```

配置成功后访问：

```text
https://your-domain.com
```

## 10. 更新项目代码

以后如果本地代码更新并推送到了 GitHub，服务器上执行：

```bash
cd /opt/chinese-coreference-rewrite
git pull
source .venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart coreference-app
```

## 11. 常见问题

### 11.1 页面打不开

检查服务是否运行：

```bash
sudo systemctl status coreference-app
```

检查 Nginx：

```bash
sudo nginx -t
sudo systemctl status nginx
```

检查安全组是否放行 `80` 和 `443`。

### 11.2 502 Bad Gateway

通常说明 Nginx 能访问，但 Streamlit 没启动。

查看日志：

```bash
sudo journalctl -u coreference-app -n 100
```

### 11.3 WebSocket 报错

Streamlit 需要 WebSocket，Nginx 配置中必须包含：

```nginx
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
```

### 11.4 HanLP / LTP 没有启用

当前项目默认使用规则版 baseline。HanLP / LTP 是可选增强接口。如果服务器没有安装对应库，页面会提示并自动回退，不影响演示。

## 12. 推荐展示方式

期末展示时可以这样介绍：

```text
系统已部署为 Web Demo，用户可以通过域名访问。
后端使用 Streamlit 提供交互界面，Nginx 负责公网反向代理。
系统支持单文本分析、数据集评估、真实语料错误分析和可选 NLP 后端切换。
```

