"""
Playwright 기반 Pamtek HR API 서버
"""
import os
import sys
import io
import logging
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, jsonify
from src.auth_playwright import PamtekAuthPlaywright
from src.parser_playwright import PamtekParserPlaywright

# 인코딩 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask 앱 생성
app = Flask(__name__)

# 전역 변수
auth = None
parser = None

# 환경 변수 로드
load_dotenv()

USER_ID = os.getenv('PAMTEK_USER_ID')
PASSWORD = os.getenv('PAMTEK_PASSWORD')


def init_playwright():
    """Playwright 초기화 및 로그인"""
    global auth, parser

    if not USER_ID or not PASSWORD:
        raise Exception("PAMTEK_USER_ID 또는 PAMTEK_PASSWORD 환경 변수가 설정되지 않음")

    logger.info("Playwright 인증 초기화 중...")
    auth = PamtekAuthPlaywright(USER_ID, PASSWORD, headless=True)

    if not auth.login():
        raise Exception("로그인 실패")

    logger.info("Playwright 로그인 성공")

    # 파서 생성
    parser = PamtekParserPlaywright(auth)


def is_weekend():
    """오늘이 주말인지 확인"""
    today = datetime.now().weekday()
    return today in [5, 6]  # 5=토요일, 6=일요일


def ensure_logged_in():
    """
    로그인 상태 확인 및 필요 시 재로그인

    Returns:
        bool: 로그인 성공 여부
    """
    global auth, parser

    if not auth:
        logger.warning("인증 객체 없음 - 재초기화 시도")
        try:
            init_playwright()
            return True
        except Exception as e:
            logger.error(f"재초기화 실패: {e}")
            return False

    # 로그인 상태 확인
    if not auth.is_logged_in():
        logger.warning("세션 만료 감지 - 재로그인 시도")
        try:
            # 기존 브라우저 종료
            auth.close()

            # 재초기화
            init_playwright()
            logger.info("재로그인 성공")
            return True
        except Exception as e:
            logger.error(f"재로그인 실패: {e}")
            return False

    return True


@app.route('/api/status', methods=['GET'])
def get_status():
    """
    출근 상태 확인

    Returns:
        {
            "is_checked_in": bool,
            "is_checked_out": bool,
            "check_in_time": str,
            "check_out_time": str,
            "status": str,
            "need_action": bool,
            "is_weekend": bool
        }
    """
    try:
        # 로그인 상태 확인 및 재로그인
        if not ensure_logged_in():
            return jsonify({"error": "로그인 실패 - 서버 재시작 필요"}), 500

        if not parser:
            return jsonify({"error": "서버 초기화 안됨"}), 500

        # 주말 체크
        weekend = is_weekend()

        # 주말이면 간단한 응답 반환
        if weekend:
            return jsonify({
                "is_checked_in": False,
                "is_checked_out": False,
                "check_in_time": None,
                "check_out_time": None,
                "status": "weekend",
                "need_action": False,
                "is_weekend": True,
                "error": None
            })

        # 평일이면 실제 출근 상태 확인
        status = parser.get_attendance_status()

        # 세션 만료로 인한 에러 체크
        if status.get('error') and '세션' in str(status.get('error')):
            logger.warning("세션 만료 감지 - 재로그인 후 재시도")
            if ensure_logged_in():
                # 재로그인 성공 - 다시 시도
                status = parser.get_attendance_status()

        if status.get('error'):
            return jsonify({"error": status['error']}), 500

        # iOS Shortcuts에서 사용할 필드 추가
        status['need_action'] = not status['is_checked_in'] or not status['is_checked_out']
        status['is_weekend'] = False

        return jsonify(status)

    except Exception as e:
        logger.error(f"상태 조회 중 오류: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/summary', methods=['GET'])
def get_summary():
    """
    출근 현황 요약

    Returns:
        {
            "summary": str
        }
    """
    try:
        # 로그인 상태 확인 및 재로그인
        if not ensure_logged_in():
            return jsonify({"error": "로그인 실패 - 서버 재시작 필요"}), 500

        if not parser:
            return jsonify({"error": "서버 초기화 안됨"}), 500

        summary = parser.get_today_attendance_summary()

        # 에러 체크 및 재시도
        if "오류" in summary or "세션" in summary:
            logger.warning("세션 만료 가능성 - 재로그인 후 재시도")
            if ensure_logged_in():
                summary = parser.get_today_attendance_summary()

        return jsonify({"summary": summary})

    except Exception as e:
        logger.error(f"요약 조회 중 오류: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    """헬스 체크"""
    return jsonify({"status": "ok"})


if __name__ == '__main__':
    try:
        print("=" * 60)
        print("Pamtek HR Helper - Playwright 기반 서버")
        print("=" * 60)

        # Playwright 초기화
        print("\n[1/2] Playwright 초기화 및 로그인 중...")
        init_playwright()
        print("✅ Playwright 로그인 성공")

        # Flask 서버 시작
        print("\n[2/2] Flask 서버 시작 중...")
        print("=" * 60)
        print("서버 준비 완료!")
        print("API 엔드포인트:")
        print("  - GET /api/status   : 출근 상태 확인")
        print("  - GET /api/summary  : 출근 현황 요약")
        print("  - GET /health       : 헬스 체크")
        print("=" * 60)

        app.run(host='0.0.0.0', port=5000, debug=False)

    except KeyboardInterrupt:
        print("\n\n서버 종료 중...")
    except Exception as e:
        print(f"❌ 오류: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 브라우저 종료
        if auth:
            print("브라우저 종료 중...")
            auth.close()
        print("완료!")
