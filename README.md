# Pamtek HR Helper

Pamtek 근태 시스템 자동화 도우미 - Selenium 기반 실시간 출퇴근 확인

## 🎯 주요 기능

- ✅ 아침 회사 도착 시 출근 여부 자동 확인
- ✅ 미출근 시 알림 및 근태 앱 자동 실행
- ✅ 저녁 시간 퇴근 여부 확인 및 알림
- ✅ 주말 자동 감지 및 스킵
- ✅ 세션 만료 시 자동 재로그인
- ✅ 실시간 데이터 (페이지 자동 새로고침)

## 🏗️ 시스템 구성

```
┌─────────────────────┐
│   Flask API Server  │
│  (Selenium-based)   │
│                     │
│  - Auto re-login    │
│  - Real-time data   │
│  - Weekend check    │
└─────────────────────┘
          ↓
    ┌─────────┐
    │   API   │
    └─────────┘
          ↓
┌─────────────────────┐
│  iOS Shortcuts      │
│                     │
│  - Location trigger │
│  - Time trigger     │
│  - Smart alerts     │
└─────────────────────┘
```

## 🚀 빠른 시작 (Docker - 권장)

### 1. 저장소 클론

```bash
git clone https://github.com/YOUR_USERNAME/Pamtek_HR_Helper.git
cd Pamtek_HR_Helper
```

### 2. 환경 변수 설정

`.env` 파일 생성:

```bash
cp .env.example .env
# .env 파일을 열어서 로그인 정보 입력
```

`.env` 내용:
```env
PAMTEK_USER_ID=your_id
PAMTEK_PASSWORD=your_password
```

### 3. Docker로 실행

```bash
# 빌드 및 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f
```

### 4. 접속 확인

```bash
# 헬스 체크
curl http://localhost:5000/health

# 출근 상태 확인
curl http://localhost:5000/api/status
```

## 🐍 Python으로 직접 실행

### 1. 저장소 클론

```bash
git clone https://github.com/YOUR_USERNAME/Pamtek_HR_Helper.git
cd Pamtek_HR_Helper
```

### 2. 가상환경 생성 및 의존성 설치

```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

### 3. 환경 변수 설정

```bash
cp .env.example .env
# .env 파일 수정
```

### 4. 서버 실행

```bash
python main_selenium.py
```

## 📱 iOS Shortcuts 설정

자세한 설정 방법은 [iOS Shortcuts Guide](docs/iOS_Shortcuts_Guide.md)를 참고하세요.

**간단 요약:**
1. Shortcuts 앱에서 새 단축어 생성
2. URL: `http://YOUR_SERVER_IP:5000/api/status`
3. 위치 자동화: 회사 도착 시 실행
4. 시간 자동화: 오후 6시 퇴근 알림

## 📚 문서

- [iOS Shortcuts 설정 가이드](docs/iOS_Shortcuts_Guide.md) - 영어 버전 iOS 기준
- [Docker 실행 가이드](DOCKER_GUIDE.md) - Docker 배포 상세 설명

## 🔧 API 엔드포인트

### GET /api/status

출근 상태 확인 (실시간 데이터)

**응답 예시:**
```json
{
  "is_checked_in": true,
  "is_checked_out": false,
  "check_in_time": "08:45",
  "check_out_time": null,
  "status": "not_checked_out",
  "need_action": true,
  "is_weekend": false,
  "error": null
}
```

### GET /api/summary

간단한 텍스트 요약

**응답 예시:**
```json
{
  "summary": "출근: 08:45 (퇴근 전)"
}
```

### GET /health

헬스 체크

**응답 예시:**
```json
{
  "status": "ok"
}
```

## 🔐 보안

⚠️ **중요: 절대로 .env 파일을 Git에 커밋하지 마세요!**

- `.env` 파일은 `.gitignore`에 포함되어 있습니다
- 로그인 정보는 환경 변수로 안전하게 관리됩니다
- 외부 접속 시 HTTPS 사용 권장 (ngrok 또는 reverse proxy)

## 🛠️ 트러블슈팅

### 서버 접속 안됨

```bash
# 서버 상태 확인 (Docker)
docker-compose ps

# 로그 확인
docker-compose logs -f

# 직접 실행 시 방화벽 확인
```

### 세션 만료

서버가 자동으로 재로그인합니다. 로그를 확인하세요:
```
세션 만료 감지 - 재로그인 시도
재로그인 성공
```

### 주말에도 알림 옴

서버가 자동으로 주말을 감지합니다. `is_weekend: true` 확인하세요.

## 📋 요구사항

- Python 3.11+
- Chrome 브라우저 (Selenium용)
- Docker & Docker Compose (선택사항, 권장)
- iOS 14+ (Shortcuts 앱)

## 🌟 주요 기술

- **Flask** - REST API 서버
- **Selenium** - 브라우저 자동화 (암호화 우회)
- **BeautifulSoup** - HTML 파싱
- **Docker** - 컨테이너화 배포
- **iOS Shortcuts** - 자동화 트리거

## 📝 License

개인 사용 목적

## 🤝 Contributing

개인 프로젝트이므로 기여는 받지 않습니다.

## ⚠️ 면책 조항

이 프로젝트는 개인적인 편의를 위한 도구입니다. 회사 정책을 확인하고 사용하세요.
