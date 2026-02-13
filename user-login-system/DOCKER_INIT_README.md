# Docker 数据库初始化说明

## 初始化机制说明

本项目提供了**三层保障**确保数据库正确初始化：

### 1. 自动初始化（首次启动）

```yaml
volumes:
  - ./init_db.sql:/docker-entrypoint-initdb.d/01_init.sql
```

MySQL 官方镜像会在**首次启动且数据目录为空时**自动执行 `/docker-entrypoint-initdb.d/` 目录下的 SQL 文件。

**适用场景**: 全新部署

### 2. 初始化容器（每次启动）

```yaml
db-init:
  command: mysql -h mysql -u root -proot123 user_login_db < /init_db.sql
```

独立的初始化容器会在 MySQL 就绪后执行 SQL 脚本，确保表结构存在。

**适用场景**: 每次启动都确保表结构正确

### 3. 手动初始化脚本

```bash
./init_db.sh
```

手动执行初始化，可随时重建表结构。

---

## 使用方法

### 方式一：一键启动（推荐）

```bash
# 启动所有服务（自动初始化数据库）
docker compose up -d

# 查看初始化日志
docker compose logs db-init
```

### 方式二：手动初始化

```bash
# 1. 启动 MySQL
docker compose up -d mysql

# 2. 等待 MySQL 就绪
sleep 10

# 3. 执行初始化脚本
./init_db.sh

# 4. 启动其他服务
docker compose up -d
```

### 方式三：手动执行 SQL

```bash
# 直接在容器内执行
docker exec -i user_login_mysql mysql -uroot -proot123 user_login_db < init_db.sql

# 或进入容器手动执行
docker exec -it user_login_mysql mysql -uroot -proot123
mysql> source /docker-entrypoint-initdb.d/01_init.sql
```

---

## 重置环境

如果需要完全重置数据：

```bash
# 方式一：使用重置脚本
./reset.sh

# 方式二：手动重置
docker compose down -v  # -v 删除数据卷
docker compose up -d
```

---

## 验证数据库

```bash
# 检查表是否创建成功
docker exec -it user_login_mysql mysql -uroot -proot123 -e "
USE user_login_db;
SHOW TABLES;
DESC users;
"
```

预期输出：
```
+-------------------------+
| Tables_in_user_login_db |
+-------------------------+
| login_logs              |
| users                   |
+-------------------------+
```

---

## 常见问题

### Q: init_db.sql 没有执行？

检查是否已有数据：
```bash
docker volume ls | grep mysql
```

如果有旧数据，需要删除 volume：
```bash
docker compose down -v
docker compose up -d
```

### Q: 表已存在报错？

这是正常的，SQL 使用了 `CREATE TABLE IF NOT EXISTS`，重复执行不会有问题。

### Q: 如何查看初始化日志？

```bash
# 查看 MySQL 启动日志
docker compose logs mysql

# 查看初始化容器日志
docker compose logs db-init
```
