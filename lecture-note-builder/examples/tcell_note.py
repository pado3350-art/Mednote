"""Authored structured note (Topic JSON) for the 'T림프구에 대한 항원제시' script.

Written by Claude Code from the script's 21 units (20 time blocks + 검증 참고).
Every statement carries `slide_refs` = unit numbers so the validator can trace it.
Run:  python examples/tcell_note.py > outputs/tcell/note_authored.json
Markup: {r|red} {b|blue} {g|gray} {p|purple} **bold**
"""
import json
import sys

from app.models import SlideTable, Statement, Topic


def P(text, *refs, **kw):
    return Statement(text=text, slide_refs=list(refs), origin="both", **kw)


def B(text, *refs, **kw):
    return Statement(text=text, slide_refs=list(refs), origin="both", kind="bullet", **kw)


def B2(text, *refs, **kw):
    return B(text, *refs, level=1, **kw)


def STAR(text, *refs):
    return Statement(text=text, slide_refs=list(refs), origin="both", kind="star")


def topic(heading, units, body, tables=(), flags=()):
    return Topic(heading=heading, slide_numbers=list(units), sections={"body": body},
                 tables=list(tables), review_flags=list(flags))


def build(schedule_rows):
    T = []

    # ---------------------------------------------------------------- 0
    T.append(topic("0. 시험 포인트 & 강의 구성", [], [
        P("이번 강의는 **MHC 유전자의 구성·다양성 → T세포의 MHC restriction → 예외처럼 보이는 반응(alloresponse, superantigen) → "
          "비전형적 분자(class Ib, CD1)와 unconventional T cell** 순서로 진행됩니다. 이름 암기보다 "
          "'왜 다른 역할을 하는지'를 연결해서 이해하라는 것이 강의 전체의 기조입니다.", 1, 2),
        STAR("꼭 챙길 부분 (스크립트에서 강조·시험 언급된 내용)", 2, 4, 7, 9, 11, 14, 16, 19, 20),
        B("{r|Polygenic ≠ Polymorphic}: polygenic = 한 개체가 서로 다른 MHC 유전자를 여러 개 가짐 / polymorphic = 같은 유전자 자리에 집단 내 allele이 여러 형태. 둘을 혼동하지 말 것.", 2, 7),
        B("{r|질문 문구 구분}: 'MHC class II **분자**'인지 'class II **region에 존재하는 유전자**'(DM, DO, TAP 등 포함)인지 확인.", 4),
        B("사람 **HLA** vs 생쥐 **H-2** (생쥐 유전자 영역은 {r|17번 염색체}; 사람은 6번).", 3, 4),
        B("다형성은 {r|peptide 결합 부위}에 집중 — class I은 α1·α2, class II는 β1 (class II는 β chain에 다형성 집중).", 8, 9),
        B("{r|MHC restriction}: T세포 인식 대상 = **peptide–자기 MHC 복합체** (peptide만이 아님).", 11, 12),
        B("{r|Alloreactive T cell ≈ 전체 T세포의 1~10%}, MLR에서는 한쪽을 irradiation 또는 mitomycin C로 증식 억제.", 14),
        B("{r|Superantigen}의 핵심 = 비특이적 대규모 T세포 활성화. 예) staphylococcal enterotoxin(식중독), TSST-1(toxic shock syndrome).", 15, 16),
        B("{r|CD1 = lipid/glycolipid 항원제시} — 스크립트에서 국가시험 빈출로 언급됨.", 19),
        B("마무리 4줄 요약(아래 VII장 끝)을 연결해서 복습.", 20),
    ], tables=[SlideTable(rows=schedule_rows, caption="강의 시간대별 구성 (시간은 연습용 가상 타임스탬프)")]))

    # ---------------------------------------------------------------- I
    T.append(topic("I. MHC 유전자의 구성과 용어", [1, 2, 3, 4, 5, 6], [
        STAR("도입: 왜 MHC 다양성이 필요한가", 1),
        P("앞 시간에는 항원이 세포 안에서 처리되어 MHC 위에 올라가는 과정을 배웠고, 이번에는 **MHC 자체가 왜 여러 종류인지**, "
          "T세포가 **실제로 무엇을 인식하는지**를 다룹니다.", 1),
        P("감염원의 입장에서 보면, 자기 단백질 조각이 MHC에 얹혀 T세포에 보이면 면역계가 자신을 알아보게 되므로 그 경로를 피하려 합니다. "
          "만약 인간에게 MHC가 **한 종류**뿐이라면 이 결합을 피하는 돌연변이가 생길 때 **모두에게** 통하기 쉽습니다. "
          "실제로는 (1) 한 사람 안에서도 여러 MHC 유전자가 발현되고, (2) 사람들 사이에 allele 종류가 매우 다양합니다 — {b|이 두 가지가 오늘의 출발점}.", 1),
        STAR("기본 용어", 2),
        B("{b|Polygenic}: 한 개체가 서로 다른 MHC 유전자를 여러 개 가짐.", 2),
        B("{b|Polymorphic}: 같은 유전자 자리라도 집단 안에 여러 형태의 allele이 존재.", 2),
        B("{b|Haplotype}: 한쪽 염색체 위에 모여 함께 유전되는 MHC allele의 조합.", 2),
        P("오늘의 순서: ① 6번 염색체 MHC 영역 → ② 다양성과 항원 인식의 관계 → ③ T세포의 MHC restriction과 예외처럼 보이는 이식 반응·superantigen "
          "→ ④ HLA-E/F/G, CD1 같은 비전형적 분자.", 2),
        STAR("인간 MHC 유전자 구성 (6번 염색체)", 3),
        P("사람의 MHC = **HLA (human leukocyte antigen)**, 6번 염색체에 유전자가 밀집. **class I / class II / class III** 영역을 구분해서 봅니다.", 3),
        B("**Classical MHC class I**: {b|HLA-A, HLA-B, HLA-C} — 큰 α chain 1개 + **β2-microglobulin** ('다리 하나짜리'로 기억).", 3),
        B("**Classical MHC class II**: {b|HLA-DR, HLA-DP, HLA-DQ} — α chain과 β chain이 짝 ('다리 두 개짜리').", 3),
        P("{g|유전자 영역과 실제 분자의 기능을 구분하는 것이 이름 암기보다 중요합니다.}", 3),
        STAR("Class II 영역과 관련 분자", 4),
        P("class II region에는 DR, DQ, DP 외에도 **HLA-DM, HLA-DO**가 있습니다. 이들은 고전적 항원제시 MHC class II와는 구별되지만 "
          "peptide editing 등 항원제시 과정의 조절에 관여합니다. **TAP**처럼 항원 처리에 참여하는 분자도 이 MHC 유전자 영역 안에서 함께 볼 수 있습니다.", 4),
        P("{r|문제에서 'MHC class II 분자'를 묻는지, 'class II region에 존재하는 유전자'를 묻는지 구분!} 두 질문은 같지 않습니다.", 4),
        STAR("사람(HLA) vs 생쥐(H-2)", 4),
        B("사람은 HLA, 생쥐는 **H-2**; 생쥐 MHC 영역은 {r|17번 염색체}에 위치.", 4),
        B("생쥐 class I: **H-2D, H-2L** (그림에서 D, L, K 등으로 표기) / class II: **H-2A, H-2E** 등.", 4),
        B("나중에 실험 그림을 읽을 때 필요한 명칭 차이.", 4),
        STAR("MHC 영역의 복잡성 — 확대 유전자 지도", 5),
        P("그림은 위아래로 나뉘어 있지만 사실 **길게 연결된 하나의 영역**입니다. class I/II만 정돈되어 모여 있는 것이 아니라 "
          "사이사이에 **항원 가공·제시에 관여하는 유전자**가 섞여 있습니다.", 5),
        B("항원 가공 관련: **TAP**, **proteasome** 관련 성분 / 염증 관련: **TNF** 유전자.", 5),
        B("Class I region에는 A, B, C 외에 **HLA-E, HLA-F, HLA-G** — 나중에 {b|class Ib(비고전적 MHC class I)}로 다시 등장.", 5),
        B("Class III region에는 **MIC-A, MIC-B** 등이 표시됨.", 5),
        P("하나의 영역에 여러 면역 관련 유전자가 함께 모여 있어 면역 반응이 **함께 조절**된다는 설명으로 이어집니다.", 5),
        STAR("인터페론과 유전자 발현 조절", 6),
        P("감염이 생기면 면역 관련 유전자 발현이 변합니다. 자료는 **interferon α, β, γ**가 MHC 관련 유전자 발현을 조절한다고 제시하며, "
          "그 결과 감염 세포가 바이러스 단백질 유래 peptide를 제시할 기회가 늘어납니다.", 6),
        B("{b|CIITA}: MHC class II 전사 조절의 핵심 co-activator.", 6),
        B("{b|Interferon-γ}는 class II 관련 유전자 발현과 연결해서 기억.", 6),
        P("{g|모든 조절 경로를 외울 필요는 없고, '항원제시 분자만 따로 만들어지는 게 아니라 가공·제시에 필요한 여러 구성요소가 연동되어 조절된다'는 큰 흐름만 잡으면 됩니다.}", 6),
    ], flags=["인터페론 관련 세부 내용은 원자료에서 일부가 PPT에만 있고 강의에서는 다루지 않았다고 표시됨 → 개념 연결 수준으로만 정리 (VIII장 참고)."]))

    # ---------------------------------------------------------------- II
    T.append(topic("II. Polymorphism과 polygeny", [7, 8, 9], [
        STAR("두 개념의 구분", 7),
        B("{r|Polymorphism}: **동일한 유전자 자리**의 allele이 집단 전체에서 여러 형태로 존재.", 7),
        B("{r|Polygeny}: **한 개인 안에** 서로 다른 MHC 유전자들이 여러 개 존재.", 7),
        P("예) HLA-A와 HLA-B는 서로 다른 유전자(polygeny)이고, 각각의 HLA-A·HLA-B에도 다양한 allele이 있을 수 있음(polymorphism). **두 층위의 다양성이 함께 작동**합니다.", 7),
        P("발현은 **codominant** — 어머니·아버지에게서 받은 것이 모두 발현되어 한 개체에서 실제 만들어지는 MHC 분자 종류가 늘어납니다. "
          "그래서 한 사람의 MHC 조합이 다른 사람과 같기 어렵습니다.", 7),
        P("{r|'한 개체의 유전자 수가 많다'와 '집단 전체의 allele 종류가 많다'를 바꿔 쓰지 말 것.}", 7),
        STAR("다형성이 집중되는 위치", 8),
        P("다형성은 모든 MHC 분자에서 똑같이 크지 않습니다. 강조점은 **고전적 class I의 다양성이 크고, class Ib는 상대적으로 제한적**이라는 것입니다.", 8),
        B("Class I에서는 {b|HLA-B, A, C}의 순서로 다양성 비교.", 8),
        B("Class II에서는 {b|DRB, DQB, DPB}를 비교; {r|class II의 다형성은 β chain 쪽에 집중}.", 8),
        P("중요한 이유: polymorphism은 특히 **peptide가 들어가는 결합 부위**와 관련됩니다. 같은 감염원의 peptide라도 **사람의 MHC 종류에 따라 결합 가능성이 달라집니다.**", 8),
        P("{g|allele 개수는 시점과 자료에 따라 달라지므로 최신 개수를 기계적으로 외우기보다 상대적 경향과 기능을 먼저 이해.}", 8),
        STAR("다양성의 기원: gene conversion", 9),
        P("다양성은 **gene conversion**으로 설명합니다. 서로 유사한 서열을 가진 유전자 사이에서 일부 유전정보가 바뀌어 원래와 조금 다른 형태가 생기며, "
          "자료는 **감수분열 과정**에서 유사 서열 사이의 변화가 MHC 다양성에 기여했다고 설명합니다.", 9),
        B("변화가 일어난 부위: {r|class I은 α1·α2 영역, class II는 β1 영역} — peptide 결합과 관련된 다양성 부위.", 9),
        B("결합 홈의 구조가 달라지면 결합하는 peptide의 종류도 달라짐.", 9),
        P("따라서 MHC polymorphism은 이름의 다양성이 아니라 **'어떤 항원을 T세포에 보여줄 수 있는가'와 직결되는 기능적 다양성**입니다 — 오늘의 핵심.", 9),
    ], tables=[SlideTable(rows=[
        ["구분", "Polygeny", "Polymorphism"],
        ["의미", "한 개체 안의 서로 다른 MHC 유전자 여러 개", "같은 유전자 자리의 집단 내 allele 다양성"],
        ["예", "HLA-A, HLA-B, HLA-C ...", "HLA-B 하나에도 다양한 allele"],
        ["수준", "개체 수준", "집단 수준"],
    ], caption="Polygeny vs Polymorphism 비교 (스크립트 설명을 표로 정리)")]))

    # ---------------------------------------------------------------- III
    T.append(topic("III. Peptide binding motif와 MHC restriction", [10, 11, 12], [
        STAR("Peptide binding motif와 anchor residue", 10),
        P("여러 peptide가 하나의 MHC에 결합한다고 해서 **전체 서열이 같아야 하는 것은 아닙니다.** 대신 특정 위치에 **유사한 성질의 아미노산**이 반복해서 나타납니다. "
          "정리본은 예시로 **2번, 5번, 8번 위치**를 살펴봅니다.", 10),
        B("{b|Anchor residue}: 이런 위치에서 MHC와 중요한 접촉을 형성하는 잔기.", 10),
        B("어떤 MHC allele은 특정 **peptide motif**를 선호 → 그 motif를 가진 서로 다른 항원 peptide가 결합 가능.", 10),
        B("MHC 종류가 바뀌면 잘 결합하는 peptide 집합도 달라짐.", 10),
        B("응용: 종양 항원 예측, 백신 후보 peptide 선택 전략.", 10),
        P("{g|번호 자체보다 '결합의 원리'를 기억. 표를 볼 때는 전체 서열보다 공통된 위치와 성질을 먼저 찾을 것.}", 10),
        STAR("MHC restriction의 기본 원칙", 11),
        P("T세포는 외래 peptide만 인식하는 것이 아닙니다. **TCR이 맞는 peptide**를 인식해야 하고, 그 peptide를 제시하는 **MHC도 자신이 인식하도록 교육받은 종류**여야 반응합니다. 두 조건을 같이 봐야 합니다.", 11),
        B("자기 MHC + 적절한 peptide → 인식 가능.", 11),
        B("peptide가 같아도 MHC가 맞지 않으면 일반적인 자기 MHC 제한 반응이 일어나지 않음.", 11),
        B("자기 MHC라도 해당 TCR이 인식하지 못하는 peptide면 반응하지 않음.", 11),
        P("{r|T세포 인식의 대상은 분리된 peptide 하나가 아니라 peptide–MHC 복합체.}", 11),
        STAR("Restriction의 실험적 의미 (Doherty & Zinkernagel)", 12),
        P("지금은 기본 지식처럼 들리지만 처음 밝혀졌을 때는 매우 중요한 발견이었습니다. **Doherty와 Zinkernagel**의 연구가 대표 예이며, "
          "특정 항원에 반응하는 T세포가 아무 세포에서나 반응하는 것이 아니라 **적절한 자기 MHC 환경에서 항원이 제시**되어야 함을 보였습니다.", 12),
        P("실험 세부사항보다 **비교하는 사고방식**을 익힙니다:", 12),
        B("항원은 같고 MHC가 다른 경우", 12),
        B("MHC는 같고 항원이 다른 경우", 12),
        B("두 조건이 모두 맞는 경우", 12),
        P("→ 무엇이 T세포 반응을 결정하는지 알 수 있음. 여기서 의문: **자기 MHC에 제한되는데 왜 장기 이식 때는 타인의 MHC에 엄청난 반응이 나타날까?** → 다음 장.", 12),
    ]))

    # ---------------------------------------------------------------- IV
    T.append(topic("IV. Alloresponse와 이식 거부반응", [13, 14], [
        STAR("Alloresponse", 13),
        P("**Alloresponse** = 다른 개체의 MHC에 대한 강한 T세포 반응.", 13),
        B("같은 종 사이의 이식: {b|allogeneic}", 13),
        B("서로 다른 종 사이의 이식: {b|xenogeneic (xenograft)}", 13),
        P("이식에서 핵심 문제는 **서로 다른 MHC를 인식하는 T세포의 반응**입니다.", 13),
        P("자기 MHC에 반응하도록 교육받은 T세포가 타인의 MHC에 반응하는 이유: TCR은 본래 어느 정도 **교차 반응성**을 가질 수 있어, "
          "자기 MHC와 구조가 비슷한 다른 MHC에 예기치 않게 강하게 결합할 수 있습니다. 정리본은 **alloreactive T cell이 상당한 비율로 존재**하여 "
          "일반적인 peptide-specific 반응보다 이식편에 대한 반응이 크게 나타날 수 있다고 설명합니다.", 13),
        STAR("Mixed lymphocyte reaction (MLR)과 T세포 선택", 14),
        P("alloresponse를 관찰하는 고전적 실험 = **MLR**: MHC가 다른 두 개체의 림프구를 섞어 반응을 봅니다.", 14),
        B("양쪽이 모두 증식하면 어느 쪽 반응인지 구별 불가 → 한쪽을 **irradiation 또는 mitomycin C**로 처리해 증식하지 못하게 함.", 14),
        B("처리하지 않은 쪽의 반응만 관찰 가능.", 14),
        B("{r|Alloreactive T cell은 전체 T세포의 약 1~10%.}", 14),
        B("TCR의 **CDR 부위**가 MHC–peptide 복합체와 상호작용.", 14),
        P("흉선의 **positive selection / negative selection**을 떠올리기: 자기 MHC에 적절히 반응하는 세포가 남도록 선택되지만, "
          "{r|그것이 타인의 MHC에 대한 반응까지 완전히 없애 주지는 않는다} — 이식 거부반응 이해의 핵심.", 14),
    ]))

    # ---------------------------------------------------------------- V
    T.append(topic("V. Superantigen", [15, 16], [
        STAR("Superantigen의 작동 원리", 15),
        P("정상적인 항원제시: peptide 생성 → MHC 결합 홈에 위치 → 특정 TCR이 복합체를 인식. 반면 **superantigen**은 일반적인 peptide 처리·결합 방식과 달리 "
          "**MHC class II와 TCR을 연결**하여 많은 T세포를 동시에 활성화합니다. 그림에서도 결합 위치가 일반적인 peptide–MHC–TCR 인식과 다르다는 점부터 확인.", 15),
        P("특정 항원을 가진 병원체를 정교하게 제거하는 반응이 아니라, 많은 T세포가 한꺼번에 자극되어 **염증성 신호가 크게 발생**하고 숙주에 심한 부담이 됩니다.", 15),
        P("{r|Superantigen의 핵심 = 비특이적인 대규모 T세포 활성화.}", 15),
        STAR("Superantigen의 예", 16),
        B("**Staphylococcal enterotoxin**: {b|식중독}과 관련.", 16),
        B("**TSST-1**: {b|toxic shock syndrome}과 관련.", 16),
        P("{r|두 이름을 구별해서 기억.}", 16),
    ], tables=[SlideTable(rows=[
        ["", "일반 항원 (peptide)", "Superantigen"],
        ["MHC와의 결합", "결합 홈에 peptide가 위치", "일반적인 peptide 처리·결합 방식과 다름 (MHC class II와 TCR을 연결)"],
        ["T세포 반응", "특정 TCR이 복합체를 인식 → 항원 특이적", "많은 T세포 동시 활성화 → 비특이적"],
        ["결과", "정교한 병원체 제거", "큰 염증성 신호, 숙주 부담"],
    ], caption="정상 항원제시 vs superantigen (스크립트 서술을 표로 정리)")]))

    # ---------------------------------------------------------------- VI
    T.append(topic("VI. MHC 다양성의 집단 수준 의미", [16, 17], [
        STAR("집단 수준에서 본 MHC polymorphism", 16),
        P("사람 집단에서 MHC가 다양하면 **모든 사람이 똑같은 감염원 회피 전략에 취약해질 가능성**이 줄어듭니다. 자료가 든 사례:", 16),
        B("**EBV**의 면역 회피와 특정 인구집단의 HLA 분포", 16),
        B("**서아프리카에서 HLA-B53과 중증 말라리아**의 관련성", 16),
        P("개별 수치보다 중요한 메시지: **병원체와 숙주의 유전적 다양성이 서로 영향을 주고받으며**, 다양성이 감염원 방어의 범위를 넓히는 데 기여할 수 있다는 점.", 16),
        STAR("MHC가 많을수록 항상 좋은가?", 17),
        P("MHC 종류가 많을수록 좋다면 왜 무한정 늘어나지 않을까? 다양한 MHC를 발현하면 더 많은 peptide를 제시할 가능성이 있지만, "
          "동시에 **T세포가 흉선에서 선택되는 조건도 더 복잡**해집니다. 자가 반응성과 적절한 면역 반응 사이에 **균형**이 필요하며, "
          "정리본은 **많은 MHC 유전자와 T세포 교육의 부담 사이에서 균형이 형성되었다**는 설명으로 마무리합니다.", 17),
        P("{g|여기까지는 고전적 MHC와 peptide 항원. 이후는 이 틀로 설명하기 어려운 인식 방식(class Ib, nonclassical MHC, MHC-like molecule). 분류 용어는 자료마다 조금씩 다르므로 기능을 함께 볼 것.}", 17),
    ]))

    # ---------------------------------------------------------------- VII
    T.append(topic("VII. Class Ib, CD1과 unconventional T cell", [18, 19, 20], [
        STAR("Class Ib (nonclassical MHC class I)", 18),
        P("고전적 class I과 형태는 비슷하지만 **다형성이 상대적으로 제한적**이고 기능이 다양합니다.", 18),
        B("**HLA-E, HLA-F, HLA-G** 중심으로 학습. 일부는 {b|NK세포에 억제 신호}를 주는 경로와 연결.", 18),
        B("**HLA-G**: 모체–태아 사이의 면역 조절과 관련.", 18),
        B("**HLA-C**: NK세포 수용체와 상호작용한다는 점에서 함께 거론.", 18),
        STAR("Unconventional T cell", 18),
        P("정리본에서 예로 드는 것: **γδ T cell, MAIT cell (점막 관련), invariant NKT cell.** 이름이 다른 만큼 인식 표적과 생리적 역할이 같지 않습니다. "
          "먼저 '고전적 αβ T세포의 peptide–MHC 인식과 다른 항원 인식 경로가 있다'는 점을 잡으세요.", 18),
        STAR("CD1과 lipid 항원제시", 19),
        P("{r|CD1은 peptide가 아니라 lipid 또는 glycolipid 항원을 제시}한다는 점이 핵심이며, 병원체 유래 지질 항원 인식 경로와 연결됩니다. "
          "정리본에서 이 부분은 {r|국가시험에 자주 나온다}고 강조한 것으로 기록되어 있습니다.", 19),
        B("CD1a부터 CD1e까지 여러 유형이 있으나 우선 {b|'CD1 — 지질 항원제시'}를 확실히.", 19),
        B("NKT 세포는 lipid 항원 인식과 관련. 세부 분자(CD1c, CD1d) 구분은 복습 시 확인 필요 {p|(검증 대상)}.", 19),
        B("**FcRn**: MHC 유사 분자이지만 전형적 항원제시보다 **모체 IgG 전달**과 관련.", 19),
        STAR("γδ T cell, MAIT, 마무리", 20),
        P("**γδ T cell**: 인식하는 ligand가 여러 가지로 제시됨. 항목별 암기보다 {b|고전적 peptide–MHC 인식과 다른 방식으로 다양한 신호를 감지}한다는 점이 중요 "
          "{g|(수업 필기에서도 '종류가 다양하다' 정도로 넘어감)}.", 20),
        P("**MAIT cell**: 점막 면역과 관련, 미생물 유래 물질을 인식 — 선천면역과 적응면역을 잇는 성격.", 20),
        STAR("오늘 내용 4줄 정리", 20),
        B("① {r|MHC는 polygenic & polymorphic} → 항원제시 범위를 넓힘.", 20),
        B("② {r|일반 T세포 반응은 peptide + 자기 MHC 두 조건}을 함께 봄 (MHC restriction).", 20),
        B("③ {r|Alloresponse와 superantigen}: 다른 형태의 강한 반응.", 20),
        B("④ {r|CD1과 unconventional T cell}: peptide 중심 고전 경로를 벗어난 인식.", 20),
    ], flags=["CD1c와 invariant NKT cell의 연결은 원자료 기재 내용이며, 일반적으로 invariant NKT의 대표 인식 분자는 CD1d로 알려져 있음 → 원자료·교과서로 확인 필요."]))

    # ---------------------------------------------------------------- VIII
    T.append(topic("VIII. 부록 & 검증 참고", [21], [
        P("{p|이 강의록은 실제 녹음이 아니라 '정리본 기반 가상 강의 스크립트'에서 만든 것입니다. 아래 사항을 확인하고 사용하세요.}", 21),
        B("전체 발화는 정리본의 주제 순서에 따라 새로 작성한 **가상 발화**이며 실제 표현·말투·강조의 재현이 아닙니다.", 21),
        B("인터페론 관련 세부 설명 중 일부는 원래 PPT에만 있고 강의에서 다루지 않았다고 표시됨 → 개념 연결 수준으로만 정리.", 21),
        B("{p|CD1c와 invariant NKT cell의 연결}은 원자료 기재이나 일반적으로 대표 분자는 CD1d → 원자료와 대조 필요.", 21),
        B("일부 숫자·연구 연도·용어는 독립 검증하지 않음. 최신 교과서·진료지침을 대체하지 않음.", 21),
        B("표기된 시간 구간(가상 40분)은 편집 및 프로그램 테스트용 가상 타임스탬프.", 21),
    ]))
    return T


if __name__ == "__main__":
    rows = json.loads(sys.argv[1]) if len(sys.argv) > 1 else [["시간", "강의 내용", "원본 쪽"]]
    json.dump({"topics": [t.model_dump() for t in build(rows)]}, sys.stdout, ensure_ascii=False, indent=2)
