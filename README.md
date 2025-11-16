# Pamtek HR Helper

Pamtek 근태 시스템 자동화 도우미 - Playwright 기반 실시간 출퇴근 확인

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
│ (Playwright-based)  │
│                     │
│  - Auto re-login    │
│  - Real-time data   │
│  - Weekend check    │
│  - Fast & stable    │
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

## 🚀 빠른 시작

### 1. 저장소 클론

```bash
git clone https://github.com/sung9155/PAMTEK_HR_HELPER.git
cd PAMTEK_HR_HELPER
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

`.env` 파일 생성 및 로그인 정보 입력:

```bash
PAMTEK_USER_ID=your_user_id
PAMTEK_PASSWORD=your_password
```

### 4. Playwright 브라우저 설치

```bash
# 가상환경 활성화된 상태에서
playwright install chromium
```

### 5. 서버 실행

```bash
python main_playwright.py
```

서버가 시작되면 `http://localhost:5000` 또는 `http://[YOUR_PC_IP]:5000`에서 접속 가능합니다.

## 📱 iOS Shortcuts 설정

자세한 설정 방법은 [iOS Shortcuts Guide](docs/iOS_Shortcuts_Guide.md)를 참고하세요.

**간단 요약:**
1. Shortcuts 앱에서 새 단축어 생성
2. URL: `http://YOUR_SERVER_IP:5000/api/status`
3. 위치 자동화: 회사 도착 시 실행
4. 시간 자동화: 오후 6시 퇴근 알림

## 📚 문서

- [iOS Shortcuts 설정 가이드](docs/iOS_Shortcuts_Guide.md) - 영어 버전 iOS 기준

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

**확인 사항:**
1. 서버가 실행 중인지 확인
2. 방화벽 설정 확인 (5000 포트 허용)
3. PC와 iPhone이 같은 네트워크에 있는지 확인
4. PC의 IP 주소가 올바른지 확인 (`ipconfig` 명령어로 확인)

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
- iOS 14+ (Shortcuts 앱)
- 서버를 항상 실행할 PC (Windows/Mac/Linux)
- 인터넷 연결 (Playwright가 Chromium 브라우저 자동 다운로드)

## 🌟 주요 기술

- **Flask** - REST API 서버
- **Playwright** - 현대적이고 빠른 브라우저 자동화 (Selenium보다 2-3배 빠름)
- **BeautifulSoup** - HTML 파싱
- **iOS Shortcuts** - 자동화 트리거
- **Python Virtual Environment** - 의존성 격리

## 💡 Selenium에서 Playwright로 전환한 이유

- **속도**: Selenium보다 2-3배 빠른 페이지 로딩 및 작업 실행
- **안정성**: 자동 대기(auto-wait) 및 재시도 메커니즘 내장
- **리소스 효율**: 헤드리스 모드 최적화로 메모리 사용량 절감
- **현대적 API**: async/await 지원 및 더 직관적인 API
- **브라우저 자동 설치**: ChromeDriver 수동 설치 불필요

## 📝 License

개인 사용 목적

## 🤝 Contributing

개인 프로젝트이므로 기여는 받지 않습니다.

## ⚠️ 면책 조항

이 프로젝트는 개인적인 편의를 위한 도구입니다. 회사 정책을 확인하고 사용하세요.
