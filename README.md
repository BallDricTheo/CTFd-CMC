\# CTFd-CMC



Repository quản lý source code của hệ thống \*\*CTFd CMC\*\*, bao gồm CTFd Core, các custom plugin và source của các challenge phục vụ hệ thống CTF.



\## 1. Cấu trúc Repository



```text

CTFd-CMC/

├── CTFd/

│   ├── CTFd/

│   ├── conf/

│   ├── migrations/

│   ├── tests/

│   ├── Dockerfile

│   ├── docker-compose.yml

│   └── ...

│

├── CTFd-custom-plugins/

│   ├── ctf\_tracks/

│   ├── jedi\_challenge/

│   ├── dynamic\_challenges/

│   └── ...

│

├── Challenge/

│   └── ...

│

└── .gitignore

```



\### `CTFd/`



Chứa source code CTFd Core và các thành phần phục vụ triển khai hệ thống.



Thành phần chính:



\* CTFd application

\* Dockerfile

\* Docker Compose

\* Nginx configuration

\* Database migration

\* Theme và static assets

\* Các thành phần backend/API của CTFd



\### `CTFd-custom-plugins/`



Chứa các plugin được sử dụng hoặc tùy chỉnh cho hệ thống.



\#### `ctf\_tracks`



Quản lý cấu trúc bài thi theo:



```text

Track

&#x20;└── Level

&#x20;     └── Lab

&#x20;          └── Challenge

```



Plugin sử dụng dữ liệu solve của CTFd để xác định tiến độ của người chơi.



\#### `jedi\_challenge`



Custom challenge engine phục vụ các bài điều tra nhiều giai đoạn.



Luồng xử lý:



```text

Challenge

&#x20;  │

&#x20;  ├── Stage 1

&#x20;  │

&#x20;  ├── Stage 2

&#x20;  │

&#x20;  ├── Stage 3

&#x20;  │

&#x20;  └── ...

&#x20;  │

&#x20;  └── Final Stage

&#x20;         │

&#x20;         └── Solve

```



Các stage trung gian được ghi nhận dưới dạng tiến độ; challenge chỉ được tính hoàn thành khi người chơi hoàn thành stage cuối.



Configuration của challenge được quản lý trong:



```text

CTFd-custom-plugins/jedi\_challenge/configs/

```



\#### `dynamic\_challenges`



Plugin hỗ trợ cơ chế dynamic scoring của CTFd.



Plugin này phục vụ tính điểm challenge và không phải thành phần provision runtime/container challenge.



\## 2. Challenge Source



Thư mục:



```text

Challenge/

```



chứa source và các thành phần cần thiết của challenge.



Các forensic artifact dung lượng lớn không được lưu trực tiếp trong Git repository.



Các loại file được loại trừ bao gồm:



```text

\*.ad1

\*.E01

\*.e01

\*.raw

\*.mem

\*.dmp

\*.vmem

\*.pcap

\*.pcapng

\*.tar.gz

```



Các thư mục giải nén tạm thời cũng không được quản lý bằng Git:



```text

Challenge/\*\*/temp\_extract\_dir/

```



Evidence dung lượng lớn cần được lưu tại kho lưu trữ riêng và triển khai vào server theo quy trình vận hành.



\## 3. Kiến trúc triển khai



Hệ thống sử dụng Docker Compose.



Các thành phần chính:



```text

Client

&#x20;  │

&#x20;  ▼

&#x20;Nginx

&#x20;  │

&#x20;  ▼

&#x20;CTFd

&#x20;  │

&#x20;  ├──────────► MariaDB

&#x20;  │

&#x20;  └──────────► Redis

```



Các service chính:



| Service       | Chức năng                            |

| ------------- | ------------------------------------ |

| `nginx`       | Reverse proxy                        |

| `ctfd`        | CTFd application                     |

| `db`          | MariaDB database                     |

| `cache`       | Redis cache                          |

| `permissions` | Chuẩn bị quyền cho persistent volume |



\## 4. Custom Plugin Deployment



Custom plugins được quản lý riêng tại:



```text

CTFd-custom-plugins/

```



Khi triển khai bằng Docker Compose, thư mục plugin được mount vào plugin directory của CTFd.



Khuyến nghị sử dụng relative path:



```yaml

volumes:

&#x20; - ../CTFd-custom-plugins:/opt/CTFd/CTFd/plugins:ro

```



Điều này giúp repository có thể triển khai trên server khác mà không phụ thuộc vào absolute path của host.



\## 5. Environment Configuration



Không lưu password, API key, token hoặc credential trực tiếp trong repository.



`docker-compose.yml` sử dụng environment variables:



```yaml

DATABASE\_URL=mysql+pymysql://ctfd:${MARIADB\_PASSWORD}@db/ctfd

MARIADB\_ROOT\_PASSWORD=${MARIADB\_ROOT\_PASSWORD}

MARIADB\_PASSWORD=${MARIADB\_PASSWORD}

```



Tạo file:



```text

.env

```



trên server triển khai.



Ví dụ:



```text

MARIADB\_ROOT\_PASSWORD=<STRONG\_ROOT\_PASSWORD>

MARIADB\_PASSWORD=<STRONG\_CTFD\_PASSWORD>

```



File `.env` không được commit lên Git.



Có thể duy trì `.env.example` trong repository:



```text

MARIADB\_ROOT\_PASSWORD=CHANGE\_ME

MARIADB\_PASSWORD=CHANGE\_ME

```



`.env.example` chỉ chứa placeholder, không chứa credential thật.



\## 6. Triển khai hệ thống



Clone repository:



```bash

git clone <REPOSITORY\_URL>

cd CTFd-CMC

```



Tạo environment configuration:



```bash

cp .env.example .env

```



Cập nhật credential trong `.env`.



Sau đó:



```bash

cd CTFd

docker compose config

```



Kiểm tra configuration trước khi khởi động.



Nếu không có lỗi:



```bash

docker compose up -d --build

```



Kiểm tra container:



```bash

docker compose ps

```



Kiểm tra log:



```bash

docker compose logs --tail=100

```



\## 7. Cập nhật Source



Trước khi thay đổi:



```bash

git status

git pull

```



Sau khi chỉnh sửa:



```bash

git status

git diff

```



Stage thay đổi:



```bash

git add .

```



Commit:



```bash

git commit -m "Mô tả thay đổi"

```



Push:



```bash

git push

```



Không sử dụng `git push --force` trong quy trình cập nhật thông thường.



\## 8. Quy ước Commit



Nên sử dụng commit message ngắn gọn và thể hiện rõ phạm vi thay đổi.



Ví dụ:



```text

Update JEDI challenge configuration

Fix CTF Tracks progress calculation

Update HawkEye challenge

Fix challenge API

Update Docker deployment configuration

Security hardening for CTFd deployment

```



Có thể áp dụng convention:



```text

feat:     chức năng mới

fix:      sửa lỗi

security: thay đổi liên quan bảo mật

config:   thay đổi cấu hình

challenge: thay đổi challenge

docs:     cập nhật tài liệu

refactor: tái cấu trúc code

```



Ví dụ:



```bash

git commit -m "feat: add JEDI investigation stage"

git commit -m "fix: correct CTF Tracks progress calculation"

git commit -m "security: remove hardcoded database credentials"

git commit -m "challenge: update HawkEye configuration"

```



\## 9. Quy trình cập nhật Production



Không chỉnh sửa trực tiếp source production nếu thay đổi có thể được thực hiện thông qua Git workflow.



Luồng khuyến nghị:



```text

Development

&#x20;    │

&#x20;    ▼

Source Modification

&#x20;    │

&#x20;    ▼

Local Test

&#x20;    │

&#x20;    ▼

Git Commit

&#x20;    │

&#x20;    ▼

Git Push

&#x20;    │

&#x20;    ▼

Production Server

&#x20;    │

&#x20;    ▼

Git Pull

&#x20;    │

&#x20;    ▼

Deploy / Restart

&#x20;    │

&#x20;    ▼

Validation

```



Trên production:



```bash

git pull

```



Nếu thay đổi application hoặc dependency:



```bash

docker compose up -d --build

```



Nếu chỉ cần restart:



```bash

docker compose restart

```



Sau deployment:



```bash

docker compose ps

docker compose logs --tail=100

```



\## 10. Backup trước khi triển khai



Trước các thay đổi lớn cần backup tối thiểu:



\* Database

\* Uploaded files

\* Challenge configuration

\* Custom plugins

\* Environment configuration



Không commit database dump hoặc production credential vào repository.



\## 11. Security



Các nguyên tắc bắt buộc:



\* Không commit `.env`.

\* Không commit password.

\* Không commit private key.

\* Không commit API token.

\* Không commit production database dump.

\* Không commit forensic evidence dung lượng lớn.

\* Không hard-code credential trong `docker-compose.yml`.

\* Repository chứa source hệ thống nên được quản lý ở chế độ \*\*Private\*\*.

\* Quyền truy cập repository chỉ cấp cho nhân sự cần thiết.

\* Credential production phải được quản lý ngoài Git.



Trước khi push nên kiểm tra:



```bash

git status

git diff --cached

```



Có thể kiểm tra các loại file nhạy cảm:



```bash

git ls-files | grep -Ei '\\.env$|\\.pem$|\\.key$|\\.bak|\\.save|\\.tar\\.gz$|\\.ad1$|\\.E01$|\\.raw$|\\.mem$|\\.dmp$|\\.vmem$|\\.pcap$|\\.pcapng$'

```



\## 12. Rollback



Kiểm tra lịch sử:



```bash

git log --oneline

```



Nếu cần quay lại phiên bản trước để kiểm tra:



```bash

git checkout <COMMIT\_ID>

```



Đối với production, không nên reset hoặc force push tùy tiện. Nên xác định commit cần rollback và thực hiện quy trình rollback có kiểm soát.



Sau khi rollback source, rebuild/restart service nếu cần:



```bash

docker compose up -d --build

```



\## 13. Nguyên tắc quản lý Repository



Repository này được sử dụng làm nguồn quản lý source của hệ thống CTFd CMC.



```text

GitHub Private Repository

&#x20;         │

&#x20;         │ git pull

&#x20;         ▼

&#x20;  Production Server

&#x20;         │

&#x20;         ▼

&#x20;   Docker Compose

&#x20;         │

&#x20;   ┌─────┼──────┐

&#x20;   ▼     ▼      ▼

&#x20;  CTFd MariaDB Redis

&#x20;   │

&#x20;   ▼

Custom Plugins

&#x20;   │

&#x20;   ▼

Challenges

```



Mọi thay đổi quan trọng đối với source nên có commit tương ứng để đảm bảo:



\* Truy vết thay đổi.

\* Xác định người thực hiện.

\* So sánh phiên bản.

\* Rollback khi xảy ra lỗi.

\* Đồng bộ source giữa môi trường phát triển và production.



\## 14. Repository



Repository được quản lý trên GitHub dưới chế độ Private.



Branch triển khai chính:



```text

main

```



Initial source baseline:



```text

e7893af - Initial CTFd platform source

```



