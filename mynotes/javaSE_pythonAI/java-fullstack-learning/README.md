# 部署与监控

## 一、Docker 部署

### 1. Dockerfile

```dockerfile
# 多阶段构建
FROM maven:3.8-openjdk-17 AS builder

# 设置工作目录
WORKDIR /app

# 复制文件
COPY pom.xml .
COPY src ./src

# 编译打包
RUN mvn clean package -DskipTests

# 镜像构建阶段
FROM openjdk:17-jre-slim

# 设置时区
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && echo 'Asia/Shanghai' > /etc/timezone

# 创建用户和组
RUN groupadd -r appuser && useradd -r -g appuser appuser

# 创建应用目录
RUN mkdir -p /app/logs && \
    chown -R appuser:appuser /app && \
    chmod -R 755 /app

# 复制 jar 包
COPY --from=builder /app/target/*.jar /app/app.jar

# 复制启动脚本
COPY docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

# 切换用户
USER appuser

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s \
    CMD curl -f http://localhost:8080/actuator/health || exit 1

# 暴露端口
EXPOSE 8080

# 设置 JVM 参数
ENV JAVA_OPTS="-Xms512m -Xmx512m -Xss256k \
    -XX:+UseG1GC -XX:MaxGCPauseMillis=200 \
    -XX:+PrintGCDetails -XX:+PrintGCTimeStamps \
    -XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/app/logs"

# 设置时区
ENV TZ=Asia/Shanghai

# 启动脚本
ENTRYPOINT ["/app/docker-entrypoint.sh"]
```

### 2. docker-entrypoint.sh

```bash
#!/bin/bash
set -e

# 默认 JVM 参数
DEFAULT_JAVA_OPTS="-Xms512m -Xmx512m"

# 组合 JVM 参数
JAVA_OPTS="$DEFAULT_JAVA_OPTS $JAVA_OPTS"

# 应用配置
APP_OPTS="--spring.profiles.active=prod"

# 日志目录
LOG_DIR="/app/logs"
mkdir -p $LOG_DIR

# 应用启动
echo "Starting application with options: $APP_OPTS"
exec java $JAVA_OPTS -jar /app/app.jar $APP_OPTS
```

### 3. docker-compose.yml

```yaml
version: '3.8'

services:
  # MySQL
  mysql:
    image: mysql:8.0
    container_name: mysql
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: ecommerce
      MYSQL_USER: appuser
      MYSQL_PASSWORD: password
      TZ: Asia/Shanghai
    ports:
      - "3306:3306"
    volumes:
      - mysql-data:/var/lib/mysql
      - ./mysql/init:/docker-entrypoint-initdb.d
    command:
      - --character-set-server=utf8mb4
      - --collation-server=utf8mb4_unicode_ci
    restart: unless-stopped
    networks:
      - ecommerce

  # Redis
  redis:
    image: redis:7-alpine
    container_name: redis
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
      - ./redis/redis.conf:/etc/redis/redis.conf
    command: redis-server /etc/redis/redis.conf
    restart: unless-stopped
    networks:
      - ecommerce

  # RabbitMQ
  rabbitmq:
    image: rabbitmq:3-management-alpine
    container_name: rabbitmq
    environment:
      RABBITMQ_DEFAULT_USER: admin
      RABBITMQ_DEFAULT_PASS: admin
      RABBITMQ_DEFAULT_VHOST: /
    ports:
      - "5672:5672"
      - "15672:15672"
      - "15674:15674"
    volumes:
      - rabbitmq-data:/var/lib/rabbitmq
    restart: unless-stopped
    networks:
      - ecommerce

  # Nacos
  nacos:
    image: nacos/nacos-server:v2.2.3
    container_name: nacos
    environment:
      MODE: standalone
      SPRING_DATASOURCE_PLATFORM_mysql
      MYSQL_SERVICE_HOST: mysql
      MYSQL_SERVICE_DB_NAME: nacos
      MYSQL_SERVICE_USER: nacos
      MYSQL_SERVICE_PASSWORD: nacos
      JVM_XMS=256m
      JVM_XMX=256m
    ports:
      - "8848:8848"
    depends_on:
      - mysql
    volumes:
      - nacos-logs:/home/nacos/logs
    restart: unless-stopped
    networks:
      - ecommerce

  # RocketMQ NameServer
  rocketmq-namesrv:
    image: apache/rocketmq:4.9.4
    container_name: rocketmq-namesrv
    ports:
      - "9876:9876"
    volumes:
      - rocketmq-namesrv-logs:/home/rocketmq/logs
      - rocketmq-namesrv-store:/home/rocketmq/store
    command: sh mqnamesrv
    restart: unless-stopped
    networks:
      - ecommerce

  # RocketMQ Broker
  rocketmq-broker:
    image: apache/rocketmq:4.9.4
    container_name: rocketmq-broker
    ports:
      - "10909:10909"
      - "10911:10911"
      - "10912:10912"
    environment:
      NAMESRV_ADDR: rocketmq-namesrv:9876
    depends_on:
      - rocketmq-namesrv
    volumes:
      - rocketmq-broker-logs:/home/rocketmq/logs
      - rocketmq-broker-store:/home/rocketmq/store
      - rocketmq-broker-conf:/home/rocketmq/conf
    command: sh mqbroker -n rocketmq-namesrv:9876
    restart: unless-stopped
    networks:
      - ecommerce

  # RocketMQ Console
  rocketmq-console:
    image: styletang/rocketmq-console-ng
    container_name: rocketmq-console
    ports:
      - "8180:8180"
    environment:
      JAVA_OPTS="-Drocketmq.namesrv.addr=rocketmq-namesrv:9876"
    depends_on:
      - rocketmq-broker
    restart: unless-stopped
    networks:
      - ecommerce

  # 应用服务 - 用户服务
  user-service:
    build:
      context: ./user-service
      dockerfile: Dockerfile
    container_name: user-service
    environment:
      SPRING_PROFILES_ACTIVE: prod
      SPRING_CLOUD_NACOS_SERVER_ADDR: nacos:8848
      SPRING_DATASOURCE_URL: jdbc:mysql://mysql:3306/ecommerce?useSSL=false
      SPRING_DATASOURCE_USERNAME: appuser
      SPRING_DATASOURCE_PASSWORD: password
      SPRING_REDIS_HOST: redis
      SPRING_REDIS_PORT: 6379
      ROCKETMQ_NAME_SERVER: rocketmq-namesrv:9876
      TZ: Asia/Shanghai
      JAVA_OPTS: -Xms256m -Xmx256m -Xss256k
    ports:
      - "8081:8080"
    depends_on:
      - mysql
      - redis
      - nacos
    restart: always
    networks:
      - ecommerce

  # 应用服务 - 订单服务
  order-service:
    build:
      context: ./order-service
      dockerfile: Dockerfile
    container_name: order-service
    environment:
      SPRING_PROFILES_ACTIVE: prod
      SPRING_CLOUD_NACOS_SERVER_ADDR: nacos:8848
      SPRING_DATASOURCE_URL: jdbc:mysql://mysql:3306/ecommerce?useSSL=false
      SPRING_DATASOURCE_USERNAME: appuser
      SPRING_DATASOURCE_PASSWORD: password
      SPRING_REDIS_HOST: redis
      SPRING_REDIS_PORT: 6379
      ROCKETMQ_NAME_SERVER: rocketmq-namesrv:9876
      TZ: Asia/Shanghai
      JAVA_OPTS: -Xms256m -Xmx256m -Xss256k
    ports:
      - "8082:8080"
    depends_on:
      - mysql
      - redis
      - nacos
    restart: always
    networks:
      - ecommerce

  # 应用服务 - 商品服务
  product-service:
    build:
      context: ./product-service
      dockerfile: Dockerfile
    container_name: product-service
    environment:
      SPRING_PROFILES_ACTIVE: prod
      SPRING_CLOUD_NACOS_SERVER_ADDR: nacos:8848
      SPRING_DATASOURCE_URL: jdbc:mysql://mysql:3306/ecommerce?useSSL=false
      SPRING_DATASOURCE_USERNAME: appuser
      SPRING_DATASOURCE_PASSWORD: password
      SPRING_REDIS_HOST: redis
      SPRING_REDIS_PORT: 6379
      TZ: Asia/Shanghai
      JAVA_OPTS: -Xms256m -Xmx256m -Xss256k
    ports:
      - "8083:8080"
    depends_on:
      - mysql
      - redis
      - nacos
    restart: always
    networks:
      - ecommerce

  # 网关
  gateway:
    build:
      context: ./gateway
      dockerfile: Dockerfile
    container_name: gateway
    environment:
      SPRING_PROFILES_ACTIVE: prod
      SPRING_CLOUD_NACOS_SERVER_ADDR: nacos:8848
      SPRING_REDIS_HOST: redis
      SPRING_REDIS_PORT: 6379
      TZ: Asia/Shanghai
      JAVA_OPTS: -Xms256m -Xmx256m -Xss256k
    ports:
      - "8080:8080"
    depends_on:
      - user-service
      - order-service
      - product-service
    restart: always
    networks:
      - ecommerce

  # Prometheus
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
    restart: unless-stopped
    networks:
      - ecommerce

  # Grafana
  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3000:3000"
    environment:
      GF_SECURITY_ADMIN_PASSWORD: admin
      GF_USERS_ALLOW_SIGN_UP: "true"
      GF_INSTALL_PLUGINS: "redis-datasource,mysql"
    volumes:
      - grafana-data:/var/lib/grafana
    depends_on:
      - prometheus
    restart: unless-stopped
    networks:
      - ecommerce

  # Nginx
  nginx:
    image: nginx:alpine
    container_name: nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - gateway
    restart: unless-stopped
    networks:
      - ecommerce

volumes:
  mysql-data:
  redis-data:
  rabbitmq-data:
  nacos-logs:
  rocketmq-namesrv-logs:
  rocketmq-namesrv-store:
  rocketmq-broker-logs:
  rocketmq-broker-store:
  rocketmq-broker-conf:
  grafana-data:

networks:
  ecommerce:
    driver: bridge
```

## 二、Kubernetes 部署

### 1. Namespace

```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ecommerce
```

### 2. ConfigMap

```yaml
# application-configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: application-config
  namespace: ecommerce
data:
  application.yml: |
    spring:
      application:
        name: ecommerce

      cloud:
        nacos:
          discovery:
            server-addr: nacos:8848
          config:
            server-addr: nacos:8848
            file-extension: yml
            namespace: ecommerce
            group: DEFAULT_GROUP

      redis:
        host: redis
        port: 6379
        database: 0

      datasource:
        url: jdbc:mysql://mysql:3306/ecommerce
        username: ${DB_USERNAME:appuser}
        password: ${DB_PASSWORD:password}
        driver-class-name: com.mysql.cj.jdbc.Driver

      rocketmq:
        name-server: rocketmq-namesrv:9876

      jpa:
        hibernate:
          ddl-auto: update
        show-sql: false
        properties:
          hibernate:
            dialect: org.hibernate.dialect.MySQL8Dialect

    logging:
      level:
        root: INFO
        com.ecommerce: DEBUG

    server:
      port: 8080
      compression:
        enabled: true
```

### 3. Secret

```yaml
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: mysql-secret
  namespace: ecommerce
type: Opaque
data:
  username: YXBwdXNlcg==
  password: cGFzc3dvcmQ=

---
apiVersion: v1
kind: Secret
metadata:
  name: redis-secret
  namespace: ecommerce
type: Opaque
data:
  password: ""
```

### 4. 部署文件

```yaml
# user-service-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: user-service
  namespace: ecommerce
  labels:
    app: user-service
    version: v1
spec:
  replicas: 2
  selector:
    matchLabels:
      app: user-service
  template:
    metadata:
      labels:
        app: user-service
        version: v1
    spec:
      containers:
        - name: user-service
          image: registry.example.com/ecommerce/user-service:1.0.0
          ports:
            - containerPort: 8080
          env:
            - name: SPRING_PROFILES_ACTIVE
              value: "prod"
            - name: DB_USERNAME
              valueFrom:
                secretKeyRef:
                  name: mysql-secret
                  key: username
            - name: DB_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: mysql-secret
                  key: password
            - name: JAVA_OPTS
              value: "-Xms256m -Xmx256m"
          resources:
            requests:
              memory: "256Mi"
              cpu: "250m"
            limits:
              memory: "512Mi"
              cpu: "500m"
          livenessProbe:
            httpGet:
              path: /actuator/health/liveness
              port: 8080
            initialDelaySeconds: 60
            periodSeconds: 10
            timeoutSeconds: 5
          readinessProbe:
            httpGet:
              path: /actuator/health/readiness
              port: 8080
            initialDelaySeconds: 30
            periodSeconds: 5
            timeoutSeconds: 3
          volumeMounts:
            - name: logs
              mountPath: /app/logs
          lifecycle:
            preStop:
              exec:
                command: ["sh", "-c", "sleep 10 && curl -XPOST localhost:8080/actuator/shutdown"]
---
apiVersion: v1
kind: Service
metadata:
  name: user-service
  namespace: ecommerce
spec:
  selector:
    app: user-service
  ports:
    - port: 8080
      targetPort: 8080
      name: http
  type: ClusterIP
  sessionAffinity: ClientIP
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: user-service-hpa
  namespace: ecommerce
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: user-service
  minReplicas: 2
  maxReplicas: 10
  metrics:
    metrics:
      - type: Resource
        resource:
          target:
            type: Utilization
            averageUtilization: 70
      - type: Pods
        metric:
          name: pod_memory_usage_bytes
          target:
            type: AverageValue
            averageValue: 80
```

### 5. Ingress

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ecommerce-ingress
  namespace: ecommerce
  annotations:
    nginx.ing.kubernetes.io/rewrite-target: /
    nginx.ing.kubernetes.io/ssl-redirect: "true"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
      - api.example.com
    secretName: api-tls
  rules:
    - host: api.example.com
      http:
        paths:
          - path: /api
            pathType: Prefix
            backend:
              service:
                name: gateway
                port:
                  number: 8080
```

## 三、监控告警

### 1. Prometheus 配置

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  # Spring Boot 应用
  - job_name: 'user-service'
    metrics_path: /actuator/prometheus
    static_configs:
      - targets:
          - 'user-service.ecommerce.svc.cluster.local:8081'

  - job_name: 'order-service'
    metrics_path: /actuator/prometheus
    static_configs:
      - targets:
          - 'order-service.ecommerce.svc.cluster.local:8082'

  - job_name: 'product-service'
    metrics_path: /actuator/prometheus
    static_configs:
      - targets:
          - 'product-service.ecommerce.svc.cluster.local:8083'

  # Nginx 监控
  - job_name: 'nginx'
    metrics_path: /metrics
    static_configs:
      - targets:
          - 'nginx.ecommerce.svc.cluster.local:9113'

  # MySQL 监控
  - job_name: 'mysql'
    static_configs:
      - targets:
          - 'mysql:3306'
    relabel_configs:
      - source_labels: [address]
        target_label: address
      metric_relabel_configs:
      - source_labels: [state]
        target_label: state

  # Redis 监控
  - job_name: 'redis'
    static_configs:
      - targets:
          - 'redis:6379'
```

### 2. Grafana 仪表盘

```json
{
  "dashboard": {
    "title": "电商系统监控",
    "panels": [
      {
        "id": 1,
        "title": "系统概览",
        "type": "stat",
        "gridPos": {"h": 8, "x": 0, "y": 0, "w": 4, "h": 4},
        "targets": [
          {
            "expr": "up{job=\"user-service\"}",
            "legendFormat": "{{job}}",
            "refId": "A"
          },
          {
            "expr": "up{job=\"order-service\"}",
            "legendFormat": "{{job}}",
            "refId": "B"
          },
          {
            "expr": "up{job=\"product-service\"}",
            "legendFormat": "{{job}}",
            "refId": "C"
          }
        ]
      },
      {
        "id": 2,
        "title": "QPS 监控",
        "type": "graph",
        "gridPos": {"h": 8, "x": 4, "y": 0, "w": 8, "h": 4},
        "targets": [
          {
            "expr": "rate(http_server_requests_seconds_count{uri!=\"/actuator/health\"} * 60)",
            "legendFormat": "{{uri}}",
            "refId": "D"
          }
        ],
        "yaxes": [
          {
            "format": "short"
          }
        ]
      },
      {
        "id": 3,
        "title": "响应时间",
        "type": "graph",
        "gridPos": {"h": 8, "x": 12, "y": 0, "w": 12, "h": 4},
        "targets": [
          {
            "expr": "histogram_quantile(0.95)",
            "legendFormat": "{{le}}",
            "refId": "G"
          },
          {
            "expr": "histogram_quantile(0.99)",
            "legendFormat": "{{le}}",
            "refId": "H"
          }
        ]
      },
      {
        "id": 4,
        "title": "JVM 内存",
        "type": "graph",
        "gridPos": {"h": 8, "x": 0, "y": 4, "w": 8, "h": 4},
        "targets": [
          {
            "expr": "jvm_memory_used_bytes / 1024 / 1024",
            "legendFormat": "堆内存",
            "refId": "I"
          },
          {
            "expr": "jvm_memory_max_bytes / 1024 / 1024",
            "legendFormat": "最大堆内存",
            "refId": "J"
          }
        ]
      },
      {
        "id": 5,
        "title": "GC 时间",
        "type": "graph",
        "gridPos": {"h": 8, "x": 8, "y": 4, "w": 8, "h": 4},
        "targets": [
          {
            "expr": "rate(jvm_gc_pause_seconds_sum[5m])",
            "legendFormat": "Young GC",
            "refId": "K"
          },
          {
            "expr": "rate(jvm_gc_pause_seconds_sum{gc=\"old\"}[5m])",
            "legendFormat": "Old GC",
            "refId": "L"
          }
        ]
      }
    ]
  }
}
```

### 3. 告警规则

```yaml
# alertmanager-config.yaml
global:
  resolve_timeout: 5m
  smtp_smarthost: smtp.example.com
  smtp_from: alerts@example.com
  smtp_require_tls: false

templates:
  - '/etc/alertmanager/template/*.tmpl'

receivers:
  - name: 'email'
    email_configs:
      - to: 'team@example.com'
        from: 'alerts@example.com'
        smarthost: smtp.example.com
        auth_username: alerts@example.com
        auth_password: password

route:
  group_by: ['alertname', 'cluster', 'service']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
  receiver: 'email'
  routes:
    - match:
        severity: warning
      receiver: 'email'
    - match:
        severity: critical
      receiver: 'email'

  inhibit_rules:
    - source_match:
        severity: warning
      target_match:
        severity: critical
      equal: ['alertname']

inhibit_rules:
  - source_match:
      severity: critical
      alertname: "HighErrorRate"
      start_time: "00:00"
      end_time: "06:00"
    target_match_re:
      severity: critical

# 告警规则
alert_rules:
  - name: HighErrorRate
    expr: |
      rate(http_server_requests_seconds_count{status=~"5[0-9]{2}"}[5m]) > 100
    for: 5m
    labels:
      severity: critical
      team: backend
    annotations:
      summary: "服务错误率过高"

  - name: HighResponseTime
    expr: |
      histogram_quantile(0.95) > 5
    for: 5m
    labels:
      severity: warning
      team: backend
    annotations:
      summary: "P95 响应时间过长"

  - name: MemoryUsageHigh
    expr: |
      jvm_memory_used_bytes / jvm_memory_max_bytes > 0.8
    for: 5m
    labels:
      severity: warning
      team: backend
    annotations:
      summary: "JVM 内存使用率过高"

  - name ServiceDown
    expr: up{job=~"user.*"} == 0
    for: 1m
    labels:
      severity: critical
      team: backend
    annotations:
      summary: "用户服务宕机"

  - name DiskSpaceHigh
    expr: |
      (node_filesystem_avail_bytes / node_filesystem_size_bytes) < 0.2
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "磁盘空间不足"
```

## 四、日志收集

### 1. Logback 配置

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <!-- 控制台输出 -->
    <appender name="CONSOLE" class="ch.qos.logback.core.ConsoleAppender">
        <encoder>
            <pattern>%d{yyyy-MM-dd HH:mm:ss.SSS} [%thread] %-5level %logger{50} - %msg%n</pattern>
        </encoder>
    </appender>

    <!-- 文件输出 -->
    <appender name="FILE" class="ch.qos.logback.core.rolling.RollingFileAppender">
        <file>logs/application.log</file>
        <rollingPolicy class="ch.qos.logback.core.rolling.SizeAndTimeBasedRollingPolicy">
            <fileNamePattern>logs/application-%d{yyyy-MM-dd}.log</fileNamePattern>
            <maxFileSize>100MB</maxFileSize>
            <maxHistory>30</maxHistory>
            <totalSizeCap>5GB</totalSizeCap>
        </rollingPolicy>
        <encoder>
            <pattern>%d{yyyy-MM-dd HH:mm:ss.SSS} [%thread] %-5level %logger{50} - %msg%n</pattern>
        </encoder>
    </appender>

    <!-- 错误日志 -->
    <appender name="ERROR_FILE" class="ch.qos.logback.core.rolling.RollingFileAppender">
        <file>logs/error.log</file>
        <filter class="ch.qos.logback.class.filter.LevelFilter">
            <level>ERROR</level>
        </filter>
        <rollingPolicy class="ch.qos.logback.core.rolling.SizeAndTimeBasedRollingPolicy">
            <fileNamePattern>logs/error-%d{yyyy-MM-dd}.log</fileNamePattern>
            <maxFileSize>100MB</maxFileSize>
            <maxHistory>30</maxHistory>
            <totalSizeCap>2GB</totalSizeCap>
        </rollingPolicy>
        <encoder>
            <pattern>%d{yyyy-MM-dd HH:mm:ss.SSS} [%thread] %-5level %logger{50} - %msg%n</pattern>
        </encoder>
    </appender>

    <!-- Async Appender（异步写入） -->
    <appender name="ASYNC_FILE" class="ch.qos.logback.class.AsyncAppender">
        <appender-ref ref="FILE" />
        <queueSize>512</queueSize>
        <discardingThreshold>0</discardingThreshold>
    </appender>

    <!-- Kafka Appender -->
    <appender name="KAFKA" class="com.github.danielwegener.logback.kafka.KafkaAppender">
        <bootstrapServers>kafka1:9092,kafka2:9092,kafka3:9092</bootstrapServers>
        <topic>application-logs</topic>
        <compressionType>gzip</compressionType>
        <producerConfig>
            <acks>all</acks>
            <retries>3</retries>
        </producerConfig>
        <encoder class="com.github.danielwegener.logback.kafka.encoder.LoggingKafkaEncoder">
            <customHeaders>{"app": "ecommerce", "env": "prod"}</customHeaders>
            <partitionKey>0</partitionKey>
        </encoder>
    </appender>

    <!-- Logger 配置 -->
    <root level="INFO">
        <appender-ref ref="CONSOLE" />
        <appender-ref ref="ASYNC_FILE" />
        <appender-ref ref="KAFKA" />
    </root>

    <logger name="com.ecommerce" level="DEBUG" additivity="false">
        <appender-ref ref="CONSOLE" />
        <appender-ref ref="ASYNC_FILE" />
    </logger>
</configuration>
```

### 2. ELK Stack

```yaml
# filebeat.yml
filebeat.inputs:
- type: container
  enabled: true
  containers.ids: ['*']

- type: log
  enabled: true
  paths:
    - /var/log/containers/*.log
  json.keys_under_root: true
  json.add_error_key: true

processors:
- add_docker_metadata:
    host: "unix:///var/run/docker.sock"

- decode_json_fields:
  fields: ["message", "@timestamp"]
  target: ""
  overwrite_keys: true
  require:
    - message
    - "@timestamp"
  max_message_size: 1048576

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
  indices:
    - index: "ecommerce-logs-%{+yyyy.MM.dd}"
  username: "elastic"
  password: "password"
  setup.template.settings:
    index.number_of_shards: 3
    index.number_of_replicas: 1
    index.refresh_interval: 5s

setup.template.name: "ecommerce-logs"
setup.template.pattern: '{"@timestamp": "%{[@timestamp]}", "level": "%{[level]}", "service": "%{[service]}", "host": "%{[host]}", "thread": "%{[thread]}", "class": "%{[logger]}", "message": "%{[message]}"}'

setup.template.settings:
  index.number_of_shards: 3
  index.number_of_replicas: 1
```

## 小结

本节学习了部署与监控：

- **Docker** - Dockerfile、docker-compose
- **Kubernetes** - Deployment、Service、ConfigMap、Secret、Ingress
- **监控** - Prometheus、Grafana、告警
- **日志** - Logback、ELK Stack

## 实践练习

### 编程题
1. 使用 Docker Compose 一键部署电商系统的全部服务（MySQL、Redis、RocketMQ、Nacos、应用服务），并验证服务间调用正常。
2. 配置 Prometheus + Grafana 监控面板，添加 QPS、响应时间、JVM 内存和 GC 四个核心监控面板。

### 思考题
1. Docker 和 Kubernetes 的关系？什么场景用 Docker Compose 就够了，什么场景需要 K8s？
2. ELK 日志系统中，Filebeat → Logstash → Elasticsearch 的数据流向中，各组件的作用是什么？

### 自测题
1. Docker 镜像和容器的区别？
2. K8s 中 Deployment、Service、Ingress 分别解决什么问题？
3. Prometheus 的四种主要 Metrics 类型是什么？

---

回顾整个 Java 全栈学习路径，你现在应该掌握了从 Java 基础到微服务架构的完整技能栈。