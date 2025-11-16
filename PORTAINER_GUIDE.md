# Portainer 실행 가이드

Portainer 웹 UI를 통해 Pamtek HR Helper를 쉽게 배포하고 관리하는 방법입니다.

## 📋 목차

1. [Portainer 설치](#portainer-설치)
2. [Docker 이미지 빌드](#docker-이미지-빌드)
3. [Portainer에서 Stack 배포](#portainer에서-stack-배포)
4. [환경 변수 설정](#환경-변수-설정)
5. [컨테이너 관리](#컨테이너-관리)
6. [문제 해결](#문제-해결)

---

## Portainer 설치

### 1. Portainer 컨테이너 실행

```bash
# Portainer 볼륨 생성
docker volume create portainer_data

# Portainer 실행 (Community Edition)
docker run -d \
  -p 9000:9000 \
  -p 9443:9443 \
  --name portainer \
  --restart=always \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v portainer_data:/data \
  portainer/portainer-ce:latest
```

**Windows의 경우:**
```bash
docker run -d ^
  -p 9000:9000 ^
  -p 9443:9443 ^
  --name portainer ^
  --restart=always ^
  -v //var/run/docker.sock:/var/run/docker.sock ^
  -v portainer_data:/data ^
  portainer/portainer-ce:latest
```

### 2. Portainer 접속

1. 브라우저에서 접속: `http://localhost:9000` 또는 `https://localhost:9443`
2. 최초 접속 시 관리자 계정 생성
   - Username: `admin`
   - Password: 최소 12자 이상
3. "Get Started" 클릭
4. "Local" 환경 선택

---

## Docker 이미지 빌드

Portainer에서 Stack을 배포하기 전에 먼저 Docker 이미지를 빌드해야 합니다.

### 방법 1: Windows PowerShell/CMD에서 빌드 (가장 쉬움) ⭐

**Windows PowerShell 또는 CMD를 관리자 권한으로 실행:**

```powershell
# 프로젝트 디렉토리로 이동
cd d:\Utility\Pamtek_HR_Helper

# Docker Desktop이 실행 중인지 확인
docker --version

# Docker 이미지 빌드 (5~10분 소요)
docker build -t pamtek-hr-helper:latest .

# 빌드 확인
docker images
```

**빌드 성공 확인:**
```
REPOSITORY            TAG       IMAGE ID       CREATED         SIZE
pamtek-hr-helper      latest    xxxxxxxxxxxxx  1 minute ago    1.5GB
```

### 방법 2: Portainer UI에서 직접 빌드 (복잡함)

**⚠️ 주의: Portainer UI 빌드는 다음과 같은 제약이 있습니다:**
- 프로젝트 전체를 ZIP으로 압축해야 함
- 파일 크기 제한 (보통 10MB)
- 빌드 시간 제한
- 에러 메시지가 불명확함

**Portainer UI에서 빌드가 실패하는 경우:**

1. **방법 1 (PowerShell 빌드)을 사용하세요** - 가장 안정적입니다
2. 또는 아래 방법 3 (Git Repository)을 사용하세요

### 방법 3: GitHub에서 자동 빌드 (고급)

**Stack 설정 시 build 옵션 사용:**

`portainer-stack.yml` 수정:

```yaml
version: '3.8'

services:
  pamtek-hr-helper:
    build:
      context: https://github.com/sung9155/PAMTEK_HR_HELPER.git
      dockerfile: Dockerfile
    image: pamtek-hr-helper:latest
    container_name: pamtek-hr-helper
    ports:
      - "5000:5000"
    environment:
      - PAMTEK_USER_ID=${PAMTEK_USER_ID}
      - PAMTEK_PASSWORD=${PAMTEK_PASSWORD}
    restart: unless-stopped
    shm_size: '2gb'
```

**⚠️ 주의:**
- Portainer는 Git URL 빌드를 제한적으로 지원합니다
- Public 저장소만 가능합니다
- 빌드 시간이 오래 걸릴 수 있습니다

### 권장 워크플로우 (가장 확실한 방법)

1. **Windows에서 이미지 빌드:**
   ```powershell
   cd d:\Utility\Pamtek_HR_Helper
   docker build -t pamtek-hr-helper:latest .
   ```

2. **Portainer에서 Stack 배포:**
   - 이미 빌드된 이미지(`pamtek-hr-helper:latest`)를 사용
   - Stack 설정에서 환경 변수만 입력
   - Deploy 클릭

---

## Portainer에서 Stack 배포

### 1. Stack 생성

1. Portainer 왼쪽 메뉴에서 **Stacks** 클릭
2. **Add stack** 버튼 클릭
3. Stack 이름 입력: `pamtek-hr-helper`

### 2. Stack 설정 방법 (2가지 중 선택)

#### 방법 A: Web editor 사용

1. **Web editor** 탭 선택
2. `portainer-stack.yml` 내용 복사 & 붙여넣기:

```yaml
version: '3.8'

services:
  pamtek-hr-helper:
    image: pamtek-hr-helper:latest
    container_name: pamtek-hr-helper
    ports:
      - "5000:5000"
    environment:
      - PAMTEK_USER_ID=${PAMTEK_USER_ID}
      - PAMTEK_PASSWORD=${PAMTEK_PASSWORD}
    restart: unless-stopped
    shm_size: '2gb'
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

#### 방법 B: Git Repository 사용

1. **Repository** 탭 선택
2. 설정:
   - **Repository URL**: GitHub 저장소 URL
   - **Repository reference**: `refs/heads/main`
   - **Compose path**: `portainer-stack.yml`
3. **Automatic updates** 활성화 (선택사항)

### 3. 환경 변수 설정

Stack 설정 화면 아래 **Environment variables** 섹션에서:

**Advanced mode** 활성화 후:

```env
PAMTEK_USER_ID=your_user_id
PAMTEK_PASSWORD=your_password
```

또는 **Simple mode**에서 개별 입력:
- Name: `PAMTEK_USER_ID`, Value: `your_user_id`
- Name: `PAMTEK_PASSWORD`, Value: `your_password`

### 4. Stack 배포

1. **Deploy the stack** 버튼 클릭
2. 배포 완료 대기 (30초~1분)
3. Status가 **running**으로 변경 확인

---

## 환경 변수 설정

### 보안 권장사항

Portainer의 **Secrets** 기능을 사용하여 민감한 정보를 안전하게 저장:

#### 1. Secret 생성

1. **Secrets** 메뉴 클릭
2. **Add secret** 클릭
3. Secret 생성:
   - Name: `pamtek_user_id`
   - Secret: `your_actual_user_id`
4. 비밀번호도 동일하게 생성:
   - Name: `pamtek_password`
   - Secret: `your_actual_password`

#### 2. Stack에서 Secret 사용

`portainer-stack.yml` 수정:

```yaml
version: '3.8'

services:
  pamtek-hr-helper:
    image: pamtek-hr-helper:latest
    container_name: pamtek-hr-helper
    ports:
      - "5000:5000"
    secrets:
      - pamtek_user_id
      - pamtek_password
    environment:
      - PAMTEK_USER_ID=/run/secrets/pamtek_user_id
      - PAMTEK_PASSWORD=/run/secrets/pamtek_password
    restart: unless-stopped
    shm_size: '2gb'

secrets:
  pamtek_user_id:
    external: true
  pamtek_password:
    external: true
```

---

## 컨테이너 관리

### 로그 확인

1. **Stacks** → `pamtek-hr-helper` 클릭
2. **pamtek-hr-helper** 컨테이너 클릭
3. **Logs** 탭 선택
4. 옵션:
   - **Auto-refresh logs**: 실시간 로그 확인
   - **Fetch**: 최신 로그 다시 불러오기
   - **Lines**: 표시할 라인 수 (기본 100)

### 컨테이너 재시작

1. **Containers** 메뉴 클릭
2. `pamtek-hr-helper` 체크박스 선택
3. **Restart** 버튼 클릭

또는:

1. **Stacks** → `pamtek-hr-helper` 클릭
2. 컨테이너 이름 클릭
3. 상단 **Restart** 버튼 클릭

### 컨테이너 중지/시작

**중지:**
1. 컨테이너 선택
2. **Stop** 버튼 클릭

**시작:**
1. 컨테이너 선택
2. **Start** 버튼 클릭

### Stack 업데이트

1. **Stacks** → `pamtek-hr-helper` 클릭
2. **Editor** 탭에서 설정 수정
3. **Update the stack** 버튼 클릭
4. 옵션 선택:
   - ✅ **Re-pull image and redeploy**: 이미지 다시 다운로드
   - ✅ **Prune services**: 사용하지 않는 서비스 제거

### 리소스 모니터링

1. **Containers** → `pamtek-hr-helper` 클릭
2. **Stats** 탭 선택
3. 실시간 확인:
   - CPU 사용률
   - 메모리 사용량
   - 네트워크 I/O
   - 블록 I/O

---

## 문제 해결

### 1. 이미지를 찾을 수 없음 (Image not found)

**증상:**
```
Error: pull access denied for pamtek-hr-helper, repository does not exist
```

**해결:**
```bash
# 로컬에서 이미지 빌드
cd d:\Utility\Pamtek_HR_Helper
docker build -t pamtek-hr-helper:latest .

# Portainer에서 Stack 재배포
```

### 2. 환경 변수가 적용되지 않음

**확인 방법:**
1. 컨테이너 클릭 → **Inspect** 탭
2. "Env" 섹션에서 환경 변수 확인

**해결:**
- Stack 편집 → Environment variables 재설정
- **Update the stack** 클릭

### 3. 컨테이너가 계속 재시작됨

**로그 확인:**
1. **Logs** 탭에서 에러 메시지 확인
2. 일반적인 원인:
   - 잘못된 로그인 정보
   - Chrome 실행 실패 (shm_size 부족)
   - 네트워크 연결 문제

**해결:**
```bash
# shm_size 확인
docker inspect pamtek-hr-helper | grep -i shm

# 로그인 정보 재확인
# Portainer에서 환경 변수 수정
```

### 4. 포트 충돌 (Port already in use)

**증상:**
```
Bind for 0.0.0.0:5000 failed: port is already allocated
```

**해결:**
1. Stack 편집
2. 포트 변경:
   ```yaml
   ports:
     - "5001:5000"  # 호스트 포트를 5001로 변경
   ```
3. Stack 업데이트

### 5. Health check 실패

**확인:**
1. 컨테이너 클릭
2. **Health** 상태 확인 (healthy/unhealthy)

**해결:**
```bash
# 컨테이너 내부에서 테스트
docker exec pamtek-hr-helper curl http://localhost:5000/health

# 응답이 없으면 서버 로그 확인
```

---

## 고급 설정

### 1. 외부 접근 허용 (Reverse Proxy)

nginx-proxy-manager Stack 추가:

```yaml
version: '3.8'

services:
  nginx-proxy-manager:
    image: 'jc21/nginx-proxy-manager:latest'
    restart: unless-stopped
    ports:
      - '80:80'
      - '81:81'
      - '443:443'
    volumes:
      - ./data:/data
      - ./letsencrypt:/etc/letsencrypt
```

### 2. 자동 업데이트 (Watchtower)

```yaml
  watchtower:
    image: containrrr/watchtower
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      - WATCHTOWER_CLEANUP=true
      - WATCHTOWER_POLL_INTERVAL=86400  # 24시간
```

### 3. 리소스 제한

Stack에 추가:

```yaml
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 2G
        reservations:
          memory: 512M
```

---

## Portainer vs Docker Compose 비교

| 기능 | Docker Compose | Portainer |
|------|----------------|-----------|
| 배포 방식 | CLI 명령어 | 웹 UI |
| 관리 편의성 | 중간 | 높음 |
| 로그 확인 | `docker logs` | 웹 UI 클릭 |
| 재시작 | CLI 명령어 | 버튼 클릭 |
| 환경 변수 수정 | 파일 수정 | 웹 UI 폼 |
| 모니터링 | 별도 도구 필요 | 내장 |
| 접근성 | 서버 접속 필요 | 웹 브라우저 |

---

## 다음 단계

1. ✅ Portainer 설치 완료
2. ✅ Stack 배포 완료
3. ✅ 컨테이너 정상 실행 확인
4. 🔄 iOS Shortcuts 설정
5. 🔄 자동화 테스트

---

## 참고 링크

- [Portainer 공식 문서](https://docs.portainer.io/)
- [Docker Compose 파일 레퍼런스](https://docs.docker.com/compose/compose-file/)
- [Portainer Community Edition](https://www.portainer.io/products/community-edition)

---

## 요약

Portainer를 사용하면:
- ✅ 웹 UI로 쉽게 컨테이너 관리
- ✅ 클릭 한 번으로 재시작/중지/시작
- ✅ 실시간 로그 및 리소스 모니터링
- ✅ Git 연동으로 자동 배포 가능
- ✅ 환경 변수 및 Secret 관리 간편

Docker 명령어를 몰라도 누구나 쉽게 관리할 수 있습니다!
