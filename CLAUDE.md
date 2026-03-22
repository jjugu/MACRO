# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

인터파크 NOL 티켓 좌석 자동 선택 매크로. Python + Selenium + CustomTkinter GUI 단일 파일 프로그램.
타겟 사이트: `poticket.interpark.com/Book/BookMain.asp` (예매 팝업 창)

## Running

```bash
python macro.py

# exe 빌드
python -m PyInstaller --onefile --windowed --name "인터파크좌석매크로" macro.py
```

## Dependencies

- Python 3.14+
- `selenium` (4.15+) — Chrome 자동화
- `customtkinter` — 모던 다크 테마 GUI (없으면 tkinter 폴백)
- `pyinstaller` — exe 빌드용

## Architecture

**단일 파일** `macro.py` — `SeatMacroEngine` (엔진) + `App(ctk.CTk)` (GUI)

### 인터파크 페이지 DOM 구조

```
BookMain.asp (메인 페이지)
  └─ ifrmSeat                    ← enter_frame() — 등급/구역 클릭 레벨
       ├─ <span class="select" onclick="fnSwapGrade(N)">  ← 등급 (내부에 <strong>등급명</strong>)
       ├─ <a href="javascript:fnBlockSeatUpdate('','','309')">  ← 구역 링크 (display:none 컨테이너 안)
       ├─ BlockBuffer (JS 변수)  ← {SeatBlock, SeatGradeName, RemainCnt} 구역 데이터
       └─ ifrmSeatDetail          ← enter_seat_detail() — 좌석 탐색 레벨
            ├─ <span class="SeatN">  ← 사용 가능 좌석 (파란색, onclick="SelectSeat(...)")
            ├─ <span class="SeatR">  ← 매진 좌석 (회색)
            ├─ <span class="SeatB">  ← 빈 공간
            └─ <span class="SeatT">  ← 테이블 레이아웃 (무시)
```

### 2단계 iframe 전환이 핵심

- `enter_frame()` → ifrmSeat만 진입 (등급 클릭, 구역 JS 호출용)
- `enter_seat_detail()` → ifrmSeat → ifrmSeatDetail 2단계 진입 (좌석 탐색용)
- 구역 클릭/등급 클릭은 ifrmSeat에서, 좌석 탐색은 ifrmSeatDetail에서

### 매크로 실행 흐름

1. Chrome 연결 (`--remote-debugging-port=9222`)
2. 예매 팝업 창 전환 → ifrmSeat 진입
3. `_scan_grades()`: `<strong>` 태그에서 등급 수집
4. `_scan_sections(grade)`: **`BlockBuffer` JS 변수**에서 해당 등급 구역만 추출 (잔여석 > 0 우선)
5. 메인 루프: 등급 클릭(`fnSwapGrade`) → 구역 진입(`fnBlockSeatUpdate`) → ifrmSeatDetail 진입 → 좌석 탐색 → 클릭 → 완료

### 좌석 탐색 (`find_seats`)

- JS 일괄 탐색: `document.querySelectorAll('span.SeatN')` (개별 Selenium 대비 387배 빠름)
- 인터파크 형식 감지 (`span[class^="Seat"]` 존재 시) → 폴백 스킵으로 속도 확보
- 인터파크가 아닌 경우 onclick/이미지 기반 폴백

### 좌석 클릭 (`click_seats_batch`)

- JS `arguments[i].click()`으로 일괄 클릭 — Selenium 왕복 없이 즉시 (4석 8ms)
- JS 클릭은 캡차 오버레이를 우회함 (DOM 이벤트 직접 발생)

### 구역 관련 핵심 이슈

- 구역 링크는 **`display:none`인 `<td id="GradeDetail">`** 안에 있음
- `is_displayed()` 체크하면 못 찾음 → **`fnBlockSeatUpdate` JS 직접 호출**로 해결
- 구역 목록은 DOM이 아닌 **`BlockBuffer` JS 변수**에서 추출해야 등급별 필터링 가능

### 캡차 처리 (4종류)

ifrmSeatDetail에 좌석 대신 `parent.CaptchaOpen(type, 'seat')` 스크립트가 오면 캡차 활성:

| 타입 | 방식 | 매크로 처리 |
|------|------|-----------|
| `S` | 슬라이더 퍼즐 | JS 이벤트로 **자동 풀이** (역산 공식 + 서버 검증) |
| `H` | hCaptcha 체크박스 | 서버 토큰 검증 필수 → **사용자 수동 풀이 대기** |
| `R` | Google reCAPTCHA | 서버 토큰 검증 필수 → **사용자 수동 풀이 대기** |
| `T` | 문자입력 (레거시) | - |

- 슬라이더(S) 풀이 공식: `drag = (sCaptcha.x - 3) * (width - 40) / (width - 60)`
  - `sCaptcha.x`는 정답 위치, 블록은 스케일링됨 (`block.left = (w-60)/(w-40) * drag`)
  - verify 조건: `Math.abs(block.left + 3 - x) < offset(5px)`
  - JS `dispatchEvent`로 mousedown→mousemove(20단계)→mouseup, iframe 내부 document에 발생
  - 폴백: `rcckYN='Y' + fnRefresh()` (서버 상태에 따라 되기도 함)
- `fnRefresh()` 반복 호출하면 서버가 느려짐 → **1회만 호출**
- 캡차 발생은 간격이 아닌 **서버 세션 상태**에 따라 랜덤
- 좌석 데이터가 이미 로딩되어 있으면 캡차 오버레이 무시하고 진행 가능

### 주요 이슈 히스토리

- Chrome은 `--user-data-dir` 없이 `--remote-debugging-port`만 주면 포트를 열지 않음
- 기존 Chrome 프로세스가 있으면 새 인스턴스의 debug 플래그가 무시됨 → taskkill 필요
- 인터파크 예매 페이지는 팝업 창으로 열림 → `window_handles`로 올바른 창 전환 필수
- bash에서 Windows `taskkill` 플래그는 `/F`가 아닌 `//F`로 이스케이프 필요
- onclick만으로 좌석 판정하면 안 됨 — 매진 좌석도 onclick이 있음 (false positive)
- `a.btn_red` 같은 범용 CSS 셀렉터로 완료 버튼 찾으면 "예매대기하기" 버튼을 잘못 클릭함

## Config

`config.json` 필드:
- `seat_grade`: 등급 키워드 ("지정석"만 써도 "지정석 VIP석", "지정석 R석" 매칭)
- `sections`: 콤마 구분 구역 (비우면 BlockBuffer에서 자동 스캔)
- `num_seats`: 선택할 좌석 수
- `debug_port`: Chrome 디버그 포트 (기본 9222)
- `stealth_mode`: `navigator.webdriver` 탐지 방지
- `refresh_interval`: 구역 간 대기 시간 (초)
