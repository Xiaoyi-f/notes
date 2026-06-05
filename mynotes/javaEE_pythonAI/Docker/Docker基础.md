# Docker 学习笔记

## 一、Docker 是什么

### 1.1 从问题开始

假设你开发了一个 Java Web 应用，要部署到服务器：

```
传统流程：
  买服务器 → 装 Linux → 装 JDK → 装 MySQL → 装 Redis → 
  配置环境变量 → 配置防火墙 → 部署项目 → 启动...

  🤦 问题：换一台服务器就要重新配置一遍！
  🤦 问题：同事的 Windows 能跑，你的 Mac 报错！
  🤦 问题："我本地能跑啊！" —— 环境不一致导致的经典甩锅
```

**Docker 的解决方案**：把你的应用 + 它依赖的所有环境（JDK、MySQL、Redis、配置文件）打包成一个 **镜像**，拿到任何机器上都能直接跑。

### 1.2 Docker 和虚拟机的区别

| 对比维度 | 虚拟机（VM） | Docker 容器 |
|---------|-------------|------------|
| **启动速度** | 分钟级（需要启动完整 OS） | 毫秒/秒级（共用宿主机内核） |
| **磁盘占用** | GB 级（每个 VM 完整 OS） | MB 级（共享基础镜像层） |
| **性能损耗** | 有（硬件虚拟化损耗） | 几乎无（直接调用宿主机内核） |
| **资源密度** | 一台机器跑几个 VM | 一台机器跑几十上百个容器 |
| **隔离性** | 强（完全独立内核） | 中等（共用内核，命名空间隔离） |
| **迁移性** | 镜像大，迁移慢 | 镜像小，秒级迁移 |

```
直观理解：

虚拟机：             Docker 容器：
┌──────┐ ┌──────┐    ┌──────┐ ┌──────┐
│ App1 │ │ App2 │    │ App1 │ │ App2 │
│  OS  │ │  OS  │    ├──────┤ ├──────┤
├──────┤ ├──────┤    │共享内核│
│虚拟化层│           ├──────┤
├──────┤             │ 操作系统 │
│  OS  │             └──────┘
└──────┘
    每个 VM 有自己的完整 OS     容器共享宿主机内核
```

### 1.3 Docker 核心架构

```
┌─────────────────────────────────────────────────┐
│                   Docker Client                 │
│          (docker pull, run, build ...)          │
└──────────────────────┬──────────────────────────┘
                       │  REST API
┌──────────────────────▼──────────────────────────┐
│                Docker Daemon (dockerd)           │
│    管理镜像、容器、网络、存储卷                  │
└──┬─────────┬──────────┬───────────┬─────────────┘
   │         │          │           │
   ▼         ▼          ▼           ▼
 镜像      容器       网络        数据卷
(Image)  (Container) (Network)   (Volume)
   │
   ▼
镜像仓库 (Registry) ---- Docker Hub（官方）
                      ---- 私有仓库（Harbor）
```

| 组件 | 说明 | 类比 |
|------|------|------|
| **Docker Daemon** | 后台守护进程，管理容器和镜像 | 引擎 |
| **Docker Client** | 命令行工具 `docker`，与 Daemon 通信 | 方向盘 |
| **Image（镜像）** | 应用 + 环境的只读模板 | 类（Class） |
| **Container（容器）** | 镜像的运行实例，可读写 | 对象（Instance） |
| **Registry（仓库）** | 存储和分发镜像 | 应用商店 |
| **Dockerfile** | 构建镜像的配方文件 | 食谱 |

> **一句话总结**：Dockerfile 写配方 → build 出镜像 → push 到仓库 → pull 到任意机器 → run 成容器。

---

## 二、Docker 安装

> 小白提示：先确认你的操作系统，按对应的方式安装即可。

### 2.1 Windows 安装

**方式一：Docker Desktop（推荐，Windows 10/11）**

```
1. 开启硬件虚拟化（BIOS 中开启 VT-x/AMD-V）
2. 安装 WSL2（管理员 PowerShell 运行）：
   wsl --install
3. 下载 Docker Desktop：
   https://www.docker.com/products/docker-desktop/
4. 安装后重启，Docker Desktop 会自动使用 WSL2 后端
```

```bash
# 验证安装
docker --version
docker run hello-world    # 跑通第一个容器
```

**方式二：在 WSL2 中安装 Docker Engine（不装 Docker Desktop）**

```bash
# 在 WSL2 (Ubuntu) 中
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER   # 免 sudo 运行 docker
newgrp docker                   # 刷新组权限
docker run hello-world
```

### 2.2 macOS 安装

```bash
# 方案一：Docker Desktop
# 从官网下载 .dmg 安装

# 方案二：Homebrew
brew install --cask docker
```

### 2.3 Linux 安装

```bash
# Ubuntu / Debian
sudo apt update
sudo apt install docker.io -y
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER
newgrp docker

# CentOS / RHEL
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install docker-ce docker-ce-cli containerd.io -y
sudo systemctl start docker
sudo systemctl enable docker
```

### 2.4 验证安装

```bash
docker version                # 查看 Docker 版本
docker info                   # 查看 Docker 系统信息
docker run hello-world        # 运行测试容器

# 看到以下输出说明成功：
# Hello from Docker!
# This message shows that your installation appears to be working correctly.
```

---

## 三、Docker 基本操作（初学者必会）

### 3.1 镜像操作

镜像（Image）是容器的模板，就像安装包。

```bash
# 搜索镜像
docker search nginx
docker search mysql

# 拉取镜像（从 Docker Hub 下载）
docker pull nginx:latest          # 最新版
docker pull nginx:1.25            # 指定版本
docker pull redis:7-alpine        # Alpine 版（更小）
docker pull mysql:8.0

# 查看本地镜像
docker images                     # 列出所有镜像
docker images | grep nginx        # 按名称过滤
docker image ls

# 删除镜像
docker rmi nginx:latest           # 删除指定镜像
docker rmi $(docker images -q)    # 删除所有镜像（慎用）

# 镜像信息
docker inspect nginx:latest       # 查看镜像详细信息
docker history nginx:latest       # 查看镜像构建历史（各层）
```

### 3.2 容器操作

容器（Container）是镜像的运行实例。

```bash
# 创建并启动容器
docker run nginx                          # 前台运行（Ctrl+C 停止）
docker run -d nginx                       # 后台运行（-d = daemon）
docker run --name my-nginx -d nginx       # 指定容器名称
docker run -p 8080:80 -d nginx            # 端口映射（宿主机8080 → 容器80）

# 查看容器
docker ps                                 # 查看运行中的容器
docker ps -a                              # 查看所有容器（包括已停止的）
docker ps -q                              # 只显示容器ID

# 停止与启动
docker stop my-nginx                      # 优雅停止（发 SIGTERM）
docker kill my-nginx                      # 强制停止（发 SIGKILL）
docker start my-nginx                     # 启动已停止的容器
docker restart my-nginx                   # 重启

# 删除容器
docker rm my-nginx                        # 删除已停止的容器
docker rm -f my-nginx                     # 强制删除运行中的容器
docker rm $(docker ps -aq)                # 删除所有容器
docker container prune                    # 删除所有已停止的容器

# 进入容器内部
docker exec -it my-nginx bash             # 进入容器并打开 bash
docker exec -it my-nginx sh               # Alpine 镜像用 sh
docker exec my-nginx ls /etc/nginx        # 在容器中执行单条命令

# 查看日志
docker logs my-nginx                      # 查看日志
docker logs -f my-nginx                   # 实时跟踪日志（tail -f）
docker logs --tail 100 my-nginx           # 只看最后100行
```

### 3.3 端口映射详解

```
docker run -p [宿主机端口]:[容器端口] -d nginx

示例：
  -p 8080:80    → 访问 http://localhost:8080 到达容器80端口
  -p 80:80      → 访问 http://localhost:80 到达容器80端口
  -p 3000:3000  → Node.js 应用常用
  -p 3306:3306  → MySQL 映射

多个端口映射：
docker run -p 8080:80 -p 8443:443 -d nginx
```

### 3.4 实操示例：运行一个完整应用

```bash
# 1. 运行 Nginx 网页服务器
docker run -d --name my-site -p 8080:80 nginx:alpine
# 访问 http://localhost:8080 能看到 Nginx 欢迎页

# 2. 运行 MySQL 数据库
docker run -d \
  --name my-mysql \
  -p 3306:3306 \
  -e MYSQL_ROOT_PASSWORD=root123 \
  -e MYSQL_DATABASE=testdb \
  mysql:8.0

# 3. 运行 Redis
docker run -d --name my-redis -p 6379:6379 redis:7-alpine

# 4. 查看所有容器状态
docker ps

# 5. 测试 MySQL 连接（需要宿主机有 mysql 客户端或进入容器）
docker exec -it my-mysql mysql -uroot -proot123 testdb

# 6. 一键清理
docker stop my-site my-mysql my-redis
docker rm my-site my-mysql my-redis
```

---

## 四、Dockerfile —— 构建自己的镜像

### 4.1 什么是 Dockerfile

Dockerfile 是一个文本文件，告诉 Docker 如何构建你的镜像。

```
类比：
  食谱（Dockerfile）→ 按照食谱做菜（build）→ 做好的菜（Image）→ 端上桌开吃（Run）
```

### 4.2 第一个 Dockerfile

```dockerfile
# 基于什么基础镜像
FROM openjdk:17-jdk-alpine

# 作者信息
LABEL author="your-name"

# 设置工作目录
WORKDIR /app

# 把当前目录的 app.jar 复制到镜像里
COPY app.jar app.jar

# 暴露端口
EXPOSE 8080

# 容器启动时执行的命令
CMD ["java", "-jar", "app.jar"]
```

```bash
# 构建镜像
docker build -t my-app:1.0 .        # -t 标签，. 表示当前目录

# 运行容器
docker run -d --name my-app -p 8080:8080 my-app:1.0
```

### 4.3 Dockerfile 指令详解

| 指令 | 作用 | 示例 |
|------|------|------|
| **FROM** | 指定基础镜像（必选） | `FROM openjdk:17-jdk-alpine` |
| **WORKDIR** | 设置工作目录（推荐） | `WORKDIR /app` |
| **COPY** | 复制文件到镜像 | `COPY target/app.jar app.jar` |
| **ADD** | 复制文件（支持自动解压 tar、URL） | `ADD app.tar.gz /app` |
| **RUN** | 在构建时执行命令 | `RUN apt update && apt install -y curl` |
| **ENV** | 设置环境变量 | `ENV JAVA_OPTS="-Xmx512m"` |
| **EXPOSE** | 声明容器监听端口 | `EXPOSE 8080` |
| **CMD** | 容器启动时的默认命令（可被覆盖） | `CMD ["java", "-jar", "app.jar"]` |
| **ENTRYPOINT** | 容器启动的主命令（不可被覆盖） | `ENTRYPOINT ["java", "-jar", "app.jar"]` |
| **ARG** | 构建时参数 | `ARG VERSION=1.0` |
| **VOLUME** | 声明匿名卷 | `VOLUME /data` |
| **HEALTHCHECK** | 健康检查 | `HEALTHCHECK CMD curl -f http://localhost/ || exit 1` |
| **USER** | 指定运行用户（安全） | `USER 1000:1000` |

### 4.4 CMD vs ENTRYPOINT（重要）

| 指令 | 可否被 `docker run` 参数覆盖 | 典型用法 |
|------|--------------------------|---------|
| `CMD ["cmd", "arg"]` | ✅ 可覆盖 | 提供默认命令，用户可替换 |
| `ENTRYPOINT ["cmd"]` | ❌ 不可覆盖 | 容器入口，固定主命令 |
| 两者结合 | ENTRYPOINT 固定主命令，CMD 提供默认参数 | 最常见的正确用法 |

```dockerfile
# 推荐用法：ENTRYPOINT + CMD
ENTRYPOINT ["java", "-jar", "app.jar"]
CMD ["--server.port=8080"]   # 默认参数，用户可覆盖

# docker run my-app --server.port=9090
# 实际执行：java -jar app.jar --server.port=9090
```

### 4.5 完整示例：Java Spring Boot 应用

```dockerfile
# 1. 使用 Maven 构建阶段
FROM maven:3.9-eclipse-temurin-17 AS builder
WORKDIR /build
COPY pom.xml .
RUN mvn dependency:go-offline          # 提前下载依赖（利用缓存）
COPY src ./src
RUN mvn package -DskipTests

# 2. 运行阶段（多阶段构建，最终镜像只有运行环境）
FROM eclipse-temurin:17-jre-alpine
WORKDIR /app
COPY --from=builder /build/target/*.jar app.jar

# 安全：不使用 root 用户运行
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD wget -qO- http://localhost:8080/actuator/health || exit 1

ENTRYPOINT ["java", "-jar", "app.jar"]
CMD ["--spring.profiles.active=prod"]
```

### 4.6 完整示例：Python Flask 应用

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 先复制依赖文件（利用层缓存）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 再复制源码（依赖层不变时不会重装）
COPY app.py .

EXPOSE 5000

# 非 root 用户
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

CMD ["python", "app.py"]
```

```python
# app.py
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, Docker!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

```bash
# 构建和运行
docker build -t flask-app:1.0 .
docker run -d -p 5000:5000 flask-app:1.0
curl http://localhost:5000
```

### 4.7 Dockerfile 最佳实践

| 建议 | 说明 |
|------|------|
| **使用 .dockerignore** | 排除 node_modules、target、.git 等避免上下文过大 |
| **多阶段构建** | 构建环境和运行环境分离，减少镜像体积 |
| **减少层数** | 相关 RUN 命令用 `&&` 合并（`RUN apt update && apt install ...`）|
| **利用缓存** | 不变的依赖先 COPY，频繁修改的源码后 COPY |
| **指定精确基础镜像** | `python:3.11-slim` 而不是 `python:latest` |
| **非 root 运行** | 用 `USER` 指定普通用户，提升安全性 |
| **设置 HEALTHCHECK** | 让容器平台能检测应用健康状态 |

```dockerfile
# .dockerignore
.git
node_modules
target
__pycache__
*.log
.env
.idea
```

---

## 五、Docker Compose —— 管理多容器应用

### 5.1 为什么需要 Compose

一个 Web 应用通常需要多个服务配合：

```
你的应用 = Java后端 + MySQL + Redis + Nginx
           ↓         ↓       ↓       ↓
        4个容器     需要 4 次 docker run 命令
         还要建网络、配连接... 太麻烦了！
```

**Docker Compose**：用一个 `docker-compose.yml` 文件定义所有服务，一键启动。

### 5.2 第一个 docker-compose.yml

```yaml
version: '3.8'

services:
  web:
    build: .                    # 从当前目录 Dockerfile 构建
    ports:
      - "8080:8080"
    depends_on:
      - mysql
      - redis
    environment:
      SPRING_DATASOURCE_URL: jdbc:mysql://mysql:3306/testdb
      SPRING_REDIS_HOST: redis

  mysql:
    image: mysql:8.0
    ports:
      - "3306:3306"
    environment:
      MYSQL_ROOT_PASSWORD: root123
      MYSQL_DATABASE: testdb
    volumes:
      - mysql-data:/var/lib/mysql    # 持久化数据

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data

volumes:
  mysql-data:
  redis-data:
```

```bash
# 启动所有服务
docker compose up -d

# 查看日志
docker compose logs -f

# 查看服务状态
docker compose ps

# 停止并移除所有容器
docker compose down

# 停止并移除容器 + 数据卷
docker compose down -v
```

### 5.3 Compose 常用命令

```bash
docker compose up -d              # 后台启动所有服务
docker compose up -d web          # 只启动 web 服务
docker compose down               # 停止并删除容器
docker compose ps                 # 查看服务状态
docker compose logs -f            # 跟踪所有日志
docker compose logs -f web        # 跟踪 web 服务日志
docker compose exec web bash      # 进入 web 容器
docker compose restart web        # 重启 web 服务
docker compose build              # 重新构建镜像
docker compose pull               # 拉取最新镜像
docker compose config             # 验证 yml 配置是否正确
```

### 5.4 Compose 文件结构详解

```yaml
version: '3.8'

services:
  # 第一个服务
  服务名:
    image: nginx:alpine           # 使用已有镜像
    build: ./dir                  # 或从 Dockerfile 构建
    container_name: my-nginx      # 容器名称（不指定则自动生成）
    ports:
      - "宿主机端口:容器端口"
    expose:
      - "80"                      # 仅对内部网络暴露（不映射到宿主机）
    environment:
      - KEY=VALUE
    env_file: .env                # 从文件加载环境变量
    volumes:
      - 宿主机路径:容器路径        # 挂载目录
      - 卷名:容器路径              # 使用命名卷
    networks:
      - 网络名
    depends_on:
      - mysql                     # 依赖服务（控制启动顺序）
    restart: always               # 重启策略
    healthcheck:                  # 健康检查
      test: ["CMD", "curl", "-f", "http://localhost"]
      interval: 30s
      timeout: 3s
      retries: 3

networks:
  网络名:
    driver: bridge

volumes:
  卷名:
```

### 5.5 重启策略

| 策略 | 行为 |
|------|------|
| `no` | 容器退出时不重启（默认） |
| `always` | 容器退出时总是重启 |
| `on-failure` | 仅退出码非0时重启 |
| `unless-stopped` | 总是重启，除非手动停止 |

```yaml
services:
  app:
    restart: always       # 生产推荐：服务器重启后自动拉起容器
```

### 5.6 完整示例：Spring Boot + MySQL + Redis + Nginx

```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
    depends_on:
      - app
    networks:
      - frontend

  app:
    build:
      context: .
      dockerfile: Dockerfile
    expose:
      - "8080"
    environment:
      SPRING_PROFILES_ACTIVE: prod
      SPRING_DATASOURCE_URL: jdbc:mysql://mysql:3306/mydb?useSSL=false
      SPRING_DATASOURCE_USERNAME: root
      SPRING_DATASOURCE_PASSWORD: root123
      SPRING_REDIS_HOST: redis
    depends_on:
      mysql:
        condition: service_healthy
      redis:
        condition: service_started
    networks:
      - frontend
      - backend
    restart: always

  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: root123
      MYSQL_DATABASE: mydb
    volumes:
      - mysql-data:/var/lib/mysql
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql  # 初始化SQL
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 3s
      retries: 5
    networks:
      - backend
    restart: always

  redis:
    image: redis:7-alpine
    volumes:
      - redis-data:/data
    networks:
      - backend
    restart: always

networks:
  frontend:
  backend:

volumes:
  mysql-data:
  redis-data:
```

```nginx
# nginx.conf —— 反向代理到 Java 应用
server {
    listen 80;
    location / {
        proxy_pass http://app:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

> **容器间通信**：Compose 自动为所有服务创建一个网络，可以用**服务名**作为 hostname（如 `app` 访问 `mysql:3306`）。

---

## 六、Docker 网络

### 6.1 网络模式

| 网络模式 | 命令 | 说明 |
|---------|------|------|
| **bridge** | `--network bridge` | 默认模式，容器在独立网段，通过 NAT 通信 |
| **host** | `--network host` | 容器直接使用宿主机网络（无隔离，性能最好） |
| **none** | `--network none` | 无网络，完全隔离 |
| **overlay** | `--network overlay` | 跨多台主机的容器通信（Swarm/K8s 用） |
| **macvlan** | `--network macvlan` | 容器有独立 MAC 地址，像一台实体机 |

```yaml
# bridge 网络示意
# 宿主机：192.168.1.100
# docker0 网桥：172.17.0.1
# 容器A：172.17.0.2
# 容器B：172.17.0.3
```

### 6.2 自定义网络

```bash
# 创建网络
docker network create my-network

# 指定网络启动容器
docker run -d --name app1 --network my-network nginx
docker run -d --name app2 --network my-network nginx

# 容器间通过名称通信（Docker 内置 DNS）
docker exec app1 ping app2       # ✅ 能 ping 通！

# 查看网络
docker network ls
docker network inspect my-network

# 将运行中的容器连接到网络
docker network connect my-network app3

# 断开连接
docker network disconnect my-network app3
```

### 6.3 容器间通信方式

| 方式 | 使用场景 | 示例 |
|------|---------|------|
| **同一网络下用服务名** | Compose 多服务 | `app` 访问 `mysql:3306` |
| `--link`（已废弃） | 单机通信 | `--link mysql:mysql` |
| **宿主机端口映射** | 外部访问容器 | `-p 8080:80` |
| **共享网络命名空间** | 需要高性能的场景 | `--network host` |

---

## 七、Docker 数据管理

### 7.1 数据持久化问题

```
容器删除后，里面的数据会全部丢失！

docker run -d --name my-mysql -e MYSQL_ROOT_PASSWORD=root mysql:8.0
docker rm -f my-mysql     # 删除容器 → 数据全没了 😱
```

**解决方案**：三种数据挂载方式

| 方式 | 存储位置 | 由 Docker 管理 | 适用场景 |
|------|---------|:------------:|---------|
| **Volume（卷）** | `/var/lib/docker/volumes/` | ✅ | 数据库数据、生产环境（推荐） |
| **Bind Mount（绑定挂载）** | 宿主机任意路径 | ❌ | 开发热重载、配置文件 |
| **tmpfs** | 内存 | ❌ | 敏感数据（不写入磁盘） |

### 7.2 Volume（推荐）

```bash
# 创建卷
docker volume create my-volume

# 查看卷
docker volume ls
docker volume inspect my-volume

# 使用卷
docker run -d \
  --name my-mysql \
  -v my-volume:/var/lib/mysql \    # 卷名:容器路径
  -e MYSQL_ROOT_PASSWORD=root \
  mysql:8.0

# 删除卷
docker volume rm my-volume
docker volume prune    # 删除所有未使用的卷
```

```yaml
# docker-compose 中使用卷
services:
  mysql:
    image: mysql:8.0
    volumes:
      - mysql-data:/var/lib/mysql   # 命名卷

volumes:
  mysql-data:    # 声明卷
```

### 7.3 Bind Mount（绑定挂载）

```bash
# 挂载宿主机的代码目录到容器（开发时代码热更新）
docker run -d \
  --name my-app \
  -v /home/user/myapp:/app \       # 宿主机路径:容器路径
  -p 8080:8080 \
  my-app:dev
  
# 挂载配置文件
docker run -d \
  --name nginx \
  -v /home/user/nginx.conf:/etc/nginx/nginx.conf:ro \   # ro=只读
  -p 80:80 \
  nginx
```

```yaml
# docker-compose 中使用 bind mount
services:
  app:
    build: .
    volumes:
      - ./src:/app/src          # 开发时源码热更新
      - ./config:/app/config:ro  # 配置文件（只读）

  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
```

### 7.4 文件复制（不通过挂载）

```bash
# 从宿主机复制到容器
docker cp /path/to/file.txt container_name:/path/in/container/

# 从容器的复制到宿主机
docker cp container_name:/path/in/container/file.txt /path/on/host/
```

---

## 八、Docker 进阶（大厂面试核心）

### 8.1 镜像分层与 UnionFS

**Docker 镜像由多个只读层叠加而成**，这是 Docker 轻量和高效的核心。

```dockerfile
FROM debian:11          # 层1：基础 OS
RUN apt update          # 层2：安装依赖
COPY app.jar            # 层3：复制应用
CMD ["java", "-jar"]    # 层4：启动命令（元数据层）
```

```
镜像分层示意：
┌─────────────────┐  ← 容器层（可读写，容器删除后消失）
├─────────────────┤
│ CMD ["java"...]  │  ← 镜像层4（只读）
├─────────────────┤
│ COPY app.jar     │  ← 镜像层3（只读）
├─────────────────┤
│ apt install      │  ← 镜像层2（只读）
├─────────────────┤
│ debian:11        │  ← 镜像层1（只读，基础镜像）
└─────────────────┘
```

**Copy-on-Write（写时复制）**：
- 容器读取文件：从上往下找，找到即用
- 容器修改文件：从镜像层把文件**复制到容器层**，再修改（下层原文件不变）
- 容器删除文件：在容器层创建一个"白障"（whiteout）标记文件已被删除

**层共享**：多个容器共用相同基础镜像时，内存中只有一份。

```bash
# 查看镜像分层
docker history nginx:latest

# 查看容器挂载的层
docker inspect container_name | grep GraphDriver
```

### 8.2 Namespace —— 容器隔离的基石

> 面试重点：Docker 用 Linux Namespace 实现"看起来像独立机器"的效果。

| Namespace | 隔离内容 | 作用 |
|-----------|---------|------|
| **PID** | 进程编号 | 容器内看到自己的进程树（PID 从 1 开始） |
| **Network** | 网络设备、IP、端口 | 每个容器有独立的 lo、eth0 |
| **Mount** | 文件系统挂载点 | 容器有独立的根文件系统 |
| **UTS** | 主机名和域名 | 容器可以有自己的 hostname |
| **IPC** | 进程间通信 | 隔离 System V IPC 和 POSIX 消息队列 |
| **User** | 用户和组 ID | 容器内的 root 在宿主机上可能是普通用户 |
| **Cgroup** | 见 8.3 | 资源限制，不是严格意义上的 namespace |

```bash
# 查看容器在宿主机上的 PID
docker inspect --format '{{.State.Pid}}' container_name

# 查看容器的 namespace
ls -la /proc/<PID>/ns/
```

### 8.3 Cgroups —— 资源限制

Cgroups 控制容器能**用多少** CPU、内存、磁盘 IO。

```bash
# 运行容器时限制资源
docker run -d \
  --name my-app \
  --memory="512m" \              # 内存上限 512MB
  --memory-swap="1g" \           # 内存 + Swap 上限 1GB
  --cpus="1.5" \                 # 限制使用 1.5 个 CPU 核心
  --blkio-weight=500 \           # 磁盘 IO 权重（100-1000）
  --pids-limit=200 \             # 最大进程数
  nginx

# 查看容器的资源使用
docker stats                     # 实时查看所有容器资源
docker stats my-app              # 查看单个容器
```

```yaml
# docker-compose 中资源限制
services:
  app:
    image: my-app:1.0
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M
```

**Cgroups 版本**：
- **cgroup v1**：旧版，每种资源有独立的层级
- **cgroup v2**（Linux 4.5+，推荐）：统一的层级结构，更简洁
- Docker 20.10+ 默认使用 cgroup v2

### 8.4 多阶段构建

> 大厂必考：如何让 Java 镜像从 500MB 减到 100MB？

```dockerfile
# ❌ 错误做法：构建环境和运行环境混在一起
FROM maven:3.9-eclipse-temurin-17
COPY . /app
WORKDIR /app
RUN mvn package
CMD ["java", "-jar", "target/app.jar"]
# → 镜像大小：~700MB（包含 JDK、Maven、依赖、源码...）

# ✅ 多阶段构建
# 阶段1：构建
FROM maven:3.9-eclipse-temurin-17 AS builder
WORKDIR /build
COPY pom.xml .
RUN mvn dependency:go-offline
COPY src ./src
RUN mvn package -DskipTests

# 阶段2：运行（只取构建产物）
FROM eclipse-temurin:17-jre-alpine
WORKDIR /app
COPY --from=builder /build/target/app.jar .
EXPOSE 8080
CMD ["java", "-jar", "app.jar"]
# → 镜像大小：~180MB（仅 JRE + app.jar，不含 Maven 和源码）
```

```dockerfile
# 前端项目多阶段构建
# 阶段1：npm 构建
FROM node:20 AS builder
WORKDIR /build
COPY package*.json .
RUN npm ci
COPY . .
RUN npm run build

# 阶段2：Nginx 运行
FROM nginx:alpine
COPY --from=builder /build/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
# → 最终镜像 ~25MB（只含静态文件和 Nginx）
```

### 8.5 Docker 安全

```bash
# 1. 不使用 root 运行
RUN adduser -D myuser
USER myuser

# 2. 只读根文件系统（防止容器内写文件）
docker run --read-only --tmpfs /tmp nginx

# 3. 丢弃危险能力
docker run --cap-drop=ALL --cap-add=NET_BIND_SERVICE nginx

# 4. 限制系统调用
docker run --security-opt seccomp=/path/to/seccomp-profile.json nginx

# 5. 安全扫描
docker scan nginx:latest         # 扫描镜像漏洞（需 Docker Scout）

# 6. 内容信任（只拉取签名镜像）
export DOCKER_CONTENT_TRUST=1
docker pull nginx:latest         # 只拉取经过签名的镜像
```

### 8.6 镜像体积优化技巧

```bash
# 查看镜像大小
docker images
docker system df                 # 查看 Docker 磁盘使用

# 常见大小参考
openjdk:17-jdk           → ~350MB
openjdk:17-jre           → ~250MB（推荐）
eclipse-temurin:17-jre-alpine → ~180MB（强烈推荐）
python:3.11-slim         → ~120MB
python:3.11-alpine       → ~50MB
node:20-alpine           → ~120MB
nginx:alpine             → ~25MB
alpine:latest             → ~7MB（最小基础镜像）
scratch                   → 0MB（空镜像，Go 静态编译用）
```

**优化策略**：

| 策略 | 效果 | 做法 |
|------|------|------|
| 使用 Alpine/slim 基础镜像 | 减少 50-80% | `FROM eclipse-temurin:17-jre-alpine` |
| 多阶段构建 | 减少 60-80% | 构建环境和运行环境分离 |
| 合并 RUN 命令 | 减少层数 | `RUN apt update && apt install -y pkg && rm -rf /var/lib/apt/lists/*` |
| 清理缓存 | 减少 10-30% | `apt clean`、`yum clean all`、`pip --no-cache-dir` |
| 使用 .dockerignore | 减少构建上下文 | 排除 node_modules, target, .git |

---

## 九、Docker 监控与运维

### 9.1 容器监控

```bash
# 实时资源查看
docker stats                    # 显示所有容器的 CPU、内存、网络、IO
docker stats my-app --no-stream  # 只显示一次

# 容器进程查看
docker top my-app               # 查看容器内的进程

# 容器资源变更
docker update --memory="1g" my-app   # 动态修改资源限制

# 查看事件
docker events                   # 实时查看 Docker 事件流
docker events --since 5m        # 最近 5 分钟的事件
```

### 9.2 日志管理

```bash
# 日志驱动配置
docker run -d \
  --log-driver json-file \       # 默认驱动，写到 JSON 文件
  --log-opt max-size=10m \       # 单个日志文件最大 10MB
  --log-opt max-file=3 \         # 保留 3 个轮转文件
  nginx

# 生产推荐：使用 json-file 或 外部日志系统
# json-file → 默认，轮转配置即可
# syslog    → 发送到 syslog 服务器
# fluentd   → 发送到 Fluentd 聚合
# awslogs   → 发送到 CloudWatch
# gelf      → 发送到 Graylog

# 查看日志
docker logs --tail 100 -f my-app    # 跟踪最后 100 行
docker logs -t my-app               # 带时间戳
```

### 9.3 镜像仓库与 CI/CD

```bash
# 登录仓库
docker login                      # 登录 Docker Hub
docker login my-registry.com      # 登录私有仓库

# 打标签
docker tag my-app:1.0 myusername/my-app:1.0
docker tag my-app:1.0 registry.example.com/my-app:1.0

# 推送
docker push myusername/my-app:1.0

# 拉取
docker pull myusername/my-app:1.0

# 私有仓库（Harbor / Nexus / Docker Registry）
docker run -d \
  --name registry \
  -p 5000:5000 \
  -v /data/registry:/var/lib/registry \
  registry:2
```

```yaml
# GitHub Actions + Docker 示例
name: Build and Push Docker Image

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Build Docker image
        run: docker build -t my-app:${{ github.sha }} .
      
      - name: Push to registry
        run: |
          docker tag my-app:${{ github.sha }} registry.example.com/my-app:latest
          docker push registry.example.com/my-app:latest
```

### 9.4 常用清理命令

```bash
docker system prune                 # 清理未使用的容器、网络、 dangling 镜像
docker system prune -a              # 清理所有未使用的镜像（包括无标签的 dangling 镜像）
docker system prune --volumes       # 同时清理未使用的卷

docker container prune              # 清理所有已停止的容器
docker image prune                  # 清理 dangling 镜像
docker volume prune                 # 清理未使用的卷
docker network prune                # 清理未使用的网络

# 一键大扫除
docker rm -f $(docker ps -aq) 2>/dev/null; docker rmi $(docker images -q) 2>/dev/null; docker volume prune -f
```

---

## 十、面试高频考点

### 10.1 Docker 与 Kubernetes 的关系

```
Docker 是"容器引擎"——负责在单台机器上运行容器。
Kubernetes 是"容器编排平台"——负责管理多台机器上的成千上万个容器。

比喻：
  Docker = 火车车厢（单个单元）
  Kubernetes = 铁路调度系统（管理整条铁路线）
```

| 维度 | Docker 负责 | Kubernetes 负责 |
|------|------------|----------------|
| 单机容器运行 | ✅ docker run | ❌（通过 kubelet 调用容器运行时）|
| 多机集群管理 | ❌ | ✅ 自动调度、扩缩容 |
| 服务发现 | ❌ | ✅ Service + DNS |
| 自动修复 | ❌ 仅 restart=always | ✅ 自动重启、重新调度 |
| 滚动更新 | ❌ 手动 | ✅ 自动滚动更新 |
| 负载均衡 | ❌ | ✅ Service + Ingress |
| 存储编排 | ❌ Volume 手动挂载 | ✅ PV/PVC 自动管理 |

> **大厂现状**：生产环境用 Kubernetes 编排，但 Docker 仍是开发和 CI/CD 的核心工具。

### 10.2 Docker 核心面试题

**Q1：Docker 容器和虚拟机的根本区别是什么？**

虚拟机通过 **Hypervisor** 虚拟化硬件，每个 VM 有**独立内核**；Docker 容器通过 **Namespace + Cgroups** 实现资源隔离，所有容器**共享宿主机内核**。因此容器更轻量、启动更快，但隔离性不如虚拟机。

**Q2：Docker 镜像分层是怎么工作的？**

Docker 镜像由多个**只读层**组成，每层对应 Dockerfile 的一条指令。容器启动时在最上层加一个**可写层**（容器层）。读取文件时从上往下找，修改时**复制到容器层再改**（Copy-on-Write）。多个容器共享相同镜像层，节省磁盘和内存。

**Q3：如何减小 Docker 镜像体积？**

1. 多阶段构建（构建环境和运行环境分离）
2. 使用 Alpine 或 slim 基础镜像
3. 合并 RUN 命令，减少层数
4. 清理包管理器缓存
5. 使用 .dockerignore 排除不必要的文件
6. Java 项目使用 jre 而不是 jdk

**Q4：容器之间如何通信？**

- 同一 Docker 网络下通过**容器名**通信（Docker DNS）
- 通过 `--link`（已废弃但仍在用）
- 通过宿主机端口映射 `-p`
- 跨主机用 Overlay 网络（Swarm/K8s）

**Q5：ENTRYPOINT 和 CMD 的区别？**

`CMD` 提供默认命令和参数，`docker run` 时可覆盖。`ENTRYPOINT` 固定容器的主命令，不可覆盖。两者结合使用最灵活：ENTRYPOINT 固定可执行文件，CMD 提供默认参数。

**Q6：Docker 的资源限制是怎么实现的？**

通过 Linux **Cgroups** | 限制 CPU、内存、磁盘 IO、网络带宽。`--memory` 限制内存，`--cpus` 限制 CPU。

**Q7：什么是多阶段构建？解决了什么问题？**

在单个 Dockerfile 中使用多个 FROM 语句，每个 FROM 是一个独立的构建阶段。前面的阶段用于编译/构建，后面的阶段只取构建产物（`COPY --from=builder`）。解决了**镜像体积过大**的问题——最终镜像只包含运行所需的最小文件。

**Q8：COPY 和 ADD 的区别？**

`COPY` 只复制文件，功能简单明确。`ADD` 在 COPY 基础上支持自动解压 tar 文件和 URL 下载。**最佳实践**：纯文件复制用 COPY，需要自动解压用 ADD，一般不推荐从 URL 下载（应先用 RUN wget/curl）。

### 10.3 排错指南

```bash
# 容器起不来
docker logs container_name           # 看日志
docker inspect container_name        # 看详细状态和退出码

# 端口冲突
docker run -p 8080:80 nginx          # Error: port is already allocated
# 解决：换端口或 kill 占用端口的容器

# 磁盘爆满
docker system prune -a --volumes     # 一键清理

# 容器内连不上网
docker network ls                    # 检查网络
docker network inspect bridge        # 检查网络配置

# 进入不了容器
docker exec -it container_name sh    # 有的镜像用 bash，有的用 sh

# 镜像拉不下来
docker pull nginx:latest --platform=linux/amd64   # 指定架构

# Docker Desktop 启动失败
# Windows：检查 WSL2 是否安装，虚拟机是否开启
# Mac：检查是否开启了 Hypervisor.framework
```

### 10.4 Docker 命令速查

```bash
# 镜像
docker pull       # 拉取
docker images     # 查看
docker rmi        # 删除
docker build      # 构建
docker tag        # 打标签
docker push       # 推送
docker inspect    # 详情

# 容器
docker run        # 创建并启动
docker ps         # 查看
docker stop       # 停止
docker start      # 启动
docker restart    # 重启
docker rm         # 删除
docker exec       # 进入
docker logs       # 日志
docker cp         # 复制
docker top        # 进程
docker stats      # 资源

# 系统
docker info       # 系统信息
docker version    # 版本
docker system df  # 磁盘使用
docker system prune  # 清理

# 网络
docker network ls
docker network create
docker network connect
docker network disconnect

# 卷
docker volume ls
docker volume create
docker volume rm
docker volume prune

# Compose
docker compose up
docker compose down
docker compose logs
docker compose ps
docker compose exec
```

---

## 附：从零到一学习路线

```
新手阶段 → Docker 是什么 + 安装 + 跑第一个容器
  ↓
基础操作 → 镜像管理 + 容器管理 + 端口映射
  ↓
Dockerfile → 写第一个 Dockerfile + 构建自己镜像
  ↓
Compose → 用 docker-compose.yml 管理多容器（MySQL+Redis+应用）
  ↓
数据管理 → Volume + Bind Mount 持久化数据
  ↓
网络 → bridge/host 网络模式 + 容器间通信
  ↓
进阶 → 镜像分层 + Namespace + Cgroups + 多阶段构建 + 安全
  ↓
生产实践 → CI/CD + 镜像仓库 + 监控 + 日志 + 资源限制
  ↓
编排 → Kubernetes（后续学习方向）
```

> **一句话总结**：Docker 让你说"我本地能跑"时，对方也能跑得起来。
