# Pamtek HR Helper 설치 및 실행 가이드

## 시스템 요구사항

- **Python**: 3.8 이상
- **OS**: Windows, macOS, Linux
- **네트워크**: PC와 iPhone이 같은 네트워크 또는 외부 접속 설정
- **iPhone**: iOS 14 이상 (단축어 앱 지원)

---

## 1. 프로젝트 설치

### 1-1. 저장소 다운로드

현재 폴더에 이미 프로젝트가 있다면 이 단계는 건너뛰세요.

### 1-2. Python 패키지 설치

```bash
cd d:\Utility\Pamtek_HR_Helper
pip install -r requirements.txt
```

**설치되는 패키지:**
- Flask: 웹 API 서버
- requests: HTTP 요청
- beautifulsoup4: HTML 파싱
- selenium: 웹 자동화 (필요시)
- python-dotenv: 환경 변수 관리
- cryptography: 암호화
- flask-cors: CORS 지원

---

## 2. 환경 설정

### 2-1. 환경 변수 파일 생성

1. `.env.example` 파일을 복사하여 `.env` 파일 생성:

```bash
copy .env.example .env
```

2. `.env` 파일을 편집기로 열어 정보 입력:

```env
# Pamtek HR 로그인 정보
PAMTEK_USER_ID=your_id_here
PAMTEK_PASSWORD=your_password_here

# 서버 설정
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=False

# 회사 위치 (GPS 좌표) - 필요시 수정
COMPANY_LATITUDE=37.5665
COMPANY_LONGITUDE=126.9780
LOCATION_RADIUS_METERS=100

# 근무 시간 설정
WORK_START_TIME=09:00
WORK_END_TIME=18:00
CHECK_MORNING_TIME=08:30
CHECK_EVENING_TIME=18:00
```

**중요:** `.env` 파일은 절대 공유하거나 git에 커밋하지 마세요!

### 2-2. 설정 파일 생성 (선택사항)

`config/settings.example.json`을 `config/settings.json`으로 복사하여 추가 설정 가능:

```bash
copy config\settings.example.json config\settings.json
```

---

## 3. 서버 실행

### 3-1. 기본 실행

```bash
python main.py
```

### 3-2. 실행 확인

브라우저에서 다음 URL 접속:

```
http://localhost:5000
```

다음과 같은 응답이 나오면 정상:

```json
{
  "status": "running",
  "service": "Pamtek HR Helper API",
  "version": "1.0.0"
}
```

### 3-3. API 테스트

**출근 상태 확인:**
```
http://localhost:5000/api/status
```

**출근 여부만 확인:**
```
http://localhost:5000/api/check-in
```

**퇴근 여부만 확인:**
```
http://localhost:5000/api/check-out
```

---

## 4. hr.pamtek.com 연동 설정

### 4-1. 로그인 페이지 분석 필요

현재 코드는 일반적인 형태로 작성되어 있습니다. 실제 사이트에 맞게 수정이 필요합니다.

**확인이 필요한 사항:**

1. **로그인 페이지 URL**
   - 실제 로그인 페이지 주소
   - 로그인 폼의 action URL

2. **로그인 폼 필드명**
   - 사용자 ID 입력 필드 name
   - 비밀번호 입력 필드 name
   - CSRF 토큰 등 추가 필드

3. **출근 현황 페이지**
   - 출근/퇴근 시간을 확인할 수 있는 페이지 URL
   - HTML 구조 (테이블, div 등)

### 4-2. 코드 수정 방법

**방법 1: 브라우저 개발자 도구 사용**

1. Chrome에서 `https://hr.pamtek.com` 접속
2. F12 눌러 개발자 도구 열기
3. Network 탭 선택
4. 로그인 시도
5. POST 요청 확인하여 다음 정보 수집:
   - URL
   - 폼 데이터 (Form Data)
   - 헤더 (Headers)

**방법 2: 직접 테스트**

`test_login.py` 파일을 만들어 테스트:

```python
from src.auth import PamtekAuth
import os
from dotenv import load_dotenv

load_dotenv()

auth = PamtekAuth(
    os.getenv('PAMTEK_USER_ID'),
    os.getenv('PAMTEK_PASSWORD')
)

if auth.login():
    print("로그인 성공!")

    # 출근 현황 페이지 HTML 출력
    response = auth.session.get('https://hr.pamtek.com/attendance')
    print(response.text)
else:
    print("로그인 실패")
```

**수정이 필요한 파일:**
- [src/auth.py](src/auth.py) - 로그인 로직
- [src/parser.py](src/parser.py) - HTML 파싱 로직

---

## 5. PC의 IP 주소 확인

iPhone에서 접속하려면 PC의 로컬 IP 주소가 필요합니다.

### Windows:

```bash
ipconfig
```

출력에서 `IPv4 주소` 찾기 (예: 192.168.0.10)

### macOS/Linux:

```bash
ifconfig
```

또는

```bash
ip addr
```

**중요:** `192.168.x.x` 또는 `10.x.x.x` 형태의 주소를 사용하세요.

---

## 6. 방화벽 설정

PC의 방화벽에서 포트 5000을 허용해야 합니다.

### Windows 방화벽:

1. Windows Defender 방화벽 > 고급 설정
2. 인바운드 규칙 > 새 규칙
3. 포트 선택 > TCP 5000 허용
4. 규칙 이름: "Pamtek HR Helper"

### macOS:

보통 추가 설정 불필요. 문제 시:
```bash
sudo pfctl -d  # 방화벽 임시 비활성화 (테스트용)
```

---

## 7. 백그라운드 실행 (선택사항)

### Windows - 작업 스케줄러 사용

1. 작업 스케줄러 실행
2. 기본 작업 만들기
3. 트리거: 로그온 시
4. 동작: `python d:\Utility\Pamtek_HR_Helper\main.py` 실행

### macOS/Linux - systemd 또는 launchd

`pamtek-hr.service` 파일 생성 (systemd):

```ini
[Unit]
Description=Pamtek HR Helper API Server

[Service]
ExecStart=/usr/bin/python3 /path/to/main.py
WorkingDirectory=/path/to/Pamtek_HR_Helper
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## 8. 외부 접속 설정 (선택사항)

회사와 집에서 모두 사용하려면:

### 방법 1: ngrok (가장 간단)

1. ngrok 설치: https://ngrok.com/download
2. ngrok 실행:
```bash
ngrok http 5000
```
3. 생성된 URL 사용 (예: `https://xxxx.ngrok.io`)

**장점:** 간단하고 빠름
**단점:** 무료 버전은 URL이 매번 바뀜, 속도 제한

### 방법 2: 클라우드 서버

- AWS EC2, Google Cloud, Azure VM 등
- 고정 IP 또는 도메인 사용
- 24시간 안정적 운영

---

## 9. 문제 해결

### 서버 실행 실패

**오류: "ModuleNotFoundError"**
```bash
pip install -r requirements.txt
```

**오류: "PAMTEK_USER_ID not found"**
- `.env` 파일이 있는지 확인
- 환경 변수가 올바르게 설정되었는지 확인

### 로그인 실패

1. `.env` 파일의 ID/PW 확인
2. 브라우저에서 수동 로그인 가능한지 확인
3. [src/auth.py](src/auth.py) 수정 필요할 수 있음

### iPhone에서 연결 안 됨

1. PC와 iPhone이 같은 WiFi 확인
2. IP 주소 재확인
3. 방화벽 설정 확인
4. 서버가 실행 중인지 확인

---

## 10. 로그 확인

서버 실행 시 터미널에 로그가 출력됩니다.

**로그 파일 생성 (선택사항):**

```python
# main.py 수정
import logging

logging.basicConfig(
    filename='logs/server.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

---

## 다음 단계

1. ✅ 서버 실행 확인
2. ✅ API 테스트 완료
3. ✅ hr.pamtek.com 연동 확인
4. → [iOS Shortcuts 설정](iOS_Shortcuts_Guide.md)

---

## 지원

문제가 발생하면:
1. 로그 확인
2. `.env` 설정 재확인
3. GitHub Issues에 문의
