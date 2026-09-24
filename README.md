# CTFd-CMC

Tài liệu cài đặt, triển khai, vận hành và khôi phục hệ thống **CTFd CMC**.

Repository bao gồm:

* CTFd Core
* Docker Compose
* Nginx Reverse Proxy
* MariaDB
* Redis
* CTF Tracks
* JEDI Challenge Engine
* Dynamic Challenge Scoring
* Challenge source/content
* Cấu hình phục vụ triển khai hệ thống

---

# 1. Kiến trúc hệ thống

Kiến trúc runtime:

```text
                    Player / Admin
                          |
                          v
                     Nginx :80
                          |
                          v
                     CTFd :8000
                          |
              +-----------+-----------+
              |                       |
              v                       v
        MariaDB 10.11              Redis 4
              |
              v
       CTFd Persistent Data

                     CTFd
                      |
        +-------------+-------------+
        |             |             |
        v             v             v
   CTF Tracks       JEDI        Dynamic
                   Challenge     Scoring
```

Các service Docker:

```text
ctfd
nginx
db
cache
permissions
```

---

# 2. Cấu trúc Repository

```text
CTFd-CMC/
├── README.md
├── .gitignore
│
├── CTFd/
│   ├── CTFd/
│   ├── conf/
│   │   └── nginx/
│   │       └── http.conf
│   ├── migrations/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── ...
│
├── CTFd-custom-plugins/
│   ├── challenges/
│   ├── ctf_tracks/
│   ├── dynamic_challenges/
│   ├── flags/
│   ├── jedi_challenge/
│   ├── migrations.py
│   └── __init__.py
│
└── Challenge/
    ├── CMC-JEDI-INVESTIGATION/
    ├── ctfd-challenge-assets/
    ├── fakegpt/
    ├── hawkeye/
    └── insider/
```

---

# 3. Thành phần chính

## 3.1 CTFd Core

Application chính nằm tại:

```text
/opt/CTFd
```

Container:

```text
ctfd-ctfd-1
```

Application port:

```text
8000
```

Các biến runtime chính:

```text
UPLOAD_FOLDER=/var/uploads
DATABASE_URL=mysql+pymysql://ctfd:${MARIADB_PASSWORD}@db/ctfd
REDIS_URL=redis://cache:6379
WORKERS=1
LOG_FOLDER=/var/log/CTFd
REVERSE_PROXY=true
```

---

## 3.2 Nginx

Nginx đóng vai trò reverse proxy:

```text
Client
   |
   v
Nginx :80
   |
   v
CTFd :8000
```

Configuration:

```text
/opt/CTFd/conf/nginx/http.conf
```

---

## 3.3 MariaDB

Image:

```text
mariadb:10.11
```

Database mặc định:

```text
ctfd
```

Persistent storage:

```text
/opt/CTFd/.data/mysql
```

Container path:

```text
/var/lib/mysql
```

---

## 3.4 Redis

Image:

```text
redis:4
```

Persistent storage:

```text
/opt/CTFd/.data/redis
```

Container path:

```text
/data
```

Redis chỉ hoạt động trong Docker internal network.

---

# 4. Custom Plugins

Production plugin directory:

```text
/opt/CTFd-custom-plugins
```

Directory này được mount vào:

```text
/opt/CTFd/CTFd/plugins
```

bên trong container CTFd.

Docker Compose sử dụng:

```yaml
- /opt/CTFd-custom-plugins:/opt/CTFd/CTFd/plugins:ro
```

Do đó đường dẫn `/opt/CTFd-custom-plugins` trên host là bắt buộc với cấu hình hiện tại.

---

## 4.1 CTF Tracks

Plugin:

```text
/opt/CTFd-custom-plugins/ctf_tracks
```

Mô hình:

```text
Track
 |
 +-- Level
      |
      +-- Lab
           |
           +-- challenge_id
```

Progress được xác định từ native CTFd Solve.

---

## 4.2 JEDI Challenge Engine

Plugin:

```text
/opt/CTFd-custom-plugins/jedi_challenge
```

Config:

```text
/opt/CTFd-custom-plugins/jedi_challenge/configs/
```

Hiện có:

```text
35.json
36.json
37.json
38.json
```

Mapping:

| Challenge ID | Challenge                     | Stage |
| ------------ | ----------------------------- | ----: |
| 35           | CMC DFIR - JEDI INVESTIGATION |     3 |
| 36           | HawkEye                       |    24 |
| 37           | Insider                       |    11 |
| 38           | FakeGPT                       |    10 |

Luồng xử lý:

```text
Q1
 |
 v
Q2
 |
 v
...
 |
 v
Qn
 |
 v
Final Correct
 |
 v
CTFd Solve
 |
 +------> Score
 |
 +------> Track Progress
```

Các stage trung gian được lưu dưới dạng progress/Partial.

---

## 4.3 Dynamic Challenge

Plugin:

```text
/opt/CTFd-custom-plugins/dynamic_challenges
```

Plugin xử lý dynamic scoring.

Đây không phải runtime provisioning engine.

---

# 5. Yêu cầu máy chủ

Baseline hiện tại:

```text
OS            Ubuntu Server 22.04 LTS
Architecture  x86_64
CPU           >= 4 vCPU
RAM           >= 8 GB
Docker        Docker Engine
Compose       Docker Compose Plugin
```

Khuyến nghị production:

```text
CPU     4 vCPU hoặc cao hơn
RAM     8 GB hoặc cao hơn
Disk    >= 50 GB
```

Dung lượng thực tế cần tăng nếu lưu forensic evidence hoặc upload lớn.

---

# 6. Cài đặt Ubuntu Server

Sau khi cài Ubuntu Server:

```bash
sudo apt update
sudo apt upgrade -y
```

Cài các utility cơ bản:

```bash
sudo apt install -y \
    ca-certificates \
    curl \
    git \
    gnupg \
    lsb-release \
    vim \
    unzip
```

Kiểm tra:

```bash
lsb_release -a
uname -a
```

---

# 7. Cài Docker Engine

Xóa các package Docker cũ nếu tồn tại:

```bash
sudo apt remove -y \
    docker.io \
    docker-doc \
    docker-compose \
    podman-docker \
    containerd \
    runc
```

Tạo keyring:

```bash
sudo install -m 0755 -d /etc/apt/keyrings
```

Import Docker signing key:

```bash
curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
```

Phân quyền:

```bash
sudo chmod a+r /etc/apt/keyrings/docker.gpg
```

Thêm Docker repository:

```bash
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

Cài Docker:

```bash
sudo apt update
sudo apt install -y \
    docker-ce \
    docker-ce-cli \
    containerd.io \
    docker-buildx-plugin \
    docker-compose-plugin
```

Enable Docker:

```bash
sudo systemctl enable --now docker
```

Kiểm tra:

```bash
docker --version
docker compose version
sudo systemctl status docker
```

---

# 8. Chuẩn bị thư mục triển khai

Hệ thống sử dụng:

```text
/opt/CTFd
/opt/CTFd-custom-plugins
```

Chuyển sang `/opt`:

```bash
cd /opt
```

---

# 9. Clone Repository

Clone repository:

```bash
sudo git clone <REPOSITORY_URL> CTFd-CMC
```

Kiểm tra:

```bash
cd /opt/CTFd-CMC
git status
git log --oneline -5
```

Cấu trúc phải có:

```bash
ls -lah
```

Kỳ vọng:

```text
README.md
CTFd/
CTFd-custom-plugins/
Challenge/
```

---

# 10. Deploy CTFd Source

Docker Compose hiện được thiết kế chạy tại:

```text
/opt/CTFd
```

Copy CTFd:

```bash
sudo cp -a /opt/CTFd-CMC/CTFd /opt/CTFd
```

Kiểm tra:

```bash
ls -lah /opt/CTFd
```

Phải có:

```text
docker-compose.yml
Dockerfile
CTFd/
conf/
```

---

# 11. Deploy Custom Plugins

Copy production plugins:

```bash
sudo cp -a \
  /opt/CTFd-CMC/CTFd-custom-plugins \
  /opt/CTFd-custom-plugins
```

Kiểm tra:

```bash
ls -lah /opt/CTFd-custom-plugins
```

Phải có tối thiểu:

```text
challenges
ctf_tracks
dynamic_challenges
flags
jedi_challenge
```

Kiểm tra JEDI:

```bash
ls -lah /opt/CTFd-custom-plugins/jedi_challenge
```

Kiểm tra config:

```bash
ls -lah /opt/CTFd-custom-plugins/jedi_challenge/configs
```

Kỳ vọng:

```text
35.json
36.json
37.json
38.json
```

---

# 12. Deploy Challenge Source

Tạo các directory:

```bash
sudo mkdir -p \
    /opt/fakegpt \
    /opt/hawkeye \
    /opt/insider \
    /opt/CMC-JEDI-INVESTIGATION \
    /opt/ctfd-challenge-assets
```

Copy source:

```bash
sudo cp -a /opt/CTFd-CMC/Challenge/fakegpt/. \
    /opt/fakegpt/

sudo cp -a /opt/CTFd-CMC/Challenge/hawkeye/. \
    /opt/hawkeye/

sudo cp -a /opt/CTFd-CMC/Challenge/insider/. \
    /opt/insider/

sudo cp -a /opt/CTFd-CMC/Challenge/CMC-JEDI-INVESTIGATION/. \
    /opt/CMC-JEDI-INVESTIGATION/

sudo cp -a /opt/CTFd-CMC/Challenge/ctfd-challenge-assets/. \
    /opt/ctfd-challenge-assets/
```

Kiểm tra:

```bash
ls -lah /opt/fakegpt
ls -lah /opt/hawkeye
ls -lah /opt/insider
ls -lah /opt/CMC-JEDI-INVESTIGATION
ls -lah /opt/ctfd-challenge-assets
```

> Lưu ý: forensic evidence dung lượng lớn có thể không tồn tại trong Git do `.gitignore`. Các evidence này phải được restore riêng từ kho backup/evidence.

---

# 13. Tạo Environment Configuration

Chuyển vào:

```bash
cd /opt/CTFd
```

Tạo `.env`:

```bash
sudo nano .env
```

Nội dung:

```env
MARIADB_ROOT_PASSWORD=<ROOT_DATABASE_PASSWORD>
MARIADB_USER=ctfd
MARIADB_PASSWORD=<CTFD_DATABASE_PASSWORD>
MARIADB_DATABASE=ctfd
```

Ví dụ cấu trúc:

```env
MARIADB_ROOT_PASSWORD=CHANGE_ME_STRONG_ROOT_PASSWORD
MARIADB_USER=ctfd
MARIADB_PASSWORD=CHANGE_ME_STRONG_CTFD_PASSWORD
MARIADB_DATABASE=ctfd
```

Không sử dụng credential mẫu trên production.

Kiểm tra:

```bash
sudo cat .env
```

Sau khi xác nhận, giới hạn permission:

```bash
sudo chmod 600 .env
```

`.env` không được commit lên Git.

---

# 14. Tạo Persistent Storage

Tạo directory:

```bash
cd /opt/CTFd

sudo mkdir -p \
    .data/CTFd/logs \
    .data/CTFd/uploads \
    .data/mysql \
    .data/redis
```

Kiểm tra:

```bash
find .data -maxdepth 3 -type d
```

Kỳ vọng:

```text
.data
.data/CTFd
.data/CTFd/logs
.data/CTFd/uploads
.data/mysql
.data/redis
```

Container `permissions` sẽ thiết lập ownership cho:

```text
/var/uploads
/var/log/CTFd
```

---

# 15. Validate Docker Compose

Chạy:

```bash
cd /opt/CTFd

sudo docker compose config
```

Không được xuất hiện lỗi:

```text
variable is not set
```

Kiểm tra service:

```bash
sudo docker compose config --services
```

Kỳ vọng:

```text
permissions
db
cache
ctfd
nginx
```

---

# 16. Build CTFd

Build application:

```bash
sudo docker compose build ctfd
```

Hoặc:

```bash
sudo docker compose build
```

Kiểm tra image:

```bash
sudo docker images
```

---

# 17. Khởi động hệ thống

```bash
sudo docker compose up -d
```

Kiểm tra:

```bash
sudo docker compose ps
```

Các service chính phải ở trạng thái running:

```text
ctfd
nginx
db
cache
```

`permissions` có thể ở trạng thái exited sau khi hoàn thành nhiệm vụ; đây là hành vi dự kiến.

---

# 18. Kiểm tra Container

```bash
sudo docker ps
```

Kiểm tra riêng:

```bash
sudo docker compose ps ctfd
sudo docker compose ps nginx
sudo docker compose ps db
sudo docker compose ps cache
```

---

# 19. Kiểm tra Logs

Toàn bộ stack:

```bash
sudo docker compose logs --tail=100
```

CTFd:

```bash
sudo docker compose logs --tail=100 ctfd
```

MariaDB:

```bash
sudo docker compose logs --tail=100 db
```

Redis:

```bash
sudo docker compose logs --tail=100 cache
```

Nginx:

```bash
sudo docker compose logs --tail=100 nginx
```

Theo dõi realtime:

```bash
sudo docker compose logs -f ctfd
```

---

# 20. Kiểm tra Network

```bash
sudo docker network ls
```

Kiểm tra:

```bash
sudo docker network inspect ctfd_default
sudo docker network inspect ctfd_internal
```

MariaDB và Redis không nên publish port trực tiếp ra host.

Kiểm tra:

```bash
sudo docker ps --format "table {{.Names}}\t{{.Ports}}"
```

---

# 21. Kiểm tra Web

Từ server:

```bash
curl -I http://127.0.0.1
```

Kiểm tra trực tiếp CTFd:

```bash
curl -I http://127.0.0.1:8000
```

Nginx:

```text
TCP/80
```

CTFd application:

```text
TCP/8000
```

Trong production nên giới hạn truy cập trực tiếp TCP/8000 và chỉ cho client đi qua reverse proxy.

---

# 22. Khởi tạo CTFd lần đầu

Truy cập:

```text
http://<SERVER_IP>/
```

Nếu database mới hoàn toàn, CTFd sẽ hiển thị giao diện setup.

Thực hiện:

1. Đặt tên CTF.
2. Tạo Administrator.
3. Cấu hình mode User/Team phù hợp.
4. Cấu hình thời gian CTF nếu cần.
5. Hoàn tất Setup.

Sau đó đăng nhập bằng tài khoản Administrator.

---

# 23. Kiểm tra Custom Plugin

Kiểm tra trong container:

```bash
sudo docker exec ctfd-ctfd-1 \
  ls -lah /opt/CTFd/CTFd/plugins
```

Kiểm tra:

```bash
sudo docker exec ctfd-ctfd-1 \
  ls -lah /opt/CTFd/CTFd/plugins/jedi_challenge
```

```bash
sudo docker exec ctfd-ctfd-1 \
  ls -lah /opt/CTFd/CTFd/plugins/ctf_tracks
```

```bash
sudo docker exec ctfd-ctfd-1 \
  ls -lah /opt/CTFd/CTFd/plugins/dynamic_challenges
```

---

# 24. Kiểm tra JEDI Config

```bash
sudo docker exec ctfd-ctfd-1 \
  ls -lah /opt/CTFd/CTFd/plugins/jedi_challenge/configs
```

Phải có:

```text
35.json
36.json
37.json
38.json
```

---

# 25. Database mới và Database Production

Có hai trường hợp triển khai.

## Trường hợp A — Cài mới hoàn toàn

Không restore database.

Khởi động CTFd và cấu hình hệ thống từ Admin UI.

Challenge/Track phải được tạo/import lại theo dữ liệu vận hành.

## Trường hợp B — Khôi phục hệ thống hiện tại

Phải restore MariaDB backup.

Database chứa các dữ liệu quan trọng:

```text
Users
Teams
Challenges
Flags
Hints
Submissions
Partials
Solves
Configuration
Tracks
Levels
Labs
Dynamic Challenge configuration
```

Đây là phương án cần dùng nếu muốn tái dựng nguyên trạng hệ thống hiện tại.

---

# 26. Backup MariaDB

Tạo thư mục:

```bash
sudo mkdir -p /opt/backups/ctfd
```

Backup:

```bash
cd /opt/CTFd

sudo docker compose exec -T db \
  mariadb-dump \
  -u root \
  -p"${MARIADB_ROOT_PASSWORD}" \
  --single-transaction \
  --routines \
  --triggers \
  ctfd \
  > /opt/backups/ctfd/ctfd.sql
```

Nếu shell host chưa có biến password, có thể load `.env` trước theo quy trình quản trị secret của môi trường.

Kiểm tra:

```bash
ls -lh /opt/backups/ctfd/ctfd.sql
```

Không commit file SQL backup vào Git.

---

# 27. Restore MariaDB

Trước restore phải xác nhận đúng database và backup.

Restore:

```bash
cd /opt/CTFd

sudo docker compose exec -T db \
  mariadb \
  -u root \
  -p"<ROOT_DATABASE_PASSWORD>" \
  ctfd \
  < /opt/backups/ctfd/ctfd.sql
```

Sau restore:

```bash
sudo docker compose restart ctfd
```

Kiểm tra:

```bash
sudo docker compose logs --tail=100 ctfd
```

---

# 28. Backup Uploads

Uploads nằm tại:

```text
/opt/CTFd/.data/CTFd/uploads
```

Backup:

```bash
sudo tar -czf \
  /opt/backups/ctfd/ctfd-uploads.tar.gz \
  -C /opt/CTFd/.data/CTFd \
  uploads
```

---

# 29. Restore Uploads

```bash
sudo tar -xzf \
  /opt/backups/ctfd/ctfd-uploads.tar.gz \
  -C /opt/CTFd/.data/CTFd/
```

Sau đó:

```bash
cd /opt/CTFd
sudo docker compose run --rm permissions
```

---

# 30. Backup Challenge Evidence

Các location cần xem xét:

```text
/opt/fakegpt
/opt/hawkeye
/opt/insider
/opt/CMC-JEDI-INVESTIGATION
/opt/ctfd-challenge-assets
```

Có thể backup:

```bash
sudo tar -czf \
  /opt/backups/ctfd/challenge-content.tar.gz \
  /opt/fakegpt \
  /opt/hawkeye \
  /opt/insider \
  /opt/CMC-JEDI-INVESTIGATION \
  /opt/ctfd-challenge-assets
```

Đối với forensic evidence lớn nên lưu tại storage/backup riêng và duy trì checksum.

---

# 31. Kiểm tra End-to-End

Sau cài đặt/restore phải kiểm tra tối thiểu:

```text
Login
  ↓
Tracks
  ↓
Level
  ↓
Lab
  ↓
JEDI Challenge
  ↓
Intermediate Stage
  ↓
Partial
  ↓
Final Stage
  ↓
Solve
  ↓
Score
  ↓
Track Progress
```

Kiểm tra các challenge:

```text
35
36
37
38
```

---

# 32. Kiểm tra MariaDB

```bash
sudo docker compose exec db \
  mariadb -u root -p
```

Trong MariaDB:

```sql
SHOW DATABASES;

USE ctfd;

SHOW TABLES;
```

Kiểm tra các bảng quan trọng:

```sql
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM challenges;
SELECT COUNT(*) FROM solves;
SELECT COUNT(*) FROM partials;
```

Thoát:

```sql
exit;
```

---

# 33. Update Source từ Git

Repository source:

```text
/opt/CTFd-CMC
```

Update:

```bash
cd /opt/CTFd-CMC

sudo git status
sudo git pull
```

Sau đó đồng bộ CTFd:

```bash
sudo rsync -a --delete \
  /opt/CTFd-CMC/CTFd/ \
  /opt/CTFd/
```

Không dùng `--delete` cho `.data` hoặc `.env`.

Đồng bộ plugin:

```bash
sudo rsync -a --delete \
  /opt/CTFd-CMC/CTFd-custom-plugins/ \
  /opt/CTFd-custom-plugins/
```

Sau thay đổi application:

```bash
cd /opt/CTFd

sudo docker compose up -d --build
```

---

# 34. Kiểm tra sau Update

```bash
sudo docker compose ps
```

```bash
sudo docker compose logs --tail=100 ctfd
```

```bash
sudo docker compose logs --tail=100 nginx
```

Kiểm tra:

```bash
curl -I http://127.0.0.1
```

Sau đó test:

```text
Login
Tracks
JEDI
Submit
Solve
Score
Progress
```

---

# 35. Rollback Source

Xem lịch sử:

```bash
cd /opt/CTFd-CMC

git log --oneline
```

Không sử dụng `git reset --hard` tùy tiện trên production.

Khuyến nghị checkout/tag phiên bản cần phục hồi trong maintenance window, đồng bộ lại source và rebuild.

Ví dụ kiểm tra một revision:

```bash
git checkout <COMMIT_ID>
```

Sau đó deploy lại source đã xác nhận.

---

# 36. Stop hệ thống

```bash
cd /opt/CTFd

sudo docker compose stop
```

---

# 37. Start lại hệ thống

```bash
sudo docker compose start
```

Hoặc:

```bash
sudo docker compose up -d
```

---

# 38. Restart

Toàn bộ:

```bash
sudo docker compose restart
```

Chỉ CTFd:

```bash
sudo docker compose restart ctfd
```

Chỉ Nginx:

```bash
sudo docker compose restart nginx
```

---

# 39. Không xóa Persistent Data tùy tiện

Không chạy:

```bash
rm -rf /opt/CTFd/.data
```

nếu chưa có backup.

Các directory quan trọng:

```text
/opt/CTFd/.data/mysql
/opt/CTFd/.data/CTFd/uploads
/opt/CTFd/.data/redis
```

Đặc biệt:

```text
.data/mysql
```

chứa database physical files.

---

# 40. Troubleshooting

## CTFd không start

```bash
sudo docker compose ps
sudo docker compose logs --tail=200 ctfd
```

---

## Database error

```bash
sudo docker compose ps db
sudo docker compose logs --tail=200 db
```

Kiểm tra `.env`:

```bash
sudo grep '^MARIADB_' /opt/CTFd/.env
```

Không gửi output chứa password lên ticket/chat không được kiểm soát.

---

## Redis error

```bash
sudo docker compose ps cache
sudo docker compose logs --tail=200 cache
```

---

## Nginx error

```bash
sudo docker compose logs --tail=200 nginx
```

Kiểm tra config:

```bash
sudo docker compose exec nginx nginx -t
```

---

## Plugin không load

```bash
sudo docker exec ctfd-ctfd-1 \
  ls -lah /opt/CTFd/CTFd/plugins
```

Sau đó:

```bash
sudo docker compose logs ctfd | \
  grep -Ei "plugin|jedi|track|dynamic|error|exception"
```

---

# 41. Kiểm tra dung lượng

```bash
df -h
```

Docker:

```bash
sudo docker system df
```

CTFd:

```bash
sudo du -sh /opt/CTFd/.data/*
```

Challenge:

```bash
sudo du -sh \
  /opt/fakegpt \
  /opt/hawkeye \
  /opt/insider \
  /opt/CMC-JEDI-INVESTIGATION \
  /opt/ctfd-challenge-assets
```

Không chạy `docker system prune -a` trên production nếu chưa đánh giá các image/container cần giữ.

---

# 42. Security Checklist

Trước khi đưa vào production:

* [ ] Repository ở chế độ Private.
* [ ] Không có `.env` trong Git.
* [ ] Không có password trong Git.
* [ ] Không có API token trong Git.
* [ ] Không có private key trong Git.
* [ ] MariaDB không publish ra host.
* [ ] Redis không publish ra host.
* [ ] Hạn chế truy cập trực tiếp TCP/8000.
* [ ] Production traffic đi qua reverse proxy.
* [ ] Có phương án TLS/HTTPS phù hợp.
* [ ] Backup MariaDB.
* [ ] Backup uploads.
* [ ] Backup challenge evidence.
* [ ] Kiểm tra restore.
* [ ] Kiểm tra dung lượng filesystem.
* [ ] Kiểm soát quyền truy cập `/opt/CTFd/.env`.

---

# 43. Kiểm tra Git trước khi Push

Trên máy development:

```bash
git status
git diff
```

Stage:

```bash
git add <file>
```

Kiểm tra:

```bash
git diff --cached
```

Commit:

```bash
git commit -m "type: description"
```

Push:

```bash
git push
```

Không sử dụng:

```bash
git push --force
```

trong workflow thông thường.

---

# 44. Commit Convention

```text
feat:       chức năng mới
fix:        sửa lỗi
security:   thay đổi bảo mật
config:     cấu hình
challenge:  challenge/content
docs:       tài liệu
refactor:   tái cấu trúc
```

Ví dụ:

```bash
git commit -m "feat: add JEDI investigation stage"
git commit -m "fix: correct CTF Tracks progress"
git commit -m "security: remove hardcoded database credentials"
git commit -m "challenge: update HawkEye configuration"
git commit -m "docs: update installation guide"
```

---

# 45. Quy trình Deployment chuẩn

```text
Developer
    |
    v
Modify Source
    |
    v
Local Test
    |
    v
git status / diff
    |
    v
Commit
    |
    v
Push
    |
    v
Private Git Repository
    |
    v
Production Server
    |
    v
git pull
    |
    v
Backup
    |
    v
Deploy
    |
    v
docker compose up -d --build
    |
    v
Validation
    |
    +--> Login
    +--> Tracks
    +--> JEDI
    +--> Solve
    +--> Score
    +--> Progress
```

---

# 46. Backup tối thiểu trước Deployment

Trước thay đổi production cần bảo vệ:

```text
MariaDB
Uploads
.env
CTFd configuration
Custom plugins
JEDI configs
Challenge evidence
```

Không coi container filesystem là backup.

---

# 47. Source of Truth

Git repository là source-of-truth cho source code.

Production paths:

```text
/opt/CTFd
/opt/CTFd-custom-plugins
```

Persistent runtime data:

```text
/opt/CTFd/.data
```

Challenge content:

```text
/opt/fakegpt
/opt/hawkeye
/opt/insider
/opt/CMC-JEDI-INVESTIGATION
/opt/ctfd-challenge-assets
```

Secret:

```text
/opt/CTFd/.env
```

Secret không thuộc Git repository.

---

# 48. Final Validation Checklist

Sau cài mới hoặc migration:

```bash
cd /opt/CTFd

sudo docker compose ps
```

Kiểm tra HTTP:

```bash
curl -I http://127.0.0.1
```

Kiểm tra plugin:

```bash
sudo docker exec ctfd-ctfd-1 \
  ls /opt/CTFd/CTFd/plugins
```

Kiểm tra database:

```bash
sudo docker compose exec db \
  mariadb -u root -p
```

Sau đó kiểm thử trên UI:

* [ ] Admin login thành công.
* [ ] User login thành công.
* [ ] Challenge hiển thị.
* [ ] CTF Tracks hiển thị.
* [ ] JEDI challenge hiển thị đúng stage.
* [ ] Challenge 35 hoạt động.
* [ ] Challenge 36 hoạt động.
* [ ] Challenge 37 hoạt động.
* [ ] Challenge 38 hoạt động.
* [ ] Intermediate answer tạo progress.
* [ ] Final answer tạo Solve.
* [ ] Score cập nhật.
* [ ] Track Progress cập nhật.
* [ ] Upload/download hoạt động.
* [ ] Nginx hoạt động.
* [ ] MariaDB không expose ra ngoài.
* [ ] Redis không expose ra ngoài.
* [ ] Log không có exception nghiêm trọng.

Khi toàn bộ checklist đạt yêu cầu, hệ thống có thể được coi là hoàn thành bước triển khai kỹ thuật.

---

# 49. Lưu ý quan trọng về Evidence

Repository Git không chứa đầy đủ các forensic artifact lớn nếu chúng bị loại bởi `.gitignore`, ví dụ:

```text
*.ad1
*.E01
*.e01
*.raw
*.mem
*.dmp
*.vmem
*.pcap
*.pcapng
*.tar.gz
```

Vì vậy:

```text
Clone Git
   +
Restore Evidence
   +
Restore Database/Uploads (nếu migration)
   =
Complete CTFd Environment
```

Không được coi Git repository là bản backup duy nhất của toàn bộ challenge evidence.

---

# 50. Kết luận

Hệ thống gồm ba nhóm dữ liệu cần quản lý riêng:

```text
1. SOURCE
   Git Repository
   ├── CTFd
   ├── Plugins
   └── Challenge Source

2. PERSISTENT DATA
   /opt/CTFd/.data
   ├── MariaDB
   ├── Uploads
   └── Redis

3. SECRET / LARGE EVIDENCE
   ├── /opt/CTFd/.env
   └── Forensic Evidence
```

Muốn tái dựng đầy đủ production cần có cả:

```text
Source
+
Environment Configuration
+
MariaDB
+
Uploads
+
Challenge Evidence
```

Không chỉ riêng Docker image hoặc Git repository.
