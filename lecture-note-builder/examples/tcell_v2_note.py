"""Fresh note for 'T림프구에 대한 항원제시' built ONLY from the two inputs of this run:
  * lecture material  inputs/tcell_v2_material.docx   (18 slides: text + 15 figures)
  * script            inputs/tcell_v2_script.docx     (40 speech paragraphs + 5 remarks)
No PAD was supplied -> no blue text. Nothing is taken from earlier notes of this lecture.

Refs: s = slide numbers (PPT p.N), g = script paragraph ids (발화 ¶n).
Run:  python -m examples.tcell_v2_note inputs/tcell_v2_material.docx > outputs/tcell_v2/note_authored.json
"""
import sys

from app.material import extract_docx_material
from examples.authoring import (ADV, B, DIA, P, QUIZ, REF, ROW, STAR, TERM, Arrow, Diagram, Group, SlideTable, T, dump,
                                slide_lines)

CH1 = "MHC 유전자 영역과 다양성"
CH2 = "T세포의 MHC 인식과 예외"
CH3 = "비전형 MHC와 unconventional T cell"


def build(S):
    top = []

    # =========================================================== front: 핵심 어휘
    top.append(T("핵심 어휘", "", [3, 4, 6, 7, 8, 9, 10, 11, 16], [
        P("슬라이드의 ‘핵심 어휘’ 14개를 이번 파트의 내용으로 풀어 놓았다. 뒤에서 하나씩 다시 나오니 가볍게 읽고 가도 된다.", s=[3]),
        TERM("MHC class I", "HLA-A, B, C. 큰 α chain 1개 + β2-microglobulin이 결합한 구조 — 교수님 표현으로 ‘다리 하나짜리’.", s=[3, 6], g=[6]),
        TERM("MHC class II", "HLA-DR, DP, DQ. α chain과 β chain이 짝을 이룬 구조 — ‘다리 두 개짜리’.", s=[3, 6], g=[6]),
        TERM("펩티드 (peptide)", "MHC가 T세포에게 보여주는 항원 조각. 결합 홈의 pocket과 peptide의 anchor residue가 상호작용해서 결합한다.", s=[3, 8], g=[19, 20]),
        TERM("항원제시 (antigen presentation)", "peptide가 MHC에 얹혀 T세포에 보이는 것. T세포가 인식하는 것은 peptide 하나가 아니라 peptide–MHC 복합체이다.", s=[3], g=[21, 22]),
        TERM("endoplasmic reticulum", "슬라이드 6-15: adenovirus가 만드는 단백질이 ER 안에서 MHC class I에 결합해 세포 표면으로의 이동을 막는다. (강의에서는 따로 설명하지 않음)", s=[3, 11]),
        TERM("endosome", "앞 시간(항원 처리와 제시)의 어휘. 이번 파트의 슬라이드에서는 어휘로만 나오고 설명은 없다.", s=[3]),
        TERM("CD4 molecule", "슬라이드 6-14: superantigen이 CD4 T세포의 cytokine 대량 생산을 일으킨다.", s=[3, 10]),
        TERM("CD8 molecule", "슬라이드 6-15: adenovirus는 MHC class I의 이동을 막아 CD8 cytotoxic T cell이 바이러스 peptide를 인식하지 못하게 한다.", s=[3, 11]),
        TERM("invariant chain", "슬라이드 6-10: 유전자는 β2-microglobulin처럼 MHC 영역 밖에 있고(사람에서 invariant chain 5번, β2-microglobulin 15번 염색체), IFN-γ로 class II와 함께 발현이 늘어난다.", s=[3, 6]),
        TERM("TAP", "항원 가공에 참여하는 분자. 그 유전자가 MHC 영역 안에 있고, interferon이 transcription을 높인다.", s=[3, 6], g=[7, 9]),
        TERM("MHC polymorphism", "같은 유전자 자리의 allele이 집단 안에 여러 형태로 존재하는 것. MHC 유전자는 알려진 가장 다형성이 큰 유전자이다.", s=[3, 4], g=[3, 13]),
        TERM("CD1 molecule", "peptide가 아니라 lipid / glycolipid 항원을 제시하는 MHC class I-like 분자.", s=[3, 16], g=[37]),
        TERM("동종이식편반응 (alloreactivity)", "다른 개체의 MHC에 대한 강한 T세포 반응. 한 개체 T세포의 1~10%가 반응한다.", s=[3, 9], g=[25, 28]),
        TERM("초항원 (superantigen)", "peptide 처리 없이 TCR과 MHC에 직접 결합해 많은 T세포를 한꺼번에 활성화하는 물질.", s=[3, 10], g=[29, 30]),
    ], role="front"))

    # =========================================================== Ch 1 · § 1  도입
    top.append(T("도입: 왜 MHC는 여러 종류일까?", CH1, [1, 2, 4, 5], [
        STAR("이야기의 출발점 — 지난 시간에서 오늘의 질문으로", s=[1, 2], g=[1]),
        P("지난 시간에 우리는 항원이 세포 안에서 처리되어 MHC에 올라가는 과정을 보았다. 그렇다면 이야기는 자연스럽게 다음 질문으로 이어진다. "
          "교수님은 오늘 수업을 이렇게 여신다. “**MHC 자체는 왜 이렇게 여러 종류가 있는가, 그리고 T세포는 실제로 무엇을 인식하는가.**” "
          "먼저 MHC 유전자의 구성과 기능을 살펴보고, 마지막에는 조금 특이한 형태의 T세포 인식까지 이야기하겠다고 하셨다.", s=[1], g=[1]),
        ROW(S, 2, "- 이번 파트(Chapter 6 part II)는 학습성과 3(MHC 유전자 부위의 구성과 다형성)과 4(항원제시 이외의 기능)에 해당한다.\n"
                  "- 학습성과 1·2(class I·II의 항원 처리와 제시)는 앞 시간에 다룬 내용이다.", g=[1]),
        STAR("감염원의 입장에서 생각해 보자", s=[4], g=[2]),
        P("교수님은 한번 **감염원의 입장**에서 생각해 보라고 하셨다. 우리 몸의 단백질 조각이 MHC에 얹혀 T세포에 보이면 면역계는 그것을 알아본다. "
          "감염원은 당연히 그 경로를 피하고 싶을 것이다. 그런데 사람에게 MHC가 **딱 한 종류**뿐이라면 어떻게 될까? "
          "그 결합을 피하는 돌연변이가 한 번 생기는 순간, 그 돌연변이는 **모든 사람에게** 통할 가능성이 커진다.", s=[4], g=[2]),
        P("그래서 실제 우리 몸은 두 겹으로 대비하고 있다. ① 한 사람 안에서도 **여러 MHC 유전자**가 발현되고, ② 사람 사이에서는 같은 유전자의 **대립유전자(allele) 종류가 아주 다양**하다. "
          "교수님은 “이 두 가지가 오늘의 중요한 출발점”이라고 하셨다.", s=[4], g=[2]),
        ROW(S, 4, "- 자기 단백질 조각이 MHC에 얹혀 T세포에 보이면 면역계가 알아본다 → 감염원은 그 경로를 피하고 싶어 한다.\n"
                  "- 사람에게 MHC가 **한 종류**뿐이라면, 그 결합을 피하는 돌연변이 하나가 **모든 사람에게** 통할 가능성이 커진다.\n"
                  "- 실제로는 ① 한 사람 안에서도 여러 MHC 유전자가 발현되고(polygenic) ② 사람 사이에 allele 종류가 아주 다양하다(polymorphic).\n"
                  "- {r|이 두 가지가 오늘 강의의 출발점}이다.", g=[2], drop=("퀴즈",)),
        STAR("그 두 겹을 부르는 이름부터 정리하고 가자", s=[4], g=[3]),
        P("이야기를 따라가려면 용어를 먼저 구분해 두어야 한다. **Polygenic**은 한 개체가 서로 다른 MHC 유전자를 여러 개 가진다는 뜻이고, "
          "**polymorphic**은 같은 유전자 자리라도 집단 안에 여러 형태의 allele이 존재한다는 뜻이다. 교수님은 “둘을 혼동하면 뒤의 설명이 어려워진다”고 경고하셨다. "
          "여기에 하나가 더 있다. 한쪽 염색체 위에 모여서 함께 물려받는 MHC allele의 조합을 **haplotype**이라고 한다.", s=[4], g=[3]),
        ADV("**‘한 사람 안의 유전자 수’(polygenic)와 ‘집단 안의 allele 종류’(polymorphic)** 로 갈라서 기억하자.", s=[4], g=[3]),
        STAR("오늘의 여정: 세 부분", s=[5], g=[4]),
        P("오늘 이야기는 크게 세 부분으로 흐른다. 먼저 **6번 염색체의 MHC 영역**을 살펴보고, 이어서 **다양성이 실제 항원 인식과 어떤 관계인지** 본다. "
          "그다음 **T세포의 MHC restriction**을 설명하고, 이 원칙의 예외처럼 보이는 **이식 반응과 superantigen**을 만난다. "
          "끝부분에서는 HLA-E, F, G나 CD1 같은 **비전형적인 분자**도 다룬다. 교수님이 특히 당부하신 것은 "
          "“이름만 외우기보다 **왜 다른 역할을 하는지 연결**해서 이해해 보라”는 것이다.", s=[5], g=[4]),
        ROW(S, 5, "- 슬라이드 개요에서 오늘의 위치는 ‘MHC class I and II genes and their tremendous variability’와 ‘Ligands for unconventional classes of T cells’이다.\n"
                  "- 이식 조직에 대한 강한 효과(주조직적합항원)도 같은 맥락에서 이야기한다.", g=[4]),
        QUIZ("If having three MHC class I loci is better than having one, why are there not far more?  (MHC class I loci가 1개보다 3개가 낫다면, 왜 훨씬 더 많지 않을까?)",
             answer="MHC 분자가 하나 추가될 때마다 그 MHC에 얹힌 자기 peptide에 반응하는 T세포를 모두 제거해야 자기관용이 유지된다 → 많을수록 좋은 것이 아니라 균형(Balance)이 필요하다. (슬라이드 6-15, 본문 ‘MHC 다양성의 이점과 한계’에서 다시)",
             s=[4, 11], g=[33]),
    ], basics_title="이번 파트의 출발점", basics=[
        "Chapter 6 part II는 MHC 유전자 영역의 구성과 다양성(학습성과 3), 그리고 MHC의 항원제시 이외의 기능(학습성과 4)을 다룬다.",
        "감염원은 MHC에 얹히는 경로를 피하려 하므로, MHC가 한 종류뿐이면 돌연변이 하나가 모든 사람에게 통한다.",
        "그래서 MHC는 한 사람 안에서 여러 유전자(polygenic), 사람 사이에서는 allele이 다양(polymorphic)하다.",
    ], tip="슬라이드 퀴즈(‘왜 MHC class I loci는 3개보다 더 많지 않을까?’)의 답은 ‘MHC 다양성의 이점과 한계’ 쪽에서 확인하세요."))

    # =========================================================== Ch 1 · § 2  유전자 영역
    s6 = slide_lines(S, 6)
    top.append(T("MHC 유전자 영역의 구성", CH1, [6], [
        STAR("그럼 이 유전자들은 어디에 있을까? — 6번 염색체", s=[6], g=[5]),
        P("이제 그림으로 들어가 보자. 인간의 MHC 유전자는 **6번 염색체**에 있고, 사람에서는 흔히 **HLA(human leukocyte antigen)** 라고 부른다. "
          "이 좁은 영역에 여러 유전자가 빽빽하게 모여 있는데, 교수님은 크게 **class I, class II, class III 영역**으로 나누어 보라고 하셨다.", s=[6], g=[5]),
        STAR("class I은 ‘다리 하나’, class II는 ‘다리 두 개’", s=[6], g=[6]),
        P("고전적 **class I**은 HLA-A, HLA-B, HLA-C이다. 한 개의 큰 α chain에 β2-microglobulin이 붙은 구조를 떠올리면 되고, "
          "교수님은 기억하기 쉽게 {r|‘다리 하나짜리’}라고 생각해도 좋다고 하셨다. **class II**는 HLA-DR, HLA-DP, HLA-DQ이며 α chain과 β chain이 짝을 이루므로 {r|‘다리 두 개짜리’}로 기억하면 된다. "
          "여기서 중요한 것은 이름 암기가 아니라 **유전자 영역과 실제 분자의 기능을 구분**하는 것이다.", s=[6], g=[6]),
        ROW(S, 6, "- 인간 MHC 유전자는 **6번 염색체**에 있고 사람에서는 HLA(human leukocyte antigen)라고 부른다. 이 영역은 class I · II · III로 나누어 본다.\n"
                  "- class I α chain 유전자와 class II α·β chain 유전자는 MHC 영역 안에 **연결**되어 있고, β2-microglobulin(15번)·invariant chain(5번) 유전자는 다른 염색체에 있다(생쥐는 2번·18번).\n"
                  "- 고전적 **class I = HLA-A, B, C** (큰 α chain 1개 + β2-microglobulin, {r|‘다리 하나짜리’}).\n"
                  "- 고전적 **class II = HLA-DR, DP, DQ** (α chain과 β chain이 짝, {r|‘다리 두 개짜리’}).\n"
                  "- HLA-DR cluster에는 추가 β chain 유전자가 있는 사람이 많다. 모든 class I·II 분자가 T세포에 peptide를 제시하지만 분자마다 결합하는 peptide 범위가 다르다.",
            g=[5, 6], left=s6[:7]),
        STAR("그림을 자세히 보면 — class II region에는 DR·DQ·DP만 있지 않다", s=[6], g=[7]),
        P("그림의 class II region을 자세히 보면 DR, DQ, DP만 있는 것이 아니다. 앞 시간에 언급한 **HLA-DM, HLA-DO**도 이 영역에 있다. "
          "이 분자들은 고전적인 항원제시용 class II와는 **구분**해야 하지만, peptide editing 같은 항원제시 과정의 조절에 관여한다. "
          "**TAP**처럼 항원 처리에 참여하는 분자들도 이 유전자 영역 안에서 함께 볼 수 있다.", s=[6], g=[7]),
        STAR("시험에서 놓치기 쉬운 점, 그리고 생쥐 이름", s=[6], g=[8]),
        P("교수님은 문제에서 **‘MHC class II 분자’** 를 묻는 것인지 **‘class II region에 존재하는 유전자’** 를 묻는 것인지 잘 보라고 하셨다. “두 질문은 같지 않다.” "
          "또 사람과 실험동물의 이름도 구별해야 한다. 사람은 HLA, 생쥐는 **H-2**이고 생쥐의 MHC 영역은 {r|17번 염색체}에 있다. "
          "생쥐 class I에는 H-2D, H-2L이, class II에는 H-2A와 H-2E 등이 나오는데, 나중에 실험 그림을 읽으려면 이 차이를 알아 두어야 한다.", s=[6], g=[8]),
        ADV("문제 문구가 ‘분자’인지 ‘영역의 유전자’인지부터 확인하자. 이름 암기보다 **영역과 기능의 구분**이 더 중요하다.", s=[6], g=[6, 8]),
        STAR("한 걸음 물러나 전체 지도를 보면 — 길게 이어진 하나의 영역", s=[6], g=[9, 10]),
        P("이번에는 조금 더 확대된 유전자 지도이다. 위아래로 나뉘어 있지만 사실은 **길게 연결된 하나의 영역**이다. class I과 class II 유전자만 단정하게 모여 있는 것이 아니라, "
          "사이사이에 항원을 가공하고 제시하는 데 관여하는 여러 유전자가 섞여 있다. 그림에서 **TAP**, **proteasome** 성분, 그리고 **TNF** 같은 유전자를 찾아볼 수 있다.", s=[6], g=[9]),
        P("**class I region**에는 전형적인 A, B, C 말고도 **HLA-E, HLA-F, HLA-G**가 있다. 이들은 뒤에서 **class Ib(비고전적 MHC class I)** 를 이야기할 때 다시 만나게 된다. "
          "**class III region**에는 **MIC-A, MIC-B** 같은 분자가 표시되어 있다. 교수님은 “하나의 영역 안에 여러 면역 관련 유전자가 함께 모여 있다는 점을 기억하면, "
          "뒤에서 면역 반응이 **함께 조절**된다는 설명이 이해될 것”이라고 하셨다.", s=[6], g=[10]),
        STAR("그래서 감염이 생기면 — 인터페론과 MHC 발현", s=[6], g=[11, 12]),
        P("한 영역에 모여 있으니 조절도 함께 일어난다. 감염이 생기면 여러 면역 관련 유전자의 발현이 변하는데, 특히 **인터페론**이 중요하다. "
          "강의 자료는 interferon α, β, γ가 MHC 관련 유전자의 발현을 조절한다고 제시하고, 그 결과 감염된 세포가 **바이러스 단백질에서 유래한 peptide를 제시할 기회가 늘어난다**고 설명한다.", s=[6], g=[11]),
        P("class II와 관련해서는 **CIITA**라는 이름을 봐 두자. MHC class II의 전사 조절에 중요한 co-activator이다. interferon-γ는 class II 관련 유전자 발현과 연결해 기억하면 된다. "
          "다만 교수님은 “지금 모든 조절 경로를 외울 필요는 없다”고 하셨다. 잡아야 할 큰 흐름은 "
          "{g|‘항원제시 분자만 따로 만들어지는 것이 아니라, 가공과 제시에 필요한 여러 구성요소가 연동되어 조절된다’}는 것이다.", s=[6], g=[12]),
        ROW(S, 6, "- 감염이 생기면 interferon α·β·γ가 MHC 관련 유전자의 발현을 조절한다. IFN으로 class I α chain·β2-microglobulin, proteasome, tapasin, TAP 유전자의 transcription이 크게 늘고, 감염 세포가 바이러스 peptide를 제시할 기회가 늘어난다.\n"
                  "- 인터페론은 바이러스 감염 초기에 만들어지고, MHC 발현이 늘면 모든 세포가 바이러스 단백질을 가공해 virus-derived peptide를 표면에 제시할 수 있다.\n"
                  "- class II는 invariant chain, DMα, DMβ, DOα(DOβ는 제외)와 함께 IFN-γ(활성화된 TH1, CD8 T cell, NK cell이 생산)로 같이 늘어난다. **CIITA**(class II transactivator)는 class II 유전자의 positive transcriptional co-activator이다.\n"
                  "- {g|모든 조절 경로를 외울 필요는 없다.}",
            g=[11, 12], left=s6[7:], title="6-10 (이어서) interferon과 MHC 발현"),
        P("이제 질문이 남는다. 이 유전자들 사이에는 왜 그렇게 많은 차이가 존재할까? 이야기는 다음 장면, **다형성**으로 넘어간다.", s=[6], g=[12]),
    ], basics_title="인간 MHC의 구성", basics=[
        "사람 MHC(HLA)는 6번 염색체에 있고, 약 4~7백만 bp·200개 이상의 유전자가 class I · II · III 영역에 모여 있다.",
        "class I = HLA-A, B, C(α chain + β2-microglobulin, ‘다리 하나짜리’), class II = HLA-DR, DP, DQ(α·β chain 한 쌍, ‘다리 두 개짜리’).",
        "같은 영역에 HLA-DM·DO, TAP, proteasome, TNF, HLA-E/F/G(class Ib), MIC-A/B가 함께 있다 — 유전자 영역과 분자의 기능은 다르다.",
    ], tip="문제 문구가 ‘class II 분자’인지 ‘class II region의 유전자’인지부터 확인하세요. 사람 = HLA(6번), 생쥐 = H-2(17번)도 함께.",
        flags=["인터페론 관련 세부 내용은 원자료에서 일부가 PPT에만 있고 강의에서는 다루지 않았다고 표시됨(부록 참고)."]))

    # =========================================================== Ch 1 · § 3  polymorphism / polygeny
    top.append(T("다형성(polymorphism)과 polygeny", CH1, [7], [
        STAR("가장 중요한 두 단어가 등장한다", s=[7], g=[13]),
        P("교수님은 “여기서 제일 중요한 두 단어가 나온다”고 하셨다. **Polymorphism**은 동일한 유전자 자리의 allele이 집단 전체에서 여러 형태로 존재한다는 뜻이고, "
          "**polygeny**는 한 개인 안에 서로 다른 MHC 유전자가 여러 개 있다는 뜻이다. 예를 들어 HLA-A와 HLA-B는 서로 다른 유전자(polygeny)이고, "
          "HLA-A나 HLA-B 각각에도 다양한 allele(polymorphism)이 있을 수 있다. “이 두 층위의 다양성이 **함께 작동**하는 것이다.”", s=[7], g=[13]),
        STAR("부모에게서 받은 것이 모두 발현된다 — codominant", s=[7], g=[14]),
        P("여기에 **발현 방식**이 더해진다. 발현은 **codominant**이다. 어머니에게서 받은 것과 아버지에게서 받은 것이 **둘 다 발현**될 수 있다는 뜻이다. "
          "그래서 한 개체에서 실제로 만들어지는 MHC 분자의 종류가 더 늘어나고, 한 사람의 MHC 조합이 다른 사람과 같기 어려운 이유도 여기에 있다.", s=[7], g=[14]),
        ROW(S, 7, "- **Polymorphism(다형성)**: 동일한 유전자 자리의 allele이 집단 전체에서 여러 형태로 존재한다. 예) HLA-B 하나에도 다양한 allele이 있다.\n"
                  "- **Polygeny**: 한 개인 안에 서로 다른 MHC 유전자(HLA-A, HLA-B ...)가 여러 개 존재한다.\n"
                  "- 두 층위의 다양성이 **함께** 작동한다.\n"
                  "- 대부분의 개인은 heterozygous이고, 한쪽 염색체에 모여 있는 allele의 조합이 **haplotype**이다.\n"
                  "- 발현은 **codominant**: 어머니와 아버지에게서 받은 allele이 모두 발현되어, 한 사람이 실제로 만드는 MHC 분자의 종류가 늘고 다른 사람과 조합이 같기 어렵다.",
            g=[3, 13, 14], drop=("Fig. 6.18",)),
        ADV("교수님이 종종 있는 혼동으로 짚으신 부분이다. ‘한 개체의 유전자 수가 많다’(polygeny)와 ‘집단 전체의 allele 종류가 많다’(polymorphism)를 **바꿔 쓰지 말고 반드시 구분**하자.", s=[7], g=[14]),
        STAR("다양성은 어느 쪽에 더 몰려 있을까?", s=[7], g=[15, 16]),
        P("그렇다면 다형성은 모든 MHC 분자에서 똑같이 클까? 아니다. 정리본이 강조하는 것은 **고전적 class I 쪽의 다양성이 크고, class Ib에서는 상대적으로 제한적**이라는 점이다. "
          "비교할 때는 class I에서는 **HLA-B, A, C 순서**로, class II에서는 **DRB, DQB, DPB**를 보라고 되어 있다. "
          "교수님은 “숫자나 대립유전자 개수는 시점과 자료에 따라 달라지므로, 기계적으로 최신 개수까지 외우기보다 **상대적인 경향과 기능**을 먼저 이해하라”고 하셨다.", s=[7], g=[15]),
        P("class II의 경우에는 다형성이 {r|β chain 쪽에 집중}되어 있다는 설명이 붙는다. 왜 중요할까? 뒤의 그림에서 보겠지만 polymorphism은 특히 **peptide가 들어가는 결합 부위**와 관련되어 있다. "
          "같은 감염원에서 나온 peptide라도 **사람의 MHC 종류에 따라 결합 가능성이 달라질 수 있다**는 뜻이다.", s=[7], g=[16]),
        STAR("그 다양성은 어디서 왔을까? — gene conversion", s=[7], g=[17]),
        P("다양성의 기원도 궁금해진다. 강의에서는 **gene conversion**을 중요한 기전으로 소개한다. 서로 비슷한 서열을 가진 유전자들 사이에서 일부 유전정보가 바뀌면 원래 유전자와 조금 다른 형태가 만들어진다. "
          "정리본은 **감수분열(meiosis)** 과정에서 일어나는 이런 유사 서열 사이의 변화가 MHC 다양성에 기여했다고 설명한다.", s=[7], g=[17]),
        P("{g|allele의 개수는 시점과 자료에 따라 달라진다. 최신 개수를 외우기보다 어느 쪽이 더 다양한가를 먼저 이해하자.}", s=[7], g=[15]),
    ], basics_title="Polymorphism과 polygeny", basics=[
        "Polymorphism = 같은 자리의 allele이 집단에 여러 형태(집단 수준), polygeny = 한 개인 안의 서로 다른 MHC 유전자 여러 개(개체 수준). 둘이 함께 작동한다.",
        "대부분의 개인은 heterozygous이고, 한쪽 염색체의 allele 조합이 haplotype이며 발현은 codominant이다.",
        "다형성은 class I > class Ib이고(class I: B, A, C 순 / class II: DRB, DQB, DPB, β chain에 집중), 다양성은 gene conversion으로 설명한다.",
    ], tip="allele 개수는 외우지 말고 ‘어느 쪽이 더 다양한가’(순서)와 ‘β chain에 몰려 있다’만 확실히."))

    # =========================================================== Ch 1 · § 4  다형성과 항원 인식
    s8 = slide_lines(S, 8)
    top.append(T("다형성이 항원 인식에 미치는 영향", CH1, [8], [
        STAR("그래서 다양성이 달라지는 곳은 정확히 어디일까?", s=[8], g=[18]),
        P("이번에는 **어디가 달라졌는지** 보자. 정리본에 따르면 **class I은 α1·α2 영역, class II는 특히 β1 영역**이 peptide 결합과 관련된 다양성을 보이는 부분이다. "
          "결합 홈의 구조가 달라지면 결합하는 peptide의 종류도 달라진다. 그래서 교수님은 이렇게 정리하셨다. "
          "“MHC polymorphism은 그냥 유전자 이름의 다양성이 아니라, 실제로 **어떤 항원을 T세포에 보여줄 수 있는가와 직결된 기능적인 다양성**이다. {r|이 연결이 오늘의 핵심이다.}”", s=[8], g=[18]),
        ROW(S, 8, "- {u|class I은 α1·α2 영역, class II는 β1 영역}이 peptide 결합과 관련된 다양성을 보이는 부분이다.\n"
                  "- peptide는 결합 홈 안의 pocket과 **anchor residue**의 상호작용으로 결합하고, 한 MHC isoform에 결합을 허용하는 anchor residue의 세트가 **sequence motif**이다.\n"
                  "- {g|슬라이드에만 있음} Ir gene 결함은 모든 MHC 유전자좌가 동형접합인 inbred 생쥐에서 흔하다. MHC 다형성은 한 개체가 충분히 다양한 MHC 분자를 갖게 해 이런 무반응이 일어나기 어렵게 한다.",
            g=[16, 18, 19], left=s8[:4]),
        STAR("peptide 서열표를 읽는 법 — anchor residue", s=[8], g=[19]),
        P("그렇다면 MHC에 결합하는 peptide들은 서로 어떻게 닮았을까? 교수님은 peptide 서열을 비교한 표를 보여 주며, 하나의 MHC에 결합한다고 해서 **전체 아미노산 서열이 같아야 하는 것은 아니다**라고 하셨다. "
          "대신 **특정 위치에 비슷한 성질의 아미노산이 반복**해서 나타난다. 정리본은 예로 **2번, 5번, 8번 위치**를 짚는다. "
          "이런 위치에서 MHC와 중요한 접촉을 형성하는 잔기를 **anchor residue**라고 한다.", s=[8], g=[19]),
        STAR("외울 것은 번호가 아니라 결합의 원리", s=[8], g=[20]),
        P("“여기서 외워야 할 것은 특정 번호 자체보다 **결합의 원리**”라고 하셨다. 어떤 MHC allele은 특정한 **peptide motif**를 선호하고, 그 motif를 가진 서로 다른 항원 peptide들이 결합할 수 있다. "
          "그러니 MHC 종류가 바뀌면 잘 결합하는 peptide의 집합도 달라진다. 이 원리는 **종양 항원 예측이나 백신 후보 peptide를 고르는 전략**에도 응용된다. "
          "표를 볼 때는 전체 서열보다 **공통된 위치와 성질을 먼저** 찾아보라는 것이 교수님의 요령이다.", s=[8], g=[20]),
        ADV("번호(2·5·8)가 아니라 ‘MHC마다 선호하는 motif가 다르다’는 **원리**를 가져가자.", s=[8], g=[20]),
    ], basics_title="다형성의 기능적 의미", basics=[
        "다형성은 peptide 결합 부위에 몰려 있다 — class I은 α1·α2, class II는 β1.",
        "결합 홈의 구조가 달라지면 결합하는 peptide가 달라지므로, MHC 다형성은 ‘어떤 항원을 보여줄 수 있는가’와 직결된 기능적 다양성이다.",
        "peptide는 anchor residue(예: 2·5·8번 위치)와 결합 pocket의 상호작용으로 결합하고, 이 공통 패턴이 sequence motif이다.",
    ], tip="번호(2·5·8)가 아니라 ‘MHC마다 선호하는 motif가 다르다’는 원리를 기억하세요."))

    # =========================================================== Ch 2 · § 1  MHC restriction
    top.append(T("MHC restriction", CH2, [8], [
        STAR("이제 T세포의 눈으로 보자 — 두 가지 조건", s=[8], g=[21]),
        P("지금까지는 MHC가 얼마나 다양한지를 보았다. 이제 **T세포가 실제로 무엇을 인식하는가**로 넘어간다. 교수님은 “T세포는 단순히 외래 peptide만 인식하는 것이 아니다”라고 하셨다. "
          "T세포가 반응하려면 **두 조건이 함께** 맞아야 한다. ① **TCR이 맞는 peptide**가 있어야 하고, ② 그 peptide를 제시하는 **MHC도 자신이 인식하도록 교육받은 종류(자기 MHC)** 여야 한다. "
          "“이 두 조건을 같이 생각하는 것이 중요하다.”", s=[8], g=[21]),
        STAR("조합을 바꿔 가며 비교해 보면", s=[8], g=[22]),
        P("그림에서 몇 가지 조합을 비교해 보자. **자기 MHC에 적절한 peptide**가 올라가면 인식이 가능하다. 반대로 **peptide가 같아도 MHC가 맞지 않으면** 일반적인 자기 MHC 제한 반응이 일어나지 않는다. "
          "또 **자기 MHC라도 그 TCR이 인식하지 못하는 peptide**라면 역시 반응하지 않는다. 그래서 교수님은 T세포 인식의 대상이 분리된 peptide 하나가 아니라 "
          "{r|peptide–MHC 복합체}라고 생각하는 편이 정확하다고 하셨다.", s=[8], g=[22]),
        ROW(S, 8, "- 자기 MHC + 그 TCR이 아는 peptide → **인식(Recognition)**.\n"
                  "- peptide가 같아도 MHC가 자기 것이 아니면 → 인식 X(No recognition).\n"
                  "- 자기 MHC라도 그 TCR이 인식하지 못하는 peptide가 올라가면 → 인식 X.\n"
                  "- {r|즉 T세포 인식의 대상은 peptide 하나가 아니라 peptide–MHC 복합체}이다.",
            g=[22], left=s8[4:], title="6-12 (이어서) MHC restriction — Fig. 6.23"),
        STAR("지금은 상식이지만 처음에는 큰 발견이었다", s=[8], g=[23, 24]),
        P("지금은 기본 지식처럼 들리지만 처음 밝혀졌을 때는 굉장히 중요한 발견이었다. **Peter Doherty와 Rolf Zinkernagel**의 연구가 대표적인 예이고, 이들은 1996년 Nobel상을 받았다. "
          "특정 항원에 반응하는 T세포가 어떤 세포에서나 똑같이 반응하는 것이 아니라 **적절한 자기 MHC 환경에서 항원이 제시되어야** 한다는 사실을 보여 주었다.", s=[8], g=[23]),
        P("교수님은 실험의 모든 세부를 따라갈 필요는 없다고 하시면서, **실험군을 비교하는 사고방식**을 익히라고 하셨다. "
          "{g|‘항원은 같고 MHC가 다른 경우 / MHC는 같고 항원이 다른 경우 / 두 조건이 모두 맞는 경우’로 나누면 무엇이 T세포 반응을 결정하는지 알 수 있다.}", s=[8], g=[24]),
        STAR("그런데 여기서 의문이 생긴다", s=[8], g=[24]),
        P("자기 MHC에 제한되어 반응한다면, **왜 장기 이식 때는 타인의 MHC에 엄청난 반응이 나타나는 걸까?** "
          "이야기는 이제 ‘예외처럼 보이는 현상’으로 넘어간다.", s=[8], g=[24]),
    ], basics_title="MHC restriction", basics=[
        "T세포가 반응하려면 ① TCR이 특이성을 갖는 peptide ② 그 peptide를 제시하는 자기 MHC, 두 조건이 함께 필요하다 = MHC restriction.",
        "자기 MHC + 맞는 peptide → 인식 O / peptide가 같아도 MHC가 다르면 X / 자기 MHC라도 TCR이 모르는 peptide면 X.",
        "T세포 인식의 대상은 peptide 하나가 아니라 peptide–MHC 복합체이다 (Doherty·Zinkernagel, 1996년 Nobel상).",
    ], tip="원칙은 ‘두 조건’ 한 줄. 이어지는 두 예외(alloreactivity, superantigen)가 왜 예외인지 이 원칙에 비춰서 보세요."))

    # =========================================================== Ch 2 · § 2  alloreactivity
    top.append(T("예외 1 · Alloreactivity (동종이식편반응)", CH2, [9], [
        STAR("첫 번째 예외: 타인의 MHC에 대한 강한 반응", s=[9], g=[25]),
        P("**Alloresponse**는 다른 개체의 MHC에 대해 일어나는 강한 T세포 반응이다. 같은 종 사이의 이식은 **allogeneic**, 서로 다른 종 사이의 이식은 **xenogeneic(xenograft)** 이라고 부른다. "
          "이식에서 가장 중요한 문제가 바로 이 ‘서로 다른 MHC를 인식하는 T세포의 반응’이다.", s=[9], g=[25]),
        STAR("자기 MHC만 알도록 교육받았는데 왜 타인의 MHC에 반응할까?", s=[9], g=[26]),
        P("교수님은 이 모순을 이렇게 풀어 주셨다. T세포 수용체는 본래 어느 정도의 **교차 반응성**을 가질 수 있다. 자기 MHC와 구조가 비슷하면서도 다른 MHC에 "
          "**예기치 않게 강하게 결합**하는 경우가 있다. 정리본에서는 alloreactive T cell이 상당한 비율로 존재해서, 일반적인 peptide 특이적 반응보다 **이식편에 대한 반응이 훨씬 크게** 나타날 수 있다고 설명한다.", s=[9], g=[26]),
        ROW(S, 9, "- 공여자의 MHC가 수혜자와 다르면 이식 장기는 빠르게 거부된다. 어느 개인에게나 nonself(allogeneic) MHC에 반응하는 T세포가 **대량** 있기 때문이다.\n"
                  "- 슬라이드의 positive selection 설명도 같은 이야기다: 자기 MHC와 약하게 상호작용하는 TCR이 생존 신호를 받으므로, 한 MHC와 상호작용하는 TCR은 다른 nonself MHC 변이체와도 교차 반응하기 쉽다.\n"
                  "- TCR 유전자(germline-encoded CDR1·CDR2 잔기)가 MHC 분자를 인식하는 능력을 본래 지니고 있다 (Fig. 6.24).",
            g=[25, 26, 28]),
        STAR("이 반응을 어떻게 눈으로 확인할까? — mixed lymphocyte reaction", s=[9], g=[27]),
        P("이 반응을 관찰하는 고전적인 실험이 **mixed lymphocyte reaction(MLR)** 이다. MHC가 다른 두 개체의 림프구를 섞어 놓고 반응을 본다. "
          "그런데 양쪽이 모두 활발히 증식하면 **어느 쪽의 반응인지 구별하기 어렵다.** 그래서 한쪽은 **irradiation이나 mitomycin C**로 처리해 증식하지 못하게(cytostatic) 한다. "
          "그러면 처리하지 않은 쪽의 반응만 관찰할 수 있다.", s=[9], g=[27]),
        STAR("얼마나 많은 T세포가 반응할까?", s=[9], g=[28]),
        P("정리본은 alloreactive T cell이 **한 개체 전체 T세포의 약** {r|1~10%}라는 범위를 소개하고(alloreaction, alloreactivity), TCR의 **CDR 부위**가 MHC–peptide 복합체와 상호작용한다고 덧붙인다. "
          "교수님은 여기서 흉선에서 일어나는 **positive selection과 negative selection**을 떠올려 보라고 하셨다. "
          "자기 MHC에 적절히 반응하는 세포가 남도록 선택되지만, {r|그것이 타인의 MHC에 대한 반응까지 완전히 없애 준다는 뜻은 아니다.} "
          "“이식 거부반응을 이해할 때 이 점이 중요하다.”", s=[9], g=[28]),
    ], basics_title="Alloreactivity", basics=[
        "Alloresponse = 다른 개체의 MHC에 대한 강한 T세포 반응. 같은 종 사이 이식은 allogeneic, 다른 종 사이는 xenogeneic(xenograft).",
        "이식 장기가 빨리 거부되는 것은 사람마다 nonself MHC에 반응하는 alloreactive T cell(전체 T세포의 1~10%)이 매우 많기 때문이다.",
        "MLR로 관찰하며 양쪽 증식을 막기 위해 한쪽을 irradiation 또는 mitomycin C로 처리한다. TCR의 CDR1·CDR2가 MHC 인식 능력을 본래 지닌다.",
    ], tip="‘왜 1~10%나 되나’ = TCR의 교차 반응성 + 자기 MHC와 닮은 타인 MHC. 선택 과정이 이 반응을 없애 주지 못한다는 점까지."))

    # =========================================================== Ch 2 · § 3  superantigen
    s10 = slide_lines(S, 10)
    top.append(T("예외 2 · Superantigen (초항원)", CH2, [10], [
        STAR("두 번째 예외: 정상적인 항원제시를 건너뛰는 항원", s=[10], g=[29]),
        P("두 번째 예외는 **superantigen**이다. 정상적인 항원제시는 peptide가 만들어져 MHC의 결합 홈에 자리하고, 특정 TCR이 그 복합체를 인식하는 과정이다. "
          "그런데 superantigen은 정리본의 그림처럼 일반적인 peptide 처리와 결합 방식을 따르지 않고 **MHC class II와 TCR을 연결**해서 **많은 T세포를 동시에** 활성화한다.", s=[10], g=[29]),
        STAR("왜 문제가 되는가", s=[10], g=[30]),
        P("이 반응은 특정 항원을 가진 병원체만 효율적으로 제거하는 정교한 반응과 다르다. 많은 T세포가 한꺼번에 자극되면 **염증성 신호가 크게 발생**하고 숙주에 심한 부담이 된다. "
          "교수님은 정상적인 항원 특이성과 비교할 때 superantigen의 핵심을 {r|‘비특이적인 대규모 활성화’}라고 생각해 두라고 하셨다. "
          "그림에서도 **결합 위치가 일반적인 peptide–MHC–TCR 인식과 다르다**는 점을 먼저 보면 된다.", s=[10], g=[30]),
        ROW(S, 10, "- Superantigen은 allogeneic MHC에 대한 반응과 **비슷한 크기**의 일차 T세포 반응을 일으킨다.\n"
                   "- peptide로 가공되어 MHC에 잡히는 과정 없이 T세포에 인식된다.\n"
                   "- 많은 T세포가 한꺼번에 자극되어 염증성 신호가 크게 발생하고, 숙주에 심한 부담이 된다 (CD4 T cell의 cytokine 대량 생산 → 전신 독성과 적응면역 반응의 억제).\n"
                   "- 병원체 입장에서만 유리한 반응이며, 병원체에 대한 적응면역 반응을 일으키지 않는다. 세균, mycoplasma, 바이러스 등 여러 병원체가 만든다.\n"
                   "- {r|핵심 = 비특이적인 대규모 T세포 활성화.}",
            g=[29, 30], left=s10[:1] + s10[2:5]),
        ADV("‘정상 항원 = peptide 처리 + 특정 TCR(특이적)’, ‘superantigen = 처리 없이 TCR과 MHC에 직접 결합(비특이적)’. 이 대비를 한 줄로 가져가자.", s=[10], g=[30]),
        STAR("대표적인 예 두 가지", s=[10], g=[31]),
        P("대표적인 superantigen으로 **staphylococcal enterotoxin(SE)** 과 **TSST-1**(Staphylococcus aureus)이 나온다. 전자는 **식중독**과, 후자는 **toxic shock syndrome**과 관련된 독소이다. "
          "{r|교수님은 이름을 구별해서 기억해 두라고 하셨다.}", s=[10], g=[31]),
        REF("슬라이드에만 있는 내용: MHC-identical하지만 유전적으로 다른 생쥐 림프구의 MLR에서 반응을 일으키는 **minor lymphocyte stimulating (Mls) antigen**은 mouse mammary tumor virus 같은 retrovirus가 생쥐 염색체에 안정적으로 끼어들어 만든 것이다 — 강의에서는 언급하지 않았다.", s=[10]),
    ], basics_title="Superantigen", basics=[
        "Superantigen은 peptide로 처리되지 않고 TCR과 MHC(class II)에 직접 결합해 많은 T세포를 한꺼번에 활성화한다.",
        "반응 크기는 allogeneic MHC에 대한 일차 반응과 비슷하지만 비특이적이고, 병원체 제거에는 도움이 안 되며 숙주에 독성(cytokine 폭발)을 준다.",
        "대표 예: staphylococcal enterotoxin(식중독), TSST-1(toxic shock syndrome).",
    ], tip="SE = 식중독, TSST-1 = toxic shock syndrome. 이름을 짝지어 외우세요."))

    # =========================================================== Ch 2 · § 4  이점과 한계
    top.append(T("MHC 다양성의 이점과 한계", CH2, [11, 12], [
        STAR("다시 처음 질문으로 — 다양성은 집단에 무엇을 주는가", s=[11], g=[32]),
        P("두 가지 예외를 지나 처음 이야기한 MHC polymorphism으로 돌아왔다. 사람 집단에서 MHC가 다양하면 **모든 사람이 똑같은 감염원 회피 전략에 취약해질 가능성**이 줄어든다. "
          "자료는 **EBV의 면역 회피와 특정 인구집단의 HLA 분포**, 그리고 **서아프리카에서 HLA-B53과 중증 말라리아의 관련성**을 사례로 든다. "
          "교수님은 사례의 모든 수치보다 중요한 메시지가 "
          "“**병원체와 숙주의 유전적 다양성이 서로 영향을 주고받는다**는 것”이라고 하셨다. 다양성은 감염원 방어의 범위를 넓히는 데 기여한다.", s=[11], g=[32]),
        ROW(S, 11, "- **Epstein–Barr virus (EBV)**: 중국 남동부와 파푸아뉴기니의 고립 집단은 약 **60%**가 HLA-A11 allele을 가지고 있다. 이 집단의 EBV 분리주 중 다수가 HLA-A11이 제시하는 우세 epitope에 돌연변이를 가져, 변이 peptide는 HLA-A11에 더 이상 결합하지 못하고 HLA-A11-restricted T세포가 인식하지 못한다 → 면역 회피와 인구집단의 HLA 분포가 연결된다.\n"
                   "- **HLA-B53**과 중증 말라리아: 이 allele은 말라리아가 풍토병인 서아프리카에 흔하고 다른 곳에는 드물며, 치명적일 수 있는 말라리아에서의 회복과 강하게 연관된다.\n"
                   "- {g|슬라이드에만 있음} **Adenovirus**는 ER에서 MHC class I에 결합해 세포 표면으로의 이동을 막는 단백질을 만들어 CD8 cytotoxic T cell이 바이러스 peptide를 인식하지 못하게 한다.",
            g=[32], drop=("if having three",)),
        STAR("그렇다면 MHC는 많을수록 좋을까? — 슬라이드 퀴즈의 답", s=[11], g=[33]),
        P("그럼 교수님이 던진 질문을 다시 보자. “MHC 종류가 많을수록 좋다면 **왜 무한정 늘어나지 않을까?**” "
          "다양한 MHC를 발현하면 더 많은 peptide를 제시할 가능성이 생기지만, 동시에 **T세포가 흉선에서 선택되는 조건도 더 복잡**해진다. "
          "MHC 분자가 하나 추가될 때마다 그 MHC에 얹힌 자기 peptide에 반응하는 T세포를 모두 제거해야 자기관용이 유지된다. "
          "결국 **자가 반응성과 적절한 면역 반응 사이의 균형(Balance)** 이 필요하고, 정리본은 많은 MHC 유전자와 T세포 교육의 부담 사이에서 균형이 형성되었다는 설명으로 이 부분을 마무리한다.", s=[11], g=[33]),
        STAR("여기까지의 이야기를 슬라이드는 이렇게 정리한다 (Summary 1)", s=[12]),
        ROW(S, 12, "- MHC 유전자는 항원제시에 관여하는 많은 단백질을 부호화하는 **연결된 유전자좌들의 집합**이며 다형성이 매우 크다.\n"
                   "- T세포는 특정 allele의 MHC에 결합한 peptide를 항원으로 인식하고, 같은 peptide가 다른 MHC에 결합하면 인식하지 않는다 = **MHC restriction**.\n"
                   "- MHC allele들은 대개 여러 아미노산 치환으로 서로 다르며, 그 치환은 peptide 결합 부위와 TCR이 직접 접촉하는 표면에 몰려 있다.\n"
                   "- 다형성은 ① 결합하는 peptide의 범위 ② 결합한 peptide의 conformation ③ MHC와 TCR의 직접 상호작용에 영향을 준다.\n"
                   "- 다형성이 기능적 결과를 낳고 진화적으로 선택되어 왔다는 점은 MHC가 면역 반응에 핵심적임을 시사한다. 이 선택압은 감염원에서 오며, 결과적으로 면역계는 **개인마다 다르게** 반응한다.",
            g=[]),
    ], basics_title="다양성의 이점과 한계", basics=[
        "MHC가 다양하면 모든 사람이 같은 회피 전략에 취약해질 가능성이 줄고, 병원체와 숙주의 유전적 다양성이 서로 영향을 준다 (EBV와 HLA-A11, HLA-B53과 말라리아).",
        "MHC가 많을수록 항상 좋은 것은 아니다 — 하나가 추가될 때마다 그 MHC의 자기 peptide에 반응하는 T세포를 모두 제거해야 하므로 균형(Balance)이 필요하다.",
        "Summary 1: 다형성은 결합 peptide의 범위·conformation·TCR과의 직접 상호작용에 영향을 주고, 감염원의 선택압 때문에 면역계는 개인마다 다르다.",
    ], tip="사례 수치(60%, 서아프리카)보다 ‘병원체와 숙주의 다양성은 서로 영향을 준다’는 메시지, 그리고 ‘왜 더 많지 않은가’의 답(균형)을 기억하세요."))

    # =========================================================== Ch 3 · § 1  class Ib
    s14 = slide_lines(S, 14)
    top.append(T("Class Ib (nonclassical MHC)", CH3, [13, 14, 15], [
        STAR("이야기의 마지막 장면 — 고전적 틀로 설명되지 않는 인식", s=[13], g=[34]),
        P("이제 남은 시간에는 조금 다른 형태의 T세포 인식을 본다. 지금까지 다룬 것은 주로 **고전적인 MHC와 peptide 항원**이었다. "
          "하지만 면역계에는 이 틀로 설명하기 어려운 인식 방식도 있고, 그와 연결된 분자를 **class Ib, nonclassical MHC, MHC-like molecule**이라고 부른다. "
          "교수님은 “분류 용어는 자료마다 조금 다르게 쓰이므로 **기능을 함께** 보라”고 하셨다.", s=[13], g=[34]),
        STAR("class Ib는 어떤 분자들인가", s=[14], g=[35]),
        P("**Class Ib 계열**은 고전적인 class I과 형태는 비슷하지만 **다형성이 상대적으로 제한적**인 경우가 많고, 기능은 다양하다. "
          "자료는 **HLA-E, HLA-F, HLA-G**를 중심으로 보라고 강조한다. 이 중 일부는 **NK세포에 억제 신호**를 주는 경로와 연결되고, **HLA-G는 모체와 태아 사이의 면역 조절**과 관련된다. "
          "**HLA-C**도 NK세포 수용체와 상호작용한다는 점에서 함께 거론된다.", s=[14], g=[35]),
        ROW(S, 14, "- 고전적 class I과 형태는 비슷하지만 **다형성이 상대적으로 제한적**이고 기능이 다양하다(많은 수가 아직 기능이 정해지지 않았다).\n"
                   "- ‘nonclassical’ MHC 유전자는 많은 수가 MHC 안에, 일부는 MHC 밖에 있다.\n"
                   "- 대부분(전부는 아님) 세포 표면에서 β2-microglobulin과 결합하며, 세포에서의 발현 양과 조직 분포는 분자마다 다르다.",
            g=[35]),
        ROW(S, 15, "- 슬라이드 6-17의 제목: 특수화된 MHC class I 분자는 **NK세포와 unconventional T cell의 활성화·억제 ligand**로 작용한다 (Fig. 6.26의 표).", g=[35]),
        ADV("class Ib는 antigen presentation을 하는 분자도 있고 NK세포 억제에 관여하는 분자도 있다. 한 가지 역할로 외우지 말고 **HLA-E, F, G(+C)** 와 그 기능을 짝지어 보자.", s=[14], g=[34, 35]),
        STAR("그렇다면 unconventional T cell은 무엇일까?", s=[13], g=[36]),
        P("교수님은 스스로 묻고 답하신다. 정리본에서는 **γδ T cell**, 점막과 관련된 **MAIT cell**, 그리고 **invariant NKT cell**을 예로 든다. "
          "이름이 다른 만큼 **인식하는 표적과 생리적 역할도 똑같지는 않다.** 지금은 고전적인 αβ T세포의 peptide–MHC 인식과 **다른 항원 인식 경로가 있다**는 것부터 잡자. "
          "그 대표적인 예가 곧 이어지는 CD1이다.", s=[13], g=[36]),
        ROW(S, 13, "- 고전적인 αβ T세포의 peptide–MHC 인식과 다른 항원 인식 경로를 쓰는 T세포이다.\n"
                   "- 예: **γδ T cell**, 점막과 관련된 **MAIT cell**(비다형성 MHC class I-like 분자가 제시하는 미생물 대사산물을 인식), **invariant NKT cell**(peptide가 아니라 lipid 항원을 검출).",
            g=[36]),
    ], basics_title="Class Ib molecule", basics=[
        "Class Ib(nonclassical MHC class I)는 고전적 class I과 비슷하지만 다형성이 제한적이고 MHC 안팎에 있으며 기능이 다양하다.",
        "HLA-E, F, G 중심: 일부는 NK세포 억제 신호(HLA-G는 모체–태아 면역 조절), HLA-C도 NK세포 수용체와 상호작용한다.",
        "Unconventional T cell = γδ T cell, MAIT cell, invariant NKT cell — 고전적 peptide–MHC 인식과 다른 경로.",
    ], tip="HLA 위주로 보세요. 분류 용어가 자료마다 달라서 ‘기능’과 함께 외우는 편이 안전합니다."))

    # =========================================================== Ch 3 · § 2  CD1
    top.append(T("CD1과 lipid 항원제시", CH3, [16], [
        STAR("그 대표적인 예 — peptide가 아닌 lipid를 보여 주는 CD1", s=[16], g=[37]),
        P("먼저 **CD1 molecule**이다. 지금까지 고전적 MHC를 공부하면서 우리는 계속 peptide 항원을 이야기했다. 교수님은 CD1이 그와 달리 "
          "**lipid 또는 glycolipid 항원을 제시한다**는 점이 핵심이라고 하셨다. 그래서 병원체 유래 지질 항원을 인식하는 경로와 연결된다. "
          "{r|정리본에는 이 부분이 국가시험에 자주 나온다고 강조한 것으로 기록되어 있다.} CD1a부터 CD1e까지 여러 유형이 있지만 일단은 "
          "**‘CD1 — 지질 항원제시’** 를 확실히 기억해 두자.", s=[16], g=[37]),
        ROW(S, 16, "- **CD1 molecule**은 peptide가 아니라 **lipid 또는 glycolipid 항원**을 제시한다 → 병원체 유래 지질 항원을 인식하는 경로와 연결된다.\n"
                   "- Fig. 6.27은 CD1c가 microbial lipid를 invariant NKT cell에 제시하는 모습, Fig. 6.28은 CD1이 lipid 항원과 결합한 구조이다.", g=[37]),
        STAR("lipid 항원을 보는 세포, 그리고 MHC를 닮은 또 하나의 분자", s=[16], g=[38]),
        P("**NKT 세포**가 바로 이러한 lipid 항원 인식과 관련된다. 또 하나 알아 둘 분자는 **FcRn**이다. MHC와 닮은 분자이지만 전형적인 항원제시가 아니라 "
          "**모체의 IgG를 태아에게 전달**하는 역할을 한다고 소개된다.", s=[16], g=[38]),
        P("{p|세부 분자(CD1c, CD1d)와 invariant NKT cell의 연결은 복습 때 확인할 것. 교수님도 ‘invariant NKT cell과의 대표적인 연관은 특히 CD1d를 중심으로 다시 확인할 필요가 있다’며 검증 대상으로 표시해 두겠다고 하셨다. 슬라이드(6-18, Summary 2)는 CD1c와 CD1d 모두 lipid·glycolipid를 iNKT cell에 제시한다고 적고 있어 원자료와 대조가 필요하다.}", s=[16, 18], g=[38]),
    ], basics_title="CD1 molecule", basics=[
        "CD1(a~e)은 peptide가 아니라 lipid / glycolipid 항원을 제시하는 MHC class I-like 분자이며 병원체 유래 지질 항원 인식과 연결된다.",
        "‘CD1 — 지질 항원제시’는 국가시험에 자주 나온다고 강조된 부분이다.",
        "NKT 세포는 이 lipid 항원 인식과 관련되고, FcRn은 MHC 유사 분자이지만 모체의 IgG 전달과 관련된다.",
    ], tip="CD1 = lipid. 이 한 줄이 이번 파트에서 가장 확실한 시험 포인트입니다. FcRn은 따로 외우지 않아도 됩니다.",
        flags=["CD1c와 invariant NKT cell의 연결은 슬라이드와 스크립트의 표현이 달라 원자료·교과서로 확인 필요 (일반적으로 iNKT의 대표 분자는 CD1d)."]))

    # =========================================================== Ch 3 · § 3  γδ, MAIT, 마무리
    s18 = slide_lines(S, 18)
    top.append(T("γδ T cell, MAIT, 마무리", CH3, [17, 18], [
        STAR("γδ T cell — 하나의 정답이 없는 세포", s=[17], g=[39]),
        P("마지막으로 **γδ T cell**이다. 정리본의 표(Fig. 6.29)를 보면 이 세포가 인식할 수 있는 ligand가 여러 가지로 제시되어 있다. "
          "교수님은 “모든 항목을 하나하나 암기하기보다, **고전적인 peptide–MHC 인식과는 다른 방식으로 다양한 신호를 감지**할 수 있다는 점이 중요하다”고 하셨다. "
          "{g|수업 필기에서도 이 부분은 종류가 다양하다는 정도로 넘어갔다고 적혀 있다.}", s=[17], g=[39]),
        ROW(S, 17, "- 정리본의 표(Fig. 6.29)에는 γδ T cell이 인식하는 ligand가 여러 가지로 나온다.", g=[39]),
        STAR("MAIT cell — 선천면역과 적응면역 사이", s=[18], g=[40]),
        P("**MAIT cell**도 함께 기억해 두자. 점막 면역과 관계가 있고 **미생물 유래 물질**을 인식한다는 점에서, 선천면역과 적응면역 **사이를 연결하는 성격**으로 설명된다. "
          "슬라이드 Summary 2에 따르면 사람에 많은 이 세포는 MR1(MHC class Ib 분자)이 제시하는 vitamin B9 대사산물을 인식한다.", s=[18], g=[40]),
        ROW(S, 18, "- 비전형 T세포(unconventional subset)와 γδ T cell의 항원제시는 대개 **peptide:MHC 복합체를 만들지 않는다**.\n"
                   "- 대신 세포 스트레스·형질전환·세포내 감염을 알리는 표면 단백질(ULBPs, RAET-1)이나 CD1이 제시하는 microbial glycolipid·folate metabolite 같은 **비peptide 항원**을 인식한다. MHC 영역에는 class I과 구조가 비슷한 ‘nonclassical(class Ib) MHC’ 유전자가 많다.\n"
                   "- 이 중 일부는 면역과 무관한 일을 하지만, 많은 수가 NK세포·γδ T cell·αβ T cell의 활성화·억제 수용체에 인식된다.\n"
                   "- **CD1** 분자는 MHC 영역 밖에 있으며 CD1c와 CD1d는 lipid·glycolipid를 invariant TCR을 가진 iNKT cell에 제시한다.\n"
                   "- **MAIT cell**은 MR1이 제시하는 vitamin B9 대사산물을 인식해 선천·적응면역 사이의 ‘transitional’ 역할을 시사한다.\n"
                   "- γδ T cell을 활성화하는 항원도 스트레스·감염의 지표일 수 있으며, 이 세포는 cytokine을 만들어 면역 방어 경로를 증폭한다.", g=[40]),
        STAR("이야기를 닫으며 — 오늘의 네 마디", s=[18], g=[40]),
        P("교수님은 오늘 내용을 네 마디로 연결해 마무리하셨다. 처음에 던진 질문, ‘MHC는 왜 이렇게 여러 종류인가’에서 출발해 여기까지 왔다.", s=[18], g=[40]),
        B("① {r|MHC는 polygenic하고 polymorphic해서} 항원제시의 범위를 넓힌다.", s=[18], g=[40]),
        B("② {r|일반적인 T세포 반응은 peptide와 자기 MHC라는 두 조건}을 함께 봐야 한다 (MHC restriction).", s=[18], g=[40]),
        B("③ {r|alloresponse와 superantigen}처럼 다른 형태의 강한 반응이 있다.", s=[18], g=[40]),
        B("④ {r|CD1과 unconventional T cell}처럼 peptide 중심의 고전적인 경로를 벗어난 인식도 존재한다.", s=[18], g=[40]),
        P("“이 네 가지를 연결해 복습하시면 됩니다.”", s=[18], g=[40]),
    ], basics_title="비전형 T세포와 마무리", basics=[
        "γδ T cell은 한 가지가 아니라 다양한 ligand를 인식한다 — 표(Fig. 6.29)는 암기용이 아니라 ‘다양하다’를 보여 준다.",
        "MAIT cell: 점막 면역, 미생물 대사산물을 MR1이 제시 → 선천면역과 적응면역 사이의 transitional한 세포.",
        "Summary 2: 비전형 T세포의 항원제시는 대개 peptide:MHC 복합체가 아니라 stress 표면 단백질이나 CD1이 제시하는 비peptide 항원을 대상으로 한다.",
    ], tip="마지막 ‘네 마디 정리’ ①~④를 연결해서 복습하면 이번 파트가 끝납니다."))

    # =========================================================== appendix
    top.append(T("부록 & 검증 참고", "", [], [
        STAR("스크립트와 자료에 대한 참고"),
        P("{p|이 강의록은 실제 녹음이 아니라 정리본에서 재구성한 가상 40분 스크립트와 강의자료(슬라이드)로 만들었다. 아래를 확인하고 사용하자.}", g=[41]),
        B("전체 발화는 정리본의 주제 순서를 따라 새로 쓴 **가상 발화**이며, 실제 표현·말투·강조의 정확한 재현이 아니다.", g=[41]),
        B("정리본 5쪽의 인터페론 관련 상세 설명은 일부가 원래 PPT에만 있고 강의에서 다루지 않았다고 되어 있다 → 본문에서는 Reference로 따로 두었다.", g=[42]),
        B("{p|CD1c와 invariant NKT cell의 연결}은 정리본 12쪽의 기재이지만 일반적으로 대표 분자는 CD1d이다 → 원자료와 대조 필요.", g=[43]),
        B("일부 숫자·연구 연도·용어는 독립 검증하지 않았다. 이 문서는 역사적 강의 필기의 재구성이며 최신 교과서나 진료지침을 대체하지 않는다.", g=[44]),
        B("실제 40분 재생 시간은 말하기 속도, 판서, 그림 지시, 휴지 시간에 따라 달라진다. 표기된 시간 구간은 편집용이라 이 강의록의 구성에는 사용하지 않았다.", g=[45]),
        STAR("슬라이드에만 있고 강의에서 다루지 않은 내용 (Reference)"),
        B("interferon과 MHC 발현의 세부(6-10), Ir gene 결함(6-12), Mls antigen(6-14), adenovirus의 MHC class I 이동 차단(6-15), MR1·vitamin B9(Summary 2).", s=[6, 8, 10, 11, 18]),
    ]))

    # =========================================================== 요약 정리 (front)
    summary = T("요약 정리", "", [6, 7, 8, 9, 10, 11, 14, 16, 18], [
        STAR("먼저 전체 그림 — 이번 강의는 세 단계다", s=[6, 8, 14], g=[1, 2, 3]),
        DIA(Diagram(kind="flow", arrows=[Arrow(src=0, dst=1, label="그래서"), Arrow(src=1, dst=2, label="그런데 peptide가 아니면?")], groups=[
            Group(title="① MHC는 왜 다양한가", color="teal", items=["여러 유전자 (polygeny)", "집단 안에 여러 allele (polymorphism)", "→ 다양한 peptide를 보여줄 수 있다"]),
            Group(title="② T세포는 무엇을 보는가", color="blue", items=["{r|peptide + 자기 MHC} (MHC restriction)", "예외: alloreactivity, superantigen"]),
            Group(title="③ peptide가 아닌 항원", color="salmon", items=["Class Ib · CD1(lipid) · MR1", "γδ T cell, MAIT, NKT"]),
        ]), "강의 전체 흐름 한눈에 (이 흐름으로 본문 3개 챕터가 이어진다)", s=[6, 8, 14], g=[1, 2, 3]),
        STAR("MHC 영역의 구성", s=[6, 7], g=[5, 6, 10]),
        DIA(Diagram(kind="tree", root="사람 MHC (HLA) · 6번 염색체", groups=[
            Group(title="Class I", color="teal", items=["HLA-A, B, C", "α chain 1개 + β2-microglobulin", "{r|다리 하나짜리}"]),
            Group(title="Class II", color="blue", items=["HLA-DR, DP, DQ", "α·β chain 한 쌍", "{r|다리 두 개짜리}", "DM, DO는 조절 분자"]),
            Group(title="Class Ib", color="salmon", items=["HLA-E, F, G", "class I region에 위치", "NK세포 억제 경로"]),
            Group(title="Class III region", color="amber", items=["MIC-A, MIC-B", "TNF 등 면역 관련 유전자"]),
        ]), "MHC 유전자 영역 한눈에 (생쥐는 H-2, 17번 염색체)", s=[6], g=[5, 6, 8, 10]),
        STAR("Polymorphism과 polygeny", s=[7], g=[13, 14, 15]),
        DIA(Diagram(kind="compare", row_labels=["의미", "수준", "예", "특징"], groups=[
            Group(title="Polymorphism (다형성)", color="blue", items=["같은 유전자 자리의 allele이 집단에 여러 형태", "집단 수준", "HLA-B 하나에도 다양한 allele",
                                                                 "class I(B, A, C) > class II(DRB, DQB, DPB) · {r|β chain}에 집중 · 원인 = gene conversion"]),
            Group(title="Polygeny", color="salmon", items=["한 개인 안에 서로 다른 MHC 유전자 여러 개", "개체 수준", "HLA-A, HLA-B, HLA-C ...",
                                                           "발현은 codominant → 한 사람의 MHC 조합이 다양"]),
        ]), "Polymorphism vs Polygeny", s=[7], g=[13, 14, 15, 17]),
        STAR("다형성의 기능적 의미와 MHC restriction", s=[8], g=[18, 19, 20, 21, 22]),
        DIA(Diagram(kind="tree", root="MHC restriction과 두 예외", groups=[
            Group(title="원칙", color="teal", items=["TCR이 아는 peptide + {r|자기 MHC} 둘 다 필요", "peptide가 같아도 MHC가 다르면 X", "인식 대상 = peptide–MHC 복합체"]),
            Group(title="예외 1 · Alloreactivity", color="salmon", items=["타인의 MHC에 강한 반응", "alloreactive T cell = 전체의 {r|1~10%}", "MLR: 한쪽을 irradiation / mitomycin C 처리"]),
            Group(title="예외 2 · Superantigen", color="violet", items=["peptide 처리 없이 TCR + MHC class II에 결합", "비특이적 대규모 T세포 활성화", "SE(식중독), TSST-1(TSS)"]),
        ]), "MHC restriction과 두 가지 예외", s=[8, 9, 10], g=[21, 22, 25, 28, 29, 30, 31]),
        STAR("Class Ib와 unconventional T cell", s=[14, 16], g=[35, 36, 37, 40]),
        DIA(Diagram(kind="flow", arrows=[Arrow(src=0, dst=1, label="ligand"), Arrow(src=1, dst=2, label="인식")], groups=[
            Group(title="peptide가 아닌 항원", color="teal", items=["CD1: lipid / glycolipid 제시", "MR1: vitamin B9 대사산물", "stress 표면 단백질 (ULBPs, RAET-1)"]),
            Group(title="Class Ib · MHC-like", color="blue", items=["HLA-E, F, G (+C): NK세포 억제 경로", "HLA-G: 모체–태아 면역 조절", "FcRn: 모체 IgG 전달", "{r|CD1 = 지질 항원제시}"]),
            Group(title="Unconventional T cell", color="salmon", items=["γδ T cell: 다양한 ligand", "MAIT: 선천–적응면역 사이", "invariant NKT: lipid 검출"]),
        ]), "비전형 항원이 비전형 T세포에 인식되는 흐름", s=[13, 14, 16, 18], g=[35, 36, 37, 38, 39, 40]),
    ], role="front")
    top.insert(0, summary)
    return top


if __name__ == "__main__":
    S = extract_docx_material(sys.argv[1], "/tmp/_tcell_v2_slides")
    dump(build(S), sys.stdout)
