"""Mixed-style note for 'Clinical Therapeutics: 중환자와 항균제' (임상약리, 2026-08-19 2교시, 한성필 교수님) - layout v2 (L16).

Written TOP-DOWN from outputs/abx/storyline.md (4 chapters by content, § order = script paragraph order), and laid out
the way the human MOM note reads (outputs/abx/review_vs_MOM.md section 8):
  A  list § = table (`ROWS`: label | one line -> conclusion), not bullets
  B  one anchor per page: the big slide picture first (`FIG`), no bullets that repeat the picture; `new_page` on anchor §
  C  핵심 답 = one light line; 개념 Check boxes collected at the end of each chapter (template checks_where: chapter)
  D  10.5 pt text (template)
  E  the lecturer's own units: yellow `[질문]` box + `A.` line (`QA`), 질문1 / 역질문1-3 / 질문2
  the same exam tables appear twice in the SAME form (front page and body)

Inputs (nothing else is used):
  * script   inputs/abx_script.txt  (52 paragraphs; live lecture + recorded video of 조성연·한성필 교수님)
  * pictures inputs/abx_figs/       (slide images taken from the 정리본 PDF - pictures only; f34 = f3 + f4 side by side)
  * PAD      inputs/abx_pad.pdf     (6 questions: 20/19/18학번 x 2) - used ONLY to decide what is blue.
Run:  python -m examples.abx_note > outputs/abx/note_authored.json
"""
from app.models import Arrow, Diagram, Group, Statement
from examples.authoring import T, dump
from examples.stemcell_note import CHK, MEMO, _st

FIG_DIR = "inputs/abx_figs/"
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


def QA(label, question, answers, g=()):
    """The lecturer's own (역)질문 in a yellow box + the answer lines 'A. ...' (E)."""
    return Statement(text=question, kind="qa", left_title=label, left=list(answers), slide_refs=list(g))


def ROWS(rows, col_titles=(), col_widths=(), g=()):
    """Table: [[label, cell, ...], ...]; "\\n" = new line inside a cell, '→' lines show the conclusion (A)."""
    return Statement(text="", kind="rows", rows=[list(r) for r in rows], col_titles=list(col_titles),
                     col_widths=list(col_widths), slide_refs=list(g))


def FIG(img, caption, g=()):
    """Big slide picture (B). The caption tells what it is; what it shows is written in the table / sentences."""
    return Statement(text=caption, kind="figure", image=FIG_DIR + img, slide_refs=list(g))


def DFULL(caption, diagram, g=()):
    return Statement(text=caption, kind="diagram", slide_refs=list(g), diagram=diagram)


def EX(heading, chapter, answer, body, refs=(), new_page=False):
    """explain §: question heading + (핵심 답 line | the lecturer's QA box) + connected paragraphs."""
    t = T(heading, chapter, [], body, basics_title="핵심 답", basics=[answer] if answer else [], style="explain")
    t.basics_refs, t.new_page = list(refs), new_page
    return t


def LS(heading, chapter, body, new_page=False):
    t = T(heading, chapter, [], body, style="list")
    t.new_page = new_page
    return t


# ---- the two exam tables: SAME object on the front page and in the body (same form, twice)
QUAD = ROWS([
    ["{b|community acquired}", "{b|competent}", "{b|건강했던 18세 남학생, 두통, 구토, 고열, 경부강직 (응급실)}\n{b|→ 병원 밖에서 감염, 면역 정상}"],
    ["{b|nosocomial}", "{b|competent}", "{b|18세, 외상성 경막하 출혈로 개두술, 7일째 두통, 고열, 경부강직}\n{b|→ 침습적 수술 뒤 병원 감염, 젊어서 면역 결함 없음}"],
    ["nosocomial", "compromised", "AML, BMT D12, 백혈구 200/mm³, 39 °C, 두통, 구토, 경부강직\n→ 면역저하 환자의 병원 감염 (슬라이드 사례)"],
], col_titles=["획득 경로", "면역 상태", "사례와 의미"], col_widths=[3.6, 2.9, 10.9], g=[14] + PAD_QUAD)

PKPD = ROWS([
    ["유리한 것", "{b|MIC 이상 유지 시간이 길수록}", "{b|잠깐이라도 고농도로 노출될수록}"],
    ["용법", "저용량, 짧은 간격", "{b|고용량, 긴 간격 (투약 간격도 고려)}"],
    ["대표 약물", "β-lactam\n그림: vancomycin, macrolide, clindamycin", "{b|aminoglycoside}\n그림: fluoroquinolone"],
    ["지표", "T>MIC", "Cmax/MIC, AUC/MIC"],
    ["PAE", "{b|MIC 이하로 떨어진 뒤에도 항균 효과가 지속되는 것}\n그림: 작거나 중간", "그림: 길다"],
], col_titles=["", "시간 의존성 (time-dependent)", "농도 의존성 (concentration-dependent)"], col_widths=[2.6, 7.4, 7.4],
    g=[41, 42, 43, 44] + PAD_PKPD)


def build():
    top = []

    # ================================================================ 앞쪽: 기출 두 유형 표 + 전체 지도
    top.append(T("요약 정리 · 시험 정리", "", [], [
        P("기출 6문항은 두 유형뿐이다. 아래 두 표가 그 두 유형이고, 본문에 같은 표가 근거와 함께 다시 나온다.", [2]),
        DFULL("강의 전체 지도 — 항균제 선택에서 용법과 병용까지, 강의 순서대로", Diagram(
            kind="tree", root="항균제 처방", groups=[
                Group(title="1. 항균제 선택 원칙", color="teal", items=["사용 목적 4가지", "감염 장기", "환자: 4사분면 (기출)"]),
                Group(title="2. 경험적 → 표적 치료", color="blue", items=["감수성 검사", "정균제 vs 살균제", "환자 인자"]),
                Group(title="3. 용량, 용법, 투여 경로", color="salmon", items=["용법의 근거", "기관별, 환자별 경로", "주사 vs 경구"]),
                Group(title="4. PK/PD, 경로 원칙, 병용", color="amber", items=["시간 vs 농도 의존 (기출)", "경구가 기본", "병용은 근거 있을 때만"]),
            ]), [7, 10, 18, 29, 40, 47]),
        QUAD,
        PKPD,
    ], role="front"))

    # ================================================================ 1장 항균제 선택 원칙 (¶1-17)
    top.append(EX("항균제 선택은 사용 목적, 감염 장기, 환자 중 무엇에서 시작하나?", CH1, None, [
        QA("질문1", "항균제의 종류가 많은데, 감염 질환에 따라 항균제가 선택되는 원칙을 알고 싶습니다.",
           ["스펙트럼(어떤 균을 커버하는가)만 외워서는 부족하고, 사용 목적, 감염 장기, 환자 세 가지를 먼저 고려한다."], [7, 8, 10]),
        MEMO("수업은 녹화 문답 영상(감염내과 조성연 교수님, 한성필 교수님)을 틀고 교수님이 덧붙이는 방식이었습니다. "
             "영상 재생 준비, 휴식과 출석 안내는 생략했습니다.", [4, 5, 6, 9, 16, 17, 28, 51, 52]),
        P("이 강의는 영상의 질문 두 개로 짜여 있다. 질문1은 항균제 선택 원칙이고, 질문2는 용량, 용법, 투여 경로의 결정이다. "
          "학습목표도 목적에 따른 치료 전략, 용량과 용법의 결정 인자, 환자 개인차에 따른 고려점의 같은 순서다. "
          "{g|감염내과와 임상약리과는 항균제 PK/PD 분야에서 함께 연구를 많이 해 왔고, 미충족 의료 수요도 목표에 있었지만 이번 시간에는 다루지 않았다.}",
          [1, 2, 3, 29]),
        P("그래서 선택은 세 가지 질문을 차례로 던지는 일이다. 왜 쓰는가(목적), 어느 장기의 감염인가, 어떤 환자인가. 아래 세 소절이 이 순서로 하나씩 다룬다.", [10]),
        CHK("항균제 선택의 첫 단계는 항균제의 스펙트럼을 외우는 것이다.", "X", [8, 10], why="목적, 장기, 환자를 먼저 묻는다."),
    ], new_page=True))
    top.append(LS("항균제 사용 목적 4가지(예방적, 선제적, 경험적, 표적 치료)는 어떻게 나누나?", CH1, [
        QA("역질문1", "항균제를 쓰는 목적이 무엇인가?", ["목적은 감염, 증상, 원인균이 얼마나 확인되었는지로 네 가지로 나눈다."], [11]),
        ROWS([
            ["감염", "없음", "—", "모름", "확인"],
            ["증상", "없음", "아직 없음", "있음 (예: 열)", "있음"],
            ["원인균", "—", "—", "아직 모름", "확인됨"],
            ["특징", "수술 전 예방적 항균제", "—", "**가장 많이 쓴다**", "균을 겨냥해 바꾼다"],
        ], col_titles=["", "예방적 (prophylactic)", "선제적 (pre-emptive)", "경험적 (empiric)", "표적 (targeted)"],
            col_widths=[2.2, 3.9, 3.7, 3.8, 3.8], g=[11]),
        B("즉 같은 항균제라도 감염, 증상, 원인균이 어디까지 확인되었는지에 따라 쓰는 목적이 달라진다. {g|선제적 치료는 소리가 작아 설명이 짧았다.}", [11]),
        CHK("원인균이 확인되기 전에 증상을 근거로 시작하는 치료는 경험적 치료이다.", "O", [11]),
    ]))
    top.append(EX("감염 장기(CNS 등)는 항균제 선택에 왜 중요한가?", CH1, None, [
        QA("역질문2", "어느 장기의 감염이 의심되는가?",
           ["증상으로 어느 장기인지 추론하고, 그 장기에 흔한 균과 약이 닿는지를 함께 본다. 예: CNS 감염이면 BBB를 잘 통과하는 항균제."], [12]),
        P("장기를 알면 흔한 균을 떠올릴 수 있고, 약이 그 장기에 닿는지도 따질 수 있다. 두통과 발열이면 CNS 감염(뇌수막염)을 의심하고, "
          "그러면 BBB(혈액뇌장벽)를 잘 통과하는 약을 고른다. 다만 같은 장기의 감염이라도 환자가 다르면 약이 달라지고, 그 기준이 다음 소절의 4사분면이다.", [12, 13]),
        CHK("CNS 감염에서는 BBB를 잘 통과하는 항균제를 고른다.", "O", [12]),
    ]))
    top.append(EX("획득 경로(community acquired, nosocomial)와 면역 상태(competent, compromised)는 항균제 선택을 어떻게 바꾸나?", CH1, None, [
        QA("역질문3", "어떤 환자에게, 어떤 환경에서 사용하는가?",
           ["같은 감염, 같은 증상이라도 환자를 어떤 맥락에서 만나느냐가 치료 전략을 정한다. 획득 경로와 면역 상태의 4사분면으로 나눈다."], [13, 14, 15]),
        P("{r|교수님은 이 4사분면 슬라이드가 굉장히 중요하고, 여기서 시험 문제가 나왔다고 했다.}", [14, 15]),
        FIG("f1_quadrant.png", "생각해야 될 원인균? 획득 경로 × 면역 4사분면 (슬라이드)", [14]),
        P("{b|환자는 원인균을 얻은 곳이 community acquired(지역사회 획득)인지 nosocomial(병원 감염)인지, 면역이 competent(정상)인지 compromised(저하)인지로 나눈다}.",
          [14] + PAD_QUAD),
        QUAD,
        P("이 원리를 약 선택에 대 보자. 같은 65세 남성이 발열과 의식저하로 세균성 뇌수막염이 의심되어도, 획득 경로에 따라 약이 달라진다.", [13]),
        ROWS([
            ["community acquired", "건강하던 사람", "ceftriaxone + vancomycin\n50세 이상이므로 Listeria를 커버하는 ampicillin 추가"],
            ["hospital-acquired", "뇌종양 수술 뒤 중환자실", "Pseudomonas(녹농균)를 고려\nceftriaxone 대신 ceftazidime 또는 meropenem + vancomycin"],
        ], col_titles=["획득 경로", "환자", "항균제 선택"], col_widths=[3.6, 4.6, 9.2], g=[13]),
        P("따라서 감염 장소가 생각할 균을, 생각할 균이 약을 정한다. 만나는 장소(입원실, ICU, 개원 진료실)가 그 맥락을 알려 준다.", [13, 15]),
        CHK("개두술 7일 뒤 뇌수막염 증상을 보이는 18세 남성은 community acquired / compromised로 평가한다.", "X", [14],
            why="nosocomial / competent이다."),
    ], refs=PAD_QUAD, new_page=True))

    # ================================================================ 2장 경험적 -> 표적 (¶18-27)
    top.append(EX("경험적 치료(empiric)는 언제 표적 치료(targeted)로 바뀌나?", CH2,
                  "감수성 검사로 균과 감수성이 확인되면 바꾼다. 바꿀지 판단할 때 가장 중요한 것은 치료 반응이다.", [
        P("경험적 치료는 원인균을 모르는 채 시작한다. 그럼 균이 확인된 뒤에는 어떻게 바꿀까? "
          "치료는 환자 평가에서 증상과 징후를 확인하는 데서 시작해, 경험적 치료, 감수성 검사, 표적 치료, 모니터링의 다섯 단계로 이어진다.", [18]),
        DFULL("항균제 치료의 흐름", Diagram(kind="flow", size="full", groups=[
            Group(title="환자 평가", color="gray", items=["증상과 징후 확인"]),
            Group(title="경험적 치료", color="salmon", items=["initial empirical therapy"]),
            Group(title="감수성 검사", color="amber", items=["치료 전 검체로", "균 동정, MIC"]),
            Group(title="표적 치료", color="teal", items=["definitive therapy", "약, 용량, 용법 조정"]),
            Group(title="모니터링", color="blue", items=["치료 반응 확인", "→ 치료 완료"]),
        ], arrows=[Arrow(src=0, dst=1, label=""), Arrow(src=1, dst=2, label="동시에"),
                   Arrow(src=2, dst=3, label=""), Arrow(src=3, dst=4, label="")]), [18, 19]),
        P("경험적 치료를 시작하면서, 치료 전에 채취한 혈액 등의 검체로 감수성 검사(susceptibility test)를 함께 한다. "
          "이 검사로 균이 동정되고 항균제별 감수성과 MIC(Minimum Inhibitory Concentration, 최소 억제 농도)가 나오면, "
          "그 결과를 보고 지금 환자에게 가장 알맞은 약으로 바꾸는 것이 표적 치료(definitive therapy)다. "
          "다만 경험적 치료가 이미 적절하다면 그대로 유지하는 것이 가장 좋고, 바꿀지는 다음 다섯 가지로 판단한다.", [19, 20, 21]),
        B("감염 부위, 원인균, 감수성 패턴, 숙주(환자) 인자, {r|치료 반응(가장 중요)}", [21]),
        P("{g|지극히 상식적인 흐름이지만 실제로 지켜지지 않는 경우가 있어 기초부터 설명했다.}", [19]),
        CHK("감수성 검사는 표적 치료로 바꾼 뒤에 검체를 채취해 시행한다.", "X", [19], why="치료 전 검체로 경험적 치료와 동시에 한다."),
    ], new_page=True))
    top.append(EX("정균제(bacteriostatic)와 살균제(bactericidal)는 언제 쓰나?", CH2,
                  "면역이 약하거나 중증 감염이면 살균제를 쓴다.", [
        ROWS([
            ["작용", "세균의 증식을 억제", "세균을 사멸"],
            ["치유는 누가", "최종 치료는 숙주의 면역계에 기댄다", "그래서 면역저하 환자(immunocompromised patient), 중증 감염에서 주로 선택"],
            ["그림 (균 수)", "유지 (예: chloramphenicol)", "급감 (예: penicillin)"],
        ], col_titles=["", "정균제", "살균제"], col_widths=[2.8, 6.8, 7.8], g=[22, 23]),
        FIG("f2_static_cidal.png", "Bacteriostatic vs bactericidal agent: 약을 넣은 뒤 살아 있는 균 수 (슬라이드)", [23]),
        P("다만 정균과 살균은 항균제의 농도나 균주에 따라 달라질 수 있는 상대적인 개념이다. "
          "그리고 면역 상태는 살균제를 고르는 기준이면서 용량을 바꾸는 환자 인자이기도 해서, 다음에 환자 인자를 본다.", [22, 23, 24]),
        CHK("면역억제 환자에서는 정균제보다 살균제를 사용해야 한다.", "O", [22, 24]),
    ]))
    top.append(LS("환자 인자(면역, 신·간기능, 저관류, 연령)는 용량을 어떻게 바꾸나?", CH2, [
        B("환자 인자는 네 가지다. 앞에서 본 면역 상태가 첫째다.", [24]),
        ROWS([
            ["면역 상태", "중증 당뇨, 악성 종양, 면역억제제 → 감염이 무거워짐 → 고용량이나 장기간 투여\n대가: 항균제 자체의 독성이 커지므로 용법을 주의해 정한다\n면역억제 환자는 정균제가 어렵고 살균제를 쓴다"],
            ["신기능, 간기능 저하", "그 장기로 제거되는 약의 혈중 농도 ↑ → 독성 위험 ↑\n일부 약은 GFR이나 간기능에 따른 용법 제한 기준이 있다\n검사로도 확인하지만 외래에서는 병력 청취(history taking)가 중요하다"],
            ["저관류 (hypoperfusion)", "감염 부위의 혈류 ↓ → 약이 균에 충분히 닿지 못함 → 다른 방법을 고려"],
            ["연령", "신생아와 노인은 용법이 크게 달라진다\n신생아는 대사 효소 기능이 미숙한 경우가 많다"],
        ], g=[24, 25, 26, 27]),
        B("즉 같은 감염이라도 면역, 제거 장기, 혈류, 나이에 따라 용량이 달라진다.", [24, 25, 26, 27]),
        CHK("신기능이 떨어진 환자에서는 신장으로 제거되는 항균제의 혈중 농도가 낮아진다.", "X", [25], why="혈중 농도가 올라가 독성 위험이 커진다."),
    ]))

    # ================================================================ 3장 용량, 용법, 투여 경로 (¶28-39)
    top.append(EX("정해진 항균제 용법은 무엇을 근거로 하나?", CH3, None, [
        QA("질문2", "주사제도 있고 경구제도 있고, 항균제의 용량, 용법, 투여 경로는 어떻게 결정되나요?",
           ["대부분의 항균제는 용량과 용법이 이미 정해져 있고, 그 근거는 표적 균주의 MIC 프로파일, 반복 투여 때의 PK/PD 자료, 그리고 임상시험이다.",
            "그래도 고를 것이 남는다. 같은 3세대 cephalosporin도 하루 한 번 주는 약과 두 번 주는 약이 있다."], [29, 30, 31]),
        P("1장에서 본 감염 장기와 환자 요인을 이번에는 용량, 용법, 투여 경로를 정하는 눈으로 다시 본다. "
          "{r|교수님은 영상의 두 번째 질문(질문2)에서 실제 중요한 내용이 많이 나왔다고 했다.} "
          "질문2의 답은 세 가지다. 어느 기관의 감염인가, 어떤 환자인가(외래, 입원, 중환자), 그리고 IV와 PO(경구) 중 무엇인가. "
          "셋째는 오랫동안 고민되어 온 문제다. 아래 세 소절이 이 순서다.", [32, 51]),
        CHK("항균제의 표준 용법은 표적 균주의 MIC와 PK/PD 자료, 임상시험을 근거로 정해졌다.", "O", [31]),
    ], new_page=True))
    top.append(LS("감염 기관(CNS, 안구, 뼈·관절, 호흡기)에 따라 투여 경로는 어떻게 달라지나?", CH3, [
        QA("역질문1", "어떤 기관에 발생한 감염증인가?", ["약이 균이 있는 곳에 충분히 닿아야 하므로 기관마다 약과 경로를 바꾼다."], [32, 33, 34]),
        ROWS([
            ["CNS", "BBB를 잘 통과하는 ceftriaxone, vancomycin을 CNS dose로\n드문 감염(cryptococcal meningitis 등)은 척수강 내 투여(intrathecal therapy)로 CSF에 바로 넣기도 한다"],
            ["안구", "IV로는 도달이 의심스럽다 → 유리체강 내 주사(intravitreal injection)"],
            ["뼈, 관절", "혈관 분포가 풍부한 기관보다 약이 덜 닿을 수 있다 (bone and joint infection)"],
            ["호흡기", "흡입 치료(inhalation therapy): 입자가 large airway까지만 가는지, alveoli(폐포)까지 가는지가 문제다. 폐렴이면 alveoli까지 가야 한다\n일반 nebulizer와 aerosol generator 중에서 고른다"],
            ["분포 (distribution)", "tigecycline: 조직으로 잘 가지만 혈중 농도는 낮다\naminoglycoside: 혈중보다 요로(urinary tract)에서 훨씬 높다"],
        ], g=[33, 34]),
        B("즉 약은 혈중이 아니라 균이 있는 곳에서 충분한 농도여야 한다.", [33, 34]),
        CHK("Aminoglycoside는 요로에서 혈중보다 훨씬 높은 농도로 존재한다.", "O", [34]),
    ]))
    top.append(LS("환자 사정(외래·입원, 혈관, 흡수, 순응도)에 따라 투여 경로는 어떻게 달라지나?", CH3, [
        QA("역질문2", "어떤 환자에게 사용하는가?", ["같은 기관의 감염이라도 환자가 실제로 맞고 먹을 수 있어야 한다."], [35]),
        ROWS([
            ["외래 vs 입원", "외래는 경구가 기본이다. 그래도 하루 한 번 주사실에서 IV를 맞는 경우가 있다\n입원 환자도 재원 기간을 줄이려 일찍 퇴원시키기도 한다"],
            ["혈관 상태", "하루 3~4번 맞거나 sodium이 많은 nafcillin을 쓰면 정맥염(phlebitis)이 잘 생긴다\nnafcillin, vancomycin은 말초 정맥관(peripheral line)으로 맞기 힘든 경우가 많다"],
            ["경구 섭취, 흡수", "설사가 계속되거나 GI bleeding이 있으면 경구약의 효과(efficacy)를 기대하기 어렵다\n동반 질환도 함께 본다"],
            ["순응도 (compliance)", "하루 3~4번 챙기기 힘든 바쁜 환자에게는 하루 1번 약이 낫다\n먹다 안 먹다 하면 치료 농도(therapeutic level)가 떨어진다"],
            ["생활 패턴", "밤낮이 바뀐 환자(예: 일부 HIV 감염인)는 하루 1번 약을 자기 전에 먹게 한다\n식후 복용이 꼭 필요한 약이 아닐 때 가능하다"],
        ], g=[35, 36, 37, 38]),
        B("즉 경로와 횟수는 약효만이 아니라 환자의 사정으로도 정한다.", [35, 36, 37, 38]),
        CHK("하루 1번 복용하는 항균제는 바쁜 환자의 순응도를 높여 치료 농도 유지에 유리하다.", "O", [37]),
    ]))
    top.append(EX("주사(IV)가 경구(PO)보다 항상 효과적인가?", CH3, None, [
        QA("역질문3", "주사제가 경구제보다 효과가 우수한가?",
           ["입원 환자에게는 주사가 가장 약효가 빠르다는 고정관념이 있지만 항상 그렇지는 않고, 환자의 상태에 따라 접근이 달라진다."], [39]),
        P("IV는 100% 들어가지만, 맞는 경로는 감염이 어디에 있느냐에 따라 다르다. 대표적인 예외가 장 안의 감염이다. "
          "Clostridium difficile 감염(CDI)과 amebic colitis에는 흡수되지 않고 장관 안에 고농도로 머무는 luminal agent를 쓰고, 경구 vancomycin이 그런 약이다. "
          "그래서 CDI에는 IV vancomycin이 아니라 경구 vancomycin이 맞다.", [39]),
        CHK("CDI에서 경구 vancomycin은 흡수되지 않고 장관 안에서 작용한다.", "O", [39]),
    ]))

    # ================================================================ 4장 PK/PD, 경로 원칙, 병용 (¶40-52)
    top.append(EX("시간 의존성과 농도 의존성 살균(PK/PD)은 용법을 어떻게 정하나?", CH4,
                  "시간 의존성은 MIC 위에 오래 머물수록, 농도 의존성은 잠깐이라도 높이 올라갈수록 유리하다.", [
        P("3장에서 약이 닿는 길을 정했다. 이제 간격과 용량을 정하는 원리를 본다. {r|교수님은 이 PK/PD 슬라이드가 중요하다고 했다.} "
          "핵심은 혈중 농도 곡선을 MIC와 견주는 것이다. MIC 위에 얼마나 오래 있나, 얼마나 높이 올라가나에 따라 약의 작용 방식이 갈린다.", [40, 44]),
        PKPD,
        FIG("f34_time_conc.png", "Time-dependent antibiotics (왼쪽) / Concentration-dependent antibiotics (오른쪽) (슬라이드)", [41, 42]),
        P("{b|시간 의존성(time-dependent killing) 약은 MIC 위에 오래 머물수록 잘 들어 저용량을 짧은 간격으로 주고, "
          "농도 의존성(concentration-dependent killing) 약은 잠깐이라도 높이 올라갈수록 잘 들어 고용량을 긴 간격으로 준다.} "
          "{b|농도가 MIC 아래로 내려가도 항균 효과가 바로 0이 되지 않는 것이 PAE(post-antibiotic effect)다.}", [40, 41, 42] + PAD_PKPD),
        ROWS([
            ["T>MIC", "MIC 위에 있는 시간의 비율\n투여 간격 24시간 중 16시간이 MIC 위면 16/24", "β-lactam, vancomycin, macrolide, clindamycin"],
            ["Cmax/MIC", "최고 농도를 MIC로 나눈 값\nMIC가 약 5, Cmax가 약 15면 3", "aminoglycoside, fluoroquinolone"],
            ["AUC/MIC", "곡선 아래 면적(area under the curve)을 MIC로 나눈 값\n‘시간 의존성이 섞인 농도 의존성’으로 따로 나누기도 한다",
             "vancomycin, azithromycin, fluoroquinolone, aminoglycoside, tigecycline, linezolid"],
        ], col_titles=["지표", "의미", "해당 약물 (슬라이드)"], col_widths=[2.8, 7.4, 7.2], g=[43, 44]),
        FIG("f5_pkpd_index.png", "PK/PD 지표별 약물: Cmax/MIC, AUC/MIC, T>MIC (슬라이드)", [43, 44]),
        CHK("Aminoglycoside는 time-dependent killing을 하는 대표 약물이다.", "X", [41], why="농도 의존성이다."),
        CHK("PAE는 항균제 농도가 MIC 이상일 때만 나타나는 효과이다.", "X", [42], why="MIC 아래로 떨어진 뒤에도 지속되는 효과다."),
    ], refs=PAD_PKPD, new_page=True))
    top.append(LS("투여 경로는 경구와 주사 중 무엇을 기본으로 정하나?", CH4, [
        B("PK/PD로 간격과 용량을 정했으면 마지막으로 경로를 확인한다.", [45]),
        ROWS([
            ["경구(PO)가 기본", "가장 선호되는 경로다. 특히 외래에서 스스로 먹을 수 있다\n중증은 IV로 시작해도 가능하면 빨리 IV → PO switch"],
            ["주사(비경구)가 필요할 때", "경구로 충분한 혈장 농도를 못 얻을 때 (흡수 시간, bioavailability)\n중증 감염, 패혈증처럼 긴급할 때\n더 높은 혈장 농도가 필요할 때"],
        ], g=[45, 46]),
        B("즉 경로는 ‘더 센 것’을 고르는 일이 아니라, 약이 필요한 곳에 필요한 농도로 가는 길을 고르는 일이다.", [39, 45, 46]),
        CHK("중증 환자도 가능하면 빨리 IV에서 경구로 바꾼다(IV → PO switch).", "O", [45]),
    ]))
    top.append(EX("항균제 병용요법(combination therapy)은 단일 제제보다 항상 나은가?", CH4,
                  "아니다. 단일 제제가 원칙이고, 근거가 뚜렷한 이득이 있을 때만 병용한다.", [
        ROWS([
            ["원칙", "단일 제제 사용"],
            ["병용이 유리한 경우", "교대 감염\n내성균 발현 억제\nAIDS 치료(항균제는 아님), 특정 폐렴\n항결핵제(당연히 병용)\n요로 감염의 TMP/SMX(박트림)"],
            ["주의할 점", "병용 약 사이의 PK, PD 상호작용\n한 약이 다른 약의 대사에 영향 → 효과 감소, 부작용 증가"],
            ["선택 기준", "근거가 명확한 병용만 고른다\n‘예전에 써 보니 좋더라’ 식의 병용은 피한다"],
        ], g=[47, 48]),
        P("병용요법을 흔히 cocktail therapy라고 하지만 정식 표현은 combination therapy다. "
          "칵테일이 단일한 술보다 늘 낫지 않듯 병용도 늘 낫지 않고, 개원가뿐 아니라 대학병원에서도 남용되는 측면이 있다. "
          "사회가 고령화될수록 이 문제는 더 중요해진다.", [49, 50]),
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
