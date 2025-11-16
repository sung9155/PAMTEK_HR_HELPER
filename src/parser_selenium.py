"""
Selenium 기반 Pamtek HR 파싱 모듈
"""
from typing import Dict
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


class PamtekParserSelenium:
    """Selenium 기반 Pamtek HR 데이터 파싱 클래스"""

    def __init__(self, auth_selenium):
        self.auth = auth_selenium

    def get_attendance_status(self) -> Dict[str, any]:
        """
        오늘의 출근/퇴근 상태 확인

        Returns:
            dict: 출근 상태 정보
        """
        try:
            # 홈 페이지로 이동
            if not self.auth.navigate_to_home():
                return {
                    'is_checked_in': False,
                    'is_checked_out': False,
                    'check_in_time': None,
                    'check_out_time': None,
                    'status': 'error',
                    'error': '홈 페이지 접근 실패'
                }

            # HTML 가져오기
            html = self.auth.get_page_source()
            if not html:
                return {
                    'is_checked_in': False,
                    'is_checked_out': False,
                    'check_in_time': None,
                    'check_out_time': None,
                    'status': 'error',
                    'error': 'HTML 소스 없음'
                }

            # BeautifulSoup으로 파싱
            soup = BeautifulSoup(html, 'html.parser')

            check_in_time = None
            check_out_time = None

            # active 클래스를 가진 오늘 날짜 찾기
            active_day = soup.find('div', class_='item-day active')

            if active_day:
                # time-wrap 안의 실적 시간 찾기
                time_wrap = active_day.find('div', class_='time-wrap')
                if time_wrap:
                    times = time_wrap.find_all('div', class_='time')

                    for time_div in times:
                        tit = time_div.find('span', class_='tit')
                        txt = time_div.find('span', class_='txt')

                        if tit and txt and '실적' in tit.text:
                            time_text = txt.text.strip()

                            # ~ 기준으로 분리
                            if '~' in time_text:
                                times_split = time_text.split('~')
                                if len(times_split) == 2:
                                    check_in_time = times_split[0].strip()
                                    check_out_time = times_split[1].strip()
                                    break

            # 출근/퇴근 여부 판단
            is_checked_in = False
            is_checked_out = False

            if check_in_time and check_in_time != '00:00' and check_in_time != '-':
                is_checked_in = True

            if check_out_time and check_out_time != '00:00' and check_out_time != '-':
                is_checked_out = True

            # 상태 결정
            if not is_checked_in:
                status = 'not_checked_in'
            elif not is_checked_out:
                status = 'not_checked_out'
            else:
                status = 'completed'

            logger.info(f"출근 상태 파싱 완료 - 출근: {check_in_time}, 퇴근: {check_out_time}")

            return {
                'is_checked_in': is_checked_in,
                'is_checked_out': is_checked_out,
                'check_in_time': check_in_time if is_checked_in else None,
                'check_out_time': check_out_time if is_checked_out else None,
                'status': status,
                'error': None
            }

        except Exception as e:
            logger.error(f"파싱 중 오류: {e}")
            return {
                'is_checked_in': False,
                'is_checked_out': False,
                'check_in_time': None,
                'check_out_time': None,
                'status': 'error',
                'error': str(e)
            }

    def get_today_attendance_summary(self) -> str:
        """오늘의 출근 현황 요약 텍스트"""
        status = self.get_attendance_status()

        if status['error']:
            return f"오류: {status['error']}"

        if status['is_checked_in'] and status['is_checked_out']:
            return f"출근: {status['check_in_time']}, 퇴근: {status['check_out_time']}"
        elif status['is_checked_in']:
            return f"출근: {status['check_in_time']} (퇴근 전)"
        else:
            return "미출근"
