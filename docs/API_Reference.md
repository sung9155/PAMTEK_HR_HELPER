# API Reference

Pamtek HR Helper API 명세서

## Base URL

```
http://[SERVER_IP]:5000
```

로컬 테스트: `http://localhost:5000`

---

## Endpoints

### 1. Health Check

서버 상태 확인

**Endpoint:** `GET /`

**Response:**
```json
{
  "status": "running",
  "service": "Pamtek HR Helper API",
  "version": "1.0.0",
  "endpoints": {
    "/api/status": "Check attendance status",
    "/api/check-in": "Check if checked in today",
    "/api/check-out": "Check if checked out today"
  }
}
```

---

### 2. Get Full Attendance Status

현재 출근/퇴근 전체 상태 조회

**Endpoint:** `GET /api/status`

**Response:**
```json
{
  "is_checked_in": true,
  "is_checked_out": false,
  "check_in_time": "08:45",
  "check_out_time": null,
  "status": "not_checked_out",
  "message": "출근 완료 (08:45), 퇴근 전입니다.",
  "timestamp": "2025-11-15T14:30:00"
}
```

**Status Values:**
- `not_checked_in`: 미출근
- `not_checked_out`: 출근 완료, 퇴근 전
- `completed`: 출근/퇴근 모두 완료
- `error`: 오류 발생

**Error Response:**
```json
{
  "error": "Failed to initialize Pamtek client",
  "status": "error"
}
```

**HTTP Status Codes:**
- `200`: 성공
- `500`: 서버 오류

---

### 3. Check-In Status

출근 여부만 간단히 확인 (iOS Shortcuts 최적화)

**Endpoint:** `GET /api/check-in`

**Response (미출근):**
```json
{
  "checked_in": false,
  "time": null,
  "need_action": true,
  "message": "출근 필요",
  "timestamp": "2025-11-15T08:30:00"
}
```

**Response (출근 완료):**
```json
{
  "checked_in": true,
  "time": "08:45",
  "need_action": false,
  "message": "출근 완료",
  "timestamp": "2025-11-15T09:00:00"
}
```

**Fields:**
- `checked_in` (boolean): 출근 여부
- `time` (string|null): 출근 시간 (HH:MM)
- `need_action` (boolean): 사용자 액션 필요 여부 (iOS Shortcuts에서 사용)
- `message` (string): 상태 메시지
- `timestamp` (string): 응답 생성 시간 (ISO 8601)

---

### 4. Check-Out Status

퇴근 여부만 간단히 확인 (iOS Shortcuts 최적화)

**Endpoint:** `GET /api/check-out`

**Response (미퇴근):**
```json
{
  "checked_out": false,
  "time": null,
  "need_action": true,
  "message": "퇴근 필요",
  "timestamp": "2025-11-15T18:00:00"
}
```

**Response (퇴근 완료):**
```json
{
  "checked_out": true,
  "time": "18:05",
  "need_action": false,
  "message": "퇴근 완료",
  "timestamp": "2025-11-15T18:30:00"
}
```

**Response (출근 전):**
```json
{
  "checked_out": false,
  "time": null,
  "need_action": false,
  "message": "출근 전입니다",
  "timestamp": "2025-11-15T18:00:00"
}
```

**Fields:**
- `checked_out` (boolean): 퇴근 여부
- `time` (string|null): 퇴근 시간 (HH:MM)
- `need_action` (boolean): 사용자 액션 필요 여부
- `message` (string): 상태 메시지
- `timestamp` (string): 응답 생성 시간

**Note:** 출근하지 않은 상태에서는 `need_action`이 `false`입니다.

---

### 5. Health Check (Detailed)

서버 상태 및 응답 시간 확인

**Endpoint:** `GET /api/health`

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-15T12:00:00"
}
```

---

## iOS Shortcuts 사용 예시

### 출근 체크 단축어

```
URL 가져오기: http://192.168.0.10:5000/api/check-in
  ↓
URL의 내용 가져오기 (GET)
  ↓
사전에서 값 가져오기: need_action
  ↓
if need_action = true
  → 알림: "출근하세요!"
  → 앱 열기: Pamtek 근태앱
else
  → 알림: "이미 출근하셨습니다"
```

### 퇴근 알림 단축어

```
URL 가져오기: http://192.168.0.10:5000/api/check-out
  ↓
URL의 내용 가져오기 (GET)
  ↓
사전에서 값 가져오기: need_action
  ↓
if need_action = true
  → 알림: "퇴근하세요!"
  → 앱 열기: Pamtek 근태앱
else
  → 알림: "이미 퇴근하셨습니다"
```

---

## Error Handling

모든 엔드포인트는 다음과 같은 오류 응답을 반환할 수 있습니다:

```json
{
  "error": "Error message here",
  "status": "error"
}
```

**HTTP Status Codes:**
- `200`: 성공
- `400`: 잘못된 요청
- `500`: 서버 내부 오류

---

## CORS

모든 엔드포인트는 CORS가 활성화되어 있어 다음에서 접근 가능:
- iOS Shortcuts
- 웹 브라우저
- 다른 도메인의 애플리케이션

---

## Rate Limiting

현재 버전에는 Rate Limiting이 없습니다.

프로덕션 환경에서는 다음 추가 권장:
- API 키 인증
- Rate Limiting (예: 분당 60회)
- HTTPS 사용

---

## 버전 정보

- **API Version**: 1.0.0
- **Last Updated**: 2025-11-15
