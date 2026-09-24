# ECG 그래픽 (Python)

`ECG 판독 연습실` HTML 페이지의 그래픽(canvas/SVG)을 matplotlib로 옮긴 모듈입니다.
파형 합성 수식, 리듬 생성기, 전도계·벡터 모델의 수치는 원본 JavaScript와 동일합니다.

| 원본 탭 | Python 함수 | CLI |
|---|---|---|
| 리듬 도감 / 퀴즈 strip (캘리퍼 포함) | `plot_strip`, `plot_gallery`, `draw_strip` | `strip`, `gallery` |
| 원리 (전도계 + 벡터 루프 + lead 파형) | `plot_mechanism`, `animate_mechanism` | `mech` |
| 계산기: 전기축 | `plot_axis`, `qrs_axis` | `axis` |
| 계산기: 심박수, QTc | `heart_rate`, `qtc` | `rate`, `qtc` |

```bash
pip install -r requirements.txt

python ecg_graphics.py strip af --seed 1 --calipers 1.0 1.8 -o af.png   # 실제 용지 1:1 크기
python ecg_graphics.py gallery -o gallery.png                            # 18개 리듬 전체
python ecg_graphics.py mech lbbb --t 0.29 -o lbbb.png                    # 특정 시점 (초)
python ecg_graphics.py mech normal --gif normal.gif --speed 0.2          # 한 심주기 애니메이션
python ecg_graphics.py axis -4 6 -o axis.png
python ecg_graphics.py qtc 400 75 --sex f
python ecg_graphics.py rate 20 --mode small
```

모든 그림 명령은 `--theme dark`를 지원합니다.
리듬 id: `nsr brady tachy af flutter svt junc avb1 mob1 mob2 chb wpw pvc vt vf stemi hyperk lqt`
원리 시나리오: `normal avb1 rbbb lbbb lafb wpw pvc stemi`

원본과 다른 점
- 인터랙션(탭 캘리퍼, 스크럽 바, 버튼)은 함수 인자(`calipers`, `t`, `leads`)로 대신합니다.
- 판독 기준·임상 포인트·단계별 설명 같은 긴 본문은 옮기지 않았고, 그래픽에 필요한 이름과 구간 정보만 남겼습니다.
- 그림 크기, 선 두께, 글자 크기는 원본 페이지의 px 치수를 그대로 따릅니다 (본문 폭 744px, strip 1 mm = 5 px). PNG는 기본 `--dpi 192`(화면 2배)로 저장합니다.
- 원본 폰트 IBM Plex Sans KR(SIL OFL)이 없으면 처음 실행할 때 `~/.cache/ecg_graphics/fonts`에 받아 씁니다. 받을 수 없으면(또는 `ECG_NO_FONT_DOWNLOAD=1`) 설치된 한글 폰트를 씁니다.

교육용 합성 파형이며 실제 환자 판독을 대신하지 않습니다.
