# UAM Olympiad — Flight Tracker : All of the Procedures in One

인천공항(RKSI)·김포공항(RKSS)의 **공시 비행절차 전체**와 **UAM 회랑 설계안**을 위성지도 한 장에 겹쳐 본 도구입니다.
2026 전국 대학생 UAM 올림피아드(공항활용 부문) 산출물.

**웹에서 바로 보기 → https://sksanwjrgh.github.io/UAM-Olympiad-Flight-Tracker-All-of-the-Procedures-in-one/**

---

## 무엇을 볼 수 있나

| 레이어 | 내용 |
|---|---|
| **RKSI 절차** | SID 26 · STAR 18 · IAP 48 = **92개** |
| **RKSS 절차** | SID 19 · STAR 14 · IAP 19 = **52개** |
| **UAM 회랑** | 중심선 7개 지점 + 회랑 폭(반폭 1.248 NM) 밴드 |
| **Class B 공역** | RKSI·RKSS 반경 5 / 10 / 20 NM 링 (AIP ENR 2.1) |
| **버티포트** | 홍대염전(VP1) |
| **실시간 항적** | OpenSky Network ADS-B (※ 로컬 실행 시에만) |

절차 좌표는 국토교통부 **AIP 원문 코딩표**와 대조 검증했습니다.
검증 과정에서 실제 오류 2건(ATKON 위도 오타, STAR 3C→2C 구버전)을 발견해 수정했습니다.

## 현재 회랑안

```
WP6    37.63490, 126.49109   Buk-Incheon IC Report Point
WP5    37.53942, 126.49658   Report Point
WP4    37.47786, 126.50105   New airport IC Report Point
HDY    37.46700, 126.50269   홍대염전 버티포트 (VP1)
WP3    37.45060, 126.51993   Incheon Bridge
WP1    37.40750, 126.61709   Wolmi-do Report Point
SIHWA  37.40466, 126.65125   시화호 경유(개략)
```

- 총 연장 **33.94 km** (도심항공교통 특별법 상한 50 km의 68%)
- 회랑 반폭 **1.248 NM** (총폭 4,624 m — 법정 최소폭 600 m의 7.7배)
- 운용고도 **SOUTHBOUND 2,150 ft / NORTHBOUND 2,450 ft** (300 ft 층분리)

설계 근거와 변경 이력은 별도 **설계결정 로그**에 REV 01~19로 기록돼 있습니다.

## 설계결정 로그

회랑을 왜 이렇게 그렸는지 — 좌표·고도·폭을 정한 계산과 AIP 원문 근거, 그리고 **무엇이 틀려서 어떻게 고쳤는지**를 REV 01~19로 기록했습니다.

**→ https://sksanwjrgh.github.io/UAM-Olympiad-Flight-Tracker-All-of-the-Procedures-in-one/decision-log.html**

위성지도 위에 회랑을 그린 제원 도면, 결정 27건 요약표, 미결 사항 9건이 함께 들어 있습니다.

---

## 두 가지 실행 방법

### ① 웹 (GitHub Pages) — 설치 없이 바로

위 링크로 접속하면 됩니다. 절차·회랑·공역·위성지도가 전부 동작합니다.

> **실시간 항적은 웹에서 동작하지 않습니다.** OpenSky API는 인증 토큰이 필요한데,
> 정적 호스팅에는 백엔드가 없고 clientSecret을 페이지에 넣을 수 없기 때문입니다.
> 실시간 기능이 필요하면 아래 ②로 실행하세요.

### ② 로컬 (실시간 항적 포함)

1. 이 저장소를 내려받습니다.
2. **Windows** — `OpenSky_start.bat` 더블클릭
   **macOS / Linux** — 터미널에서 `./OpenSky_start.sh`
3. 자동으로 열린 지도에서 **OpenSky 계정 인증**을 펼칩니다.
4. **인증 JSON 불러오기**로 본인의 credentials 파일을 선택합니다.
5. **인증 성공** 확인 후 **실시간 OFF** 버튼을 눌러 켭니다.

`OpenSky_local_proxy.py`가 `127.0.0.1`에만 열리는 최소 프록시를 띄워
`/auth/token`과 `/api/states/all`만 중계합니다.
clientSecret은 HTML·프록시 코드·로그 어디에도 저장되지 않습니다.

> Python 3 필요 · 실행 창은 지도를 쓰는 동안 닫지 마세요 · 종료는 `Ctrl+C`

---

## 저장소에 없는 파일

**`replay_data.js` (148 MB)** — 과거 항적 리플레이용 데이터입니다.
GitHub 파일 크기 한도(100 MB)를 넘어 포함하지 못했습니다.
없어도 나머지 기능은 정상 동작하며, 리플레이 탭에서 안내 문구만 표시됩니다.

---

## 데이터 출처

- 비행절차 · 공역 — 국토교통부 항공정보간행물(AIP), AIRAC AMDT 대조 검증
- 위성영상 — ESRI World Imagery
- 실시간 항적 — [OpenSky Network](https://opensky-network.org/)
- 지도 엔진 — [Leaflet](https://leafletjs.com/)

## 팀

이준호 · 이대호 · 임수현 · 김연휘 · 양승민
