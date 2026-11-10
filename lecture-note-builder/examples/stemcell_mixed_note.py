"""MIXED (혼합형, default L10) version of the stem-cell note - template templates/mom_mixed.yaml.

Each body § has a shape (Topic.style):
  * explain - concept / mechanism / "why": question heading, one-line 핵심 답, reasoning paragraphs.
  * list    - numbers / cases / products / experiment results: lead-in line, bullets or columns, "즉 …" line.
Fine-tuning learned from three human MOM notes (docs/mixed_style_analysis.md), rules L11-L14:
  L11 정의 다음에 바로 따라 나오는 결론을 "그럼 …" 한 문장으로 끌어낸다.
  L12 기전은 원인 → 결과 사슬 문단으로 쓰고 "따라서 A → B → C" 한 줄로 묶는다.
  L13 원리를 먼저 세우고 사례마다 원리를 다시 불러 적용한다("앞의 X와 달리 …", "~이므로 …").
  L14 목록 항목은 "용어(한글): 정의"에 쉬운 풀이나 이유를 한 마디 붙인다.
Same front page and quiz as examples/stemcell_note.py; L1-L9 and blue = PAD only still apply.
Run:  python -m examples.stemcell_mixed_note > outputs/stemcell_mixed/note_authored.json
"""
from app.models import Arrow, Diagram, Group, Statement
from examples.authoring import T, dump
from examples.stemcell_note import CHK, COLS, CONCEPT, FS, MEMO, _st
from examples.stemcell_note import build as build_list

CH1 = "왜 재생 의학인가"
CH2 = "재생의 재료: 줄기세포"
CH3 = "무엇을 고치려 하는가: 골관절염과 연골"
CH4 = "세포 자체의 증거: MSC 임상"
CH5 = "해결책: iPSC 연골 spheroid"
CH6 = "임상과 전망"


def P(text, g=(), effort=""):
    return _st("para", text, g, effort=effort)


def B(text, g=(), effort=""):
    return _st("bullet", text, g, effort=effort)


def DIA(kind, groups, root="", arrows=(), title="", size="side", row_labels=()):
    """Program-drawn schematic - used only where the lecture slides have no picture of the idea (L15)."""
    return Diagram(kind=kind, size=size, root=root, title=title, row_labels=list(row_labels),
                   groups=[Group(title=t, items=list(it), color=c) for t, c, it in groups],
                   arrows=[Arrow(src=a, dst=b, label=l) for a, b, l in arrows])


def DFS(diagram, caption, title, lines, g=()):
    """figure_side box whose picture is a program schematic (caption '도식 n.')."""
    return Statement(text=caption, kind="figure_side", slide_refs=list(g), diagram=diagram, left_title=title,
                     left=["- " + x for x in lines])


def DFLOW(caption, groups, arrows, g=()):
    """full-width flow schematic (caption '도식 n.')."""
    return Statement(text=caption, kind="diagram", slide_refs=list(g),
                     diagram=DIA("flow", groups, arrows=arrows, size="full"))


def CONCEPT_V(title, lines, g, diagram=None, image="", caption=""):
    """개념 정리 box with a picture on the right: slide image first, else a schematic."""
    st = CONCEPT(title, lines, g)
    st.text, st.diagram = caption or title, diagram
    if image:
        st.image = "inputs/stemcell_figs/" + image
    return st


def EX(heading, chapter, answer, body):
    """explain §: question heading + 핵심 답 + reasoning paragraphs."""
    return T(heading, chapter, [], body, basics_title="핵심 답", basics=[answer], style="explain")


def LS(heading, chapter, body):
    """list §: lead-in + bullets / columns + "즉 …" (no answer box)."""
    return T(heading, chapter, [], body, style="list")


def build():
    lst = build_list()
    front, quiz = lst[0], lst[-1]
    quiz.chapter = CH6
    top = [front]

    # ================================================================ 1. 왜 재생 의학인가
    top.append(EX("치료제는 어떻게 발전해 왔고, 다음은 무엇인가?", CH1,
                  "치료제는 케미컬 → 단백질 → 항체 → 세포로 정밀해졌고, 다음 단계는 없애는 치료가 아니라 되살리는 재생 의학이다.", [
        MEMO("50분 강의이며, 줄기세포의 종류에서 시작해 교수님 연구팀의 연골 재생 치료제 임상까지 이어집니다.", [1, 2]),
        P("치료제의 역사는 ‘무엇을 약으로 쓸 수 있는가’가 넓어진 역사다. 처음에는 아스피린 같은 small chemical이 약이었다. "
          "이어 단백질(인슐린, 백신)이 약이 되었고, 몸의 방어 물질인 **항체**가 특이성(specificity)으로 표적을 정확히 겨냥하게 되었다. "
          "마지막으로 세포 자체를 약으로 쓰는 **CAR-T** 같은 세포 치료제가 나왔다.", [3, 4, 5]),
        P("{g|그 간격은 1890년경 → 약 100년 → 30년 → 15년으로 짧아졌다. CAR-T는 ‘유도 미사일’에 비유된다. "
          "의대(아카데미아), 병원(클리닉), 산업(인더스트리)의 연결이 바이오에서 중요하다는 말도 있었다.}", [3, 4, 5]),
        FS("s01.png", "치료제 모달리티의 발전: 케미컬 → 단백질 → 항체 → 세포 → 재생", "그림에서 볼 것", [
            "왼쪽에서 오른쪽으로 갈수록 정확도와 파괴력이 커진다.",
            "맨 오른쪽 빈칸이 다음 단계, 재생 의학이다.",
        ], [3, 5, 6]),
        P("따라서 small chemical → 단백질 → 항체 → 세포로 갈수록 정확도와 파괴력이 커졌다. "
          "그런데 이 약들은 대부분 무언가를 **없애는** 약이었다. 그럼 다음 단계는 없애는 것이 아니라 되살리는 것이 된다.", [5, 6]),
        P("교수님의 답은 {r|재생 의학}이다. 부족한 부분을 메우고, 없는 장기를 새로 만들고, "
          "결국에는 장기를 젊은 상태로 되돌리는(**rejuvenation**) 치료다.", [6]),
        CHK("치료제 모달리티의 발전 순서는 small chemical → 단백질 → 항체 → 세포 치료제이다.", "O", [3, 4, 5]),
    ]))

    # ================================================================ 2. 재생의 재료: 줄기세포
    top.append(EX("재생에 어떤 줄기세포를 쓸 수 있는가?", CH2,
                  "분화능은 totipotent > pluripotent(ESC, iPSC) > multipotent(MSC) 순이고, 윤리와 안전을 함께 만족하는 것이 iPSC다.", [
        P("줄기세포를 고르는 첫 기준은 **분화능**, 즉 몇 가지 세포로 될 수 있는가이다. 분화능에 따라 나누면 다음과 같다.", [9]),
        CONCEPT_V("분화능의 위계", [
            "**totipotent cell**: 세포 하나가 생명 개체가 된다 {g|(‘신의 영역’이라 연구자들이 부담스러워한다)}",
            "**pluripotent stem cell(PSC)**: 모든 계통으로 분화한다 (ESC, iPSC = Induced pluripotent stem cell)",
            "**multipotent**: 몇 개 계통으로만 분화한다 (MSC)"], [9],
            diagram=DIA("pyramid", [("totipotent", "violet", ["세포 하나 → 생명 개체"]),
                                    ("pluripotent", "salmon", ["모든 계통", "ESC, iPSC"]),
                                    ("multipotent", "teal", ["몇 개 계통만", "MSC"])], root="분화능"),
            caption="분화능의 위계 (위로 갈수록 분화능이 크다)"),
        P("{b|분화능이 가장 높은 것은 pluripotent인 ESC와 iPSC이고, 성체줄기세포(MSC)는 그보다 낮은 multipotent이다}.", [9, 1007]),
        P("가장 강력한 pluripotent 세포는 ESC(Embryonic stem cell)다. 정자와 난자가 만나(fertilization) blastocyst가 되면, "
          "{b|그 안의 inner cell mass를 꺼내 배양한 것이 ESC다}. "
          "그럼 ESC를 얻으려면 수정란을 써야 하므로 윤리 문제가 생긴다. 천주교는 수정 순간을 생명의 시작으로 보기 때문에 "
          "이 학교에서는 ESC를 연구할 수 없다.", [7, 1009]),
        P("앞의 ESC와 달리 MSC(Mesenchymal stem cell)는 지방(adipose tissue), 골수(bone marrow), 제대혈(cord blood)에서 얻는 "
          "성체줄기세포(adult stem cell)다. 그래서 윤리 부담이 없고 안전하다. 대신 multipotent라 분화능이 제한되고, "
          "계대 배양을 거듭하면 줄기세포 능력을 잃는다.", [8]),
        FS("s02.png", "Recently available stem cells in South Korea: iPSC, ESC, MSC", "그림에서 볼 것: 세 세포의 출처", [
            "가운데 위 수정란 → blastocyst → ESC (Embryo-derived, pluripotent)",
            "왼쪽 primary cell → reprogramming(Oct4, Klf4, Sox2, c-Myc) → iPSC",
            "아래 MSC: 성체줄기세포(adult stem cell), multipotent",
        ], [7, 8, 9, 10]),
        COLS("두 세포를 나란히 놓으면 다음과 같다.", [
            ("ESC", "salmon", ["blastocyst의 inner cell mass", "pluripotent, 무한 증식", "**윤리 문제**"]),
            ("MSC", "teal", ["지방, 골수, 제대혈", "multipotent, 증식 한계", "**윤리적이고 안전**"]),
        ], [7, 8]),
        P("즉 ESC는 강력하지만 윤리 문제가, MSC는 안전하지만 분화능의 한계가 있다. "
          "그렇다면 두 장점을 함께 가질 수는 없을까? 그 답이 iPSC다. {b|체세포에 야마나카 인자 4가지를 넣어 reprogramming(역분화)하면} "
          "ESC와 같은 pluripotent 세포가 된다. 수정란을 쓰지 않으니 윤리 문제가 없고, "
          "{b|개인의 체세포에서 만들 수 있어 맞춤의학에 응용된다}.", [9, 10, 30, 1005, 1008]),
        P("{b|iPSC는 개인별 약제 독성평가와 재생 치료에도 응용될 수 있다}.", [1008]),
        P("{b|MSC는 지방, 골수, 제대혈 유래 성체줄기세포이고, iPSC는 MSC와 같은 분류가 아니다}.", [8, 9, 1011]),
        P("따라서 각각의 한계 때문에 교수님 연구팀은 iPSC에 집중한다. "
          "{g|야마나카 신야는 2006년 Cell에 reprogramming factor 논문을 내고 2012년 노벨상을 받았다. 최근 Nature는 ‘Stem cell therapy to the clinic’이라는 기사를 실었다.}", [9, 10]),
        CHK("MSC는 모든 세포 계통으로 분화할 수 있는 pluripotent 세포이다.", "X", [8, 9], why="MSC는 multipotent이다."),
    ]))

    # ================================================================ 3. 골관절염과 연골
    top.append(EX("왜 골관절염에 재생 치료가 필요한가?", CH3,
                  "초기 약물과 말기 인공관절 사이 약 20년 동안 연골이 닳는 것을 막을 방법이 없기 때문이다.", [
        P("퇴행성 골관절염은 **연골세포의 노화**, 즉 연골의 질과 양이 떨어지는 병이다. {g|연골 상태는 20대에 가장 좋고 이후 내리막이다.}", [11]),
        P("치료는 두 단계뿐이다. 초기에는 내과에서 진통제와 소염제로 증상을 조절하고, 말기에는 정형외과에서 인공관절 수술을 한다. "
          "그런데 그 사이 약 **20년** 동안 연골이 닳는 것 자체를 다룰 방법이 없다.", [11]),
        DFLOW("골관절염 치료의 공백: 초기 약물과 말기 수술 사이", [
            ("초기", "blue", ["내과: 진통제, 소염제", "증상 조절"]),
            ("약 20년", "salmon", ["연골이 닳는 것을 다룰 방법이 없다", "**재생 치료의 자리**"]),
            ("말기", "gray", ["정형외과: 인공관절 수술"]),
        ], [(0, 1, "연골 계속 닳음"), (1, 2, "")], [11, 12]),
        P("그럼 이 빈칸을 채우는 것이 재생 치료의 몫이다. 줄기세포의 재생 능력으로 연골이 닳는 과정을 늦추거나, 멈추거나, 되돌릴 수 있다면 치료의 판이 바뀐다.", [12]),
        CHK("퇴행성 골관절염의 초기에는 인공관절 수술이 일차 치료이다.", "X", [11], why="초기는 진통제와 소염제, 인공관절은 말기이다."),
    ]))
    top.append(EX("지금까지의 연골 재생 치료는 왜 성공하지 못했나?", CH3,
                  "세포를 넣는 치료는 규제의 벽이 높고, 연골이 실제로 재생된다는 증거가 부족했다.", [
        P("먼저 원리부터 세운다. 세포를 어디서 얻느냐에 따라 법적 성격이 갈린다. 내 세포를 꺼내 배양한 뒤 다시 넣는 **auto-transplantation**은 "
          "치료제가 아니라 **의료 기술**이다. 그래서 규제가 적고 의사가 할 수 있지만, 상업화는 불가능하다. "
          "반면 다른 사람의 세포를 여러 환자에게 주는 **allo-transplantation**은 **치료제**이므로 식약처 허가가 필요하다.", [12]),
        FS("s03.png", "기존 연골 재생 치료: auto와 allo, 모두 한계가 있다", "그림에서 볼 것", [
            "왼쪽 auto, 오른쪽 allo 모두 FAILED 도장이 찍혀 있다.",
            "아래 Reason에 실패 이유가 하나씩 적혀 있다.",
        ], [12, 13]),
        P("이 원리를 사례에 대 보자. 카티스템(Cartistem)은 메디포스트의 제대혈 유래 allo 세포 치료제이므로 허가를 받아 지금도 쓰인다 {g|(수술로 주입)}. "
          "인보사(Invossa)도 치료제로 허가를 받았지만 품질 관리 실패로 암세포가 섞여 **품목허가가 취소**되었다 "
          "{g|(2017년경 허가, 식약처와 코오롱티슈진의 소송이 이어지고 있다)}.", [13]),
        P("결국 실패 이유는 두 가지다. 재생된 연골의 품질이 낮거나 섬유화되었고, 정말 재생되었다는 과학적 증거가 부족했다. "
          "그래서 연구자들은 세포 대신 세포가 만든 물질로 눈을 돌렸다.", [13, 14]),
        CHK("자신의 세포를 꺼내 다시 넣는 auto 방식은 치료제가 아니라 의료 기술로 분류된다.", "O", [12]),
    ]))
    top.append(LS("세포 유래 치료제의 세 범주", CH3, [
        B("예전에는 줄기세포 치료제라 하면 single cell만 떠올렸다. 지금은 세 범주로 넓어졌다.", [14]),
        B("① **ECM**(Extracellular matrix, 세포외기질): 세포가 만든 기질. 세포가 사는 환경을 통째로 넣는 셈이다.", [14]),
        B("② **small molecule**: 세포에서 나온 물질(secretome, exosome, mitochondria). 세포 없이 세포의 효과만 빌린다.", [14]),
        B("③ **organoid**: 세포를 뭉쳐 만든 3D 구조.", [14]),
        FS("s04.png", "줄기세포 유래 치료제 후보: ECM, small molecule, 3D organoid", "그림에서 볼 것", [
            "가운데 줄기세포에서 세 갈래로 나뉜다.",
            "왼쪽부터 ECM, small molecule, organoid다.",
        ], [14]),
        B("{b|organoid는 줄기세포에서 분화한 3D 세포 덩어리이다}.", [14, 23, 1004]),
        B("{b|organoid는 장기의 구조와 기능을 모사해 약제 독성평가와 재생치료에 응용된다}.", [1004, 1010]),
        CONCEPT_V("spheroid와 organoid는 다르다", [
            "**spheroid**: 3D 세포 집합체. 교수님 연구팀의 연골 spheroid를 수업에서 강조했다",
            "**organoid**: 줄기세포에서 분화한 장기 유사 3D 구조. {b|장기의 구조와 기능을 모사하는 3D 모사체}",
            "{g|기출 해설(2023 Q2)도 ‘organoid보다 spheroid를 강조했다’고 적었다}"], [14, 23, 28, 1004],
            diagram=DIA("tree", [("spheroid", "teal", ["세포를 뭉친다", "→ 3D 집합체", "연골 spheroid"]),
                                 ("organoid", "violet", ["줄기세포가 분화", "→ 장기 유사 구조", "{b|장기 구조·기능 모사}"])],
                        root="3D 세포 구조"),
            caption="spheroid vs organoid"),
        _st("reference", "수업에서 직접 다루지 않았지만 기출에 나온 개념: {b|환자 유래 줄기세포로 환자의 병적 상태를 흉내 내는 기술 = recapitulation}, {b|신장 organoid는 혈관세포 분화가 제한적이다}", [1006, 1003]),
        B("즉 세포 치료제는 이제 세포 하나가 아니라 세포가 만든 것, 세포에서 나온 것, 세포를 뭉친 것까지 포함한다.", [14]),
    ]))
    top.append(EX("ECM은 어떻게 연골 재생을 돕는가?", CH3,
                  "연골세포가 만든 기질이 거꾸로 연골세포를 살리고, 무생물이라 규제 부담도 작다.", [
        P("연골세포는 **hyaline cartilage**라는 기질을 만든다. 흥미롭게도 이 기질이 다시 연골세포를 돌본다. "
          "세포를 오래 살게 하고 기능도 촉진한다(facilitation). 좋은 환경에 있는 세포가 일을 잘하는 것과 같다.", [15]),
        P("따라서 연골세포 → 기질 생성 → 기질이 연골세포를 살림의 순환이 생긴다. 그럼 기질만 넣어도 재생을 도울 수 있다.", [15]),
        DFS(DIA("cycle", [("연골세포", "teal", ["기질을 만든다"]),
                          ("기질", "amber", ["hyaline cartilage (ECM)"]),
                          ("생존·기능 ↑", "blue", ["오래 살고 일을 잘한다"])],
                root="ECM", arrows=[(0, 1, "생성"), (1, 2, "돌봄")]),
            "ECM이 연골세포를 돌보는 순환", "도식에서 볼 것", [
                "연골세포가 만든 기질이 다시 연골세포를 돌본다.",
                "그래서 기질(ECM)만 넣어도 재생을 도울 수 있다.",
                "{g|강의 슬라이드에는 ECM이 후보로 표시만 되어 있어(s05) 순환을 도식으로 그렸다.}",
            ], [15]),
        P("교수님 연구팀은 iPSC로 연골세포 덩어리를 만든 뒤 세포를 제거해 ECM만 남겼다. "
          "이 ECM을 분화 중인 연골세포에 처리했더니 연골세포 marker 발현이 증가했고, 연골 결손에 넣었더니 결손이 잘 메꿔졌다. "
          "즉 ECM 자체도 연골 재생 치료제가 될 수 있다.", [15]),
        P("ECM을 택한 또 다른 이유는 규제다. 살아 있는 세포는 암세포로 바뀔 수 있어 규제 기관이 까다롭게 보지만, ECM은 무생물이라 부담이 작다. "
          "실제로 연골 기질 제품이 이미 쓰인다 {g|(히루안, 시노비안, 콘드란)}. "
          "MegaCARTI는 기증받은 사체 연골 제품이다 {g|(국내는 법률상 불가능해 수입 연골로 개발한다)}.", [15, 16]),
        CHK("ECM은 살아 있는 세포가 아니므로 규제 기관이 세포 치료제보다 편하게 본다.", "O", [15]),
    ]))
    top.append(EX("mitochondria도 치료제가 될 수 있는가?", CH3,
                  "그렇다. 특히 iPSC에서 얻은 젊은 mitochondria가 연골을 더 잘 회복시켰다.", [
        P("secretome, exosome, mitochondria(미토콘드리아)처럼 세포에서 떨어져 나온 물질도 후보다. "
          "처음에는 세포를 넣기 어려워 고른 차선책이었다. 그런데 규제 기관이 원재료 기준까지 요구하면서 이 길도 쉽지 않게 되었다. "
          "세포가 아닌 물질만으로는 효능(efficacy)도 제한될 수밖에 없다.", [17]),
        P("왜 하필 mitochondria일까? 골관절염, 알츠하이머 같은 만성 퇴행성 질환(chronic degenerative disease)은 "
          "mitochondria의 기능과 양이 부족한 것과 연관되어 있다(원인이 아니라 연관 요인). "
          "그럼 부족한 mitochondria를 밖에서 채워 주는 것이 치료가 될 수 있다.", [17]),
        P("교수님 연구팀은 mitochondria를 분리해 골관절염 동물 모델(MIA)의 무릎에 투여했다. "
          "대조군보다 연골이 많이 개선되었고, 성체줄기세포보다 iPSC에서 분리한 mitochondria의 효과가 더 좋았다. "
          "즉 젊은(young) mitochondria, 말하자면 충전된 건전지를 넣어 주는 것 자체가 치료가 될 수 있다.", [17, 18]),
        DFLOW("mitochondria 치료의 논리", [
            ("만성 퇴행성 질환", "gray", ["골관절염, 알츠하이머"]),
            ("mitochondria 부족", "salmon", ["기능과 양이 부족", "(원인이 아니라 연관 요인)"]),
            ("밖에서 채운다", "teal", ["iPSC 유래 젊은 mitochondria 투여"]),
            ("연골 개선", "blue", ["MIA 모델, 대조군보다 개선", "성체줄기세포 유래보다 효과 ↑"]),
        ], [(0, 1, "연관"), (1, 2, "그럼"), (2, 3, "")], [17, 18]),
        P("{g|mitochondria 이식은 근육병증(inflammatory myopathy)에서도 효과가 보고되어 임상 연구가 진행 중이다.}", [18]),
        CHK("iPSC에서 분리한 mitochondria가 성체줄기세포 유래보다 연골 개선 효과가 좋았다.", "O", [18]),
    ]))

    # ================================================================ 4. MSC 임상 (data -> list)
    top.append(LS("MSC 골관절염 RCT 결과", CH4, [
        B("세포 유래 물질이 아니라 세포 자체는 어떨까? 교수님 연구팀은 골수 유래 MSC를 골관절염 환자 무릎에 주사하는 "
          "RCT(Randomized controlled trial)를 수행했다.", [19]),
        B("{g|약 10년 전 일로, 2018년부터 식약처와 협의해 2019년 첫 환자에게 투여했다(sono-guided injection).}", [19]),
        B("**대상**: 대조군 12명, MSC군 12명, 1년 관찰.", [20]),
        B("**통증**: **9개월째에만** WOMAC pain과 VAS pain 점수가 유의했다.", [20]),
        B("**MRI상 연골 재생**: 유의하지 않았다.", [20]),
        B("**T2 mapping(질적, qualitative 변화)**: 약간 유리했지만 **medial compartment에서만** p < 0.05였다. lateral compartment는 차이가 없었다.", [20]),
        B("즉 통증은 일부 줄었지만 연골의 양적(quantitative) 재생 증거는 얻지 못한 **절반의 성공**이었다. {g|교수님의 첫 translational research였다.}", [20]),
        CHK("MSC RCT에서 MRI상 연골 재생은 통계적으로 유의했다.", "X", [20], why="통증만 9개월째 유의했다."),
    ]))
    top.append(LS("국내외 MSC 치료제 현황", CH4, [
        B("한국은 MSC 강국이었다. 2010년대 초 MSC 치료제 4개가 허가되었다. {g|황우석 퇴출 뒤 국가가 성체줄기세포 치료제를 밀어 주었다는 배경이 있다.}", [21]),
        B("그러나 효과가 부족해 **카티스템만** 살아남았고, 이후 국가는 허가를 내주지 않는다.", [21]),
        FS("s06.png", "한국 줄기세포 치료제: 허가와 허가 거부", "그림에서 볼 것", [
            "위 4줄은 허가(Approved)다.",
            "아래 빨간 줄은 허가 거부(DoA)다.",
        ], [21]),
        B("**Neuronata-R**: 루게릭병 MSC 치료제. 3상 마지막에 실패했다 {g|(코아스템켐온 주가 10분의 1, 2,000억 원 이상 투입)}.", [21]),
        B("**비용 대비 근거**: 한 번 주사에 약 2,000만 원인데 효과의 근거가 없다. 단순 MSC 치료는 “It’s a dead end”라고 볼 수 있다.", [21]),
        B("{b|Ryoncil은 GVHD 치료제로 미국 FDA가 허가한 최초의 줄기세포(simple MSC) 치료제이다}.", [22, 1002], effort="참고"),
        B("{b|Ryoncil은 골수(bone marrow) 유래 MSC이고 2024년 12월에 승인되었다}.", [1002], effort="참고"),
        B("즉 지금까지의 MSC 치료제는 ‘도토리 키재기’다. 그렇다면 무엇을 바꾸면 세포 치료가 성공할까?", [22, 23]),
        CHK("한국에서 허가된 MSC 치료제 중 현재까지 살아남은 것은 카티스템이다.", "O", [21]),
    ]))

    # ================================================================ 5. 해결책
    top.append(EX("무엇을 바꾸면 세포 치료가 성공할까?", CH5,
                  "재료(MSC → iPSC), 제형(single cell → spheroid), 경로(수술 → 주사) 세 가지를 바꾼다.", [
        P("교수님 연구팀의 답은 세 가지를 동시에 바꾸는 것이다. 앞에서 본 실패 원인에 하나씩 대응한다.", [27]),
        FS("s11.png", "Distinguished approaches: (1) new cell, (2) CMC & (3) route", "그림에서 볼 것: 세 가지 전략", [
            "1 Good material: MSC 대신 induced pluripotent stem cell",
            "2 Formulation: single cell → cell aggregate(spheroid)",
            "3 Application: 수술(surgery) → 주사(injection)",
        ], [25, 26, 27]),
        P("첫째, **재료**다. 앞의 MSC RCT에서 보았듯 multipotent한 MSC로는 한계가 뚜렷했다. 그래서 pluripotent한 iPSC로 바꾼다. "
          "{g|교수님은 이를 ‘5G 시대에 2G 폰을 쓰는 것’에 비유했다.} "
          "국내에서 iPSC를 환자에게 투여한 곳은 교수님 연구팀이 거의 유일하다 {g|(국내 31명 중 30명, 연세대 카리스바이오 1명)}.", [25]),
        FS("s09.png", "For better cell therapy… change cell origin?", "그림에서 볼 것", [
            "피라미드 아래가 MSC, 위가 iPSC와 ESC다.",
            "왼쪽 2G 폰과 오른쪽 5G 폰이 비유다.",
        ], [25]),
        P("둘째, **제형**이다. 연골세포는 기질 안에 있을 때만 안정적인 세포다. 기질 없이 꺼내 배양하면 1주일 안에 죽거나 "
          "fibroblast로 변성된다. 따라서 기질 없음 → 세포 사멸이나 변성 → 기능 저하로 이어지므로, 세포를 덩어리로 넣는 **spheroid**가 기능적으로 우수하다.", [24, 25]),
        P("반면 single cell은 다루기 편하고 주사가 쉽다. "
          "즉 제형은 spheroid로 하되 주사가 가능하게 만드는 **중용**, 곧 주사형 spheroid(injectable spheroid)가 필요하다.", [25]),
        FS("s10.png", "For better cell therapy… different CMC?", "그림에서 볼 것", [
            "왼쪽 single cell은 다루기 쉽다(practical).",
            "오른쪽 spheroid는 기능이 좋다(functional).",
        ], [25]),
        P("셋째, **경로**다. 환자들은 인공관절 수술을 두려워한다. 그래서 수술이 아니라 주사로 넣는 접근성이 중요하다. "
          "{g|수술하는 의사(surgeon)에 따라 결과가 갈리고, 수술이 잘 안 된 환자들의 하소연이 두려움을 키운다는 이야기도 있었다.}", [26, 27]),
        P("세 가지를 합친 개념이 ‘뭉치면 살고 흩어지면 죽는다’다. 연골세포를 하나씩 넣으면 취약하지만, "
          "여러 세포(multicellular, cell aggregation)와 ECM을 함께 넣으면 강력해진다. 교수님 연구팀이 세계 최초로 제시한 개념이다. "
          "{g|제품은 입셀(YiPSCELL)의 MIUChon(뮤콘), Newer formula + Stronger cell source + Easier access.}", [27, 28]),
        FS("s12.png", "MIUChon: Newer formula + Stronger cell source + Easier access", "그림에서 볼 것: AS-IS → TO-BE", [
            "왼쪽 AS-IS: single cell therapeutics, 흩어진 작은 물고기는 상어에게 먹힌다.",
            "오른쪽 TO-BE: multi-cell therapeutics, 뭉친 물고기가 상어를 이긴다.",
            "{g|같은 뜻의 슬라이드: ‘United we stand, divided we fall’(뭉친 새 사진).}",
        ], [27, 28]),
        P("국내 회사들도 같은 방향으로 움직이고 있다. auto에서 allo로, single cell에서 조직을 모사(mimic)하는 제형으로 전환(turn)하고, "
          "MSC에서 pluripotent 세포로 바꾸고 있다. {g|경쟁사: 카티스템, 조인트스템, 카틸로이드, 카티큐어, 인보사 등}", [23, 24]),
        FS("s08.png", "연골치료제 개발 후보: MSC(×3), Chondrocyte(×3), iPSC(×1)/Single(×4), Multi(×3)", "그림에서 볼 것", [
            "윗줄이 국내 연골 치료제 후보 제품이다.",
            "맨 오른쪽 MIUChon만 iPSC 유래다.",
        ], [23, 24]),
        CHK("연골세포는 기질에서 떼어 단독으로 배양할 때 가장 안정적이고 기능이 좋다.", "X", [25, 28], why="1주일 안에 죽거나 fibroblast로 변한다."),
    ]))
    top.append(LS("iPSC spheroid 동물 실험", CH5, [
        B("교수님 연구팀은 iPSC 유래 연골 spheroid {g|(약 200 µm)}를 세 가지 동물에 투여했다. 결과는 다음과 같다.", [28]),
        B("**토끼**: 연골이 개선되었다.", [28]),
        B("**비글(beagle dog)**: 퇴행성 모델을 만들어 1년 관찰했다. 위약군은 연골이 망가지고 osteophyte가 생겼다. "
          "투여군은 기능이 회복되고 연골 결손이 채워졌다.", [28]),
        B("**핵심**: 비글에서 채워진 연골은 개가 아니라 **사람 단백질**이었다. 투여한 세포가 직접 연골을 만들었다는 뜻이다.", [28]),
        B("{g|비글 실험은 약 7, 8년 전부터 진행했다. 비글 8마리, 십자인대 절단과 반월판(meniscus) 찢김(tearing) 손상 모델.}", [28]),
        B("**돼지**: 결손 충전과 부피 변화가 대조군보다 컸고, 연골이 많이 망가지는 zone 1, 2에서 개선이 확실했다 {g|(4마리 vs 4마리)}.", [29]),
        B("즉 투여한 세포가 직접 연골을 재생할 가능성을 세 동물에서 보였다.", [29]),
        CHK("비글 실험에서 새로 채워진 연골은 개의 단백질이었다.", "X", [28], why="사람 단백질이었다."),
    ]))
    top.append(EX("왜 iPSC를 allo로 쓰는가?", CH5,
                  "auto는 한 사람에 약 10억 원과 2년이 들어 상업화가 불가능하므로, bank를 만든 off-the-shelf allo가 필요하다.", [
        P("원리는 두 가지다. pluripotent 세포는 규제 기관이 더 까다롭게 보고, 상업화는 한 제품을 여러 환자에게 줄 수 있어야(allo) 가능하다. "
          "이 두 원리를 세포 종류와 이식 방식의 네 조합에 대입하면 다음과 같다.", [30]),
        MEMO("먼저 두 원리를 이해하고, 아래 네 조합에 하나씩 대입해 보세요.", [30]),
        COLS("세포 종류 × 이식 방식", [
            ("MSC", "teal", ["auto: 쉽지만 의료 기술에 그친다", "allo: 치료제가 되지만 규제로 어려워진다"]),
            ("iPSC", "salmon", ["auto: 맞춤 의학으로는 이상적이나 약 10억 원과 2년", "allo: bank에서 꺼내 쓰는 off-the-shelf"]),
        ], [30]),
        P("iPSC는 pluripotent라 규제 기관이 더 까다롭게 본다. 그중 iPSC auto는 한 사람의 피를 뽑아 iPSC를 만들고 다시 넣는 데 "
          "**약 10억 원과 2년**이 든다. 그래서 상업화가 불가능하다.", [30]),
        P("결국 iPSC는 bank를 만들어 누구에게나 줄 수 있는 **off-the-shelf allo**여야 한다. "
          "교수님 연구팀은 여기에 spheroid 제형과 주사 경로까지 더해, 식약처가 다뤄 보지 못한 가장 어려운 길을 택했다.", [30]),
        FS("s14.png", "Part 1 Summary: MSC, iPSC × auto, allo", "그림에서 볼 것", ["오른쪽으로 갈수록 어렵고(달고나 모양), 맨 오른쪽이 교수님 연구팀의 선택이다."], [30]),
        CHK("iPSC를 자기 세포로 만들어 자신에게 넣는 방식은 비용 약 10억 원과 2년이 들어 상업화가 어렵다.", "O", [30]),
    ]))

    # ================================================================ 6. 임상과 전망
    top.append(LS("임상시험 진행 상황", CH6, [
        MEMO("Part 2(식약처 허가 과정)는 교수님께서 3분 만에 빠르게 넘어간 부분입니다.", [31]),
        B("{b|IND(Investigational New Drug) 허가는 임상시험용으로 투여하기 위해 규제기관(식약처)에서 받는 초기 허가이다}.", [31, 1001], effort="이해"),
        B("{p|확인 필요: 스크립트(음성 변환)는 허가 2023년 8월 1일, 투여 2025년. 사람이 쓴 정리본은 IND 허가를 2024년 8월로 적었다.}", [31]),
        B("**1상(Phase 1)**: 목적은 효과가 아니라 **안전성**이다. 3명에게 투여했고 부작용은 없었다. {g|샘플 1개에 1억 원이 들었지만 지금은 약 2, 300만 원 수준이다.}", [31, 32]),
        B("**1상 MRI**: 연골 결손(defect size)이 줄었고, 세 번째 환자는 연골 두께(cartilage thickness)가 연속 MRI에서 늘었다. "
          "다만 위약 대조가 없으므로 효과가 아니라 탐색적 신호다.", [32]),
        B("{g|MRI에서 검정은 뼈, 하양은 synovial fluid, 회색은 연골이다.}", [32]),
        B("**2상(Phase 2)**: 30명(뮤콘 15명, 위약 15명), 다음 주 마지막 투여다.", [32]),
        DFLOW("뮤콘 임상 단계", [
            ("IND 허가", "gray", ["식약처 초기 허가"]),
            ("1상", "teal", ["3명", "안전성: 부작용 없음", "MRI 탐색적 신호"]),
            ("2상", "blue", ["30명 (뮤콘 15, 위약 15)", "위약 대조로 효과 확인"]),
        ], [(0, 1, ""), (1, 2, "")], [31, 32]),
        B("즉 안전성은 확인했고, 효과는 위약 대조가 있는 2상에서 판가름 난다.", [32]),
        CHK("1상 임상시험은 유효성이 아니라 안전성(부작용)을 보는 단계이다.", "O", [31, 32]),
    ]))
    top.append(EX("앞으로 재생 치료는 어디로 가는가?", CH6,
                  "일본에서 iPSC 치료제가 처음 품목 허가를 받았고, 재생 치료는 곧 처방 목록에 들어올 것이다.", [
        P("일본은 10년 이상 iPSC에 투자했고, 올해 iPSC 치료제가 임상 연구가 아닌 **품목 허가(조건부)**를 받았다. "
          "심근세포 치료제와 파킨슨병 치료제로, 세계 최초다. "
          "{g|척수 손상(spinal cord injury, 오카노, 게이오대), 망막변성(타카하시 마사요), 파킨슨병 연구가 진행 중이다.}", [33]),
        FS("s15.png", "Break News: World 1st conditional approval for iPSC therapy", "그림에서 볼 것", ["조건부 허가 소식을 전한 기사다."], [33]),
        P("{r|결론적으로 pluripotent 줄기세포 기반 재생 치료가 여러분이 의사가 될 때 처방 목록에 들어올 것이다.} "
          "처음 질문으로 돌아가면, ‘없애는 치료 다음’은 바로 이 재생 치료다.", [33, 6]),
    ]))
    top.append(quiz)
    return top


if __name__ == "__main__":
    import sys

    topics = build()
    for t in topics:
        t.slide_numbers = sorted({r for sts in t.sections.values() for st in sts for r in st.slide_refs})
    dump(topics, sys.stdout)
