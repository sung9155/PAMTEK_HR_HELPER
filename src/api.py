"""
Flask API 서버
iOS Shortcuts에서 호출할 수 있는 REST API 제공
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from dotenv import load_dotenv
import logging
from datetime import datetime

from .auth import PamtekAuth
from .parser import PamtekParser

# 환경 변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask 앱 생성
app = Flask(__name__)
CORS(app)  # iOS Shortcuts에서 접근 가능하도록 CORS 허용

# Pamtek 인증 객체 (전역)
pamtek_auth = None
pamtek_parser = None


def init_pamtek_client():
    """Pamtek 클라이언트 초기화"""
    global pamtek_auth, pamtek_parser

    user_id = os.getenv('PAMTEK_USER_ID')
    password = os.getenv('PAMTEK_PASSWORD')

    if not user_id or not password:
        logger.error("환경 변수에 PAMTEK_USER_ID와 PAMTEK_PASSWORD가 설정되지 않았습니다.")
        return False

    pamtek_auth = PamtekAuth(user_id, password)
    if pamtek_auth.login():
        pamtek_parser = PamtekParser(pamtek_auth.get_session())
        logger.info("Pamtek 클라이언트 초기화 성공")
        return True
    else:
        logger.error("Pamtek 로그인 실패")
        return False


@app.route('/')
def index():
    """API 상태 확인"""
    return jsonify({
        'status': 'running',
        'service': 'Pamtek HR Helper API',
        'version': '1.0.0',
        'endpoints': {
            '/api/status': 'Check attendance status',
            '/api/check-in': 'Check if checked in today',
            '/api/check-out': 'Check if checked out today'
        }
    })


@app.route('/api/status', methods=['GET'])
def get_status():
    """
    현재 출근/퇴근 상태 확인

    Returns:
        JSON: {
            'is_checked_in': bool,
            'is_checked_out': bool,
            'check_in_time': str,
            'check_out_time': str,
            'status': str,
            'message': str
        }
    """
    try:
        if not pamtek_parser:
            if not init_pamtek_client():
                return jsonify({
                    'error': 'Failed to initialize Pamtek client',
                    'status': 'error'
                }), 500

        attendance = pamtek_parser.get_attendance_status()

        # 메시지 생성
        if attendance['status'] == 'error':
            message = f"오류 발생: {attendance['error']}"
        elif not attendance['is_checked_in']:
            message = "아직 출근하지 않았습니다."
        elif not attendance['is_checked_out']:
            message = f"출근 완료 ({attendance['check_in_time']}), 퇴근 전입니다."
        else:
            message = f"출근/퇴근 완료 ({attendance['check_in_time']} ~ {attendance['check_out_time']})"

        return jsonify({
            'is_checked_in': attendance['is_checked_in'],
            'is_checked_out': attendance['is_checked_out'],
            'check_in_time': attendance['check_in_time'],
            'check_out_time': attendance['check_out_time'],
            'status': attendance['status'],
            'message': message,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"API 오류: {e}")
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500


@app.route('/api/check-in', methods=['GET'])
def check_in_status():
    """
    출근 여부만 확인 (iOS Shortcuts에서 간단히 사용)

    Returns:
        JSON: {
            'checked_in': bool,
            'time': str,
            'need_action': bool,
            'message': str
        }
    """
    try:
        if not pamtek_parser:
            if not init_pamtek_client():
                return jsonify({
                    'error': 'Failed to initialize',
                    'need_action': True
                }), 500

        attendance = pamtek_parser.get_attendance_status()

        return jsonify({
            'checked_in': attendance['is_checked_in'],
            'time': attendance['check_in_time'],
            'need_action': not attendance['is_checked_in'],
            'message': '출근 필요' if not attendance['is_checked_in'] else '출근 완료',
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"API 오류: {e}")
        return jsonify({
            'error': str(e),
            'need_action': True
        }), 500


@app.route('/api/check-out', methods=['GET'])
def check_out_status():
    """
    퇴근 여부만 확인 (iOS Shortcuts에서 간단히 사용)

    Returns:
        JSON: {
            'checked_out': bool,
            'time': str,
            'need_action': bool,
            'message': str
        }
    """
    try:
        if not pamtek_parser:
            if not init_pamtek_client():
                return jsonify({
                    'error': 'Failed to initialize',
                    'need_action': True
                }), 500

        attendance = pamtek_parser.get_attendance_status()

        # 출근하지 않았으면 퇴근 체크 의미 없음
        if not attendance['is_checked_in']:
            return jsonify({
                'checked_out': False,
                'time': None,
                'need_action': False,
                'message': '출근 전입니다',
                'timestamp': datetime.now().isoformat()
            })

        return jsonify({
            'checked_out': attendance['is_checked_out'],
            'time': attendance['check_out_time'],
            'need_action': not attendance['is_checked_out'],
            'message': '퇴근 필요' if not attendance['is_checked_out'] else '퇴근 완료',
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"API 오류: {e}")
        return jsonify({
            'error': str(e),
            'need_action': True
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """서버 헬스 체크"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })


def run_server(host='0.0.0.0', port=5000, debug=False):
    """Flask 서버 실행"""
    logger.info(f"Starting Flask server on {host}:{port}")

    # 서버 시작 전 Pamtek 클라이언트 초기화
    if not init_pamtek_client():
        logger.warning("초기 Pamtek 클라이언트 초기화 실패 - 첫 요청 시 재시도됩니다.")

    app.run(host=host, port=port, debug=debug)
