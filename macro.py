#!/usr/bin/env python
"""
인터파크 NOL 티켓 좌석 자동 선택 - GUI 프로그램
CAPTCHA(보안문자) 자동 인식 포함
"""

import time
import json
import sys
import os
import subprocess
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox
try:
    import customtkinter as ctk
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    HAS_CTK = True
except ImportError:
    HAS_CTK = False
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    ElementClickInterceptedException,
    NoAlertPresentException,
    InvalidSessionIdException,
    WebDriverException,
)
try:
    import ddddocr
    HAS_OCR = True
except ImportError:
    HAS_OCR = False


CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

DEFAULT_CONFIG = {
    "debug_port": 9222,
    "seat_grade": "",
    "sections": "201영역,202영역,203영역,204영역,205영역,206영역",
    "num_seats": 1,
    "max_attempts": 300,
    "refresh_interval": 0.3,
    "auto_refresh": True,
    "consecutive_seats": True,
    "stealth_mode": True,           # navigator.webdriver 탐지 방지
    "telegram_token": "",
    "telegram_chat_id": "",
}




# ═══════════════════════════════════════════════════
#  매크로 엔진
# ═══════════════════════════════════════════════════
class SeatMacroEngine:
    def __init__(self, config, log_callback, app=None):
        self.config = config
        self.log = log_callback
        self.app = app
        self.driver = None
        self.running = False
        self.section_index = 0  # 현재 시도할 구역 인덱스
        self._ocr = None

    def stop(self):
        self.running = False

    # ── 포트 열려있는지 확인 ──
    @staticmethod
    def _check_port(port, timeout=2):
        import socket
        try:
            s = socket.create_connection(("127.0.0.1", port), timeout=timeout)
            s.close()
            return True
        except (ConnectionRefusedError, OSError, socket.timeout):
            return False

    # ── Chrome 연결 ──
    def connect(self):
        port = self.config["debug_port"]
        self.log(f"[연결] 포트 {port} 확인 중...")

        if not self._check_port(port):
            self.log(f"[오류] 포트 {port}이 열려있지 않습니다!")
            self.log("[안내] Chrome이 디버그 모드로 실행되지 않았습니다.")
            self.log("[안내] '크롬 디버그 실행' 버튼을 눌러주세요.")
            self.log("[안내] 기존 Chrome이 모두 종료된 상태여야 합니다!")
            return False

        self.log(f"[연결] 포트 {port} 열림 확인! 연결 중...")

        opts = Options()
        opts.debugger_address = f"127.0.0.1:{port}"

        try:
            from selenium.webdriver.chrome.service import Service
            import shutil

            driver_path = None
            found = shutil.which("chromedriver") or shutil.which("chromedriver.exe")
            if found:
                driver_path = found
            else:
                try:
                    from selenium.webdriver.common.selenium_manager import SeleniumManager
                    sm = SeleniumManager()
                    result = sm.binary_paths(["--browser", "chrome"])
                    driver_path = result.get("driver_path")
                except Exception:
                    pass

            if driver_path:
                self.log(f"[연결] chromedriver: {driver_path}")
                service = Service(executable_path=driver_path)
                self.driver = webdriver.Chrome(service=service, options=opts)
            else:
                self.driver = webdriver.Chrome(options=opts)

            self.log("[연결] Chrome 연결 성공!")
            self.log(f"[연결] 현재 페이지: {self.driver.title}")

            # 스텔스 모드 적용
            if self.config.get("stealth_mode", True):
                self._inject_stealth()

            # 예매 팝업 창으로 전환
            self._switch_to_booking_window()
            return True
        except Exception as e:
            import traceback
            self.log(f"[오류] Chrome 연결 실패: {e}")
            self.log(traceback.format_exc())
            return False

    # ── 예매 팝업 창 전환 ──
    def _switch_to_booking_window(self):
        """여러 창 중 예매 페이지(BookMain) 팝업으로 전환"""
        handles = self.driver.window_handles
        self.log(f"[연결] 열린 창 {len(handles)}개 감지")

        if len(handles) <= 1:
            self.log("[연결] 단일 창 - 전환 불필요")
            return

        best = None
        for h in handles:
            try:
                self.driver.switch_to.window(h)
                url = self.driver.current_url or ""
                title = self.driver.title or ""
                self.log(f"  창: {title[:40]} | {url[:60]}")

                # BookMain, Book, 좌석 선택 등 예매 관련 키워드
                if any(kw in url.lower() for kw in ["bookmain", "book/book", "seatselect"]):
                    best = h
                    break
                if any(kw in title for kw in ["좌석 선택", "좌석선택", "예매"]):
                    best = h
                    break
            except Exception:
                continue

        if best:
            self.driver.switch_to.window(best)
            self.log(f"[연결] 예매 창으로 전환 완료: {self.driver.title}")
        else:
            # 못 찾으면 마지막 창(가장 최근 팝업)으로
            self.driver.switch_to.window(handles[-1])
            self.log(f"[연결] 마지막 창으로 전환: {self.driver.title}")

    # ── 스텔스 모드 ──
    def _inject_stealth(self):
        """Selenium webdriver 탐지 방지"""
        try:
            self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                    window.chrome = {runtime: {}};
                """
            })
            self.log("[스텔스] 탐지 방지 적용")
        except Exception as e:
            self.log(f"[스텔스] 적용 실패 (무시): {e}")

    # ── 클릭 ──
    def _smart_click(self, element):
        """Selenium 클릭 (가로막히면 JS 폴백)"""
        try:
            element.click()
        except ElementClickInterceptedException:
            self.driver.execute_script("arguments[0].click();", element)
        return True

    # ── 프레임 전환 ──
    def enter_seat_detail(self):
        """ifrmSeat → ifrmSeatDetail 진입 + 캡차 감지 + 로딩 대기"""
        self.driver.switch_to.default_content()
        try:
            self.driver.switch_to.frame(self.driver.find_element(By.NAME, "ifrmSeat"))
            # ifrmSeatDetail 로딩 대기 + 캡차 처리
            captcha_handled = False
            for _ in range(120):  # 최대 6초 (hCaptcha 수동 풀이 대기 포함)
                try:
                    state = self.driver.execute_script("""
                        try {
                            var doc = document.getElementById('ifrmSeatDetail').contentDocument;
                            var seats = doc.querySelectorAll('span[class^="Seat"]').length;
                            if (seats > 5) return seats;
                            var html = doc.documentElement.innerHTML;
                            if (html.indexOf('Captcha') > -1) {
                                var m = html.match(/CaptchaOpen\\(['\"](.)['\"]/) ;
                                return 'captcha_' + (m ? m[1] : '?');
                            }
                            return 0;
                        } catch(e) { return 0; }
                    """)
                    if isinstance(state, int) and state > 5:
                        break
                    if isinstance(state, str) and state.startswith('captcha_'):
                        cap_type = state.split('_')[1]
                        if cap_type == 'S' and not captcha_handled:
                            # 슬라이더: JS 이벤트로 정확한 드래그 풀이
                            try:
                                solved = self.driver.execute_script("""
                                    if (!sCaptcha || !sCaptcha.x) return false;
                                    var x = sCaptcha.x, w = sCaptcha.options.width;
                                    var drag = (x - 3) * (w - 40) / (w - 60);
                                    var slider = sCaptcha.slider;
                                    var rect = slider.getBoundingClientRect();
                                    var sx = rect.x + rect.width / 2;
                                    var sy = rect.y + rect.height / 2;
                                    slider.dispatchEvent(new MouseEvent('mousedown',
                                        {clientX:sx, clientY:sy, bubbles:true}));
                                    for (var i=1; i<=20; i++) {
                                        document.dispatchEvent(new MouseEvent('mousemove',
                                            {clientX:sx+(drag*i/20), clientY:sy+(Math.random()*3-1.5), bubbles:true}));
                                    }
                                    document.dispatchEvent(new MouseEvent('mouseup',
                                        {clientX:sx+drag, clientY:sy, bubbles:true}));
                                    return true;
                                """)
                                if solved:
                                    self.log("[캡차] 슬라이더 자동 풀이")
                                    time.sleep(1.5)
                                else:
                                    self.driver.execute_script("""
                                        document.getElementById('rcckYN').value='Y';
                                        jQuery('.captchSliderLayer,#divCaptchaWrap').hide();
                                        fnRefresh();
                                    """)
                                    self.log("[캡차] 슬라이더 우회 (폴백)")
                            except Exception:
                                self.driver.execute_script("""
                                    document.getElementById('rcckYN').value='Y';
                                    jQuery('.captchSliderLayer,#divCaptchaWrap').hide();
                                    fnRefresh();
                                """)
                                self.log("[캡차] 슬라이더 우회 (폴백)")
                            captcha_handled = True
                        elif cap_type == 'T' and not captcha_handled:
                            # 문자입력 캡차: ddddocr OCR 자동 풀이
                            captcha_handled = True
                            if not HAS_OCR:
                                self.log("[캡차] 문자를 직접 입력해주세요! (ddddocr 미설치)")
                            else:
                                self._solve_text_captcha()
                        elif cap_type in ('H', 'R') and not captcha_handled:
                            # hCaptcha/reCAPTCHA: 사용자가 풀어야 함
                            self.log("[캡차] 체크박스를 클릭해주세요!")
                            captcha_handled = True
                        time.sleep(0.1)
                        continue
                except Exception:
                    pass
                time.sleep(0.05)
            try:
                self.driver.switch_to.frame(self.driver.find_element(By.NAME, "ifrmSeatDetail"))
            except NoSuchElementException:
                pass
            return True
        except NoSuchElementException:
            pass
        self.driver.switch_to.default_content()
        for name in ["ifrmBookMain", "BookSeat", "SeatFrame", "mainFrame"]:
            try:
                self.driver.switch_to.frame(self.driver.find_element(By.NAME, name))
                return True
            except NoSuchElementException:
                continue
        return True

    def _check_and_solve_text_captcha(self):
        """ifrmSeat 진입 후 문자 캡차가 표시되어 있으면 풀고 진행"""
        try:
            visible = self.driver.execute_script("""
                var wrap = document.getElementById('divCaptchaWrap');
                var img = document.getElementById('imgCaptcha');
                return wrap && wrap.offsetWidth > 0 && img && img.style.display !== 'none';
            """)
            if visible:
                if not HAS_OCR:
                    self.log("[캡차] 문자를 직접 입력해주세요! (ddddocr 미설치)")
                    while self.running:
                        still = self.driver.execute_script(
                            "var w=document.getElementById('divCaptchaWrap');"
                            "return w && w.offsetWidth>0;")
                        if not still:
                            break
                        time.sleep(0.5)
                else:
                    self._solve_text_captcha()
        except Exception:
            pass

    def _ocr_captcha_image(self, img_bytes):
        """캡차 이미지 전처리 + OCR (이진화 반전으로 90% 정확도)"""
        from PIL import Image, ImageOps
        import io as _io
        img = Image.open(_io.BytesIO(img_bytes)).convert('L')  # 그레이스케일
        bw = img.point(lambda x: 255 if x > 140 else 0)       # 이진화
        inv = ImageOps.invert(bw)                               # 반전 (검정 글씨 + 흰 배경)
        buf = _io.BytesIO()
        inv.save(buf, 'PNG')
        return self._ocr.classification(buf.getvalue()).upper().strip()

    def _solve_text_captcha(self, max_retry=5):
        """문자입력 캡차 자동 풀이 (ddddocr OCR)"""
        import base64
        if self._ocr is None:
            self._ocr = ddddocr.DdddOcr(show_ad=False)
        for attempt in range(max_retry):
            try:
                img_src = self.driver.execute_script(
                    'return document.getElementById("imgCaptcha").src')
                if not img_src or ',' not in img_src:
                    self.log("[캡차] 이미지를 가져올 수 없음")
                    return
                img_bytes = base64.b64decode(img_src.split(',')[1])
                answer = self._ocr_captcha_image(img_bytes)
                if len(answer) != 6:
                    self.log(f"[캡차] OCR 결과 길이 불일치({answer}), 새로고침")
                    self.driver.execute_script('fnCapchaRefresh()')
                    time.sleep(0.8)
                    continue
                # 입력 필드 활성화 → 값 입력 → fnCheck() 호출
                self.driver.execute_script('jQuery(".validationTxt").trigger("click")')
                time.sleep(0.3)
                self.driver.execute_script("""
                    jQuery("#txtCaptcha").val(arguments[0]).show().focus();
                    jQuery(".validationTxt").addClass("txtSet").removeClass("alert");
                """, answer)
                time.sleep(0.1)
                self.driver.execute_script('fnCheck()')
                time.sleep(1.5)
                # 캡차 해결 확인
                solved = self.driver.execute_script("""
                    var w = document.getElementById('divCaptchaWrap');
                    var gone = !w || w.offsetWidth === 0;
                    var passed = jQuery('#rcckYN').val() === 'Y';
                    return gone || passed;
                """)
                if solved:
                    self.log(f"[캡차] 문자 자동 풀이 성공 ({answer})")
                    time.sleep(0.5)
                    return
                else:
                    self.log(f"[캡차] 오답({answer}), 재시도 {attempt+1}/{max_retry}")
                    time.sleep(0.5)
            except Exception as e:
                self.log(f"[캡차] OCR 오류: {e}")
                return

    def enter_frame(self):
        """ifrmSeat 진입 (등급/구역 클릭용)"""
        self.driver.switch_to.default_content()
        try:
            self.driver.switch_to.frame(self.driver.find_element(By.NAME, "ifrmSeat"))
            return True
        except NoSuchElementException:
            pass
        for name in ["ifrmBookMain", "BookSeat", "SeatFrame", "mainFrame"]:
            try:
                self.driver.switch_to.frame(self.driver.find_element(By.NAME, name))
                return True
            except NoSuchElementException:
                continue
        return True


    # ── 좌석등급 ──
    def _scan_grades(self):
        """페이지에서 좌석등급 수집 — <strong> 태그 또는 span.select 기반"""
        found = []
        try:
            # 방법 1: <strong> 태그 (인터파크 구조: <span class="select"><strong>지정석 R석</strong> 24석</span>)
            for s in self.driver.find_elements(By.TAG_NAME, "strong"):
                try:
                    txt = (s.text or "").strip()
                    if txt and "석" in txt and len(txt) < 20 and s.is_displayed():
                        if txt not in found:
                            found.append(txt)
                except Exception:
                    continue
            # 방법 2: span.select with fnSwapGrade
            if not found:
                for s in self.driver.find_elements(By.CSS_SELECTOR, "span.select"):
                    try:
                        onclick = s.get_attribute("onclick") or ""
                        if "fnSwapGrade" not in onclick:
                            continue
                        txt = (s.text or "").strip()
                        import re
                        clean = re.sub(r'\s*\d+석.*$', '', txt).strip()
                        if clean and clean not in found:
                            found.append(clean)
                    except Exception:
                        continue
        except Exception:
            pass
        if found:
            self.log(f"[등급] 자동 감지: {', '.join(found)}")
        return found

    def click_grade(self, grade):
        """등급 클릭 — span.select[onclick*='fnSwapGrade'] 내 텍스트 매칭"""
        try:
            for s in self.driver.find_elements(By.CSS_SELECTOR, "span.select"):
                onclick = s.get_attribute("onclick") or ""
                if "fnSwapGrade" not in onclick:
                    continue
                txt = (s.text or "").strip()
                if grade in txt and s.is_displayed():
                    self._smart_click(s)
                    self.log(f"[등급] '{grade}' 클릭")
                    time.sleep(0.5)
                    return True
        except Exception:
            pass
        # 폴백: XPath 텍스트 매칭
        try:
            for e in self.driver.find_elements(By.XPATH, f"//*[contains(text(), '{grade}')]"):
                if e.is_displayed():
                    self._smart_click(e)
                    self.log(f"[등급] '{grade}' 클릭 (폴백)")
                    time.sleep(0.5)
                    return True
        except Exception:
            pass
        self.log(f"[등급] '{grade}' 찾지 못함")
        return False

    # ── 구역 클릭 ──
    def get_sections(self, grade_name=""):
        manual = [s.strip() for s in self.config.get("sections", "").split(",") if s.strip()]
        if manual:
            return manual
        return self._scan_sections(grade_name)

    def _scan_sections(self, grade_name=""):
        """BlockBuffer에서 해당 등급 구역만 추출 (잔여석 > 0 우선)"""
        found = []
        try:
            sections = self.driver.execute_script("""
                var r = [];
                if (typeof BlockBuffer === 'undefined') return r;
                for (var i = 0; i < BlockBuffer.index; i++) {
                    var o = BlockBuffer.pop(i);
                    var cnt = parseInt((o.RemainCnt||'0').replace(',',''));
                    r.push({block: o.SeatBlock, grade: o.SeatGradeName, remain: cnt});
                }
                return r;
            """)
            if sections:
                # 해당 등급만 필터
                grade_sections = [s for s in sections if not grade_name or grade_name in s.get('grade', '')]
                if not grade_sections:
                    grade_sections = sections
                # 잔여석 > 0 우선
                with_seats = [s['block'] + '영역' for s in grade_sections if s.get('remain', 0) > 0]
                if with_seats:
                    found = with_seats
                else:
                    found = [s['block'] + '영역' for s in grade_sections]
        except Exception:
            pass
        if found:
            self.log(f"[구역] {grade_name or '전체'}: {', '.join(found)}")
        return found

    def click_section(self, sec):
        """구역 클릭 — fnBlockSeatUpdate JS 직접 호출 또는 링크 클릭"""
        import re
        # 구역 번호 추출 (예: "309영역" → "309")
        m = re.search(r'(\d+)', sec)
        block_num = m.group(1) if m else ""

        # 1차: JS로 fnBlockSeatUpdate 직접 호출
        if block_num:
            try:
                self.driver.execute_script(f"fnBlockSeatUpdate('', '', '{block_num}');")
                self.log(f"[구역] '{sec}' 진입")
                return True
            except Exception:
                pass

        # 2차: 텍스트 매칭 폴백
        for tag in ("a", "span", "div", "li"):
            try:
                for e in self.driver.find_elements(By.XPATH, f"//{tag}[contains(text(), '{sec}')]"):
                    if e.is_displayed():
                        self._smart_click(e)
                        self.log(f"[구역] '{sec}' 클릭")
                        time.sleep(0.5)
                        return True
            except Exception:
                continue

        self.log(f"[구역] '{sec}' 찾지 못함")
        return False


    # ── 좌석 탐색 ──
    def find_seats(self):
        seats = []

        # JS 일괄 탐색 — span.SeatN + 인터파크 형식 감지
        try:
            result = self.driver.execute_script("""
                var avail = [], hasSeatClass = false;
                var spans = document.querySelectorAll('span[class^="Seat"]');
                for (var i = 0; i < spans.length; i++) {
                    hasSeatClass = true;
                    if (spans[i].className === 'SeatN' && spans[i].offsetWidth > 0)
                        avail.push(spans[i]);
                }
                return {seats: avail, interpark: hasSeatClass};
            """)
            if result and result.get('seats'):
                return result['seats']
            if result and result.get('interpark'):
                return []  # 인터파크 형식이지만 available 없음 → 폴백 스킵
        except Exception:
            pass
        # 폴백: 다른 사이트용 (onclick/이미지 기반)
        for css in ["[onclick*='Seat']", "[onclick*='seat']",
                     "td[onclick]", "img[onclick]"]:
            try:
                for e in self.driver.find_elements(By.CSS_SELECTOR, css):
                    try:
                        sz = e.size
                        if 3 < sz.get("width", 0) < 50 and 3 < sz.get("height", 0) < 50:
                            if e.is_displayed() and self._ok(e, strict=False):
                                seats.append(e)
                    except StaleElementReferenceException:
                        continue
            except Exception:
                pass
            if seats:
                return seats
        return seats

    def _ok(self, elem, strict=True):
        """좌석 사용 가능 판별
        strict=True: 이미지에 good 키워드 필수 (2차/3차용)
        strict=False: bad 키워드만 없으면 허용 (1차 onclick 매칭용)"""
        try:
            if not elem.is_displayed():
                return False

            cls = (elem.get_attribute("class") or "").lower()
            if any(x in cls for x in ["sold", "disabled", "off", "impossible",
                                       "reserved", "empty", "none", "close"]):
                return False

            # 이미지 src 확인
            src = ""
            if elem.tag_name.lower() == "img":
                src = (elem.get_attribute("src") or "").lower()
            else:
                imgs = elem.find_elements(By.TAG_NAME, "img")
                if imgs:
                    src = (imgs[0].get_attribute("src") or "").lower()

            if src:
                bad = ["off", "sold", "gray", "grey", "dis", "impossible",
                       "no_", "close", "none", "empty"]
                if any(x in src for x in bad):
                    return False
                good = ["_on.", "_on_", "/on.", "able", "possible",
                        "green", "blue", "pink", "available", "open",
                        "cyan", "teal", "norm", "avail"]
                if any(x in src for x in good):
                    return True
                if strict:
                    return False  # 엄격: 이미지 키워드 불명 → 거부
                return True  # 관대: bad 없으면 허용 (onclick이 좌석 확인)

            # 이미지 없는 요소 → 배경색으로 판별
            bg = elem.value_of_css_property("background-color")
            if bg and bg.startswith("rgb"):
                nums = [int(x) for x in bg.replace("rgba", "").replace("rgb", "")
                        .strip("() ").split(",")[:3]]
                if max(nums) - min(nums) < 30:
                    return False  # 무채색 → 불가
                return True  # 유채색 = 가능

            if not strict:
                return True  # 관대: bad 없으면 허용
            return False
        except Exception:
            return False

    # ── 연석 탐색 ──
    def _find_consecutive(self, seats, num):
        """사용 가능한 좌석 중 연속 num개 그룹을 찾아 반환"""
        if len(seats) < num:
            return []

        # 좌석별 위치 수집
        infos = []
        for s in seats:
            try:
                loc = s.location
                sz = s.size
                infos.append({"elem": s, "x": loc["x"], "y": loc["y"],
                              "w": sz["width"], "h": sz["height"]})
            except Exception:
                continue
        if len(infos) < num:
            return []

        # Y좌표로 같은 행 그룹핑
        infos.sort(key=lambda s: (s["y"], s["x"]))
        rows = []
        row = [infos[0]]
        for s in infos[1:]:
            if abs(s["y"] - row[0]["y"]) <= 10:
                row.append(s)
            else:
                rows.append(row)
                row = [s]
        rows.append(row)

        # 각 행에서 X좌표 순 정렬 → 연속 좌석 찾기
        for row in rows:
            row.sort(key=lambda s: s["x"])
            if len(row) < num:
                continue
            run = [row[0]]
            for i in range(1, len(row)):
                gap = row[i]["x"] - row[i - 1]["x"]
                avg_w = (row[i - 1]["w"] + row[i]["w"]) / 2
                if gap <= max(avg_w * 1.5, avg_w + 10):
                    run.append(row[i])
                else:
                    run = [row[i]]
                if len(run) >= num:
                    return [s["elem"] for s in run[:num]]

        return []

    # ── 좌석 클릭 ──
    def click_seats_batch(self, seats):
        """JS로 여러 좌석 일괄 클릭 — Selenium 왕복 없이 즉시"""
        try:
            clicked = self.driver.execute_script("""
                var cnt = 0;
                for (var i = 0; i < arguments.length; i++) {
                    try { arguments[i].click(); cnt++; } catch(e) {}
                }
                return cnt;
            """, *seats)
            if clicked:
                self.log(f"[좌석] {clicked}석 일괄 클릭!")
            time.sleep(0.15)
            # 알림 확인
            try:
                alert = self.driver.switch_to.alert
                alert_text = alert.text or ""
                self.log(f"[좌석] 알림: {alert_text}")
                alert.accept()
                return 0
            except (NoAlertPresentException, Exception):
                pass
            return clicked or 0
        except Exception as e:
            self.log(f"[좌석] 클릭 실패: {e}")
            return 0

    def click_seat(self, seat):
        return self.click_seats_batch([seat]) > 0

    # ── 실제 좌석 선택 확인 ──
    def _verify_seat_selected(self):
        """'총 N석 선택' 텍스트를 iframe/메인 프레임 모두에서 확인"""
        import re
        try:
            # 현재 프레임에서 확인
            body = self.driver.page_source[:8000]
            m = re.search(r'총\s*(\d+)\s*석\s*선택', body)
            if m:
                cnt = int(m.group(1))
                if cnt > 0:
                    self.log(f"[확인] 총 {cnt}석 선택 확인됨")
                    return True
                self.log("[확인] 총 0석 — 좌석 선택 안 됨")
                return False
            # 메인 프레임에서 확인
            self.driver.switch_to.default_content()
            body = self.driver.page_source[:8000]
            m = re.search(r'총\s*(\d+)\s*석\s*선택', body)
            if m:
                cnt = int(m.group(1))
                self.enter_frame()  # 프레임 복구
                if cnt > 0:
                    self.log(f"[확인] 총 {cnt}석 선택 확인됨")
                    return True
                self.log("[확인] 총 0석 — 좌석 선택 안 됨")
                return False
            self.enter_frame()  # 프레임 복구
        except Exception:
            try:
                self.enter_frame()
            except Exception:
                pass
        return True  # 확인 불가 시 진행 허용

    # ── 완료 버튼 ──
    def click_complete(self):
        time.sleep(0.3)

        # 실제로 좌석이 선택됐는지 확인
        if not self._verify_seat_selected():
            self.log("[완료] 좌석 미선택 — 완료 버튼 스킵")
            return False

        # "예매대기" 등 잘못 클릭하면 안 되는 키워드
        block = ["예매대기", "대기하기", "이전단계", "다시 선택", "다시선택"]

        for switch_default in [False, True]:
            if switch_default:
                try:
                    self.driver.switch_to.default_content()
                except Exception:
                    pass
            sels = [
                (By.XPATH, "//*[contains(text(), '좌석선택완료')]"),
                (By.XPATH, "//img[contains(@alt, '좌석선택완료')]"),
                (By.XPATH, "//a[contains(@title, '좌석선택완료')]"),
                (By.XPATH, "//button[contains(text(), '좌석선택완료')]"),
                (By.CSS_SELECTOR, ".btnComplete, #btnComplete"),
                (By.CSS_SELECTOR, ".btn_complete, #btn_complete"),
            ]
            for by, sel in sels:
                try:
                    for e in self.driver.find_elements(by, sel):
                        if not e.is_displayed():
                            continue
                        txt = (e.text or "").strip()
                        href = (e.get_attribute("href") or "").lower()
                        if any(kw in txt for kw in block) or "waiting" in href:
                            self.log(f"[완료] '{txt}' 스킵 (예매대기 버튼)")
                            continue
                        self._smart_click(e)
                        self.log("[완료] 좌석선택완료 버튼 클릭!")

                        # 클릭 후 알림 확인 — "좌석을 선택하세요" 등 에러면 실패 처리
                        time.sleep(0.5)
                        try:
                            alert = self.driver.switch_to.alert
                            alert_text = alert.text or ""
                            if any(kw in alert_text for kw in ["선택하세요", "선택해", "좌석을 선택"]):
                                self.log(f"[완료] 실패 알림: {alert_text}")
                                alert.accept()
                                return False
                            alert.accept()
                        except (NoAlertPresentException, Exception):
                            pass
                        return True
                except Exception:
                    continue
        self.log("[완료] 버튼 찾지 못함")
        return False

    # ── 알림 처리 ──
    def dismiss_alert(self):
        try:
            alert = self.driver.switch_to.alert
            self.log(f"[알림] {alert.text}")
            alert.accept()
        except (NoAlertPresentException, InvalidSessionIdException, WebDriverException):
            pass

    # ── 텔레그램 알림 ──
    def send_telegram(self, msg):
        token = self.config.get("telegram_token", "")
        chat_id = self.config.get("telegram_chat_id", "")
        if not token or not chat_id:
            return
        try:
            import urllib.request
            import urllib.parse
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            data = urllib.parse.urlencode({"chat_id": chat_id, "text": msg}).encode()
            urllib.request.urlopen(url, data, timeout=5)
            self.log("[텔레그램] 알림 전송 완료")
        except Exception as e:
            self.log(f"[텔레그램] 전송 실패: {e}")

    # ── 세션 유효 확인 & 재연결 ──
    def ensure_session(self):
        """세션이 끊겼으면 재연결 시도"""
        try:
            _ = self.driver.title
            return True
        except (InvalidSessionIdException, WebDriverException):
            self.log("[연결] 세션 끊김! 재연결 시도...")
            try:
                return self.connect()
            except Exception:
                return False

    # ── 메인 루프 ──
    def run(self):
        self.running = True
        if not self.connect():
            self.running = False
            return

        max_att = self.config.get("max_attempts", 300)
        interval = self.config.get("refresh_interval", 0.3)
        num = self.config.get("num_seats", 1)

        self.log("━" * 40)
        self.log("  매크로 시작!")
        self.log(f"  구역: {self.config.get('sections', '자동')}")
        self.log(f"  좌석수: {num} | 최대시도: {max_att}")
        self.log(f"  스텔스: {'ON' if self.config.get('stealth_mode') else 'OFF'}")
        self.log("━" * 40)

        self.enter_frame()
        self._check_and_solve_text_captcha()

        # 등급 목록 — 키워드 입력 시 페이지 스캔 후 매칭
        grade_input = [s.strip() for s in self.config.get("seat_grade", "").split(",") if s.strip()]
        if grade_input:
            scanned = self._scan_grades()
            if scanned:
                grades = [g for g in scanned if any(kw in g for kw in grade_input)]
                if grades:
                    self.log(f"[등급] '{','.join(grade_input)}' → {len(grades)}개 매칭: {', '.join(grades)}")
                else:
                    grades = grade_input
                    self.log(f"[등급] 스캔 매칭 없음, 입력값 직접 사용: {', '.join(grades)}")
            else:
                grades = grade_input
                self.log(f"[등급] {len(grades)}개: {', '.join(grades)}")
        else:
            self.log("[등급] 미지정 — 현재 등급에서 구역만 순환")
            grades = [""]

        # 등급별 구역 맵 구축
        manual_sections = [s.strip() for s in self.config.get("sections", "").split(",") if s.strip()]
        grade_sections = {}
        for grade in grades:
            if grade:
                self.click_grade(grade)
                time.sleep(0.3)
            if manual_sections:
                grade_sections[grade] = list(manual_sections)
            else:
                grade_sections[grade] = self.get_sections(grade)
            self.log(f"  {grade or '현재'}: {', '.join(grade_sections[grade]) if grade_sections[grade] else '구역 없음'}")

        self.log("━" * 40)

        # 등급-구역 순환 리스트 생성: [(등급, 구역), ...]
        plan = []
        for grade in grades:
            secs = grade_sections.get(grade, [])
            if secs:
                for sec in secs:
                    plan.append((grade, sec))
            else:
                plan.append((grade, ""))

        if not plan:
            self.log("[오류] 탐색할 등급/구역이 없습니다")
            self.running = False
            return

        self.log(f"[계획] 총 {len(plan)}개 등급-구역 조합 순환")
        plan_index = 0
        current_grade = None

        for att in range(1, max_att + 1):
            if not self.running:
                self.log("[중단] 사용자에 의해 중단됨")
                return
            try:
                # 세션 끊겼으면 재연결
                if not self.ensure_session():
                    self.log("[연결] 재연결 실패, 5초 후 재시도...")
                    time.sleep(5)
                    continue

                self.dismiss_alert()
                self.enter_frame()
                self._check_and_solve_text_captcha()

                grade, sec = plan[plan_index]
                label = f"{grade} > {sec}" if grade and sec else (grade or sec or "-")
                self.log(f"── 시도 {att}/{max_att} [{label}] ──")

                # 등급이 바뀔 때만 클릭
                if grade and grade != current_grade:
                    self.click_grade(grade)
                    current_grade = grade

                # 구역 클릭
                if sec:
                    if not self.click_section(sec):
                        # 구역 진입 실패 → 이 페이지에서 좌석 찾으면 가짜임
                        plan_index = (plan_index + 1) % len(plan)
                        time.sleep(interval)
                        continue

                # 좌석 탐색 (ifrmSeatDetail 진입)
                self.enter_seat_detail()
                seats = self.find_seats()
                if seats:
                    self.log(f"[탐색] 사용 가능 좌석 {len(seats)}개 발견!")

                    use_consec = num > 1 and self.config.get("consecutive_seats", True)
                    if use_consec:
                        targets = self._find_consecutive(seats, num)
                        if targets:
                            self.log(f"[연석] {num}연석 발견!")
                        else:
                            self.log(f"[연석] {num}연석 없음 → 다음")
                            plan_index = (plan_index + 1) % len(plan)
                            time.sleep(interval)
                            continue
                    else:
                        targets = seats[:num]

                    selected = self.click_seats_batch(targets)
                    if selected > 0:
                        self.log(f"[선택] {selected}석 선택 완료!")
                        if self.click_complete():
                            self.log("━" * 40)
                            self.log("  ★ 예매 성공! 결제로 이동합니다 ★")
                            self.log("━" * 40)
                            self.send_telegram(
                                f"[인터파크 매크로] 예매 성공!\n"
                                f"등급: {grade or '현재'}\n"
                                f"구역: {sec or '현재'}\n"
                                f"좌석 {selected}석 선택 완료!")
                            self.running = False
                            return
                        else:
                            self.log("[재시도] 완료 버튼 실패...")
                else:
                    self.log(f"[탐색] 좌석 없음 → 다음")

                # 항상 다음 조합으로 이동
                plan_index = (plan_index + 1) % len(plan)
                time.sleep(interval)
            except (InvalidSessionIdException, WebDriverException) as e:
                self.log(f"[연결] 세션 오류: {e.__class__.__name__}")
                time.sleep(3)
            except Exception as e:
                self.log(f"[오류] {e}")
                plan_index = (plan_index + 1) % len(plan)
                time.sleep(interval)

        self.log(f"[종료] 최대 시도 횟수({max_att}) 초과")
        self.running = False


# ═══════════════════════════════════════════════════
#  GUI (CustomTkinter)
# ═══════════════════════════════════════════════════
class App(ctk.CTk if HAS_CTK else tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("인터파크 좌석 매크로")
        self.geometry("520x640")
        self.resizable(True, True)
        self.minsize(460, 520)

        self.engine = None
        self.thread = None
        self.config = self.load_config()

        self._build_ui()

    def load_config(self):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                if isinstance(cfg.get("sections"), list):
                    cfg["sections"] = ",".join(cfg["sections"])
                return cfg
        except Exception:
            return dict(DEFAULT_CONFIG)

    def save_config(self):
        cfg = {
            "debug_port": int(self.var_port.get()),
            "seat_grade": self.var_grade.get(),
            "sections": self.var_sections.get(),
            "num_seats": int(self.var_num.get()),
            "max_attempts": int(self.var_max.get()),
            "refresh_interval": float(self.var_interval.get()),
            "auto_refresh": self.var_autoref.get(),
            "consecutive_seats": self.var_consec.get(),
            "stealth_mode": self.var_stealth.get(),
            "telegram_token": self.var_tg_token.get(),
            "telegram_chat_id": self.var_tg_chatid.get(),
        }
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
        return cfg

    def _build_ui(self):
        # ── 변수 ──
        self.var_port     = tk.StringVar(value=str(self.config.get("debug_port", 9222)))
        self.var_grade    = tk.StringVar(value=self.config.get("seat_grade", ""))
        self.var_sections = tk.StringVar(value=self.config.get("sections", ""))
        self.var_num      = tk.StringVar(value=str(self.config.get("num_seats", 1)))
        self.var_max      = tk.StringVar(value=str(self.config.get("max_attempts", 300)))
        self.var_interval = tk.StringVar(value=str(self.config.get("refresh_interval", 0.3)))
        self.var_autoref  = tk.BooleanVar(value=self.config.get("auto_refresh", True))
        self.var_consec   = tk.BooleanVar(value=self.config.get("consecutive_seats", True))
        self.var_stealth  = tk.BooleanVar(value=self.config.get("stealth_mode", True))
        self.var_tg_token = tk.StringVar(value=self.config.get("telegram_token", ""))
        self.var_tg_chatid= tk.StringVar(value=self.config.get("telegram_chat_id", ""))

        # ══════════════ 상단 헤더 ══════════════
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(16, 8))
        ctk.CTkLabel(header, text="인터파크 좌석 매크로",
                     font=ctk.CTkFont(family="맑은 고딕", size=18, weight="bold")
                     ).pack(side="left")
        ctk.CTkButton(header, text="크롬 실행", width=90, height=30,
                      fg_color="#45475a", hover_color="#585b70",
                      command=self.launch_chrome).pack(side="right")

        # ══════════════ 좌석 설정 ══════════════
        seat_card = ctk.CTkFrame(self, corner_radius=12)
        seat_card.pack(padx=16, pady=(0, 6), fill="x")

        ctk.CTkLabel(seat_card, text="좌석 설정",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color="#89b4fa").pack(anchor="w", padx=14, pady=(10, 6))

        # 등급
        gf = ctk.CTkFrame(seat_card, fg_color="transparent")
        gf.pack(fill="x", padx=14, pady=3)
        ctk.CTkLabel(gf, text="등급", width=50, anchor="w").pack(side="left")
        ctk.CTkEntry(gf, textvariable=self.var_grade, height=30,
                     placeholder_text="비우면 자동 스캔").pack(side="left", fill="x", expand=True, padx=(4, 4))
        ctk.CTkButton(gf, text="스캔", width=55, height=30,
                      fg_color="#45475a", hover_color="#585b70",
                      command=self.scan_grades).pack(side="left")

        # 구역
        sf = ctk.CTkFrame(seat_card, fg_color="transparent")
        sf.pack(fill="x", padx=14, pady=3)
        ctk.CTkLabel(sf, text="구역", width=50, anchor="w").pack(side="left")
        ctk.CTkEntry(sf, textvariable=self.var_sections, height=30,
                     placeholder_text="비우면 자동 스캔").pack(side="left", fill="x", expand=True)

        # 좌석수 + 연석
        nf = ctk.CTkFrame(seat_card, fg_color="transparent")
        nf.pack(fill="x", padx=14, pady=(3, 10))
        ctk.CTkLabel(nf, text="좌석 수", width=50, anchor="w").pack(side="left")
        ctk.CTkEntry(nf, textvariable=self.var_num, width=55, height=30).pack(side="left", padx=(4, 0))
        ctk.CTkCheckBox(nf, text="연석만 선택", variable=self.var_consec,
                        checkbox_width=18, checkbox_height=18).pack(side="left", padx=(16, 0))

        # ══════════════ 시작 / 중단 ══════════════
        bf = ctk.CTkFrame(self, fg_color="transparent")
        bf.pack(padx=16, pady=6, fill="x")
        self.btn_start = ctk.CTkButton(
            bf, text="매크로 시작", height=44,
            font=ctk.CTkFont(family="맑은 고딕", size=15, weight="bold"),
            fg_color="#1f6feb", hover_color="#1a5bc4",
            command=self.start)
        self.btn_start.pack(side="left", expand=True, fill="x", padx=(0, 4))
        self.btn_stop = ctk.CTkButton(
            bf, text="중단", height=44, width=80,
            font=ctk.CTkFont(family="맑은 고딕", size=13, weight="bold"),
            fg_color="#45475a", hover_color="#f38ba8", text_color="#cdd6f4",
            state="disabled", command=self.stop)
        self.btn_stop.pack(side="left")

        # ══════════════ 로그 ══════════════
        self.log_area = ctk.CTkTextbox(
            self, height=200, corner_radius=10,
            font=ctk.CTkFont(family="Consolas", size=12),
            fg_color="#11111b", text_color="#a6e3a1",
            state="disabled", wrap="word",
        )
        self.log_area.pack(padx=16, pady=(2, 6), fill="both", expand=True)

        # ══════════════ 고급 설정 토글 ══════════════
        self._adv_visible = False
        self._adv_toggle_btn = ctk.CTkButton(
            self, text="+ 고급 설정", height=26, anchor="w",
            font=ctk.CTkFont(size=11), fg_color="transparent",
            hover_color="#313244", text_color="#6c7086",
            command=self._toggle_advanced)
        self._adv_toggle_btn.pack(anchor="w", padx=16)

        self._adv_frame = ctk.CTkFrame(self, corner_radius=10)
        self._build_advanced(self._adv_frame)
        # 처음엔 숨김

        # ══════════════ 상태바 ══════════════
        self.status_var = tk.StringVar(value="대기 중")
        self._status_label = ctk.CTkLabel(
            self, textvariable=self.status_var, height=24,
            font=ctk.CTkFont(size=11), text_color="#6c7086", anchor="w")
        self._status_label.pack(fill="x", padx=20, pady=(2, 8))

    def _build_advanced(self, parent):
        """고급 설정 내부 구성"""
        ctk.CTkLabel(parent, text="고급 설정",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color="#89b4fa").pack(anchor="w", padx=12, pady=(8, 4))

        r1 = ctk.CTkFrame(parent, fg_color="transparent")
        r1.pack(fill="x", padx=12, pady=2)
        for lbl, var, w in [("포트", self.var_port, 60), ("최대시도", self.var_max, 90),
                             ("간격(초)", self.var_interval, 55)]:
            ctk.CTkLabel(r1, text=lbl, font=ctk.CTkFont(size=11)).pack(side="left", padx=(0, 2))
            ctk.CTkEntry(r1, textvariable=var, width=w, height=28).pack(side="left", padx=(0, 10))

        r2 = ctk.CTkFrame(parent, fg_color="transparent")
        r2.pack(fill="x", padx=12, pady=2)
        ctk.CTkCheckBox(r2, text="자동 새로고침", variable=self.var_autoref,
                        checkbox_width=16, checkbox_height=16).pack(side="left", padx=(0, 14))
        ctk.CTkCheckBox(r2, text="스텔스 모드", variable=self.var_stealth,
                        checkbox_width=16, checkbox_height=16).pack(side="left")

        r3 = ctk.CTkFrame(parent, fg_color="transparent")
        r3.pack(fill="x", padx=12, pady=(4, 8))
        ctk.CTkLabel(r3, text="텔레그램", font=ctk.CTkFont(size=11)).pack(side="left", padx=(0, 4))
        ctk.CTkEntry(r3, textvariable=self.var_tg_token, width=170, height=28,
                     placeholder_text="Bot Token").pack(side="left", padx=(0, 3))
        ctk.CTkEntry(r3, textvariable=self.var_tg_chatid, width=100, height=28,
                     placeholder_text="Chat ID").pack(side="left", padx=(0, 3))
        ctk.CTkButton(r3, text="테스트", width=55, height=28,
                      fg_color="#45475a", hover_color="#585b70",
                      command=self.test_telegram).pack(side="left")

    def _toggle_advanced(self):
        if self._adv_visible:
            self._adv_frame.pack_forget()
            self._adv_toggle_btn.configure(text="+ 고급 설정")
            self._adv_visible = False
        else:
            self._adv_frame.pack(after=self._adv_toggle_btn, padx=16, pady=(0, 4), fill="x")
            self._adv_toggle_btn.configure(text="- 고급 설정")
            self._adv_visible = True

    def append_log(self, msg):
        ts = time.strftime("%H:%M:%S")
        def _write():
            self.log_area.configure(state="normal")
            self.log_area.insert("end", f"[{ts}] {msg}\n")
            self.log_area.see("end")
            self.log_area.configure(state="disabled")
        try:
            self.after(0, _write)
        except Exception:
            pass

    def test_telegram(self):
        token = self.var_tg_token.get().strip()
        chat_id = self.var_tg_chatid.get().strip()
        if not token or not chat_id:
            messagebox.showwarning("텔레그램", "토큰과 Chat ID를 입력하세요.")
            return
        try:
            import urllib.request
            import urllib.parse
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            data = urllib.parse.urlencode(
                {"chat_id": chat_id, "text": "[인터파크 매크로] 텔레그램 알림 테스트 성공!"}).encode()
            urllib.request.urlopen(url, data, timeout=5)
            self.append_log("[텔레그램] 테스트 메시지 전송 성공!")
            messagebox.showinfo("텔레그램", "테스트 메시지 전송 성공!")
        except Exception as e:
            self.append_log(f"[텔레그램] 테스트 실패: {e}")
            messagebox.showerror("텔레그램", f"전송 실패:\n{e}")

    def scan_grades(self):
        """크롬 페이지에서 등급 스캔 → 필드에 채우기"""
        port = self.var_port.get()
        if not SeatMacroEngine._check_port(int(port)):
            messagebox.showwarning("등급 스캔", "Chrome이 연결되어 있지 않습니다.\n먼저 크롬 디버그 실행 후 예매 페이지를 열어주세요.")
            return
        try:
            opts = Options()
            opts.debugger_address = f"127.0.0.1:{port}"
            driver = webdriver.Chrome(options=opts)

            # 예매 팝업 창 전환
            for h in driver.window_handles:
                try:
                    driver.switch_to.window(h)
                    url = (driver.current_url or "").lower()
                    if any(kw in url for kw in ["bookmain", "book/book", "seatselect"]):
                        break
                except Exception:
                    continue

            # ifrmSeat 진입
            driver.switch_to.default_content()
            try:
                driver.switch_to.frame(driver.find_element(By.NAME, "ifrmSeat"))
            except NoSuchElementException:
                for name in ["ifrmBookMain", "BookSeat", "SeatFrame", "mainFrame"]:
                    try:
                        driver.switch_to.frame(driver.find_element(By.NAME, name))
                        break
                    except NoSuchElementException:
                        continue

            # 등급 스캔 — <strong> 태그 기반
            found = []
            for s in driver.find_elements(By.TAG_NAME, "strong"):
                try:
                    txt = (s.text or "").strip()
                    if txt and "석" in txt and len(txt) < 20 and s.is_displayed():
                        if txt not in found:
                            found.append(txt)
                except Exception:
                    continue
            # 폴백: span.select with fnSwapGrade
            if not found:
                import re
                for s in driver.find_elements(By.CSS_SELECTOR, "span.select"):
                    try:
                        onclick = s.get_attribute("onclick") or ""
                        if "fnSwapGrade" not in onclick:
                            continue
                        txt = (s.text or "").strip()
                        clean = re.sub(r'\s*\d+석.*$', '', txt).strip()
                        if clean and clean not in found:
                            found.append(clean)
                    except Exception:
                        continue

            if found:
                self.append_log(f"[스캔] 등급 {len(found)}개 감지: {', '.join(found)}")
                self._show_grade_selector(found)
            else:
                self.append_log("[스캔] 등급을 찾지 못했습니다")
                messagebox.showwarning("등급 스캔", "등급을 찾지 못했습니다.\n예매 좌석선택 페이지가 열려있는지 확인하세요.")
        except Exception as e:
            self.append_log(f"[스캔] 오류: {e}")
            messagebox.showerror("등급 스캔", f"스캔 실패:\n{e}")

    def _show_grade_selector(self, grades):
        """체크박스로 등급 선택하는 팝업"""
        dlg = ctk.CTkToplevel(self) if HAS_CTK else tk.Toplevel(self)
        dlg.title("등급 선택")
        dlg.resizable(False, False)
        dlg.transient(self)
        dlg.grab_set()
        dlg.geometry("280x" + str(100 + len(grades) * 36))

        ctk.CTkLabel(dlg, text="사용할 등급을 선택하세요",
                     font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(16, 10))

        frame = ctk.CTkFrame(dlg, corner_radius=10)
        frame.pack(padx=16, fill="x")

        check_vars = {}
        for g in grades:
            var = tk.BooleanVar(value=True)
            check_vars[g] = var
            ctk.CTkCheckBox(frame, text=g, variable=var,
                            checkbox_width=20, checkbox_height=20
                            ).pack(anchor="w", padx=14, pady=4)

        bf = ctk.CTkFrame(dlg, fg_color="transparent")
        bf.pack(pady=12, padx=16, fill="x")

        def on_ok():
            selected = [g for g, v in check_vars.items() if v.get()]
            self.var_grade.set(",".join(selected))
            self.append_log(f"[등급] 선택: {', '.join(selected)}")
            dlg.destroy()

        ctk.CTkButton(bf, text="전체선택", width=70, height=30,
                      fg_color="#45475a", hover_color="#585b70",
                      command=lambda: [v.set(True) for v in check_vars.values()]
                      ).pack(side="left", padx=(0, 4))
        ctk.CTkButton(bf, text="전체해제", width=70, height=30,
                      fg_color="#45475a", hover_color="#585b70",
                      command=lambda: [v.set(False) for v in check_vars.values()]
                      ).pack(side="left")
        ctk.CTkButton(bf, text="확인", width=80, height=30,
                      command=on_ok).pack(side="right")

        dlg.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 280) // 2
        y = self.winfo_y() + (self.winfo_height() - dlg.winfo_height()) // 2
        dlg.geometry(f"+{x}+{y}")

    def launch_chrome(self):
        port = self.var_port.get()
        chrome_paths = [
            os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
        ]
        chrome_exe = None
        for p in chrome_paths:
            if os.path.isfile(p):
                chrome_exe = p
                break
        if not chrome_exe:
            messagebox.showerror("오류",
                "Chrome을 찾을 수 없습니다.\n터미널에서 직접 실행:\nchrome.exe --remote-debugging-port=" + port)
            return

        # 기존 Chrome 프로세스 종료 확인
        answer = messagebox.askyesno(
            "Chrome 종료 필요",
            "디버그 모드로 실행하려면 기존 Chrome을 모두 닫아야 합니다.\n\n"
            "현재 실행 중인 Chrome을 자동으로 종료할까요?\n"
            "(저장하지 않은 작업이 있다면 '아니오'를 누르고 직접 닫아주세요)")

        if answer:
            self.append_log("[크롬] 기존 Chrome 프로세스 종료 중...")
            subprocess.run(["taskkill", "//F", "//IM", "chrome.exe"],
                           capture_output=True)
            time.sleep(2)

        # 디버그 모드 전용 프로필 경로
        debug_profile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "chrome_debug_profile")

        try:
            subprocess.Popen([
                chrome_exe,
                f"--remote-debugging-port={port}",
                f"--user-data-dir={debug_profile}",
            ])
            self.append_log(f"[크롬] 디버그 모드 실행 (포트 {port})")
            self.append_log("[크롬] 인터파크 로그인 후 좌석 선택 페이지로 이동하세요.")
            self.status_var.set("Chrome 실행됨 - 인터파크 페이지로 이동하세요")
        except Exception as e:
            messagebox.showerror("오류", f"Chrome 실행 실패: {e}")

    def start(self):
        try:
            cfg = self.save_config()
        except Exception as e:
            messagebox.showerror("설정 오류", str(e))
            return

        self.log_area.configure(state="normal")
        self.log_area.delete("0.0", "end")
        self.log_area.configure(state="disabled")

        self.btn_start.configure(state="disabled")
        self.btn_stop.configure(state="normal")
        self.status_var.set("실행 중...")
        self.append_log("매크로 시작 준비 중...")

        try:
            self.engine = SeatMacroEngine(cfg, self.append_log, app=self)
        except Exception as e:
            self.append_log(f"[오류] 엔진 생성 실패: {e}")
            self._on_finished()
            return

        self.thread = threading.Thread(target=self._run_engine, daemon=True)
        self.thread.start()

    def _run_engine(self):
        try:
            self.append_log("Chrome 연결 시도 중...")
            self.engine.run()
        except Exception as e:
            import traceback
            self.append_log(f"[치명적 오류] {e}")
            self.append_log(traceback.format_exc())
        finally:
            self.after(0, self._on_finished)

    def _on_finished(self):
        self.btn_start.configure(state="normal")
        self.btn_stop.configure(state="disabled")
        self.status_var.set("완료")

    def stop(self):
        if self.engine:
            self.engine.stop()
        self.btn_stop.configure(state="disabled")
        self.status_var.set("중단 중...")


# ═══════════════════════════════════════════════════
if __name__ == "__main__":
    app = App()
    app.mainloop()
