# Docker 실행 가이드

Pamtek HR Helper를 Docker 컨테이너로 실행하는 방법입니다.

## 사전 요구사항

- Docker 설치 (https://www.docker.com/get-started)
- Docker Compose 설치 (Docker Desktop에 포함)

## 빠른 시작

### 1. 환경 변수 설정

`.env` 파일이 프로젝트 루트에 있는지 확인:

```bash
PAMTEK_USER_ID=your_id
PAMTEK_PASSWORD=your_password
```

### 2. Docker Compose로 실행

```bash
# 이미지 빌드 및 컨테이너 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 컨테이너 상태 확인
docker-compose ps
```

### 3. API 테스트

```bash
# 헬스 체크
curl http://localhost:5000/health

# 출근 상태 확인
curl http://localhost:5000/api/status

# 출근 현황 요약
curl http://localhost:5000/api/summary
```

## Docker 명령어

### 빌드

```bash
# 이미지 빌드
docker-compose build

# 캐시 없이 빌드
docker-compose build --no-cache
```

### 실행

```bash
# 백그라운드에서 실행
docker-compose up -d

# 포그라운드에서 실행 (로그 실시간 확인)
docker-compose up

# 특정 서비스만 실행
docker-compose up pamtek-hr-helper
```

### 중지 및 제거

```bash
# 컨테이너 중지
docker-compose stop

# 컨테이너 중지 및 제거
docker-compose down

# 컨테이너, 볼륨, 이미지 모두 제거
docker-compose down -v --rmi all
```

### 로그 확인

```bash
# 모든 로그 확인
docker-compose logs

# 실시간 로그 확인
docker-compose logs -f

# 최근 100줄만 확인
docker-compose logs --tail=100

# 특정 서비스 로그만 확인
docker-compose logs pamtek-hr-helper
```

### 디버깅

```bash
# 컨테이너 내부 접속
docker-compose exec pamtek-hr-helper /bin/bash

# 컨테이너 재시작
docker-compose restart

# 컨테이너 상태 확인
docker-compose ps
docker-compose top
```

## 직접 Docker 사용 (docker-compose 없이)

### 빌드

```bash
docker build -t pamtek-hr-helper .
```

### 실행

```bash
docker run -d \
  --name pamtek-hr-helper \
  -p 5000:5000 \
  --env-file .env \
  --shm-size=2g \
  pamtek-hr-helper
```

### 환경 변수로 직접 전달

```bash
docker run -d \
  --name pamtek-hr-helper \
  -p 5000:5000 \
  -e PAMTEK_USER_ID=your_id \
  -e PAMTEK_PASSWORD=your_password \
  --shm-size=2g \
  pamtek-hr-helper
```

### 중지 및 제거

```bash
# 컨테이너 중지
docker stop pamtek-hr-helper

# 컨테이너 제거
docker rm pamtek-hr-helper

# 이미지 제거
docker rmi pamtek-hr-helper
```

## 포트 변경

기본 포트(5000)를 변경하려면 `docker-compose.yml` 수정:

```yaml
ports:
  - "8080:5000"  # 호스트:컨테이너
```

또는 직접 실행 시:

```bash
docker run -d -p 8080:5000 ... pamtek-hr-helper
```

## 문제 해결

### Chrome이 실행되지 않을 때

컨테이너에 충분한 공유 메모리를 할당해야 합니다:

```yaml
# docker-compose.yml
shm_size: '2gb'
```

### 로그인 실패

1. 환경 변수 확인:
   ```bash
   docker-compose exec pamtek-hr-helper printenv | grep PAMTEK
   ```

2. 컨테이너 내부에서 테스트:
   ```bash
   docker-compose exec pamtek-hr-helper python test_selenium_final.py
   ```

### 네트워크 문제

방화벽이나 프록시 설정을 확인하세요. 컨테이너가 hr.pamtek.com에 접근할 수 있어야 합니다.

## 프로덕션 배포

### Gunicorn 사용 (권장)

`requirements.txt`에 추가:
```
gunicorn==21.2.0
```

`Dockerfile` CMD 수정:
```dockerfile
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:5000", "--timeout", "120", "main_selenium:app"]
```

**주의**: Selenium은 상태를 유지하므로 worker를 1개만 사용해야 합니다.

### 자동 재시작

```yaml
# docker-compose.yml
restart: unless-stopped
```

### 리소스 제한

```yaml
# docker-compose.yml
deploy:
  resources:
    limits:
      cpus: '1'
      memory: 2G
    reservations:
      memory: 512M
```

## iOS Shortcuts 설정

Docker 컨테이너가 실행 중인 서버의 IP 주소를 확인:

```bash
# 로컬 네트워크 IP 확인 (Windows)
ipconfig

# 로컬 네트워크 IP 확인 (Linux/Mac)
ifconfig
```

iOS Shortcuts에서:
- 서버 주소: `http://YOUR_SERVER_IP:5000`
- 예: `http://192.168.1.100:5000/api/status`

## 참고

- Chrome은 headless 모드로 실행됩니다
- 컨테이너는 자동으로 헬스체크를 수행합니다
- 로그는 최대 10MB × 3개 파일로 제한됩니다
- 컨테이너 재시작 시 자동으로 다시 로그인합니다
