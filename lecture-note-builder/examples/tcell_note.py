"""Authored structured note (Topic JSON) for the 'T림프구에 대한 항원제시' script, written in the
`readable-note-organizer` style (all content kept, reorganised for understanding, not dictation).

Structure follows the excellent-example MOM: front pages (핵심 어휘, 요약 정리), then 2 chapters of
§ sections (기본정석 box, body, Advice / Reference), then an appendix. No 기출(PAD) section and no
practice questions; PAD is used only to justify BLUE text.

Authoring uses the old time-block numbers (1..21) for speech and 101.. for PAD questions; `_remap`
converts them to real script paragraph ids (¶) and PAD unit numbers, so the final note carries no
time-block structure.
Run:  python -m examples.tcell_note inputs/tcell_script.docx inputs/tcell_pad.pdf > outputs/tcell/note_authored.json
Markup: {r|red} {g|gray} {p|purple} {b|BLUE = 기출(PAD)에 나온 내용만} **bold**
"""
import json
import sys

from app.models import SlideTable, Statement, Topic


def P(text, *refs, **kw):
    return Statement(text=text, slide_refs=list(refs), origin="both", **kw)


def B(text, *refs, **kw):
    return P(text, *refs, kind="bullet", **kw)


def STAR(text, *refs):
    return P(text, *refs, kind="star")


def ADV(text, *refs):
    return P(text, *refs, kind="advice")


def REF(text, *refs):
    return P(text, *refs, kind="reference")


def T(heading, chapter, units, body, basics_title="", basics=(), tables=(), flags=(), role="body", basics_refs=()):
    return Topic(heading=heading, chapter=chapter, role=role, slide_numbers=list(units),
                 basics_title=basics_title, basics=list(basics), basics_refs=list(basics_refs), sections={"body": body},
                 tables=list(tables), review_flags=list(flags))


CH1 = "MHC and its function"
CH2 = "Unconventional T cell"


def build(unit_ids, exam_items=()):
    EX = {100 + i: it for i, it in enumerate(sorted(exam_items, key=lambda x: x.number), start=1)}
    top = []

    # ======================================================= 핵심 어휘
    top.append(T("핵심 어휘", "", [2, 3, 7, 9, 10, 11, 13, 14, 15, 18, 19], [
        P("강의 전체에 나오는 핵심 용어를 먼저 훑어보자. 뒤에서 하나씩 다시 나오니 가볍게 읽고 가도 좋다.", 2),
        B("**MHC / HLA** : 항원 조각(peptide)을 T세포에게 보여주는 분자 집단. 사람의 MHC는 HLA(human leukocyte antigen)라고 부른다.", 3),
        B("**Polygenic** : 한 사람이 서로 다른 MHC 유전자를 여러 개 가지고 있다. (한 개체 안의 다양성)", 2, 7),
        B("**Polymorphic** : 같은 유전자 자리에 집단 안에서 allele이 여러 형태로 존재한다. (집단 안의 다양성)", 2, 7),
        B("**Haplotype** : 한쪽 염색체 위에 모여서 함께 물려받는 MHC allele의 조합.", 2),
        B("**Codominant 발현** : 부모에게서 받은 두 allele이 모두 발현된다.", 7),
        B("**Gene conversion** : 서로 비슷한 서열의 유전자끼리 일부 정보가 바뀌는 현상. MHC 다양성의 기원으로 설명한다.", 9),
        B("**Anchor residue** : peptide가 MHC와 중요한 접촉을 하는 위치의 아미노산 (예: 2, 5, 8번 위치).", 10),
        B("**MHC restriction** : T세포는 peptide뿐 아니라 그것을 보여주는 MHC도 자기 것이어야 반응한다.", 11),
        B("**Alloresponse** : 다른 개체의 MHC에 대한 강한 T세포 반응 → 장기이식 거부반응. 같은 종 = allogeneic, 다른 종 = xenogeneic.", 13),
        B("**MLR (mixed lymphocyte reaction)** : MHC가 다른 두 개체의 림프구를 섞어 alloresponse를 관찰하는 고전적 실험.", 14),
        B("**Superantigen** : peptide 처리 없이 MHC class II와 TCR을 연결해 많은 T세포를 한꺼번에 활성화하는 물질. toxic shock syndrome 같은 문제를 일으킨다.", 15, 16),
        B("**Class Ib (nonclassical MHC class I)** : class I과 비슷하지만 다형성이 제한적이고 기능이 다양한 분자. HLA-E, F, G 등.", 18),
        B("**CD1** : peptide가 아니라 lipid / glycolipid 항원을 제시하는 MHC-like 분자.", 19),
        B("**Unconventional T cell** : 고전적 αβ T세포와 다른 방식으로 항원을 인식하는 T세포. γδ T cell, MAIT cell, invariant NKT cell.", 18),
    ], role="front"))

    # ======================================================= 요약 정리
    top.append(T("요약 정리", "", [1, 3, 4, 5, 7, 8, 9, 11, 12, 13, 15, 18, 19, 20], [
        STAR("Human MHC의 구조", 3, 4, 5),
        B("{r|6번 염색체}에 위치 (생쥐 H-2는 17번 염색체)", 3, 4),
        B("{b|Class I : HLA-A, B, C — 1개씩 / Class II : HLA-DR, DP, DQ — α·β chain 한 쌍씩 (1글자 = class I, 2글자 = class II)}", 3, 103),
        B("Class I region에 있지만 class Ib : {r|HLA-E, F, G} / DM, DO는 classical class II가 아님", 4, 5),
        STAR("Polymorphism & polygeny", 7, 8, 9),
        B("Polymorphism : 같은 자리의 allele 종류가 엄청 많다 / Polygeny : 동시에 발현되는 유전자 수가 많다 (공동우성)", 7),
        B("{b|Class I이 class II보다 다형성이 크다. class I은 B>A>C, class II는 DRB>DQB>DPB (α보다 β가 크다)}", 8, 101, 104, 105, 109),
        B("다양성은 {r|gene conversion}으로 얻어지고, peptide 결합 부위(class I α1·α2 / class II β1)에 몰려 있다", 9),
        STAR("MHC restriction", 11, 13, 15),
        B("T세포는 {r|자기 MHC + 자기에게 맞는 peptide}가 있어야 반응한다", 11),
        B("{b|restriction 적용 = adoptive T cell therapy / 예외 = alloresponse, transplantation, superantigen}", 12, 13, 15, 113, 116),
        B("예외 1) alloresponse : alloreactive T cell(전체의 1~10%)이 타인 MHC에 반응 — 장기이식 거부", 13),
        B("예외 2) superantigen : 박테리아·바이러스 유래, TCR과 MHC에 모두 결합해 비특이적으로 강하게 활성화", 15),
        STAR("Class Ib molecule", 18, 19, 20),
        B("Class I과 비슷하지만 {r|unconventional T cell과 NK cell}을 자극하는 역할", 18),
        B("{b|HLA-C(class I이면서 Ib, KIR로 NK 억제), HLA-E(NKG2A·C로 NK 억제, T cell에 항원 제시 안 함), MIC-A/B ↔ NKG2D}", 5, 18, 106, 107, 111, 112, 114, 115, 117),
        B("{r|CD1} : lipid 항원 제시 / FcRn : 엄마 → 태아 IgG 전달", 19),
        B("{b|CD1c → NKT cell(invariant NKT)을 활성화, CD1c가 제시하는 것은 lipid}", 19, 102),
        B("γδ T cell : 다양한 ligand를 인식 / MAIT : 선천면역과 적응면역 사이의 ‘transitional’ 세포", 20),
    ], role="front"))

    # ======================================================= Ch 1 · § 1
    top.append(T("MHC의 유전자 구성", CH1, [1, 2, 3, 4, 5, 6], [
        STAR("도입 : 왜 MHC는 여러 종류일까?", 1),
        P("먼저 **감염원 입장**에서 생각해보자. 자기 단백질 조각이 MHC에 얹혀 T세포에 보이면 면역계가 알아보기 때문에, 감염원은 MHC에 얹혀지는 경로를 피하고 싶어 한다. "
          "그런데 사람에게 MHC가 **단 한 종류**뿐이라면, 이 결합을 피하는 돌연변이가 하나만 생겨도 **모든 사람에게** 통하게 된다.", 1),
        P("실제로는 (1) 한 사람 안에서도 여러 MHC 유전자가 발현되고 (polygenic), (2) 사람들 사이에 allele 종류가 아주 다양하다 (polymorphic). "
          "{r|이 두 가지가 오늘 강의의 출발점}이다. 이번 장은 이 MHC 유전자가 어떻게 구성되어 있는지부터 본다.", 1),
        P("오늘의 순서 : ① 6번 염색체 MHC 영역 → ② 다양성과 항원 인식의 관계 → ③ MHC restriction과 예외(이식 반응, superantigen) → ④ HLA-E/F/G, CD1 같은 비전형적 분자. "
          "이름만 외우지 말고 ‘왜 다른 역할을 하는지’를 연결해서 이해해보자.", 2),
        STAR("용어부터 구분하자", 2),
        B("**Polygenic** : 한 개체가 서로 다른 MHC 유전자를 여러 개 가진다.", 2),
        B("**Polymorphic** : 같은 유전자 자리라도 집단 안에 allele이 여러 형태로 존재한다.", 2),
        B("**Haplotype** : 한쪽 염색체 위에 모여서 함께 물려받는 MHC allele의 조합.", 2),
        P("{r|Polygenic과 polymorphic을 혼동하면 뒤의 설명이 어려워진다.}", 2),
        STAR("인간 MHC의 유전자 구성", 3),
        P("사람의 MHC는 HLA라고 부르고 **6번 염색체**에 유전자가 밀집해 있다. 이 영역은 **class I / class II / class III**로 나누어 본다.", 3),
        B("**Class I** : HLA-A, HLA-B, HLA-C — 큰 α chain 1개 + β2-microglobulin이 결합한 구조. 교수님 표현으로 ‘다리 하나짜리’.", 3),
        B("**Class II** : HLA-DR, HLA-DP, HLA-DQ — α chain과 β chain이 짝을 이룬 구조. 교수님 표현으로 ‘다리 두 개짜리’.", 3),
        B("{b|기출 암기법 : 1글자(HLA-A, B, C)는 MHC class I, 2글자(HLA-DR, DP, DQ)는 MHC class II. ‘MHC class II에 해당하는 것은?’ → HLA-DR}", 3, 103),
        ADV("**유전자 영역**과 **실제 분자의 기능**을 구분하자. 문제가 ‘MHC class II **분자**’를 묻는지, ‘class II **region에 있는 유전자**’를 묻는지 꼭 확인해야 한다.", 3, 4),
        STAR("Class II region에는 DR · DQ · DP 말고도 있다", 4),
        P("class II region에는 앞 시간에 배운 **HLA-DM, HLA-DO**도 있다. 이들은 고전적인 항원제시 MHC class II와는 구분되지만 peptide editing 등 항원제시 과정의 조절에 관여한다. "
          "**TAP**처럼 항원 처리에 참여하는 분자도 이 MHC 유전자 영역 안에서 함께 볼 수 있다.", 4),
        STAR("사람(HLA) vs 생쥐(H-2)", 4),
        B("사람은 HLA, 생쥐는 **H-2**라고 부르고, 생쥐의 MHC 영역은 {r|17번 염색체}에 있다.", 3, 4),
        B("생쥐 class I : H-2D, H-2L 등 / class II : H-2A, H-2E 등.", 4),
        B("나중에 실험 그림을 읽을 때 필요하니 명칭 차이를 알아두자.", 4),
        STAR("MHC 영역은 생각보다 복잡하다", 5),
        P("확대한 유전자 지도는 위아래로 나뉘어 있지만 사실 **길게 연결된 하나의 영역**이다. class I, II만 정돈되어 모여 있는 것이 아니라, 그 사이사이에 **항원 가공과 제시에 관여하는 유전자**가 섞여 있다.", 5),
        B("항원 가공 관련 : **TAP**, **proteasome** 성분 / 염증 관련 : **TNF** 유전자.", 5),
        B("**Class I region** : 고전적 HLA-A, B, C 외에 **HLA-E, F, G** (나중에 class Ib로 다시 나온다).", 5),
        B("**Class III region** : **MIC-A, MIC-B** 등.", 5),
        B("{b|기출 : CD8에 바이러스 항원을 제시하는 것은 class I(HLA-A, B, C). HLA-E, F, G는 class I region에 있지만 class I의 역할을 한다고 보기 어렵다}", 5, 108),
        P("즉, 한 영역에 면역 관련 유전자가 함께 모여 있어서 **면역 반응이 함께 조절**될 수 있다.", 5),
        REF("**인터페론과 유전자 발현 조절** — 감염이 생기면 interferon α, β, γ가 MHC 관련 유전자의 발현을 조절하고, 그 결과 감염된 세포가 바이러스 단백질 유래 peptide를 제시할 기회가 늘어난다. "
            "class II에서는 **CIITA**(MHC class II 전사 조절의 핵심 co-activator)와 interferon-γ를 연결해서 기억하자. "
            "{g|모든 조절 경로를 외울 필요는 없고, 항원제시 분자만 따로 만들어지는 것이 아니라 가공과 제시에 필요한 여러 구성요소가 연동되어 조절된다는 큰 흐름만 잡으면 된다.}", 6),
    ], basics_title="MHC의 유전자 구성", basics=[
        "사람 MHC(HLA)는 6번 염색체에 있고, 한 영역 안에 class I / II / III 유전자가 모여 있다.",
        "{b|Class I = HLA-A, B, C (다리 하나짜리, 1글자) / Class II = HLA-DR, DP, DQ (α·β chain 쌍, 다리 두 개짜리, 2글자).}",
        "같은 영역에 DM, DO, TAP, proteasome, TNF, MIC-A/B가 함께 있고, HLA-E, F, G는 class I region에 있지만 class Ib이다.",
    ], basics_refs=[103], flags=["인터페론 관련 세부 내용은 원자료에서 일부가 PPT에만 있고 강의에서는 다루지 않았다고 표시됨 → 개념 연결 수준으로만 정리 (부록 참고)."]))

    # ======================================================= Ch 1 · § 2
    top.append(T("MHC의 특성", CH1, [7, 8, 9, 10], [
        STAR("Polymorphism & Polygeny", 7),
        P("두 단어는 **어느 수준의 다양성이냐**가 다르다.", 7),
        B("**Polymorphism(다형성)** : 같은 유전자 자리의 allele이 집단 전체에서 여러 형태로 존재한다. 예) HLA-B 하나에도 다양한 allele이 있다.", 7),
        B("**Polygeny** : 한 개인 안에 서로 다른 MHC 유전자(HLA-A, HLA-B ...)가 여러 개 있다.", 7),
        P("두 층위의 다양성이 **함께 작동**한다. 또 발현은 **codominant**여서 어머니·아버지에게서 받은 allele이 모두 발현되므로, 한 개체에서 실제 만들어지는 MHC 분자 종류가 늘어나고 "
          "한 사람의 MHC 조합이 다른 사람과 같기 어렵다.", 7),
        ADV("‘한 개체의 유전자 수가 많다’(polygeny)와 ‘집단 전체의 allele 종류가 많다’(polymorphism)를 바꿔 쓰지 말 것.", 7),
        STAR("다형성은 어디에 몰려 있을까?", 8),
        P("다형성은 모든 MHC 분자에서 똑같이 크지 않다. **고전적 class I의 다양성이 크고, class Ib는 상대적으로 제한적**이다.", 8),
        B("Class I에서는 **HLA-B, A, C** 순서로 다양성을 비교한다.", 8),
        B("Class II에서는 **DRB, DQB, DPB**를 비교하고, {r|다형성은 β chain 쪽에 집중}되어 있다.", 8),
        B("{b|기출 단골 : class I 다형성 B > A > C, class II DRB > DQB > DPB (DP < DQ < DR). 같은 유전자라도 α보다 β의 다양성이 훨씬 크다 → HLA-B / HLA-DR(DRB)가 정답으로 반복 출제} {r|Class I이 Class II보다 다형성이 크다는 점은 올해 직접 설명}", 8, 101, 104, 105, 109),
        P("왜 중요할까? 다형성은 특히 **peptide가 들어가는 결합 부위**와 관련되기 때문이다. 같은 감염원에서 나온 peptide라도 사람의 MHC 종류에 따라 **결합 가능성이 달라진다.**", 8),
        P("{g|allele의 개수는 시점과 자료에 따라 달라지므로 최신 개수를 외우기보다 상대적 경향과 기능을 먼저 이해하자.}", 8),
        STAR("Gene conversion — 이 다양성은 어디서 왔을까?", 9),
        P("이렇게 다양한 MHC는 **gene conversion**으로 생겼다고 설명한다. 서로 비슷한 서열을 가진 유전자들 사이에서 일부 정보가 바뀌면 원래와 조금 다른 형태가 만들어지는데, 자료는 이것이 **감수분열(meiosis)** 과정에서 일어나 MHC 다양성에 기여했다고 본다.", 9),
        STAR("Polymorphism의 기능적 의미", 9),
        B("변화가 일어난 부위 : {r|class I은 α1·α2 영역, class II는 β1 영역} — peptide 결합과 관련된 부분.", 9),
        B("결합 홈의 구조가 달라지면 결합하는 peptide의 종류도 달라진다.", 9),
        P("그러므로 MHC polymorphism은 단순한 이름의 다양성이 아니라 **‘어떤 항원을 T세포에게 보여줄 수 있는가’와 직결되는 기능적 다양성**이다. 오늘 강의의 핵심 연결고리.", 9),
        STAR("Peptide binding motif와 anchor residue", 10),
        P("여러 peptide가 한 MHC에 결합한다고 해서 **전체 서열이 같아야 하는 것은 아니다.** 대신 특정 위치에 **성질이 비슷한 아미노산**이 반복해서 나온다. 정리본은 **2번, 5번, 8번 위치**를 예로 든다.", 10),
        B("**Anchor residue** : 이런 위치에서 MHC와 중요한 접촉을 하는 잔기.", 10),
        B("어떤 MHC allele은 특정 **peptide motif**를 선호하고, 그 motif를 가진 서로 다른 항원 peptide가 결합할 수 있다.", 10),
        B("MHC 종류가 바뀌면 잘 결합하는 peptide 집합도 달라진다.", 10),
        B("응용 : 종양 항원 예측, 백신 후보 peptide를 고르는 전략.", 10),
        P("{g|외울 것은 번호가 아니라 결합의 원리. 표를 볼 때는 전체 서열보다 공통된 위치와 성질을 먼저 찾아보자.}", 10),
    ], basics_title="MHC의 특징", basics=[
        "Polymorphism(다형성) : 같은 유전자 자리에 사람마다 가질 수 있는 allele이 매우 다양하다. Polygeny : 한 사람이 여러 MHC 유전자를 갖고 함께(codominant) 발현한다.",
        "다형성은 peptide 결합 부위에 몰려 있다 — class I은 α1·α2, class II는 β1(β chain).",
        "{b|Class I이 class II보다 다형성이 크고(B>A>C / DRB>DQB>DPB)}, 다양성은 gene conversion에서 비롯된다.",
    ], basics_refs=[101, 104, 105, 109], tables=[SlideTable(rows=[
        ["구분", "Polygeny", "Polymorphism"],
        ["의미", "한 개체 안의 서로 다른 MHC 유전자 여러 개", "같은 유전자 자리의 집단 내 allele 다양성"],
        ["예", "HLA-A, HLA-B, HLA-C ...", "HLA-B 하나에도 다양한 allele"],
        ["수준", "개체 수준", "집단 수준"],
    ], caption="Polygeny vs Polymorphism 비교 (강의 설명을 표로 정리)", col_widths_cm=[2.6, 7.4, 7.4])]))

    # ======================================================= Ch 1 · § 3
    top.append(T("MHC restriction", CH1, [11, 12, 13, 14, 15, 16, 17], [
        STAR("MHC restriction의 원칙", 11),
        P("T세포는 외래 peptide만 보고 반응하지 않는다. T세포가 항원(epitope)을 인식하려면 두 조건이 **동시에** 필요하다.", 11),
        B("① **TCR이 특이성을 갖는 peptide**가 제시되어야 하고", 11),
        B("② 그 peptide를 보여주는 **MHC도 자신이 인식하도록 교육받은 것(자기 MHC)** 이어야 한다.", 11),
        P("그림으로 보면 : 자기 MHC + 맞는 peptide → 인식 O / peptide가 같아도 MHC가 자기 것이 아니면 → 인식 X / 자기 MHC라도 TCR이 모르는 peptide면 → 인식 X. "
          "{r|즉 T세포 인식의 대상은 peptide 하나가 아니라 peptide–MHC 복합체}다.", 11),
        P("{g|Doherty와 Zinkernagel의 연구가 이를 보여준 대표 예이다. 지금은 기본 지식 같지만 처음 밝혀졌을 때는 매우 중요한 발견이었다. 실험의 세부사항을 따라가기보다 ‘항원은 같고 MHC가 다른 경우 / MHC는 같고 항원이 다른 경우 / 둘 다 맞는 경우’를 나누어 무엇이 반응을 결정하는지 보는 사고방식을 익히자.}", 12),
        B("{b|기출 : MHC restriction이 적용되는 것 = adoptive T cell therapy. 예외(적용 안 됨) = alloresponse, transplantation, superantigen. NK cell은 비특이적 면역 반응이라 restriction과 거리가 멀다}", 12, 13, 15, 113, 116),
        P("그런데 의문이 생긴다. **자기 MHC에 제한되어 반응한다면 왜 장기이식 때는 타인의 MHC에 엄청난 반응이 나타날까?** 이제 그 ‘예외’를 보자.", 12),
        STAR("예외 1. Alloresponse", 13),
        P("**Alloresponse** = 다른 개체의 MHC에 대한 강한 T세포 반응. 이식에서 핵심 문제는 서로 다른 MHC를 인식하는 T세포의 반응이다.", 13),
        B("같은 종 사이의 이식 → **allogeneic**, 서로 다른 종 사이 → **xenogeneic (xenograft)**", 13),
        B("{b|기출 : allogeneic = 같은 종의 유전적으로 동일하지 않은 개체 간 이식(가장 흔함, 면역억제제 필요) / xenogeneic = 다른 종 사이 이식}", 13, 110),
        P("자기 MHC에 반응하도록 교육받은 T세포가 왜 타인의 MHC에도 반응할까? TCR은 본래 어느 정도 **교차 반응성**이 있어서, 자기 MHC와 구조가 비슷한 다른 MHC에 예기치 않게 강하게 결합할 수 있다. "
          "정리본은 이런 **alloreactive T cell**이 상당한 비율로 존재해서 일반 peptide-specific 반응보다 이식편에 대한 반응이 크게 나타날 수 있다고 설명한다.", 13),
        STAR("실험 : Mixed lymphocyte reaction (MLR)", 14),
        P("alloresponse는 **MLR**로 관찰한다. MHC가 다른 두 개체의 림프구를 섞어 놓고 반응을 본다.", 14),
        B("양쪽이 모두 증식하면 어느 쪽 반응인지 구별할 수 없다 → 한쪽을 **irradiation 또는 mitomycin C**로 처리해 증식하지 못하게 한다.", 14),
        B("그러면 처리하지 않은 쪽의 반응만 관찰할 수 있다.", 14),
        B("{r|Alloreactive T cell은 전체 T세포의 약 1~10%.}", 14),
        B("TCR의 **CDR 부위**가 MHC–peptide 복합체와 상호작용한다.", 14),
        P("흉선의 **positive / negative selection**을 떠올려보자. 자기 MHC에 적절히 반응하는 세포가 남도록 선택되지만, "
          "{r|그것이 타인의 MHC에 대한 반응까지 완전히 없애 주지는 않는다.} 이식 거부반응을 이해할 때 이 점이 중요하다.", 14),
        STAR("예외 2. Superantigen", 15),
        P("정상적인 항원제시는 peptide가 만들어져 MHC의 결합 홈에 놓이고, 특정 TCR이 그 복합체를 인식하는 과정이다. 반면 **superantigen**은 일반적인 peptide 처리·결합 방식과 달리 "
          "**MHC class II와 TCR을 연결**해서 많은 T세포를 동시에 활성화한다. 그림에서도 결합 위치가 일반적인 peptide–MHC–TCR 인식과 다르다는 점부터 확인하자.", 15),
        P("이런 반응은 특정 항원을 가진 병원체를 정교하게 제거하는 반응이 아니다. 많은 T세포가 한꺼번에 자극되면 염증성 신호가 크게 발생해 숙주에 심한 부담이 된다. "
          "{r|Superantigen의 핵심 = 비특이적인 대규모 T세포 활성화.}", 15),
        B("**Staphylococcal enterotoxin** : 식중독과 관련", 16),
        B("**TSST-1** : toxic shock syndrome과 관련", 16),
        P("{r|두 이름을 구별해서 기억하자.}", 16),
        STAR("MHC 다양성이 좋은 이유 — 집단 수준의 예", 16),
        P("강의 처음에 ‘MHC가 단조로우면 감염원이 계속 회피할 수 있어서 다양한 것이 좋다’고 했는데, 그에 대한 사례들이다.", 16),
        B("**EBV**의 면역 회피와 특정 인구집단의 HLA 분포", 16),
        B("**서아프리카에서 HLA-B53과 중증 말라리아**의 관련성", 16),
        P("개별 수치보다 중요한 메시지는 **병원체와 숙주의 유전적 다양성이 서로 영향을 주고받는다**는 점이다. 집단에서 MHC가 다양하면 모든 사람이 같은 회피 전략에 취약해질 가능성이 줄어든다.", 16),
        STAR("MHC가 많을수록 항상 좋을까?", 17),
        P("MHC 종류가 많을수록 좋다면 왜 무한정 늘어나지 않을까? 다양한 MHC를 발현하면 더 많은 peptide를 제시할 가능성이 있지만, 동시에 **T세포가 흉선에서 선택되는 조건도 더 복잡**해진다. "
          "자가 반응성과 적절한 면역 반응 사이에 **균형**이 필요하며, 정리본은 많은 MHC 유전자와 T세포 교육의 부담 사이에서 균형이 형성되었다고 설명한다.", 17),
        P("{g|여기까지는 고전적 MHC와 peptide 항원 이야기였다. 이어지는 장은 이 틀로 설명하기 어려운 인식 방식(class Ib, nonclassical MHC, MHC-like molecule)이며, 분류 용어는 자료마다 조금 다르니 기능을 함께 보자.}", 17),
    ], basics_title="MHC restriction", basics=[
        "T세포는 자신의 MHC에 국한된 반응을 한다 : TCR이 특이적인 peptide + 자기 MHC가 함께 있어야 인식한다. {b|adoptive T cell therapy는 restriction 적용, alloresponse·transplantation·superantigen은 예외.}",
        "예외 ① Alloresponse : 타인 MHC에 반응하는 alloreactive T cell(전체의 1~10%) 때문에 장기이식 거부반응이 생긴다.",
        "예외 ② Superantigen : peptide 처리 없이 TCR과 MHC class II에 모두 결합해 비특이적으로 강하게 활성화한다.",
    ], basics_refs=[113, 116], tables=[SlideTable(rows=[
        ["", "일반 항원 (peptide)", "Superantigen"],
        ["MHC와의 결합", "결합 홈에 peptide가 위치", "일반적인 peptide 처리·결합 방식과 다름 (MHC class II와 TCR을 연결)"],
        ["T세포 반응", "특정 TCR이 복합체를 인식 → 항원 특이적", "많은 T세포 동시 활성화 → 비특이적"],
        ["결과", "정교한 병원체 제거", "큰 염증성 신호, 숙주 부담"],
    ], caption="정상 항원제시 vs superantigen (강의 설명을 표로 정리)", col_widths_cm=[3.0, 6.2, 8.2])]))

    # ======================================================= Ch 2 · § 1
    top.append(T("Class Ib molecule", CH2, [17, 18], [
        STAR("Class Ib란?", 18),
        P("**Class Ib (nonclassical MHC class I)** 는 고전적 class I과 형태는 비슷하지만 **다형성이 상대적으로 제한적**이고 기능이 다양하다. "
          "{r|unconventional T cell과 NK cell을 자극할 수 있는 ligand}라고 이해하자.", 18),
        P("**Unconventional T cell**이란 고전적인 αβ T세포의 peptide–MHC 인식과 다른 항원 인식 경로를 쓰는 T세포이다.", 18),
        B("**γδ T cell**", 18),
        B("**MAIT cell** (mucosal associated invariant T cell, 점막 관련)", 18),
        B("**invariant NKT cell**", 18),
        P("이름이 다른 만큼 인식하는 표적과 생리적 역할이 같지는 않다.", 18),
        STAR("Class Ib에 속하는 분자들 (HLA 위주로 보자)", 18),
        B("**HLA-E, HLA-F, HLA-G** 중심으로 살펴보며, 일부는 {r|NK cell에 억제 신호}를 주는 경로와 연결된다.", 18),
        B("**HLA-G** : 모체–태아 사이의 면역 조절과 관련된다.", 18),
        B("**HLA-C** : NK cell 수용체와 상호작용한다는 점에서 함께 거론된다. (HLA-A, B, C는 class I이지만 C는 애매하다.)", 18),
        B("**MIC-A, MIC-B** : class III region에 있는 분자.", 5, 18),
        B("{b|기출 : HLA-E = class Ib, NK cell의 NKG2A·NKG2C 수용체에 결합해 NK를 억제 / T cell에는 항원을 제시하지 않음 (HLA-A, B, C, DR과 구분)}", 18, 115, 117),
        B("{b|기출 : HLA-C = NK cell 억제 수용체(KIR)에 결합 (KIR에 결합하는 것 = MHC class I). class I 역할도 하지만 class Ib로 분류하기도 함 (class 1b 문항에서 HLA-C, HLA-F 모두 정답 처리)}", 18, 106, 111, 114),
        B("{b|기출 : MIC-A/B ↔ NKG2D 수용체는 NK cell 활성화와 관련} {g|(PAD 해설 : 표에는 있으나 강의에서 자세히 다루지 않음)}", 5, 107, 112),
        ADV("Class Ib는 antigen presentation을 하기도 하지만(HLA-C 등) NK cell inhibition(경우에 따라 activation) 같은 **서로 다른 기능**을 한다. 한 가지 역할로 외우지 말 것.", 18),
    ], basics_title="Class Ib molecule", basics=[
        "MHC class I gene family에 속하지만 unconventional T cell과 NK cell을 자극할 수 있는 ligand를 class Ib molecule이라고 한다.",
        "{b|HLA-E / F / G가 class Ib에 속한다 (HLA-E는 NK 억제, HLA-C는 class I이면서 Ib).}",
        "CD1 molecule은 peptide가 아닌 lipid를 제시한다 (§ 2).",
    ], basics_refs=[115, 117, 106, 111, 114], tables=[SlideTable(rows=[
        ["분자", "기억할 점"],
        ["HLA-C", "class I이면서 class Ib로도 분류 — NK cell 수용체와 상호작용"],
        ["HLA-E / F", "NK cell 억제 경로와 연결 (class Ib)"],
        ["HLA-G", "모체–태아 면역 조절, NK cell에 억제 신호"],
        ["MIC-A / B", "class III region의 분자"],
    ], caption="Class Ib 분자 한눈에 보기 (강의 설명 기준)", col_widths_cm=[3.4, 14.0])]))

    # ======================================================= Ch 2 · § 2
    top.append(T("non-MHC encoded class Ib molecule", CH2, [19], [
        STAR("CD1 molecule — lipid 항원제시", 19),
        P("지금까지 MHC를 공부할 때는 peptide 항원 이야기를 계속했다. **CD1은 그와 달리 lipid 또는 glycolipid 항원을 제시**한다는 점이 핵심이고, "
          "병원체 유래 지질 항원을 인식하는 경로와 연결된다. {r|정리본에서 이 부분은 국가시험에 자주 나온다고 강조한 것으로 기록되어 있다.}", 19),
        B("CD1a부터 CD1e까지 여러 유형이 있지만 우선 **‘CD1 — 지질 항원제시’**를 확실히 기억하자.", 19),
        B("**NKT cell**은 이러한 lipid 항원 인식과 관련된다.", 19),
        B("{b|기출 : CD1c가 활성화시키는 것 = NKT cell (invariant NKT). CD1c가 제시하는 것은 lipid}", 19, 102),
        B("세부 분자(CD1c, CD1d)와 invariant NKT cell의 연결은 복습 시 확인하자 {p|(검증 대상 — 기출 정답은 CD1c → NKT로 표기됨)}.", 19),
        STAR("FcRn — MHC와 닮았지만 하는 일이 다르다", 19),
        P("**FcRn**은 MHC와 비슷하게 생긴 분자이지만 전형적인 항원제시가 아니라 **모체의 IgG를 태아에게 전달**하는 일을 한다.", 19),
        ADV("MHC class Ib 중에는 MHC 영역이 아닌 곳(다른 염색체)에서 만들어지는 것도 있다. CD1과 FcRn 두 가지만 기억해도 충분하다.", 19),
    ], basics_title="non-MHC encoded class Ib molecule", basics=[
        "MHC 유전자 영역 밖(다른 염색체)에서 만들어지는 MHC-like 분자들이다.",
        "CD1 (a~e) : peptide가 아닌 lipid / glycolipid 항원을 제시한다 — 국가시험에 자주 나온다. {b|CD1c → NKT cell}",
        "FcRn : 엄마에게서 태아로 IgG를 전달한다 (전형적 항원제시와는 다른 기능).",
    ], basics_refs=[102]))

    # ======================================================= Ch 2 · § 3
    top.append(T("γδ T cell, MAIT와 마무리", CH2, [20], [
        STAR("γδ T cell — 다양한 ligand를 인식한다", 20),
        P("정리본의 표를 보면 γδ T cell이 인식하는 ligand가 여러 가지로 나와 있다. 항목을 하나하나 암기하기보다 "
          "**고전적인 peptide–MHC 인식과는 다른 방식으로 다양한 신호를 감지**한다는 점이 중요하다. {g|수업 필기에서도 ‘종류가 다양하다’ 정도로 넘어갔다.}", 20),
        STAR("MAIT cell", 20),
        P("**MAIT cell**은 점막 면역과 관련이 있고 **미생물 유래 물질**을 인식한다. 선천면역과 적응면역 **사이를 잇는 ‘transitional’한 성격**으로 설명된다.", 20),
        STAR("오늘 내용 4줄 정리", 20),
        B("① {r|MHC는 polygenic & polymorphic} → 항원제시의 범위를 넓힌다.", 20),
        B("② {r|일반적인 T세포 반응은 peptide + 자기 MHC, 두 조건}을 함께 본다 (MHC restriction).", 20),
        B("③ {r|Alloresponse와 superantigen} : 이 원칙에서 벗어난 형태의 강한 반응.", 20),
        B("④ {r|CD1과 unconventional T cell} : peptide 중심의 고전 경로를 벗어난 인식.", 20),
    ], basics_title="Ligands that activate γδ T cell", basics=[
        "γδ T cell은 고전적 peptide–MHC가 아닌 다양한 ligand를 인식한다 (‘다양하다’ 정도로 기억).",
        "MAIT cell은 미생물 유래 물질을 인식하며 선천면역과 적응면역을 잇는 transitional한 세포이다.",
        "CD1은 lipid 항원제시, 이 강의의 네 줄 정리를 연결해서 복습한다.",
    ], flags=["CD1c와 invariant NKT cell의 연결은 원자료 기재 내용이며, 일반적으로 invariant NKT의 대표 인식 분자는 CD1d로 알려져 있음 → 원자료·교과서로 확인 필요."]))

    # ======================================================= appendix
    top.append(T("부록 & 검증 참고", "", [21], [
        P("{p|이 강의록은 실제 녹음이 아니라 ‘정리본 기반 가상 강의 스크립트’에서 만든 것입니다. 아래 사항을 확인하고 사용하세요.}", 21),
        B("전체 발화는 정리본의 주제 순서에 따라 새로 작성한 **가상 발화**이며 실제 표현·말투·강조의 재현이 아닙니다.", 21),
        B("인터페론 관련 세부 설명 중 일부는 원래 PPT에만 있고 강의에서 다루지 않았다고 표시됨 → 개념 연결 수준으로만 정리했습니다.", 21),
        B("{p|CD1c와 invariant NKT cell의 연결}(정리본 12쪽 기재)은 원자료 기재이나 일반적으로 대표 분자는 CD1d → 원자료와 대조 필요.", 21),
        B("일부 숫자·연구 연도·용어는 독립 검증하지 않음. 최신 교과서·진료지침을 대체하지 않음.", 21),
        B("스크립트의 시간 구간 표기(가상 40분)는 연습용 가상 타임스탬프라서 이 강의록의 구성에는 사용하지 않았고, 전체 흐름을 보고 목차를 새로 구성했습니다.", 21),
        B("{g|PAD의 2009년(07학번) 문항은 시험지 스캔 이미지라 문항 내용을 확인할 수 없어 본문에 반영하지 못했습니다(정답 3번만 기록됨).}", 118),
        B("{g|PAD(기출문제) 해설은 정리본 작성자의 코멘트이며 교수님 발언이 아닙니다. PAD 문항 대부분은 이전 담당 교수님 시절 것이라 올해 출제 방향과 다를 수 있습니다.}", 101),
    ]))
    return _remap(top, unit_ids, EX)


def _remap(topics, unit_ids, EX):
    def one(r):
        if r >= 100:
            return [EX[r].number] if r in EX else []
        return unit_ids.get(r, [])

    def refs(lst):
        out = []
        for r in lst:
            for x in one(r):
                if x not in out:
                    out.append(x)
        return sorted(out)

    for t in topics:
        t.slide_numbers = refs(t.slide_numbers)
        t.basics_refs = refs(t.basics_refs)
        for sts in t.sections.values():
            for st in sts:
                st.slide_refs = refs(st.slide_refs)
    return topics


def unit_ids_from_script(path):
    """Old block no. -> paragraph ids, numbered exactly like parse_flow_script (all paragraphs, 1-based)."""
    from app.transcript import parse_structured_script, read_script_text

    _, units = parse_structured_script(read_script_text(path))
    ids, n = {}, 0
    for u in units:
        ids[u.number] = list(range(n + 1, n + 1 + len(u.paragraphs)))
        n += len(u.paragraphs)
    return ids


if __name__ == "__main__":
    # usage: python -m examples.tcell_note <script.docx> <pad.pdf> > note_authored.json
    from app.exam import parse_exam_pdf
    ids = unit_ids_from_script(sys.argv[1])
    items = parse_exam_pdf(sys.argv[2])
    json.dump({"topics": [t.model_dump() for t in build(ids, items)]}, sys.stdout, ensure_ascii=False, indent=2)
