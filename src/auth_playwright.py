"""
Playwright 기반 Pamtek HR 로그인 모듈
Selenium보다 빠르고 안정적인 브라우저 자동화
"""
import logging
from typing import Optional
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
import time

logger = logging.getLogger(__name__)


class PamtekAuthPlaywright:
    """Playwright 기반 Pamtek HR 인증 클래스"""

    def __init__(self, user_id: str, password: str, headless: bool = True):
        self.user_id = user_id
        self.password = password
        self.headless = headless
        self.base_url = "https://hr.pamtek.com"
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    def _init_browser(self):
        """Playwright 브라우저 초기화"""
        if self.browser:
            return

        try:
            self.playwright = sync_playwright().start()

            # Chromium 브라우저 시작 (Chrome과 동일한 엔진)
            self.browser = self.playwright.chromium.launch(
                headless=self.headless,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                ]
            )

            # 브라우저 컨텍스트 생성 (쿠키, 세션 관리)
            self.context = self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )

            # 새 페이지 생성
            self.page = self.context.new_page()

            logger.info("Playwright 브라우저 초기화 성공")

        except Exception as e:
            logger.error(f"Playwright 브라우저 초기화 실패: {e}")
            raise

    def login(self) -> bool:
        """
        Playwright를 사용한 로그인

        Returns:
            bool: 로그인 성공 여부
        """
        try:
            self._init_browser()

            logger.info("로그인 페이지 접속 중...")
            self.page.goto(self.base_url, wait_until='networkidle')

            # 사용자 ID 입력 - Playwright는 자동으로 요소를 기다림
            logger.info(f"사용자 ID 입력: {self.user_id}")
            self.page.fill('#userID', self.user_id)

            # 비밀번호 입력
            logger.info("비밀번호 입력 완료")
            self.page.fill('#password', self.password)

            # 입력 완료 후 잠시 대기
            time.sleep(0.5)

            # 로그인 버튼 클릭
            logger.info("로그인 버튼 클릭")
            self.page.click('#btnLogin')

            # 로그인 처리 완료 대기 - 네트워크 idle 상태까지 대기
            try:
                # 로그인 폼이 사라질 때까지 대기 (최대 10초)
                self.page.wait_for_selector('#loginForm', state='hidden', timeout=10000)
                logger.info("로그인 폼 사라짐 확인")
            except:
                logger.warning("로그인 폼이 사라지지 않음 - 계속 진행")

            # 추가 대기 - AJAX 요청 완료
            self.page.wait_for_load_state('networkidle')
            time.sleep(1)

            # 로그인 성공 확인
            current_url = self.page.url
            page_content = self.page.content()

            logger.info(f"로그인 후 URL: {current_url}")

            # 로그인 페이지로 돌아갔는지 확인
            if 'loginForm' in page_content or 'login' in current_url.lower():
                logger.error("로그인 실패 - 세션 없음")
                return False

            # 홈 페이지 내용 확인
            if 'dash-layout' in page_content or 'item-dash' in page_content:
                logger.info("✅ 로그인 성공! 홈 페이지 확인됨")
                return True

            # URL로 확인
            if 'home.do' in current_url or '/module/HR/' in current_url:
                logger.info("✅ 로그인 성공! (URL 확인)")
                return True

            logger.warning(f"예상치 못한 상태: {current_url}")
            return False

        except Exception as e:
            logger.error(f"로그인 중 오류: {e}")
            return False

    def get_page_source(self) -> Optional[str]:
        """
        현재 페이지의 HTML 소스 반환

        Returns:
            str: HTML 소스 또는 None
        """
        if not self.page:
            logger.error("페이지가 초기화되지 않음")
            return None

        return self.page.content()

    def navigate_to_home(self, refresh: bool = True) -> bool:
        """
        홈 페이지로 이동 또는 새로고침

        Args:
            refresh: True면 페이지를 새로고침하여 최신 데이터 가져오기 (기본값: True)

        Returns:
            bool: 성공 여부
        """
        try:
            if not self.page:
                logger.error("페이지가 초기화되지 않음")
                return False

            # 현재 페이지 확인
            current_url = self.page.url
            page_content = self.page.content()

            # 로그인 페이지라면 실패
            if 'login' in current_url.lower() or 'loginForm' in page_content:
                logger.error("로그인 페이지에 있음 - 세션 만료")
                return False

            # 이미 홈 페이지에 있으면
            if 'dash-layout' in page_content or 'item-dash' in page_content:
                if refresh:
                    logger.info(f"홈 페이지 새로고침 중: {current_url}")
                    self.page.reload(wait_until='networkidle')
                    time.sleep(1)

                    # 새로고침 후 로그인 페이지로 돌아갔는지 확인
                    if 'loginForm' in self.page.content():
                        logger.error("새로고침 후 세션 만료됨")
                        return False

                    logger.info("페이지 새로고침 완료")
                else:
                    logger.info(f"이미 홈 페이지에 있음: {current_url}")
                return True

            logger.warning(f"예상치 못한 페이지: {current_url}")
            return False

        except Exception as e:
            logger.error(f"홈 페이지 확인 중 오류: {e}")
            return False

    def is_logged_in(self) -> bool:
        """
        현재 로그인 상태 확인

        Returns:
            bool: 로그인 상태
        """
        if not self.page:
            return False

        try:
            current_url = self.page.url
            page_content = self.page.content()

            # URL에 login이 있으면 로그아웃 상태
            if 'login' in current_url.lower():
                return False

            # 페이지에 loginForm이 있으면 로그아웃 상태
            if 'loginForm' in page_content:
                return False

            # 홈 페이지 요소가 있으면 로그인 상태
            if 'dash-layout' in page_content or 'item-dash' in page_content:
                return True

            # 그 외의 경우는 안전하게 False 반환
            return False

        except Exception as e:
            logger.error(f"로그인 상태 확인 중 오류: {e}")
            return False

    def close(self):
        """브라우저 종료"""
        try:
            if self.page:
                self.page.close()
                self.page = None

            if self.context:
                self.context.close()
                self.context = None

            if self.browser:
                self.browser.close()
                self.browser = None

            if self.playwright:
                self.playwright.stop()
                self.playwright = None

            logger.info("브라우저 종료 완료")
        except Exception as e:
            logger.warning(f"브라우저 종료 중 오류 (무시): {e}")

    def __del__(self):
        """소멸자 - 브라우저 자동 종료"""
        self.close()
