"""
Selenium 기반 Pamtek HR 로그인 모듈
암호화된 로그인을 우회하기 위해 실제 브라우저 사용
"""
import os
import logging
from typing import Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

logger = logging.getLogger(__name__)


class PamtekAuthSelenium:
    """Selenium 기반 Pamtek HR 인증 클래스"""

    def __init__(self, user_id: str, password: str, headless: bool = True):
        self.user_id = user_id
        self.password = password
        self.headless = headless
        self.base_url = "https://hr.pamtek.com"
        self.driver = None

    def _init_driver(self):
        """Chrome 드라이버 초기화"""
        if self.driver:
            return

        options = Options()
        if self.headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        try:
            # 시스템 Chrome 드라이버 사용
            self.driver = webdriver.Chrome(options=options)
            self.driver.maximize_window()
            logger.info("Chrome 드라이버 초기화 성공")
        except Exception as e:
            logger.error(f"Chrome 드라이버 초기화 실패: {e}")
            raise

    def login(self) -> bool:
        """
        Selenium을 사용한 로그인

        Returns:
            bool: 로그인 성공 여부
        """
        try:
            self._init_driver()

            logger.info("로그인 페이지 접속 중...")
            self.driver.get(self.base_url)

            # 페이지 로딩 대기
            time.sleep(2)

            # 사용자 ID 입력
            user_id_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "userID"))
            )

            # JavaScript를 사용하여 값 설정 및 이벤트 트리거
            self.driver.execute_script(
                "arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input')); arguments[0].dispatchEvent(new Event('change'));",
                user_id_field, self.user_id
            )
            logger.info(f"사용자 ID 입력: {self.user_id}")

            # 비밀번호 입력
            password_field = self.driver.find_element(By.ID, "password")

            # JavaScript를 사용하여 값 설정 및 이벤트 트리거
            self.driver.execute_script(
                "arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input')); arguments[0].dispatchEvent(new Event('change'));",
                password_field, self.password
            )
            logger.info("비밀번호 입력 완료")

            # 입력 완료 후 잠시 대기
            time.sleep(1)

            # 로그인 버튼 클릭
            login_button = self.driver.find_element(By.ID, "btnLogin")
            login_button.click()
            logger.info("로그인 버튼 클릭")

            # AJAX 로그인 처리 완료 대기
            # JavaScript가 실행되고 페이지가 변경될 때까지 대기
            time.sleep(3)

            # 디버깅: 로그인 직후 페이지 저장
            with open('after_login_click.html', 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            logger.info("디버깅: after_login_click.html 저장됨")

            # 로그인 후 페이지 변화 확인
            # 브라우저에서는 JavaScript가 비동기로 처리하므로 충분히 대기
            max_attempts = 10
            for i in range(max_attempts):
                current_url = self.driver.current_url
                page_source = self.driver.page_source

                logger.info(f"시도 {i+1}/{max_attempts}: URL={current_url}")

                # 로그인 폼이 사라졌는지 확인
                if 'loginForm' not in page_source:
                    logger.info("로그인 폼 사라짐 - 로그인 성공")
                    time.sleep(2)
                    break

                time.sleep(1)

            # 최종 확인 - 별도 네비게이션 없이 현재 페이지 확인
            final_url = self.driver.current_url
            page_source = self.driver.page_source

            logger.info(f"최종 URL: {final_url}")

            # 로그인 페이지로 돌아갔는지 확인
            if 'loginForm' in page_source or 'login' in final_url.lower():
                logger.error("로그인 실패 - 세션 없음")
                # 디버깅: HTML 저장
                with open('login_failed.html', 'w', encoding='utf-8') as f:
                    f.write(page_source)
                logger.info("디버깅: login_failed.html 저장됨")
                return False

            # 홈 페이지 내용 확인
            if 'dash-layout' in page_source or 'item-dash' in page_source:
                logger.info("✅ 로그인 성공! 홈 페이지 확인됨")
                return True

            # URL로 확인
            if 'home.do' in final_url or '/module/HR/' in final_url:
                logger.info("✅ 로그인 성공! (URL 확인)")
                return True

            logger.warning(f"예상치 못한 상태: {final_url}")
            # 디버깅: HTML 저장
            with open('unexpected_state.html', 'w', encoding='utf-8') as f:
                f.write(page_source)
            logger.info("디버깅: unexpected_state.html 저장됨")
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
        if not self.driver:
            logger.error("드라이버가 초기화되지 않음")
            return None

        return self.driver.page_source

    def navigate_to_home(self, refresh: bool = True) -> bool:
        """
        홈 페이지로 이동 또는 새로고침

        Args:
            refresh: True면 페이지를 새로고침하여 최신 데이터 가져오기 (기본값: True)

        Returns:
            bool: 성공 여부
        """
        try:
            if not self.driver:
                logger.error("드라이버가 초기화되지 않음")
                return False

            # 현재 페이지 확인
            current_url = self.driver.current_url
            page_source = self.driver.page_source

            # 로그인 페이지라면 실패
            if 'login' in current_url.lower() or 'loginForm' in page_source:
                logger.error("로그인 페이지에 있음 - 세션 만료")
                return False

            # 이미 홈 페이지에 있으면
            if 'dash-layout' in page_source or 'item-dash' in page_source:
                if refresh:
                    logger.info(f"홈 페이지 새로고침 중: {current_url}")
                    self.driver.refresh()
                    time.sleep(2)  # 페이지 로딩 대기

                    # 새로고침 후 로그인 페이지로 돌아갔는지 확인
                    if 'loginForm' in self.driver.page_source:
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
        if not self.driver:
            return False

        try:
            current_url = self.driver.current_url
            page_source = self.driver.page_source

            # URL에 login이 있으면 로그아웃 상태
            if 'login' in current_url.lower():
                return False

            # 페이지에 loginForm이 있으면 로그아웃 상태
            if 'loginForm' in page_source:
                return False

            # 홈 페이지 요소가 있으면 로그인 상태
            if 'dash-layout' in page_source or 'item-dash' in page_source:
                return True

            # 그 외의 경우는 안전하게 False 반환
            return False
        except Exception as e:
            logger.error(f"로그인 상태 확인 중 오류: {e}")
            return False

    def close(self):
        """브라우저 종료"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("브라우저 종료 완료")
            except:
                pass
            finally:
                self.driver = None

    def __del__(self):
        """소멸자 - 브라우저 자동 종료"""
        self.close()
