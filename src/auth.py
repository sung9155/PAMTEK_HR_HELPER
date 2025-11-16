"""
Pamtek HR 로그인 및 세션 관리 모듈
"""
import os
import requests
import json
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


class PamtekAuth:
    """Pamtek HR 인증 관리 클래스"""

    def __init__(self, user_id: str, password: str, company_code: str = "KO883"):
        self.user_id = user_id
        self.password = password
        self.company_code = company_code
        self.consumer_code = f"T{company_code}"
        self.session = requests.Session()
        self.base_url = "https://hr.pamtek.com"

    def login(self) -> bool:
        """
        Pamtek HR 시스템에 로그인

        브라우저에서 확인된 실제 요청 방식:
        - Content-Type: application/json
        - X-Requested-With: XMLHttpRequest (AJAX)
        - company, consumer 헤더 필요

        Returns:
            bool: 로그인 성공 여부
        """
        try:
            # 1단계: 먼저 로그인 페이지 접속 (쿠키 획득)
            self.session.get(self.base_url, timeout=10)

            # 2단계: 로그인 요청 (JSON + AJAX)
            login_url = f"{self.base_url}/login.do"

            # JSON 데이터로 전송
            login_data = {
                'userId': self.user_id,
                'password': self.password
            }

            # 브라우저와 동일한 헤더 설정
            headers = {
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
                'Content-Type': 'application/json; charset=UTF-8',
                'Origin': self.base_url,
                'Referer': f'{self.base_url}/',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'X-Requested-With': 'XMLHttpRequest',
                'company': self.company_code,
                'consumer': self.consumer_code,
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin'
            }

            # JSON으로 POST 요청
            response = self.session.post(
                login_url,
                data=json.dumps(login_data),
                headers=headers,
                timeout=10,
                allow_redirects=False  # AJAX는 리다이렉트 하지 않음
            )

            logger.info(f"로그인 응답: {response.status_code} -> {response.url}")

            # JSON 응답 확인
            if response.status_code == 200:
                try:
                    result = response.json()
                    logger.info(f"로그인 응답: {result}")

                    # isError가 false이고 step이 있으면 성공
                    if not result.get('isError', True):
                        step = result.get('data', {}).get('step')
                        if step:  # step이 있으면 로그인 프로세스 진행됨
                            logger.info(f"로그인 성공 (step: {step})")

                            # 3단계: 홈 페이지로 이동하여 세션 확인
                            home_response = self.session.get(f"{self.base_url}/module/HR/home.do", timeout=10)
                            if 'dash-layout' in home_response.text or 'item-dash' in home_response.text:
                                logger.info("홈 페이지 접근 성공")
                                return True

                        error_msg = result.get('data', {}).get('errorMessage')
                        if error_msg:
                            logger.error(f"로그인 실패: {error_msg}")
                            return False
                    else:
                        logger.error(f"로그인 실패: {result.get('message', 'Unknown error')}")
                        return False

                except ValueError:
                    # JSON이 아닌 경우
                    logger.error("JSON 응답이 아님")
                    return False

            logger.error(f"로그인 실패 - HTTP {response.status_code}")
            return False

        except requests.RequestException as e:
            logger.error(f"로그인 요청 중 오류: {e}")
            return False

    def is_logged_in(self) -> bool:
        """
        현재 세션의 로그인 상태 확인

        Returns:
            bool: 로그인 상태
        """
        try:
            response = self.session.get(self.base_url, timeout=10)
            if '로그아웃' in response.text or 'logout' in response.text.lower():
                return True
            return False
        except requests.RequestException:
            return False

    def get_session(self) -> requests.Session:
        """
        현재 세션 반환

        Returns:
            requests.Session: 인증된 세션
        """
        if not self.is_logged_in():
            self.login()
        return self.session
