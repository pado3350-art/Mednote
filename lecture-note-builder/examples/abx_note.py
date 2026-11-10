"""Mixed-style note for 'Clinical Therapeutics: 중환자와 항균제' (임상약리, 2026-08-19 2교시, 한성필 교수님).

Written TOP-DOWN: outputs/abx/storyline.md first (lecture skeleton = 질문1 무엇을 고를까 / 질문2 어떻게 줄까),
then this file expands it. Headings, order, style and 핵심 답 come from the storyline; sentences follow skill 00b
(topic sentence first, one new fact per sentence, define before use, one gloss per term, figures by content).

Inputs (nothing else is used):
  * script   inputs/abx_script.txt  (52 paragraphs; live lecture + recorded video of 조성연·한성필 교수님)
  * pictures inputs/abx_figs/       (5 slide images taken from the 정리본 PDF - pictures only)
  * PAD      inputs/abx_pad.pdf     (6 questions: 20/19/18학번 x 2) - used ONLY to decide what is blue.
Run:  python -m examples.abx_note > outputs/abx/note_authored.json
"""
from app.models import Arrow, Diagram, Group, Statement
from examples.authoring import SlideTable, T, dump
from examples.stemcell_note import CHK, COLS, CONCEPT, MEMO, _st

FIG = "inputs/abx_figs/"
CH1 = "항균제 선택 원칙: 사용 목적, 감염 장기, 환자 맥락"
CH2 = "경험적 치료에서 표적 치료로: 치료 과정, 정균제와 살균제, 환자 인자"
CH3 = "항균제 용량, 용법, 투여 경로의 결정"
CH4 = "PK/PD에 따른 용법, 투여 경로 원칙, 병용요법"

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


def DFULL(caption, diagram, g=()):
    return Statement(text=caption, kind="diagram", slide_refs=list(g), diagram=diagram)


def CONCEPT_V(title, lines, g, diagram=None, caption=""):
    st = CONCEPT(title, lines, g)
    st.text, st.diagram = caption or title, diagram
    return st


def EX(heading, chapter, answer, body, refs=()):
    t = T(heading, chapter, [], body, basics_title="핵심 답", basics=[answer], style="explain")
    t.basics_refs = list(refs)
    return t


def LS(heading, chapter, body):
    return T(heading, chapter, [], body, style="list")


def build():
    top = []

    # ================================================================ 앞쪽: 시험 축 두 표 + 전체 지도
    quad = SlideTable(
        caption="기출 ① 획득 경로 × 면역 4사분면 — 파랑 = 기출(PAD)",
        col_widths_cm=[7.2, 3.2, 2.6, 4.4],
        rows=[
            ["사례", "획득 경로", "면역", "출처"],
            ["건강하던 18세, 두통, 구토, 고열, 경부강직으로 응급실", "{b|community acquired}", "{b|competent}", "기출, 슬라이드"],
            ["18세, 외상성 경막하 출혈로 개두술, 7일째 뇌수막염 증상", "{b|nosocomial}", "{b|competent}", "기출"],
            ["AML, BMT D12, 백혈구 200/mm³, 39 °C, 경부강직", "nosocomial", "compromised", "슬라이드"],
        ])
    pkpd = SlideTable(
        caption="기출 ② 시간 의존성 vs 농도 의존성 살균 — 파랑 = 기출(PAD)",
        col_widths_cm=[2.6, 7.4, 7.4],
        rows=[
            ["", "시간 의존성 (time-dependent)", "농도 의존성 (concentration-dependent)"],
            ["유리한 것", "{b|MIC 이상 유지 시간이 길수록}", "{b|잠깐이라도 고농도로 노출될수록}"],
            ["용법", "저용량, 짧은 간격", "{b|고용량, 긴 간격 (투약 간격도 고려)}"],
            ["대표 약물", "β-lactam (그림: vancomycin, macrolide, clindamycin)", "{b|aminoglycoside} (그림: fluoroquinolone)"],
            ["지표", "T>MIC", "Cmax/MIC, AUC/MIC"],
            ["PAE", "{b|MIC 이하로 떨어진 뒤에도 항균 효과가 지속되는 것}", "그림: 농도 의존성에서 길다"],
        ])
    top.append(T("요약 정리 · 시험 정리", "", [], [
        _st("para", "기출 6문항은 두 유형뿐이다. 두 표가 그 두 유형이고, 아래 지도가 강의 전체다.", [2]),
        DFULL("강의 전체 지도 — 항균제 선택에서 용법과 병용까지, 강의 순서대로", Diagram(
            kind="tree", root="항균제 처방", groups=[
                Group(title="1. 항균제 선택 원칙", color="teal", items=["사용 목적 4가지", "감염 장기", "환자: 4사분면 (기출)"]),
                Group(title="2. 경험적 → 표적 치료", color="blue", items=["감수성 검사", "정균제 vs 살균제", "환자 인자"]),
                Group(title="3. 용량, 용법, 투여 경로", color="salmon", items=["용법의 근거", "기관별, 환자별 경로", "주사 vs 경구"]),
                Group(title="4. PK/PD, 경로 원칙, 병용", color="amber", items=["시간 vs 농도 의존 (기출)", "경구가 기본", "병용은 근거 있을 때만"]),
            ]), [7, 10, 18, 29, 40, 47]),
    ], tables=[quad, pkpd], role="front"))

    # ================================================================ 1장 질문1: 무엇을 고를까
    top.append(EX("항균제 선택은 사용 목적, 감염 장기, 환자 중 무엇에서 시작하나?", CH1,
                  "목적, 장기, 환자 세 질문에서 시작한다. 약 이름은 그다음이다.", [
        MEMO("수업은 녹화 문답 영상(감염내과 조성연 교수님, 한성필 교수님)을 틀고 교수님이 덧붙이는 방식이었습니다. "
             "영상 재생 준비, 휴식과 출석 안내는 생략했습니다.", [1, 4, 5, 6, 9, 16, 17, 28, 51, 52]),
        P("이 강의는 녹화 영상의 질문 두 개로 짜여 있다. 질문1은 항균제 선택 원칙(어떤 약을 고를까), 질문2는 용량, 용법, 투여 경로의 결정이다. "
          "{g|감염내과와 임상약리과는 항균제 PK/PD 분야에서 함께 연구를 많이 해 왔다.}", [1, 7, 29]),
        P("학습목표도 같은 순서다. 목적에 따른 치료 전략, 용량과 용법의 결정 인자, 환자 개인차에 따른 고려점이다. "
          "{g|미충족 의료 수요도 목표에 있었지만 이번 시간에는 다루지 않았다.}", [2, 3]),
        P("항균제를 스펙트럼으로만 외우면 선택 원칙이 보이지 않는다. "
          "스펙트럼은 그 약이 어떤 균을 커버하는지다(예: ceftriaxone이 Gram-positive와 negative를 커버하는가).", [7, 8], effort="참고"),
        P("질문1의 답은 세 질문이다. 첫째, 왜 쓰는가(목적). 둘째, 어느 장기의 감염인가. 셋째, 어떤 환자인가.", [10]),
        DFS(DIA("tree", [("① 목적", "teal", ["왜 쓰는가"]),
                         ("② 장기", "blue", ["어디의 감염인가"]),
                         ("③ 환자", "salmon", ["누구인가"])], root="항균제 선택"),
            "질문1의 세 축", "도식에서 볼 것", [
                "세 축을 이 순서로 묻는다.",
                "1장의 나머지 소절이 세 축을 하나씩 다룬다.",
            ], [10]),
        CHK("항균제 선택의 첫 단계는 항균제의 스펙트럼을 외우는 것이다.", "X", [8, 10], why="목적, 장기, 환자를 먼저 묻는다."),
    ]))
    top.append(LS("항균제 사용 목적 4가지(예방적, 선제적, 경험적, 표적 치료)는 어떻게 나누나?", CH1, [
        B("목적은 감염이 얼마나 확인되었는지로 네 가지로 나눈다.", [11]),
        DFULL("사용 목적 4가지: 무엇이 확인되었나", DIA("compare", [
            ("예방적", "gray", ["없음", "없음", "없음", "수술 전 예방적 항균제"]),
            ("선제적", "amber", ["—", "아직 없음", "—", ""]),
            ("경험적", "salmon", ["모름", "있음 (예: 열)", "아직 모름", "**가장 많이 쓰는 경우**"]),
            ("표적", "teal", ["확인", "있음", "확인됨", "균을 겨냥해 바꾼다"]),
        ], row_labels=["감염", "증상", "원인균", "특징"], size="full"), [11]),
        B("**예방적(prophylactic)**: 질병도 감염도 증상도 없을 때 쓴다. 수술 전 예방적 항균제가 대표다.", [11]),
        B("**선제적(pre-emptive)**: 증상이 아직 없을 때 쓴다. {g|소리가 작아 설명이 짧았다.}", [11]),
        B("**경험적(empiric)**: 증상은 있지만 감염인지, 원인균이 무엇인지 모를 때 시작한다. 가장 많이 쓰는 경우다.", [11]),
        B("**표적(targeted, definitive)**: 균주가 확인되면 그 균을 겨냥한다.", [11]),
        B("즉 목적은 ‘무엇이 확인되었나’로 갈린다. 확인된 것이 늘수록 예방 → 경험 → 표적으로 간다.", [11]),
        CHK("원인균이 확인되기 전에 증상을 근거로 시작하는 치료는 경험적 치료이다.", "O", [11]),
    ]))
    top.append(EX("감염 장기(CNS 등)는 항균제 선택에 왜 중요한가?", CH1,
                  "장기마다 흔한 균이 다르고, 약이 그 장기에 닿는 정도도 다르다.", [
        P("장기를 알면 흔한 균을 알 수 있다. 증상으로 어느 장기의 감염인지 추론하고, 그 장기에 흔한 균을 떠올린다. "
          "예를 들어 두통과 발열이면 CNS 감염(뇌수막염)을 생각한다.", [12]),
        P("장기를 알면 약이 닿는지도 따질 수 있다. CNS 감염이면 BBB(혈액뇌장벽)를 잘 통과하는 약을 고른다.", [12]),
        P("그럼 같은 장기의 감염이라도 환자가 다르면 약이 같을까? 다음 소절이 그 답이다.", [12, 13]),
        CHK("CNS 감염에서는 BBB를 잘 통과하는 항균제를 고른다.", "O", [12]),
    ]))
    top.append(EX("획득 경로(community acquired, nosocomial)와 면역 상태(competent, compromised)는 항균제 선택을 어떻게 바꾸나?", CH1,
                  "어디서 감염되었는지와 면역 상태에 따라 생각할 균이 달라지고, 그래서 약이 달라진다.",
                  [
        P("{r|교수님은 이 4사분면 슬라이드가 굉장히 중요하고, 여기서 시험 문제가 나왔다고 했다.}", [14, 15]),
        P("{b|환자는 두 축으로 나눈다. 원인균을 얻은 곳은 community acquired(지역사회 획득) 또는 nosocomial(병원 감염)이다. "
          "면역 상태는 competent(정상) 또는 compromised(저하)다}.", [14] + PAD_QUAD),
        FS("f1_quadrant.png", "생각해야 될 원인균? 획득 경로 × 면역 4사분면", "그림이 담은 사실", [
            "세로축: community acquired(위) ↔ nosocomial(아래).",
            "가로축: compromised(왼쪽) ↔ competent(오른쪽).",
            "오른쪽 위 칸: 건강했던 18세 남학생, 두통, 구토, 고열, 경부강직 → community acquired / competent.",
            "왼쪽 아래 칸: AML, BMT D12, 백혈구 200/mm³, 39 °C → nosocomial / compromised.",
        ], [14]),
        P("{b|건강하던 18세가 두통, 구토, 고열, 경부강직으로 응급실에 왔다. 병원 밖에서 감염되었으므로 community acquired이고, 면역은 정상인 competent다}.",
          [14, P18_1]),
        P("{b|같은 18세가 외상성 경막하 출혈로 개두술을 받고 7일째 뇌수막염 증상이 생겼다. 침습적 수술 뒤의 병원 감염이므로 nosocomial이다. 젊고 면역 결함이 없으므로 competent다}.",
          [14, P20_2, P19_1]),
        P("원리를 약 선택에 대 보자. 65세 남성이 발열과 의식저하로 세균성 뇌수막염이 의심된다. "
          "건강하던 사람이면 community acquired다. 그래서 ceftriaxone과 vancomycin을 쓴다. "
          "50세 이상이므로 Listeria를 커버하는 ampicillin을 더한다.", [13]),
        P("같은 나이라도 뇌종양 수술 뒤 중환자실에 있으면 hospital-acquired(병원 감염)다. "
          "그래서 Pseudomonas(녹농균)를 고려한다. ceftriaxone 대신 ceftazidime이나 meropenem을 vancomycin과 함께 쓴다.", [13]),
        P("따라서 감염 장소 → 생각할 균 → 항균제로 이어진다. 만나는 장소(입원실, ICU, 외래 진료실)가 그 맥락(context)을 알려 준다.", [13, 15]),
        CHK("개두술 7일 뒤 뇌수막염 증상을 보이는 18세 남성은 community acquired / compromised로 평가한다.", "X", [14],
            why="nosocomial / competent이다."),
    ], refs=PAD_QUAD))
    top.append(EX("경험적 치료(empiric)는 언제 표적 치료(targeted)로 바뀌나?", CH2,
                  "감수성 검사로 균과 감수성이 확인되면 바꾼다. 바꿀지 판단할 때 가장 중요한 것은 치료 반응이다.", [
        P("경험적 치료는 원인균을 모르는 채 시작한다. 그럼 균이 확인된 뒤에는 어떻게 바꿀까? 치료는 환자 평가에서 증상과 징후를 확인하는 데서 시작해, 경험적 치료, 감수성 검사, 표적 치료, 모니터링의 다섯 단계로 이어진다.", [18]),
        DFULL("항균제 치료의 흐름", DIA("flow", [
            ("환자 평가", "gray", ["증상과 sign 확인"]),
            ("경험적 치료", "salmon", ["initial empirical therapy"]),
            ("감수성 검사", "amber", ["치료 전 검체로", "균 동정, MIC"]),
            ("표적 치료", "teal", ["definitive therapy", "약, 용량, 용법 조정"]),
            ("모니터링", "blue", ["치료 반응 확인", "→ 치료 완료"]),
        ], arrows=[(0, 1, ""), (1, 2, "동시에"), (2, 3, ""), (3, 4, "")], size="full"), [18, 19]),
        P("경험적 치료를 시작하면서, 치료 전에 채취한 혈액 등의 검체로 감수성 검사(susceptibility test)를 함께 한다. "
          "이 검사로 균이 동정되고 항균제별 감수성과 MIC(Minimum Inhibitory Concentration, 최소 억제 농도)가 나오면, "
          "그 결과를 보고 지금 환자에게 가장 알맞은 약으로 바꾸는 것이 표적 치료(definitive therapy)다. "
          "다만 경험적 치료가 이미 적절하다면 그대로 유지하는 것이 가장 좋고, 바꿀지는 다음 다섯 가지로 판단한다.", [19, 20, 21]),
        B("감염 부위, 원인균, 감수성 패턴, 숙주(환자) 인자, {r|치료 반응(가장 중요)}", [21]),
        P("{g|지극히 상식적인 흐름이지만 실제로 지켜지지 않는 경우가 있어 기초부터 설명했다.}", [19]),
        CHK("감수성 검사는 표적 치료로 바꾼 뒤에 검체를 채취해 시행한다.", "X", [19], why="치료 전 검체로 경험적 치료와 동시에 한다."),
    ]))
    top.append(EX("정균제(bacteriostatic)와 살균제(bactericidal)는 언제 쓰나?", CH2,
                  "면역이 약하거나 중증 감염이면 살균제를 쓴다.", [
        P("면역이 약하면 살균제를 쓴다. 정균제는 균의 증식만 막고 마무리는 환자의 면역에 맡기기 때문이다.", [22]),
        P("**정균제(bacteriostatic)**는 세균의 증식을 억제한다. 최종 치료는 숙주의 면역계에 기댄다.", [22]),
        P("**살균제(bactericidal)**는 세균을 죽인다. 그래서 면역저하 환자(immunocompromised patient)나 중증 감염에서 고른다.", [22]),
        FS("f2_static_cidal.png", "Bacteriostatic vs bactericidal agent", "그림이 담은 사실", [
            "약이 없으면 살아 있는 균 수가 계속 는다.",
            "정균제(예: chloramphenicol)를 넣으면 균 수가 그대로 유지된다.",
            "살균제(예: penicillin)를 넣으면 살아 있는 균이 급격히 준다.",
        ], [23]),
        P("다만 정균과 살균은 상대적인 개념이다. 같은 약도 농도나 균주에 따라 달라질 수 있다.", [23]),
        P("면역 상태는 살균제를 고르는 기준이면서 용량을 바꾸는 환자 인자이기도 하다. 다음에 환자 인자를 본다.", [22, 24]),
        CHK("면역억제 환자에서는 정균제보다 살균제를 사용해야 한다.", "O", [22, 24]),
    ]))

    # ================================================================ 2장 질문2: 어떻게 줄까
    top.append(LS("환자 인자(면역, 신·간기능, 저관류, 연령)는 용량을 어떻게 바꾸나?", CH2, [
        B("환자 인자는 네 가지다. 앞에서 본 면역 상태가 첫째다.", [24]),
        B("**면역 상태**: 중증 당뇨, 악성 종양, 면역억제제 투여 환자는 감염이 무거워진다. 그래서 고용량이나 장기간 투여가 필요하다.", [24]),
        B("**그 대가**: 고용량, 장기간 투여는 항균제 자체의 독성을 키운다. 그래서 용법을 주의 깊게 정한다.", [24]),
        B("**면역억제 환자의 약**: 정균제는 쓰기 어렵고 살균제를 쓴다.", [24]),
        B("**신기능, 간기능 저하**: 그 장기로 제거되는 약의 혈중 농도가 올라간다. 그래서 독성 위험이 커진다.", [25]),
        B("**확인 방법**: 일부 약은 GFR이나 간기능에 따른 용법 제한 기준이 있다. 외래에서는 검사보다 병력 청취(history taking)로 먼저 확인한다.", [25]),
        B("**저관류(hypoperfusion)**: 감염 부위의 혈류가 줄면 약이 균에 충분히 닿지 못한다. 그러면 다른 방법을 고려한다.", [26]),
        B("**연령**: 신생아와 노인은 용법이 크게 달라진다. 신생아는 대사 효소 기능이 미숙한 경우가 많다.", [27]),
        B("즉 같은 감염이라도 면역, 제거 장기, 혈류, 나이에 따라 용량이 달라진다.", [24, 25, 26, 27]),
        CHK("신기능이 떨어진 환자에서는 신장으로 제거되는 항균제의 혈중 농도가 낮아진다.", "X", [25],
            why="혈중 농도가 올라가 독성 위험이 커진다."),
    ]))
    top.append(EX("정해진 항균제 용법은 무엇을 근거로 하나?", CH3,
                  "표적 균주의 MIC, 반복 투여 때의 PK/PD 자료, 그리고 이를 바탕으로 한 임상시험이다.", [
        P("1장에서 본 감염 장기와 환자 요인을 이번에는 용량, 용법, 투여 경로를 정하는 눈으로 다시 본다. "
          "{r|교수님은 영상의 두 번째 질문(질문2)에서 실제 중요한 내용이 많이 나왔다고 했다.}", [29, 51]),
        P("질문2는 “용량, 용법, 투여 경로는 어떻게 정하나?”다. 대부분의 항균제는 용량과 용법이 이미 정해져 있다.", [29, 30]),
        P("그래도 고를 것이 남는다. 같은 3세대 cephalosporin이라도 하루 한 번 주는 약과 두 번 주는 약이 있다. "
          "IV가 늘 나은지도 궁금해진다.", [30]),
        P("정해진 용법에는 근거가 셋 있다.", [31]),
        B("표적 균주의 MIC 프로파일", [31]),
        B("일정 용량을 계속 줄 때의 PK/PD 자료, 특히 MIC 이상으로 유지되는 농도", [31]),
        B("이를 바탕으로 한 임상시험", [31]),
        P("질문2의 답은 세 축이다. 첫째, 어느 기관의 감염인가. 둘째, 어떤 환자인가(외래, 입원, 중환자). 셋째, IV와 PO(경구) 중 무엇인가. "
          "셋째는 오랫동안 고민되어 온 문제다.", [32]),
        CHK("항균제의 표준 용법은 표적 균주의 MIC와 PK/PD 자료, 임상시험을 근거로 정해졌다.", "O", [31]),
    ]))
    top.append(LS("감염 기관(CNS, 안구, 뼈·관절, 호흡기)에 따라 투여 경로는 어떻게 달라지나?", CH3, [
        B("1장에서 감염 장기는 ‘어떤 균이 흔한가’의 문제였다. 여기서는 ‘약을 어떻게 닿게 하나’의 문제다.", [32, 33]),
        B("**CNS**: BBB를 잘 통과하는 ceftriaxone, vancomycin을 CNS dose로 준다.", [33]),
        B("**드문 CNS 감염**: cryptococcal meningitis 등은 척수강 내 투여(intrathecal therapy)로 CSF에 바로 넣기도 한다.", [33]),
        B("**안구 내 감염**: IV로는 닿기 어려워 유리체강 내 주사(intravitreal injection)를 하기도 한다.", [33]),
        B("**뼈와 관절(bone and joint infection)**: 혈관이 적어 혈관이 풍부한 기관보다 약이 덜 닿을 수 있다.", [33]),
        B("**분포(distribution)**: tigecycline은 조직에 잘 가지만 혈중 농도는 낮다. aminoglycoside는 혈중보다 요로(urinary tract)에서 훨씬 높다.", [34]),
        B("**흡입(inhalation therapy)**: 폐렴이면 입자가 large airway를 지나 alveoli(폐포)까지 가야 한다. 일반 nebulizer와 aerosol generator 중에서 고른다.", [34]),
        B("즉 약은 혈중이 아니라 균이 있는 곳에서 충분한 농도여야 한다.", [33, 34]),
        CHK("Aminoglycoside는 요로에서 혈중보다 훨씬 높은 농도로 존재한다.", "O", [34]),
    ]))
    top.append(LS("환자 사정(외래·입원, 혈관, 흡수, 순응도)에 따라 투여 경로는 어떻게 달라지나?", CH3, [
        B("같은 기관의 감염이라도 환자가 실제로 맞고 먹을 수 있어야 한다. 다섯 가지를 본다.", [35]),
        B("**외래 vs 입원**: 외래는 경구가 기본이다. 그래도 하루 한 번 주사실에서 IV를 맞는 경우가 있다. 입원 환자도 재원 기간을 줄이려 일찍 퇴원시키기도 한다.", [35]),
        B("**혈관 상태**: 하루 3~4번 맞거나 sodium이 많은 nafcillin을 쓰면 정맥염(phlebitis)이 잘 생긴다. nafcillin, vancomycin은 말초 정맥관으로 맞기 힘들 때가 많다.", [35]),
        B("**먹고 흡수할 수 있나**: 설사가 계속되거나 GI bleeding이 있으면 경구약의 효과(efficacy)를 기대하기 어렵다. 동반 질환도 본다.", [36]),
        B("**순응도(compliance)**: 하루 3~4번 챙기기 힘든 바쁜 환자에게는 하루 1번 약이 낫다. 먹다 말다 하면 치료 농도(therapeutic level)가 떨어진다.", [37]),
        B("**생활 패턴**: 밤낮이 바뀐 환자(예: 일부 HIV 감염인)에게는 하루 1번 약을 자기 전에 먹게 한다. 식후 복용이 꼭 필요한 약이 아닐 때 가능하다.", [38]),
        B("즉 경로와 횟수는 약효만이 아니라 환자의 사정으로도 정한다.", [35, 36, 37, 38]),
        CHK("하루 1번 복용하는 항균제는 바쁜 환자의 순응도를 높여 치료 농도 유지에 유리하다.", "O", [37]),
    ]))
    top.append(EX("주사(IV)가 경구(PO)보다 항상 효과적인가?", CH3,
                  "아니다. 입원 환자라도 주사가 늘 낫지는 않다. 장 안의 감염(CDI)에는 흡수되지 않는 경구 vancomycin이 맞다.", [
        P("주사가 늘 낫지는 않다. IV는 100% 들어가지만, 감염이 어디에 있느냐에 따라 맞는 경로가 다르다.", [39]),
        P("장 안의 감염이 대표적인 예외다. Clostridium difficile 감염(CDI)과 amebic colitis에는 장관 안에서 작용하는 약(luminal agent)을 쓴다.", [39]),
        P("**경구 vancomycin은 흡수되지 않는 luminal agent다.** 그래서 CDI에는 IV vancomycin이 아니라 경구 vancomycin이 맞다.", [39]),
        CHK("CDI에서 경구 vancomycin은 흡수되지 않고 장관 안에서 작용한다.", "O", [39]),
    ]))
    top.append(EX("시간 의존성과 농도 의존성 살균(PK/PD)은 용법을 어떻게 정하나?", CH4,
                  "시간 의존성은 MIC 위에 오래 머물수록, 농도 의존성은 잠깐이라도 높이 올라갈수록 유리하다.", [
        P("3장에서 약이 닿는 길을 정했다. 이제 간격과 용량을 정하는 원리를 본다. {r|교수님은 이 PK/PD 슬라이드가 중요하다고 했다.} 핵심은 혈중 농도 곡선을 MIC와 비교하는 것이다. "
          "MIC 위에 얼마나 오래 있나, 얼마나 높이 올라가나에 따라 약의 작용 방식이 갈린다.", [40, 44]),
        P("{b|시간 의존성(time-dependent killing)은 MIC 이상으로 유지되는 시간이 길수록 유리하다}. "
          "대표는 β-lactam이다. 그럼 농도를 오래 유지해야 하므로 저용량을 짧은 간격으로 준다.", [41] + PAD_PKPD),
        P("{b|농도 의존성(concentration-dependent killing)은 잠깐이라도 고농도로 노출될수록 유리하다}. "
          "{b|대표는 aminoglycoside다. 고용량을 긴 간격으로 주어 최고 농도를 높인다. 그래서 투약 간격도 중요한 고려사항이다}.",
          [41] + PAD_PKPD),
        P("{b|PAE(post-antibiotic effect)는 농도가 MIC 아래로 떨어진 뒤에도 항균 효과가 지속되는 것이다}. "
          "농도가 늘 MIC 위에 있을 수는 없다. 그래도 PAE가 있으면 효과가 바로 0이 되지 않는다.", [42] + PAD_PKPD),
        FS("f3_time_dep.png", "Time-dependent antibiotics", "그림이 담은 사실: 시간 의존성", [
            "볼 지표는 T>MIC(MIC 위에 있는 시간)다.",
            "PAE는 작거나 중간이다.",
        ], [41, 42]),
        FS("f4_conc_dep.png", "Concentration-dependent antibiotics", "그림이 담은 사실: 농도 의존성", [
            "볼 지표는 Cmax/MIC와 AUC/MIC다.",
            "PAE가 길다.",
        ], [41, 42]),
        P("지표는 세 가지다. 약마다 무엇을 보는지 다르다.", [43]),
        B("**T>MIC**: MIC 위에 있는 시간의 비율이다. 투여 간격 24시간 중 16시간이 MIC 위면 16/24다.", [43]),
        B("**Cmax/MIC**: 최고 농도를 MIC로 나눈다. MIC가 약 5, Cmax가 약 15면 3이다.", [43]),
        B("**AUC/MIC**: 곡선 아래 면적(area under the curve)을 MIC로 나눈다. ‘시간 의존성이 섞인 농도 의존성’으로 따로 나누기도 한다.", [43]),
        FS("f5_pkpd_index.png", "PK/PD 지표와 해당 약물", "그림이 담은 사실: 지표별 약물", [
            "Cmax/MIC: aminoglycoside, fluoroquinolone.",
            "AUC/MIC: vancomycin, azithromycin, fluoroquinolone, aminoglycoside, tigecycline, linezolid.",
            "T>MIC: β-lactam, vancomycin, macrolide, clindamycin.",
        ], [43, 44]),
        CONCEPT_V("시간 의존성 vs 농도 의존성", [
            "**시간 의존성**: {b|오래 유지할수록 유리}. β-lactam. 적게, 자주",
            "**농도 의존성**: {b|잠깐이라도 높을수록 유리}. {b|aminoglycoside}. {b|많이, 드물게}",
            "**PAE**: {b|MIC 아래로 떨어진 뒤에도 효과가 지속}. 농도 의존성에서 길다(그림)",
        ], [41, 42] + PAD_PKPD,
            diagram=DIA("compare", [("시간 의존성", "teal", ["오래 유지", "β-lactam", "적게, 자주", "T>MIC"]),
                                    ("농도 의존성", "salmon", ["높이 올림", "aminoglycoside", "많이, 드물게", "Cmax/MIC"])],
                        row_labels=["목표", "대표", "투여", "지표"]),
            caption="시간 의존성 vs 농도 의존성"),
        CHK("Aminoglycoside는 time-dependent killing을 하는 대표 약물이다.", "X", [41], why="농도 의존성이다."),
        CHK("PAE는 항균제 농도가 MIC 이상일 때만 나타나는 효과이다.", "X", [42], why="MIC 아래로 떨어진 뒤에도 지속되는 효과다."),
    ], refs=PAD_PKPD))
    top.append(LS("투여 경로는 경구와 주사 중 무엇을 기본으로 정하나?", CH4, [
        B("PK/PD로 간격과 용량을 정했으면 마지막으로 경로를 확인한다. 원칙은 경구가 기본이고, 주사는 경구로 안 될 때 쓴다.", [45]),
        COLS("경로를 고르는 원칙은 다음과 같다.", [
            ("경구(PO)가 기본", "teal", ["가장 선호되는 경로다. 특히 외래", "스스로 먹을 수 있다", "중증은 IV로 시작해도 빨리 **IV → PO switch**"]),
            ("주사가 필요할 때", "salmon", ["경구로 충분한 혈장 농도를 못 얻을 때 (흡수 시간, bioavailability)", "중증 감염, 패혈증처럼 급할 때", "더 높은 혈장 농도가 필요할 때"]),
        ], [45, 46]),
        B("즉 경로는 ‘더 센 것’을 고르는 일이 아니라, 약이 필요한 곳에 필요한 농도로 가는 길을 고르는 일이다.", [39, 45, 46]),
        CHK("중증 환자도 가능하면 빨리 IV에서 경구로 바꾼다(IV → PO switch).", "O", [45]),
    ]))

    top.append(EX("항균제 병용요법(combination therapy)은 단일 제제보다 항상 나은가?", CH4,
                  "아니다. 단일 제제가 원칙이다. 근거가 뚜렷한 이득이 있을 때만 병용한다.", [
        P("병용이 늘 나은 것은 아니다. 약끼리 상호작용하면 효과가 오히려 줄 수 있다.", [47, 48]),
        COLS("병용하는 경우와 주의할 점은 다음과 같다.", [
            ("병용이 유리한 경우", "teal", ["교대 감염", "내성균 발현 억제", "AIDS 치료(항균제는 아님), 특정 폐렴", "항결핵제(당연히 병용)", "요로 감염의 TMP/SMX(박트림)"]),
            ("주의할 점", "salmon", ["병용 약 사이의 PK, PD 상호작용", "한 약이 다른 약의 대사에 영향 → 효과 감소, 부작용 증가", "근거가 명확한 병용만 고른다", "‘예전에 써 보니 좋더라’ 식은 피한다"]),
        ], [47, 48]),
        P("따라서 병용 약이 늘수록 상호작용 → 치료 효과 감소로 이어질 수 있다.", [48]),
        P("병용요법을 흔히 cocktail therapy라고 하지만 정식 표현은 **combination therapy**다. "
          "칵테일이 단일한 술보다 늘 낫지 않듯 병용도 늘 낫지 않다.", [49]),
        P("병용은 개원가뿐 아니라 대학병원에서도 남용된다. 사회가 고령화될수록 더 중요한 문제가 된다.", [50]),
        CHK("항균제는 여러 개를 병용할수록 효과가 더해진다.", "X", [48], why="상호작용으로 효과가 줄 수 있다."),
    ]))

    # ================================================================ QUIZ
    top.append(T("QUIZ", CH4, [], [
        _st("quiz", "65세 남성이 뇌종양 수술 뒤 중환자실에 입원 중 세균성 뇌수막염이 의심된다. 가장 알맞은 경험적 항균제 조합은?", [13],
            options=["① ceftriaxone + vancomycin + ampicillin", "② meropenem + vancomycin", "③ 경구 vancomycin 단독",
                     "④ aminoglycoside 흡입 치료", "⑤ 감수성 결과가 나올 때까지 항균제를 쓰지 않는다"],
            answer="② meropenem + vancomycin",
            explanations=["① 건강하던 사람의 community acquired 뇌수막염 조합이다", "② 병원 감염이므로 Pseudomonas를 고려한다 (정답)",
                          "③ 경구 vancomycin은 흡수되지 않는 luminal agent다", "④ 흡입 치료는 호흡기 감염의 선택지다",
                          "⑤ 경험적 치료는 감수성 검사와 동시에 시작한다"]),
        _st("quiz", "투여 경로에 대한 설명으로 옳지 않은 것은?", [39, 45, 46],
            options=["① 외래에서는 경구 투여가 가장 선호된다", "② 중증 환자도 가능하면 빨리 IV → PO로 바꾼다",
                     "③ 입원 환자에게는 주사가 항상 더 효과적이다", "④ 경구로 적정 혈장 농도를 얻을 수 없으면 주사를 고려한다",
                     "⑤ 패혈증처럼 긴급한 경우에는 비경구 투여를 우선한다"],
            answer="③ 입원 환자에게는 주사가 항상 더 효과적이다",
            explanations=["① 스스로 먹을 수 있다", "② 가능한 한 빨리 경구로 바꾸는 것이 유리하다",
                          "③ 주사가 늘 낫지는 않다. CDI에는 경구 vancomycin을 쓴다 (정답)", "④ 흡수, bioavailability 문제 때문이다",
                          "⑤ 긴급한 항균 치료가 필요하다"]),
    ]))
    return top


if __name__ == "__main__":
    import sys

    topics = build()
    for t in topics:
        t.slide_numbers = sorted({r for sts in t.sections.values() for st in sts for r in st.slide_refs})
    dump(topics, sys.stdout)
