"""Mixed-style note for 'Clinical Therapeutics: 중환자와 항균제' (임상약리, 2026-08-19 2교시, 한성필 교수님).

Inputs of this run (nothing else is used):
  * script   inputs/abx_script.txt  (52 paragraphs; live lecture + recorded video of 조성연·한성필 교수님)
  * pictures inputs/abx_figs/       (5 slide images taken from the 정리본 PDF - pictures only, its text was not read)
  * PAD      inputs/abx_pad.pdf     (6 questions: 20/19/18학번 x 2) - used ONLY to decide what is blue.

Template templates/mom_mixed.yaml. Approved rules L1-L15: mixed explain/list sections, define -> "그럼",
mechanism chain + "따라서", principle -> cases, "**라벨**: 내용", concepts drawn (slide first, else schematic).
Run:  python -m examples.abx_note > outputs/abx/note_authored.json
"""
from app.models import Arrow, Diagram, Group, Statement
from examples.authoring import SlideTable, T, dump
from examples.stemcell_note import CHK, COLS, CONCEPT, MEMO, _st

FIG = "inputs/abx_figs/"
CH1 = "항균제 선택의 큰 틀"
CH2 = "경험적 치료에서 표적 치료로"
CH3 = "환자 인자와 용량"
CH4 = "기관, 환자, 투여 경로"
CH5 = "PK/PD로 용법 정하기"
CH6 = "병용요법"

# PAD units (parse order of inputs/abx_pad.pdf)
P20_1, P20_2, P19_1, P19_2, P18_1, P18_2 = 1001, 1002, 1003, 1004, 1005, 1006
PAD_PKPD = [P20_1, P19_2, P18_2]  # time/concentration-dependent killing, PAE
PAD_QUAD = [P20_2, P19_1, P18_1]  # nosocomial / community acquired x competent / compromised


def P(text, g=(), effort=""):
    return _st("para", text, g, effort=effort)


def B(text, g=(), effort=""):
    return _st("bullet", text, g, effort=effort)


def FS(img, caption, title, lines, g=()):
    return _st("figure_side", caption, g, image=FIG + img, left_title=title, left=["- " + x for x in lines])


def DIA(kind, groups, root="", arrows=(), size="side", row_labels=()):
    return Diagram(kind=kind, size=size, root=root, row_labels=list(row_labels),
                   groups=[Group(title=t, items=list(it), color=c) for t, c, it in groups],
                   arrows=[Arrow(src=a, dst=b, label=l) for a, b, l in arrows])


def DFS(diagram, caption, title, lines, g=()):
    return Statement(text=caption, kind="figure_side", slide_refs=list(g), diagram=diagram, left_title=title,
                     left=["- " + x for x in lines])


def DFLOW(caption, groups, arrows, g=()):
    return Statement(text=caption, kind="diagram", slide_refs=list(g), diagram=DIA("flow", groups, arrows=arrows, size="full"))


def CONCEPT_V(title, lines, g, diagram=None, image="", caption=""):
    st = CONCEPT(title, lines, g)
    st.text, st.diagram = caption or title, diagram
    if image:
        st.image = FIG + image
    return st


def EX(heading, chapter, answer, body, refs=()):
    return T(heading, chapter, [], body, basics_title="핵심 답", basics=[answer], style="explain") if not refs else \
        _with_refs(T(heading, chapter, [], body, basics_title="핵심 답", basics=[answer], style="explain"), refs)


def _with_refs(t, refs):
    t.basics_refs = list(refs)
    return t


def LS(heading, chapter, body):
    return T(heading, chapter, [], body, style="list")


def build():
    top = []

    # ================================================================ 시험 정리 (front)
    table = SlideTable(
        caption="주제별 핵심 요약 — 파랑 = 기출(PAD)에 나온 내용",
        col_widths_cm=[3.4, 14.0],
        rows=[
            ["주제", "핵심"],
            ["선택의 3요소", "① 사용 **목적** ② 감염된 **장기**(흔한 균, 약물 도달) ③ 어떤 **환자**인가(맥락)"],
            ["사용 목적 4가지", "예방적(prophylactic) → 선제적(pre-emptive) → **경험적**(empiric, 가장 흔함) → 표적(targeted/definitive)"],
            ["4사분면", "{b|원인균: community acquired vs nosocomial(병원 감염), 면역: competent vs compromised}. "
                        "{b|개두술 7일 뒤 뇌수막염인 18세 = nosocomial / competent}, {b|건강하던 18세가 응급실로 오면 community acquired / competent}"],
            ["치료 순서", "환자 평가 → 경험적 치료 + 검체로 감수성 검사(MIC) → 표적 치료 → 모니터링 → 완료"],
            ["정균 vs 살균", "정균: 증식 억제, 숙주 면역에 기댐. 살균: 세균 사멸 → **면역저하, 중증 감염**. 농도와 균주에 따라 상대적"],
            ["환자 인자", "기저 질환과 면역, 신기능과 간기능(GFR 기준), 저관류, 연령(신생아, 노인)"],
            ["투여 경로", "**경구가 원칙**, IV → PO 빨리 전환. 주사: 경구로 농도를 못 얻을 때, 중증과 패혈증, 높은 농도가 필요할 때. 경구 vancomycin = luminal agent"],
            ["PK/PD", "{b|time-dependent: MIC 이상 유지 시간이 길수록 유리(β-lactam)}. "
                      "{b|concentration-dependent: 잠깐이라도 고농도 노출이 유리, aminoglycoside, 투약 간격을 늘리고 1회량을 높인다}. "
                      "{b|PAE = MIC 이하로 떨어진 뒤에도 항균 효과가 지속}"],
            ["PK/PD 지표", "T>MIC(%), Cmax/MIC(aminoglycoside), AUC/MIC(vancomycin, azithromycin, quinolone)"],
            ["병용요법", "**단일 제제가 원칙**. 근거가 뚜렷할 때만(내성 억제, 항결핵제 등). 상호작용으로 효과가 오히려 줄 수 있다"],
        ])
    top.append(T("요약 정리 · 시험 정리", "", [], [
        _st("para", "이 한 쪽이 시험 대비용이다. 파랑은 기출(PAD)에 나온 내용이고 본문에서 근거와 함께 다시 나온다.", [2]),
        _st("diagram", "강의 전체 흐름 — 본문 6개 장", [10, 18, 24, 32, 40, 47], diagram=Diagram(
            kind="flow", arrows=[Arrow(src=i, dst=i + 1, label="") for i in range(5)], groups=[
                Group(title="① 선택의 틀", color="teal", items=["목적, 장기, 환자", "4사분면"]),
                Group(title="② 경험 → 표적", color="blue", items=["감수성 검사", "정균, 살균"]),
                Group(title="③ 환자 인자", color="salmon", items=["면역, 신간기능", "저관류, 연령"]),
                Group(title="④ 경로", color="amber", items=["기관별 도달", "경구 원칙"]),
                Group(title="⑤ PK/PD", color="violet", items=["시간 vs 농도", "PAE, 지표"]),
                Group(title="⑥ 병용", color="teal", items=["단일 원칙", "근거 있을 때만"]),
            ])),
    ], tables=[table], role="front"))

    # ================================================================ 1. 항균제 선택의 큰 틀
    top.append(EX("항균제를 고를 때 무엇을 먼저 따지는가?", CH1,
                  "사용 목적, 감염된 장기, 그리고 어떤 환자인지(만나는 맥락) 세 가지를 먼저 본다.", [
        MEMO("수업은 녹화 강의(감염내과 조성연 교수님, 한성필 교수님의 문답)를 틀고 중간중간 교수님이 덧붙이는 방식이었습니다. "
             "영상 재생 준비, 휴식과 출석 안내는 생략했습니다.", [1, 4, 5, 6, 9, 16, 17, 28, 51, 52]),
        P("{g|감염내과와 임상약리과는 항균제의 PK/PD 분야에서 함께 연구를 많이 해 왔다.}", [1]),
        P("학습목표는 세 가지다. 목적에 따른 치료 전략, 용량과 용법의 결정 인자, 환자 개인차에 따른 처방의의 고려점이다. "
          "{g|미충족 의료 수요도 목표에 있었다. 항균제는 지금도 꾸준히 승인되는 약물군이다. 균도 살아남으려고 계속 스스로를 강화하기 때문이다.}", [2, 3]),
        P("항균제는 종류가 너무 많아 외워도 금방 잊는다. {g|본과 4학년 설문에서 나온 첫 질문이 ‘감염 질환에 따라 항균제를 고르는 원칙’이었다.} "
          "항균제를 스펙트럼(ceftriaxone이 Gram-positive와 negative를 커버하는가)으로만 외우면 선택 원칙이 보이지 않는다.", [7, 8]),
        DFS(DIA("tree", [("① 목적", "teal", ["왜 쓰는가", "예방, 선제, 경험, 표적"]),
                         ("② 장기", "blue", ["어디에 감염인가", "흔한 균, 약물 도달"]),
                         ("③ 환자", "salmon", ["누구인가", "맥락, 면역"])], root="항균제 선택"),
            "항균제 선택의 세 가지 고려사항", "도식에서 볼 것", [
                "선택은 약 이름이 아니라 세 질문에서 시작한다.",
                "다음 소절들이 이 세 가지를 하나씩 다룬다.",
            ], [10]),
        P("그럼 선택의 순서가 생긴다. 먼저 왜 쓰는지 정하고, 다음으로 어느 장기의 감염인지 정하고, 마지막으로 그 환자에게 맞춘다.", [10]),
        CHK("항균제 선택의 첫 단계는 항균제의 스펙트럼을 외우는 것이다.", "X", [8, 10], why="목적, 장기, 환자를 먼저 본다."),
    ]))
    top.append(LS("항균제 사용 목적 4가지", CH1, [
        B("항균제를 쓰는 목적은 감염이 얼마나 확인되었는지에 따라 네 가지로 나눈다.", [11]),
        DFLOW("감염 확인 단계에 따른 항균제 사용 목적", [
            ("예방적", "gray", ["prophylactic", "질병, 감염, 증상 모두 없음", "예: 수술 전 예방적 항균제"]),
            ("선제적", "amber", ["pre-emptive", "증상은 아직 없음"]),
            ("경험적", "salmon", ["empiric", "증상 있음, 원인균 미확인", "**가장 흔하다**"]),
            ("표적", "teal", ["targeted / definitive", "균주가 확인됨"]),
        ], [(0, 1, ""), (1, 2, ""), (2, 3, "균 확인")], [11]),
        B("**예방적(prophylactic)**: 질병도 감염도 증상도 없을 때 쓴다. 수술 전 예방적 항균제가 대표적이다.", [11]),
        B("**선제적(pre-emptive)**: 증상이 아직 없을 때 쓴다.", [11]),
        B("**경험적(empiric)**: 열이 나는 등 증상은 있으나 감염인지, 원인균이 무엇인지 확인되지 않은 상태에서 시작한다. 가장 많은 부분을 차지한다.", [11]),
        B("**표적(targeted/definitive)**: 균주가 확인되면 그 균을 겨냥해 바꾼다.", [11]),
        B("즉 같은 항균제라도 감염이 어디까지 확인되었는지에 따라 쓰는 목적이 달라진다.", [11]),
        CHK("원인균이 확인되기 전 증상을 근거로 시작하는 치료는 경험적 치료이다.", "O", [11]),
    ]))
    top.append(EX("같은 증상이라도 왜 만나는 맥락이 중요한가?", CH1,
                  "어디서 감염되었는지(community acquired vs nosocomial)와 면역 상태(competent vs compromised)에 따라 생각할 원인균과 약이 달라진다.", [
        P("두 번째 기준은 **장기**다. 어느 장기에 감염되었는지, 그 장기에 흔한 균이 무엇인지가 가장 중요하다. "
          "또 그 장기에 약이 잘 도달하는지도 본다. 예를 들어 CNS 감염(뇌수막염)이면 BBB(혈액뇌장벽)를 잘 통과하는 약을 고른다.", [12]),
        P("세 번째 기준은 **환자**다. 교수님은 이를 4사분면으로 정리했다. "
          "{b|생각해야 할 원인균은 community acquired와 nosocomial(병원 감염)로, 환자의 면역 상태는 competent와 compromised로 나눈다}.",
          [13, 14] + PAD_QUAD),
        FS("f1_quadrant.png", "생각해야 될 원인균? community acquired / nosocomial × competent / compromised", "그림에서 볼 것: 4사분면", [
            "위아래 축: community acquired ↔ nosocomial",
            "좌우 축: compromised ↔ competent",
            "초록 칸: 건강했던 18세 남학생, 두통, 구토, 고열, 경부강직",
            "회색 칸: AML, BMT D12, 백혈구 200/mm³, 39 °C, 두통, 구토, 경부강직",
        ], [14]),
        P("{r|교수님은 이 슬라이드가 굉장히 중요하고, 여기서 시험 문제가 나왔다고 했다.} 같은 감염, 같은 증상이라도 "
          "이 환자를 어떤 맥락(context)에서 만나는지가 치료 전략을 정한다. 입원실, ICU, 개원 진료실처럼 만나는 장소가 그 맥락을 알려 준다.", [14, 15]),
        P("{b|건강하던 18세가 두통, 구토, 고열, 경부강직으로 응급실에 오면 병원 밖에서 감염된 community acquired이고, 면역은 정상인 competent다}.",
          [14, P18_1]),
        P("{b|같은 18세라도 외상성 경막하 출혈로 개두술을 받고 7일째 뇌수막염 증상이 생기면, 침습적 수술 뒤의 병원 감염인 nosocomial이다. 젊고 면역 결함이 없으므로 여전히 competent다}.",
          [14, P20_2, P19_1]),
        P("원리를 사례에 대 보자. 65세 남성이 발열과 의식저하로 세균성 뇌수막염이 의심된다. "
          "건강하던 사람이면 community acquired이므로 ceftriaxone과 vancomycin을 쓰고, 50세 이상이라 Listeria를 커버하는 ampicillin을 더한다.", [13]),
        P("반면 같은 나이라도 뇌종양 수술 뒤 중환자실에 있는 환자라면 hospital-acquired이다. "
          "그래서 Pseudomonas(녹농균)를 고려해 ceftriaxone 대신 ceftazidime이나 meropenem을 vancomycin과 함께 쓴다.", [13]),
        P("따라서 감염 장소 → 생각할 원인균 → 항균제 선택으로 이어진다. 면역 상태는 다음 장의 살균제 선택과 용량으로 이어진다.", [13, 14]),
        CHK("18세 남성이 개두술 7일 뒤 뇌수막염 증상을 보이면 community acquired / compromised로 평가한다.", "X", [14],
            why="nosocomial / competent이다."),
    ], refs=PAD_QUAD))

    # ================================================================ 2. 경험적 → 표적
    top.append(EX("항균제 치료는 어떤 순서로 진행되는가?", CH2,
                  "환자 평가 → 경험적 치료 시작과 동시에 감수성 검사 → 결과를 보고 표적 치료 → 모니터링 → 완료.", [
        DFLOW("항균제 치료의 흐름", [
            ("환자 평가", "gray", ["patient evaluation", "증상과 sign 확인"]),
            ("경험적 치료", "salmon", ["initial empirical therapy", "치료 전 검체 채취"]),
            ("감수성 검사", "amber", ["susceptibility test", "균 동정, MIC"]),
            ("표적 치료", "teal", ["definitive therapy", "약, 용량, 용법 조정"]),
            ("모니터링", "blue", ["치료 반응 확인", "→ 치료 완료"]),
        ], [(0, 1, ""), (1, 2, "동시에"), (2, 3, ""), (3, 4, "")], [18, 19]),
        P("먼저 환자를 평가한다(patient evaluation). 증상과 sign이 있어 경험적 치료를 하기로 하면 initial empirical therapy를 시작한다.", [18]),
        P("동시에 치료 전에 채취한 혈액 등 검체(specimen)로 감수성 검사(susceptibility test)를 한다. "
          "균이 동정되고 감수성이 확인되면 표적 치료(definitive therapy)로 넘어간다. 이때 항균제를 바꾸거나 용량과 용법을 조정한다.", [19]),
        P("그다음 치료가 듣는지 계속 모니터링하고, 충분한 시간이 지나면 치료를 끝낸다. "
          "{g|지극히 상식적인 흐름이지만 제대로 지켜지지 않는 경우가 있어 기초부터 설명했다.}", [19]),
        P("임상약리 시간이므로 MIC(Minimum Inhibitory Concentration)를 정하는 검사도 다뤘다. "
          "균 동정과 감수성 검사를 거치면 항균제별 감수성 결과지를 받고, 이를 보고 환자에게 가장 알맞은(optimal) 항균제를 고른다.", [20]),
        P("그럼 경험적 치료는 언제 바꾸는가? 경험적 치료가 적절하면 그대로 유지하는 것이 가장 좋은 시나리오다. "
          "수정 여부는 감염 부위, 원인균, 감수성 패턴, 숙주(환자) 인자, 그리고 {r|무엇보다 치료 반응}을 종합해 정한다.", [21]),
        CHK("감수성 검사는 표적 치료로 바꾼 뒤에 검체를 채취해 시행한다.", "X", [19], why="치료 전에 채취한 검체로 경험적 치료와 동시에 한다."),
    ]))
    top.append(EX("정균제와 살균제는 무엇이 다른가?", CH2,
                  "정균제는 증식만 막고 숙주 면역에 기대며, 살균제는 균을 죽이므로 면역저하 환자와 중증 감염에 쓴다.", [
        P("항균제와 용법을 정할 때는 치료 목적이 정균(bacteriostatic)인지 살균(bactericidal)인지도 알아야 한다.", [22]),
        P("**정균제**는 세균의 증식을 억제하고 최종 치료는 숙주의 면역계에 기대는 항생제다. "
          "그럼 면역이 약한 환자에서는 정균제만으로 끝내기 어렵다. 그래서 세균을 사멸시키는 **살균제**는 "
          "면역저하 환자(immunocompromised patient)나 중증 감염에서 주로 선택한다.", [22]),
        FS("f2_static_cidal.png", "Bacteriostatic vs bactericidal agent: number of viable bacteria over time", "그림에서 볼 것", [
            "검은 선(control)은 약이 없어 균이 계속 는다.",
            "파란 선: bacteriostatic agent(예: chloramphenicol)를 넣으면 균 수가 유지된다.",
            "빨간 선: bactericidal agent(예: penicillin)를 넣으면 살아 있는 균(viable bacteria)이 급격히 준다.",
        ], [23]),
        P("다만 정균과 살균은 항균제의 농도나 균주에 따라 달라질 수 있는 **상대적인 개념**이다.", [23]),
        CHK("면역억제 환자에서는 정균제보다 살균제를 사용해야 한다.", "O", [22, 24]),
    ]))

    # ================================================================ 3. 환자 인자
    top.append(LS("용량과 용법에 영향을 주는 환자 인자", CH3, [
        B("앞의 4사분면을 환자 인자로 풀어 나열하면 다음과 같다.", [24]),
        B("**기저 질환과 면역 상태**: 중증 당뇨, 악성 종양, 면역억제제 투여 환자는 감염의 중증도가 크게 달라진다. "
          "그래서 고용량이나 장기간 투여가 필요한데, 그러면 항균제 자체의 독성이 문제가 될 수 있어 용법을 주의 깊게 정한다.", [24]),
        B("**면역억제 환자**: 정균제는 쓰기 어렵고 살균제를 쓴다.", [24]),
        B("**신기능과 간기능 저하**: 신장이나 간으로 제거되는 항균제는 혈중 농도가 올라가 독성 가능성이 커진다. "
          "특정 항균제는 GFR 범위나 간기능에 따른 용법 제한 기준이 있으므로 확인하고 쓴다.", [25]),
        B("**외래에서 확인하는 법**: 검사(lab)로도 알 수 있지만 외래(커뮤니티)에서는 병력 청취(history taking)를 잘해야 한다.", [25]),
        B("**저관류(hypoperfusion)**: 감염 부위의 혈류가 줄면 약이 균이 있는 곳까지 충분히 가지 못하므로 다른 방법을 고려한다.", [26]),
        B("**연령**: 신생아와 노인은 상황에 따라 용법이 크게 달라진다. 신생아는 대사 효소 기능이 미숙한 경우가 많다.", [27]),
        B("즉 같은 감염이라도 면역, 제거 장기, 혈류, 나이에 따라 약의 선택과 용량이 달라진다.", [24, 25, 26, 27]),
        CHK("신기능이 떨어진 환자에서는 신장으로 제거되는 항균제의 혈중 농도가 낮아져 효과가 떨어진다.", "X", [25],
            why="혈중 농도가 올라가 독성 위험이 커진다."),
    ]))

    # ================================================================ 4. 기관, 환자, 투여 경로
    top.append(EX("이미 정해진 용법은 무엇을 근거로 하는가?", CH4,
                  "표적 균주의 MIC 프로파일, 반복 투여 때의 PK/PD 자료, 그리고 이를 바탕으로 한 임상시험이 근거다.", [
        P("{g|녹화 강의의 두 번째 질문은 ‘주사제, 경구제, 정해진 용량과 용법은 어떻게 결정되나’였다.}", [29]),
        P("대부분의 항균제는 용량과 용법이 이미 제시되어 있다. 그런데 같은 3세대 cephalosporin이라도 하루 한 번 주는 약과 두 번 주는 약이 있다. "
          "그럼 무엇을 고를지, IV가 더 우월한지 같은 궁금증이 생긴다.", [30]),
        P("정해진 용법의 근거는 세 가지다. 표적 균주의 MIC 프로파일, 일정 용량을 계속 줄 때의 PK/PD 자료와 MIC 이상으로 유지되는 농도, "
          "그리고 이를 바탕으로 한 임상시험이다. 그래도 선택지가 많으므로 다음을 따로 생각한다.", [31]),
        P("고려할 점은 세 가지다. ① 어떤 기관(organ)의 감염인가 ② 어떤 환자인가(외래, 입원, ICU의 중환자(critically ill patient)) "
          "③ IV와 PO(경구) 중 무엇이 나은가. 셋째는 오랫동안 고민되어 온 문제다.", [32]),
        CHK("항균제의 표준 용법은 표적 균주의 MIC와 PK/PD 자료, 임상시험을 근거로 정해졌다.", "O", [31]),
    ]))
    top.append(LS("감염 기관에 따른 투여 경로와 분포", CH4, [
        B("기관마다 약이 도달하는 정도가 다르므로 경로와 약을 바꾼다.", [33]),
        B("**CNS 감염**: BBB를 잘 통과하는 ceftriaxone, vancomycin을 CNS dose로 준다.", [33]),
        B("**드문 CNS 감염**: cryptococcal meningitis 등은 척수강 내 투여(intrathecal therapy)로 CSF에 바로 넣기도 한다.", [33]),
        B("**안구 내 감염**: IV로는 도달이 의심스러워 유리체강 내 주사(intravitreal injection)를 하기도 한다.", [33]),
        B("**골관절 감염(bone and joint infection)**: 혈관 분포가 풍부한 기관보다 약이 잘 도달하지 않을 수 있다.", [33]),
        B("**분포(distribution)**: tigecycline은 조직으로 잘 가지만 혈중 농도가 낮다. aminoglycoside는 혈중보다 훨씬 높은 농도로 요로(urinary tract)에 있다.", [34]),
        B("**흡입 치료(inhalation therapy)**: 입자가 large airway까지만 가는지, bronchiole과 alveoli(폐포)까지 가는지가 문제다. "
          "폐렴이면 alveoli까지 가야 한다. 일반 nebulizer와 aerosol generator 중 무엇을 쓸지도 고른다.", [34]),
        B("즉 약은 혈중이 아니라 균이 있는 곳에서 충분한 농도여야 하므로 감염 기관이 경로와 약을 정한다.", [33, 34]),
        CHK("Aminoglycoside는 요로에서 혈중보다 훨씬 높은 농도로 존재한다.", "O", [34]),
    ]))
    top.append(LS("환자에 따라 경로를 고를 때 보는 것", CH4, [
        B("같은 기관의 감염이라도 환자 상황에 따라 경로와 약이 달라진다.", [35]),
        B("**외래 vs 입원**: 외래면 경구 항균제가 기본이다. 그래도 하루 한 번 주사실에서 IV를 맞아야 하는 경우가 있다. "
          "입원 환자도 재원 기간을 줄이려고 빨리 퇴원시키는 쪽을 고려하기도 한다.", [35]),
        B("**혈관 상태**: 하루 3~4번 주거나 nafcillin처럼 sodium이 많은 약은 정맥염(phlebitis)이 잘 생긴다. "
          "nafcillin, vancomycin은 말초 정맥관(peripheral line)으로 맞기 힘든 경우가 많다.", [35]),
        B("**경구 섭취와 흡수**: 설사가 계속되거나 GI bleeding이 있으면 경구약의 효과(efficacy)를 기대하기 어렵다. 동반 질환도 본다.", [36]),
        B("**순응도(compliance)**: 하루 3~4번 챙겨 먹기 힘든 바쁜 환자에게는 같은 효과의 하루 1번 약이 낫다. 먹다 안 먹다 하면 치료 농도(therapeutic level)가 떨어진다.", [37]),
        B("**생활 패턴**: 밤낮이 바뀐 환자(예: 일부 HIV 감염인)는 하루 1번 약을 자기 전에 먹게 하는 등 시간을 맞춘다. 식후 복용이 필수가 아닌 약일 때 가능하다.", [38]),
        B("즉 경로와 투여 횟수는 약효만이 아니라 환자가 실제로 맞고 먹을 수 있는지로 정한다.", [35, 36, 37, 38]),
        CHK("하루 1번 복용하는 항균제는 바쁜 환자의 순응도를 높여 치료 농도 유지에 유리하다.", "O", [37]),
    ]))
    top.append(EX("주사가 항상 경구보다 나은가?", CH4,
                  "아니다. 경구가 기본이고 IV는 가능하면 빨리 경구로 바꾼다. 장관 감염에는 흡수되지 않는 경구약이 오히려 맞다.", [
        P("입원 환자라면 주사가 더 빠르고 좋다는 고정관념이 있다. IV는 100% 들어가지만 항상 낫지는 않다. "
          "패혈증(sepsis), 심내막염(endocarditis), CNS 감염인지, 장관(GI tract) 감염인지에 따라 다르다.", [39]),
        P("예를 들어 Clostridium difficile 감염(CDI)이나 amebic colitis에는 장관 안에서 작용하는 luminal agent를 쓴다. "
          "**경구 vancomycin은 흡수되지 않는 luminal agent**다. 그래서 장 안의 균에는 IV vancomycin보다 경구 vancomycin이 맞다.", [39]),
        COLS("경로를 고르는 원칙은 다음과 같다.", [
            ("경구(PO)가 기본", "teal", ["가장 선호되는 경로, 특히 외래", "자가 투여가 가능하다", "중증이면 초기 IV, 가능한 한 빨리 **IV → PO switch**"]),
            ("비경구(주사)가 필요할 때", "salmon", ["경구로 적정 혈장 농도를 못 얻을 때(흡수 시간, bioavailability)", "중증 감염, 패혈증처럼 긴급할 때", "더 높은 혈장 농도가 필요할 때"]),
        ], [45, 46]),
        P("따라서 경로는 ‘더 센 것’이 아니라 약이 필요한 곳에 필요한 농도로 가는 길을 고르는 문제다.", [39, 45]),
        CHK("CDI에서 경구 vancomycin은 흡수되지 않고 장관 안에서 작용한다.", "O", [39]),
    ]))

    # ================================================================ 5. PK/PD
    top.append(EX("시간 의존성 살균과 농도 의존성 살균은 어떻게 다른가?", CH5,
                  "시간 의존성은 MIC 이상으로 오래 유지할수록, 농도 의존성은 잠깐이라도 높게 올릴수록 유리하다.", [
        P("용법을 정할 때 하나 더 볼 것은 항균제가 time-dependent killing(시간 의존성 살균)을 하는지, "
          "concentration-dependent killing(농도 의존성 살균)을 하는지다.", [40]),
        P("{b|time-dependent killing은 특정 농도(MIC) 이상으로 유지되는 시간이 길수록 감염 치료에 유리하다}. "
          "대표는 β-lactam(beta-lactam) 계열이다. 그럼 농도를 오래 유지하려면 저용량을 짧은 간격으로 자주 주는 dosing regimen을 따른다.", [41] + PAD_PKPD),
        P("{b|concentration-dependent killing은 잠깐이라도 고농도로 노출시키는 것이 유리하다}. "
          "{b|aminoglycoside가 대표이며, 투약 간격을 늘리고 1회 투여량을 높여 최고 농도를 아주 높게 만든다. 따라서 투약 간격도 중요한 고려사항이다}.",
          [41] + PAD_PKPD),
        FS("f3_time_dep.png", "Time-dependent antibiotics", "그림에서 볼 것: 시간 의존성", [
            "관심 지표는 Time above MIC다.",
            "MIC 선 위에 있는 시간(T>MIC)을 화살표로 표시했다.",
            "PAE는 작거나 중간(minimal or moderate)이다.",
        ], [41, 42]),
        FS("f4_conc_dep.png", "Concentration-dependent antibiotics", "그림에서 볼 것: 농도 의존성", [
            "관심 지표는 Cmax/MIC와 AUC/MIC다.",
            "PAE가 길다(prolong).",
        ], [41, 42]),
        P("{b|PAE(post-antibiotic effect)는 항균제 농도가 MIC 미만으로 떨어진 뒤에도 항균 효과가 지속되는 것이다}. "
          "조직 농도나 PD 인자로 설명된다. 농도가 늘 MIC 위에 있을 수는 없지만, 그 아래로 내려가도 작용이 바로 0이 되지는 않는다.",
          [42] + PAD_PKPD),
        CONCEPT_V("시간 의존성 vs 농도 의존성", [
            "**time-dependent**: {b|MIC 이상 유지 시간이 길수록 유리}, β-lactam, 저용량을 짧은 간격으로",
            "**concentration-dependent**: {b|잠깐이라도 고농도가 유리}, {b|aminoglycoside}, {b|고용량을 긴 간격으로}",
            "**PAE**: {b|MIC 이하로 떨어진 뒤에도 효과 지속}. 농도 의존성 약에서 길다(그림)",
        ], [41, 42] + PAD_PKPD,
            diagram=DIA("compare", [("시간 의존성", "teal", ["오래 유지", "β-lactam", "적게, 자주"]),
                                    ("농도 의존성", "salmon", ["높게 올림", "aminoglycoside", "많이, 드물게"])],
                        row_labels=["목표", "대표", "투여"]),
            caption="시간 의존성 vs 농도 의존성"),
        CHK("Aminoglycoside는 time-dependent killing을 하는 대표 약물이다.", "X", [41],
            why="aminoglycoside는 concentration-dependent killing이다."),
        CHK("PAE는 항균제 농도가 MIC 이상일 때만 나타나는 효과이다.", "X", [42], why="MIC 이하로 떨어진 뒤에도 지속되는 효과이다."),
    ], refs=PAD_PKPD))
    top.append(LS("PK/PD 지표 세 가지", CH5, [
        B("{r|교수님은 이 슬라이드가 중요하다고 했다.} PK 곡선을 MIC와 비교해, 넘는 시간이나 올라가는 높이에 따라 항균제의 기전이 달라진다.", [44]),
        FS("f5_pkpd_index.png", "PK/PD 지표: Cmax/MIC, AUC/MIC, T>MIC", "그림에서 볼 것", [
            "파랑 글씨는 concentration-dependent, 초록은 time-dependent다.",
            "빨강은 concentration-dependent with time dependence(AUC/MIC)다.",
            "점선이 MIC, 아래 굵은 선이 MIC 위에 있는 시간이다.",
        ], [43, 44]),
        B("**T>MIC**: MIC 위에 있는 시간을 투여 간격에 대한 %로 쓴다. 투여 간격 24시간 중 16시간이 MIC 이상이면 16/24다. time-dependent 약(β-lactam)의 지표다.", [43]),
        B("**Cmax/MIC**: 최고 농도를 MIC로 나눈다. MIC가 약 5, Cmax가 약 15면 3이다. 대표는 aminoglycoside다.", [43]),
        B("**AUC/MIC**: 곡선 아래 면적(area under the curve)을 MIC로 나눈다. vancomycin, azithromycin, quinolone계가 쓴다. concentration-dependent with time-dependence로 세분하기도 한다.", [43]),
        B("즉 약마다 ‘얼마나 오래’, ‘얼마나 높이’, ‘얼마나 많이’ 중 무엇이 효과를 정하는지가 다르고, 그에 맞춰 용법을 짠다.", [43, 44]),
        CHK("AUC/MIC를 지표로 쓰는 약물에는 vancomycin과 quinolone계가 있다.", "O", [43]),
    ]))

    # ================================================================ 6. 병용요법
    top.append(EX("항균제를 여러 개 쓰면 더 좋은가?", CH6,
                  "아니다. 단일 제제가 원칙이고, 근거가 뚜렷한 이득이 있을 때만 병용한다. 상호작용으로 효과가 오히려 줄 수 있다.", [
        P("항균제는 하나만 쓰는 경우가 많지만 병용도 빈번하다. 원칙은 **단일 제제**이고, 병용은 뚜렷한 치료 이득이 있을 때만 한다.", [47]),
        COLS("병용하는 경우와 주의할 점은 다음과 같다.", [
            ("병용이 유리한 경우", "teal", ["교대 감염", "내성균 발현 억제", "AIDS 치료(항균제는 아님), 특정 폐렴", "항결핵제(당연히 병용)", "요로 감염의 TMP/SMX(박트림)"]),
            ("주의할 점", "salmon", ["병용 약 사이의 PK, PD 상호작용", "다른 약의 대사에 영향 → 효과 감소, 부작용 증가", "근거가 명확한 병용만 선택", "‘예전에 써 보니 좋더라’ 식은 지양"]),
        ], [47, 48]),
        P("왜 많이 쓰면 안 될까? 한 항균제가 다른 항균제의 대사에 영향을 주면 효과가 줄거나 부작용이 늘 수 있다. "
          "따라서 병용 약 수 증가 → 상호작용 → 치료 효과 감소로 이어질 수 있다.", [48]),
        P("병용요법을 흔히 cocktail therapy라고 하지만 정식 표현은 **combination therapy**다. "
          "칵테일이 단일한 술보다 늘 낫지 않듯 병용도 늘 낫지 않고 오히려 해가 될 수 있다.", [49]),
        P("개원가뿐 아니라 대학병원에서도 남용되는 측면이 있다. 사회가 고령화될수록 이 문제는 더 중요해진다.", [50]),
        CHK("항균제는 여러 개를 병용할수록 상호작용 없이 효과가 더해진다.", "X", [48], why="상호작용으로 효과가 줄 수 있어 근거 있는 병용만 한다."),
    ]))

    # ================================================================ QUIZ
    top.append(T("QUIZ", CH6, [], [
        _st("quiz", "65세 남성이 뇌종양 수술 뒤 중환자실에 입원 중 세균성 뇌수막염이 의심된다. 가장 알맞은 경험적 항균제 조합은?", [13],
            options=["① ceftriaxone + vancomycin + ampicillin", "② meropenem + vancomycin", "③ 경구 vancomycin 단독",
                     "④ aminoglycoside 흡입 치료", "⑤ 감수성 결과가 나올 때까지 항균제를 쓰지 않는다"],
            answer="② meropenem + vancomycin",
            explanations=["① 건강하던 사람의 community acquired 뇌수막염 조합이다", "② 원내 감염이므로 Pseudomonas를 고려한다 (정답)",
                          "③ 경구 vancomycin은 흡수되지 않는 luminal agent다", "④ 흡입 치료는 호흡기 감염의 선택지다",
                          "⑤ 경험적 치료는 감수성 검사와 동시에 시작한다"]),
        _st("quiz", "투여 경로에 대한 설명으로 옳지 않은 것은?", [39, 45, 46],
            options=["① 외래에서는 경구 투여가 가장 선호된다", "② 중증 환자도 가능하면 빨리 IV → PO로 바꾼다",
                     "③ 입원 환자에게는 주사가 항상 더 효과적이다", "④ 경구로 적정 혈장 농도를 얻을 수 없으면 주사를 고려한다",
                     "⑤ 패혈증처럼 긴급한 경우에는 비경구 투여를 우선한다"],
            answer="③ 입원 환자에게는 주사가 항상 더 효과적이다",
            explanations=["① 자가 투여가 가능하다", "② 가능한 한 빨리 경구로 전환하는 것이 유리하다",
                          "③ 주사가 항상 낫지는 않다. CDI에는 경구 vancomycin을 쓴다 (정답)", "④ 흡수, bioavailability 문제 때문이다",
                          "⑤ 긴급한 항균 치료가 필요하다"]),
    ]))
    return top


if __name__ == "__main__":
    import sys

    topics = build()
    for t in topics:
        t.slide_numbers = sorted({r for sts in t.sections.values() for st in sts for r in st.slide_refs})
    dump(topics, sys.stdout)
