"""EXPLANATORY (textbook-like) version of the stem-cell note - template templates/mom_explain.yaml.

Same inputs and the same front page / quiz as examples/stemcell_note.py (the list-style version), so the two can be
compared on the body only. Body style:
  * one storyline for the whole lecture: 파괴 → 재생 / 재료는? → ESC·MSC의 한계 → iPSC / 무엇을 고치나? (OA)
    → 왜 실패했나 → 무엇을 바꾸나 (재료·제형·경로) → 증거 → 전망
  * every § = a QUESTION heading + "핵심 답" box (answer first), then short paragraphs that build the answer
    (정의 → 왜 → 어떻게 → 한계 → 그래서), connectives 왜냐하면 / 그래서 / 그런데 / 반면 / 결국
  * approved rules L1-L9 still apply (short sentences, no dash-chains, "교수님 연구팀", English slide terms,
    grey anecdotes, 메모 합니다체); blue = PAD only.
Run:  python -m examples.stemcell_explain_note > outputs/stemcell_explain/note_authored.json
"""
from examples.authoring import T, dump
from examples.stemcell_note import AUTH, CHK, COLS, CONCEPT, FS, MEMO, _st
from examples.stemcell_note import build as build_list

CH1 = "왜 재생 의학인가"
CH2 = "재생의 재료: 줄기세포"
CH3 = "무엇을 고치려 하는가: 골관절염과 연골"
CH4 = "세포 자체의 증거: MSC 임상"
CH5 = "해결책: iPSC 연골 spheroid"
CH6 = "임상과 전망"


def P(text, g=(), effort=""):
    return _st("para", text, g, effort=effort)


def Q(heading, chapter, answer, body):
    """A § as a question: heading = the question, 핵심 답 box = the one-line answer, body = the explanation."""
    return T(heading, chapter, [], body, basics_title="핵심 답", basics=[answer])


def build():
    lst = build_list()
    front, quiz = lst[0], lst[-1]
    quiz.chapter = CH6
    top = [front]

    # ================================================================ 1. 왜 재생 의학인가
    top.append(Q("치료제는 어떻게 발전해 왔고, 다음은 무엇인가?", CH1,
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
        P("이 흐름에서 커진 것은 정확도와 파괴력이다. 그런데 지금까지의 약은 대부분 무언가를 **없애는** 약이었다. "
          "그래서 다음 질문은 ‘없애는 것 다음은 무엇인가’가 된다.", [5, 6]),
        P("교수님의 답은 {r|재생 의학}이다. 부족한 부분을 메우고, 없는 장기를 새로 만들고, "
          "결국에는 장기를 젊은 상태로 되돌리는(**rejuvenation**) 치료다. 이 강의는 ‘재생 치료를 실제로 만들려면 무엇이 필요한가’에 대한 답이다.", [6]),
        CHK("치료제 모달리티의 발전 순서는 small chemical → 단백질 → 항체 → 세포 치료제이다.", "O", [3, 4, 5]),
    ]))

    # ================================================================ 2. 재생의 재료: 줄기세포
    top.append(Q("재생에 어떤 줄기세포를 쓸 수 있는가?", CH2,
                 "분화능은 totipotent > pluripotent(ESC, iPSC) > multipotent(MSC) 순이고, 윤리와 안전을 함께 만족하는 것이 iPSC다.", [
        P("줄기세포를 고르는 첫 기준은 **분화능**, 즉 몇 가지 세포로 될 수 있는가이다. 분화능에 따라 나누면 다음과 같다.", [9]),
        CONCEPT("분화능의 위계", [
            "**totipotent cell**: 세포 하나가 생명 개체가 된다 {g|(‘신의 영역’이라 연구자들이 부담스러워한다)}",
            "**pluripotent stem cell(PSC)**: 모든 계통으로 분화한다 (ESC, iPSC = Induced pluripotent stem cell)",
            "**multipotent**: 몇 개 계통으로만 분화한다 (MSC)"], [9]),
        P("{b|분화능이 가장 높은 것은 pluripotent인 ESC와 iPSC이고, 성체줄기세포(MSC)는 그보다 낮은 multipotent이다}.", [9, 1007]),
        P("가장 강력한 pluripotent 세포는 ESC(Embryonic stem cell)다. 정자와 난자가 만나(fertilization) blastocyst가 되면, "
          "{b|그 안의 inner cell mass를 꺼내 배양한 것이 ESC다}. 문제는 윤리다. 천주교는 수정 순간을 생명의 시작으로 보기 때문에 "
          "이 학교에서는 ESC를 연구할 수 없다.", [7, 1009]),
        P("반대편에 MSC(Mesenchymal stem cell)가 있다. 지방(adipose tissue), 골수(bone marrow), 제대혈(cord blood)에 있는 "
          "성체줄기세포(adult stem cell)라서 윤리 부담이 없고 안전하다. 대신 multipotent라 분화능이 제한되고, "
          "계대 배양을 거듭하면 줄기세포 능력을 잃는다. 강력한 약일수록 부작용도 크듯이, ESC와 MSC는 강력함과 안전함의 양 끝에 있다.", [8]),
        COLS("두 세포를 나란히 놓으면 다음과 같다.", [
            ("ESC", "salmon", ["blastocyst의 inner cell mass", "pluripotent, 무한 증식", "**윤리 문제**"]),
            ("MSC", "teal", ["지방, 골수, 제대혈", "multipotent, 증식 한계", "**윤리적이고 안전**"]),
        ], [7, 8]),
        P("그렇다면 두 장점을 함께 가질 수는 없을까? 그 답이 iPSC다. {b|체세포에 야마나카 인자 4가지를 넣어 reprogramming(역분화)하면} "
          "ESC와 같은 pluripotent 세포가 된다. 수정란을 쓰지 않으니 윤리 문제가 없고, "
          "{b|개인의 체세포에서 만들 수 있어 맞춤의학에 응용된다}.", [9, 10, 30, 1005, 1008]),
        P("{b|iPSC는 개인별 약제 독성평가와 재생 치료에도 응용될 수 있다}.", [1008]),
        P("{b|MSC는 지방, 골수, 제대혈 유래 성체줄기세포이고, iPSC는 MSC와 같은 분류가 아니다}.", [8, 9, 1011]),
        P("따라서 각각의 한계 때문에 교수님 연구팀은 iPSC에 집중한다. "
          "{g|야마나카 신야는 2006년 Cell에 reprogramming factor 논문을 내고 2012년 노벨상을 받았다. 최근 Nature는 ‘Stem cell therapy to the clinic’이라는 기사를 실었다.}", [9, 10]),
        CHK("MSC는 모든 세포 계통으로 분화할 수 있는 pluripotent 세포이다.", "X", [8, 9], why="MSC는 multipotent이다."),
    ]))

    # ================================================================ 3. 골관절염과 연골
    top.append(Q("왜 골관절염에 재생 치료가 필요한가?", CH3,
                 "초기 약물과 말기 인공관절 사이 약 20년 동안 연골이 닳는 것을 막을 방법이 없기 때문이다.", [
        P("퇴행성 골관절염은 **연골세포의 노화**, 즉 연골의 질과 양이 떨어지는 병이다. {g|연골 상태는 20대에 가장 좋고 이후 내리막이다.}", [11]),
        P("치료는 두 단계뿐이다. 초기에는 내과에서 진통제와 소염제로 증상을 조절하고, 말기에는 정형외과에서 인공관절 수술을 한다. "
          "그런데 그 사이 약 **20년** 동안 연골이 닳는 것 자체를 다룰 방법이 없다.", [11]),
        P("그래서 줄기세포의 재생 능력으로 이 과정을 늦추거나, 멈추거나, 되돌릴 수 있다면 치료의 판이 바뀐다.", [12]),
        CHK("퇴행성 골관절염의 초기에는 인공관절 수술이 일차 치료이다.", "X", [11], why="초기는 진통제와 소염제, 인공관절은 말기이다."),
    ]))
    top.append(Q("지금까지의 연골 재생 치료는 왜 성공하지 못했나?", CH3,
                 "세포를 넣는 치료는 규제의 벽이 높고, 연골이 실제로 재생된다는 증거가 부족했다.", [
        P("먼저 세포를 어디서 얻느냐에 따라 법적 성격이 갈린다. 내 세포를 꺼내 배양한 뒤 다시 넣는 **auto-transplantation**은 "
          "치료제가 아니라 **의료 기술**이다. 그래서 규제가 적고 의사가 할 수 있지만, 상업화는 불가능하다. "
          "반면 다른 사람의 세포를 여러 환자에게 주는 **allo-transplantation**은 **치료제**이므로 식약처 허가가 필요하다.", [12]),
        FS("s03.png", "기존 연골 재생 치료: auto와 allo, 모두 한계가 있다", "그림에서 볼 것", [
            "왼쪽 auto, 오른쪽 allo 모두 FAILED 도장이 찍혀 있다.",
            "아래 Reason에 실패 이유가 하나씩 적혀 있다.",
        ], [12, 13]),
        P("실제 사례가 이를 보여 준다. 카티스템(Cartistem)은 메디포스트의 제대혈 유래 세포 치료제로 지금도 쓰인다 {g|(수술로 주입)}. "
          "인보사(Invossa)는 품질 관리 실패로 암세포가 섞여 **품목허가가 취소**되었다 {g|(2017년경 허가, 식약처와 코오롱티슈진의 소송이 이어지고 있다)}.", [13]),
        P("결국 실패 이유는 두 가지다. 재생된 연골의 품질이 낮거나 섬유화되었고, 정말 재생되었다는 과학적 증거가 부족했다. "
          "그래서 연구자들은 세포 대신 세포가 만든 물질로 눈을 돌렸다.", [13, 14]),
        CHK("자신의 세포를 꺼내 다시 넣는 auto 방식은 치료제가 아니라 의료 기술로 분류된다.", "O", [12]),
    ]))
    top.append(Q("세포 대신 무엇을 쓸 수 있는가?", CH3,
                 "세포가 만든 기질(ECM), 세포에서 나온 물질(small molecule), 세포 덩어리(organoid)도 세포 치료제의 범주다.", [
        P("예전에는 줄기세포 치료제라 하면 single cell만 떠올렸다. 지금은 범위가 넓다. "
          "① 세포가 만든 기질인 **ECM**(Extracellular matrix), ② 세포에서 나온 **small molecule**(secretome, exosome, mitochondria), "
          "③ 세포를 뭉친 **organoid**가 모두 포함된다.", [14]),
        FS("s04.png", "줄기세포 유래 치료제 후보: ECM, small molecule, 3D organoid", "그림에서 볼 것", [
            "가운데 줄기세포에서 세 갈래로 나뉜다.",
            "왼쪽부터 ECM, small molecule, organoid다.",
        ], [14]),
        P("{b|organoid는 줄기세포에서 분화한 3D 세포 덩어리이다}.", [14, 23, 1004]),
        P("{b|organoid는 장기의 구조와 기능을 모사해 약제 독성평가와 재생치료에 응용된다}.", [1004, 1010]),
        CONCEPT("spheroid와 organoid는 다르다", [
            "**spheroid**: 3D 세포 집합체. 교수님 연구팀의 연골 spheroid를 수업에서 강조했다",
            "**organoid**: 줄기세포에서 분화한 장기 유사 3D 구조. {b|장기의 구조와 기능을 모사하는 3D 모사체}",
            "{g|기출 해설(2023 Q2)도 ‘organoid보다 spheroid를 강조했다’고 적었다}"], [14, 23, 28, 1004]),
        _st("reference", "수업에서 직접 다루지 않았지만 기출에 나온 개념: {b|환자 유래 줄기세포로 환자의 병적 상태를 흉내 내는 기술 = recapitulation}, {b|신장 organoid는 혈관세포 분화가 제한적이다}", [1006, 1003]),
    ]))
    top.append(Q("ECM은 어떻게 연골 재생을 돕는가?", CH3,
                 "연골세포가 만든 기질이 거꾸로 연골세포를 살리고, 무생물이라 규제 부담도 작다.", [
        P("연골세포는 **hyaline cartilage**라는 기질을 만든다. 흥미롭게도 이 기질이 다시 연골세포를 돌본다. "
          "세포를 오래 살게 하고 기능도 촉진한다(facilitation). 좋은 환경에 있는 세포가 일을 잘하는 것과 같다.", [15]),
        FS("s05.png", "ECM(세포외기질): 줄기세포 유래 치료제 후보", "그림에서 볼 것", ["세 후보 중 왼쪽 ECM이 강조되어 있다."], [15]),
        P("교수님 연구팀은 iPSC로 연골세포 덩어리를 만든 뒤 세포를 제거해 ECM만 남겼다. "
          "이 ECM을 분화 중인 연골세포에 처리했더니 연골세포 marker 발현이 증가했고, 연골 결손에 넣었더니 결손이 잘 메꿔졌다. "
          "즉 ECM 자체도 연골 재생 치료제가 될 수 있다.", [15]),
        P("ECM을 택한 이유는 규제다. 살아 있는 세포는 암세포로 바뀔 수 있어 규제 기관이 까다롭게 보지만, ECM은 무생물이라 부담이 작다. "
          "실제로 연골 기질 제품이 이미 쓰인다 {g|(히루안, 시노비안, 콘드란)}. "
          "MegaCARTI는 기증받은 사체 연골 제품이다 {g|(국내는 법률상 불가능해 수입 연골로 개발한다)}.", [15, 16]),
        CHK("ECM은 살아 있는 세포가 아니므로 규제 기관이 세포 치료제보다 편하게 본다.", "O", [15]),
    ]))
    top.append(Q("mitochondria도 치료제가 될 수 있는가?", CH3,
                 "그렇다. 특히 iPSC에서 얻은 젊은 mitochondria가 연골을 더 잘 회복시켰다.", [
        P("secretome, exosome, mitochondria(미토콘드리아)처럼 세포에서 떨어져 나온 물질도 후보다. "
          "처음에는 세포를 넣기 어려워 고른 차선책이었다. 그런데 규제 기관이 원재료 기준까지 요구하면서 이 길도 쉽지 않게 되었다. 세포가 아닌 물질만으로는 효능(efficacy)도 제한될 수밖에 없다.", [17]),
        P("왜 하필 mitochondria일까? 골관절염, 알츠하이머 같은 만성 퇴행성 질환(chronic degenerative disease)은 "
          "mitochondria의 기능과 양이 부족한 것과 연관되어 있기 때문이다(원인이 아니라 연관 요인).", [17]),
        P("교수님 연구팀은 mitochondria를 분리해 골관절염 동물 모델(MIA)의 무릎에 투여했다. "
          "대조군보다 연골이 많이 개선되었고, 성체줄기세포보다 iPSC에서 분리한 mitochondria의 효과가 더 좋았다. "
          "즉 젊은(young) mitochondria, 말하자면 충전된 건전지를 넣어 주는 것 자체가 치료가 될 수 있다.", [17, 18]),
        P("{g|mitochondria 이식은 근육병증(inflammatory myopathy)에서도 효과가 보고되어 임상 연구가 진행 중이다.}", [18]),
        CHK("iPSC에서 분리한 mitochondria가 성체줄기세포 유래보다 연골 개선 효과가 좋았다.", "O", [18]),
    ]))

    # ================================================================ 4. MSC 임상
    top.append(Q("MSC를 환자에게 직접 넣으면 효과가 있었나?", CH4,
                 "통증은 9개월째에만 줄었고 연골 재생은 증명되지 않았다. 절반의 성공이었다.", [
        P("세포 유래 물질이 아니라 세포 자체는 어떨까? 교수님 연구팀은 골수 유래 MSC를 골관절염 환자 무릎에 주사하는 "
          "RCT(Randomized controlled trial)를 수행했다. {g|약 10년 전 일로, 2018년부터 식약처와 협의해 2019년 첫 환자에게 투여했다(sono-guided injection).}", [19]),
        P("대조군 12명과 MSC군 12명을 1년 동안 관찰했다. 통증은 **9개월째에만** WOMAC pain과 VAS pain 점수가 유의했다. "
          "기대했던 MRI상 연골 재생은 유의하지 않았다. T2 mapping으로 본 연골의 질적(qualitative) 변화는 약간 유리했지만, "
          "**medial compartment에서만** p < 0.05였고 lateral compartment는 차이가 없었다.", [20]),
        P("즉 통증은 일부 줄었지만 연골의 양적(quantitative) 재생 증거는 얻지 못했다. {g|교수님의 첫 translational research였다.}", [20]),
        CHK("MSC RCT에서 MRI상 연골 재생은 통계적으로 유의했다.", "X", [20], why="통증만 9개월째 유의했다."),
    ]))
    top.append(Q("그렇다면 MSC 치료제의 미래는?", CH4,
                 "한국은 4개를 허가했지만 카티스템만 남았다. 미국 Ryoncil의 첫 허가에도 근거 부족이라는 한계는 그대로다.", [
        P("한국은 MSC 강국이었다. 2010년대 초 MSC 치료제 4개가 허가되었다. 그러나 효과가 부족해 카티스템만 살아남았고, "
          "이후 국가는 허가를 내주지 않는다. {g|황우석 퇴출 뒤 국가가 성체줄기세포 치료제를 밀어 주었다는 배경이 있다.}", [21]),
        FS("s06.png", "한국 줄기세포 치료제: 허가와 허가 거부", "그림에서 볼 것", [
            "위 4줄은 허가(Approved)다.",
            "아래 빨간 줄은 허가 거부(DoA)다.",
        ], [21]),
        P("Neuronata-R은 루게릭병 MSC 치료제였지만 3상 마지막에 실패했다 {g|(코아스템켐온 주가 10분의 1, 2,000억 원 이상 투입)}. "
          "한 번 주사에 약 2,000만 원인데 효과의 근거가 없다면 앞날은 밝지 않다. 단순 MSC 치료는 “It’s a dead end”라고 볼 수 있다.", [21]),
        P("{b|Ryoncil은 GVHD 치료제로 미국 FDA가 허가한 최초의 줄기세포(simple MSC) 치료제이다}.", [22, 1002], effort="참고"),
        P("{b|Ryoncil은 골수(bone marrow) 유래 MSC이고 2024년 12월에 승인되었다}.", [1002], effort="참고"),
        P("그래도 지금까지의 MSC 치료제는 ‘도토리 키재기’다. 그래서 다음 질문은 ‘무엇을 바꾸면 세포 치료가 성공할까’가 된다.", [22, 23]),
        CHK("한국에서 허가된 MSC 치료제 중 현재까지 살아남은 것은 카티스템이다.", "O", [21]),
    ]))

    # ================================================================ 5. 해결책
    top.append(Q("무엇을 바꾸면 세포 치료가 성공할까?", CH5,
                 "재료(MSC → iPSC), 제형(single cell → spheroid), 경로(수술 → 주사) 세 가지를 바꾼다.", [
        P("교수님 연구팀의 답은 세 가지를 동시에 바꾸는 것이다. 하나씩 이유를 보자.", [27]),
        P("첫째, **재료**다. multipotent한 MSC로는 한계가 뚜렷했다. 그래서 pluripotent한 iPSC로 바꾼다. "
          "{g|교수님은 이를 ‘5G 시대에 2G 폰을 쓰는 것’에 비유했다.} "
          "국내에서 iPSC를 환자에게 투여한 곳은 교수님 연구팀이 거의 유일하다 {g|(국내 31명 중 30명, 연세대 카리스바이오 1명)}.", [25]),
        FS("s09.png", "For better cell therapy… change cell origin?", "그림에서 볼 것", [
            "피라미드 아래가 MSC, 위가 iPSC와 ESC다.",
            "왼쪽 2G 폰과 오른쪽 5G 폰이 비유다.",
        ], [25]),
        P("둘째, **제형**이다. 연골세포는 기질 안에 있을 때만 안정적인 세포다. 기질 없이 꺼내 배양하면 1주일 안에 죽거나 "
          "fibroblast로 변성된다. 그래서 세포 덩어리인 **spheroid**가 기능적으로 우수하다. 반면 single cell은 다루기 편하고 주사가 쉽다. "
          "즉 제형은 spheroid로 하되 주사가 가능하게 만드는 **중용**, 곧 주사형 spheroid(injectable spheroid)가 필요하다.", [24, 25]),
        FS("s10.png", "For better cell therapy… different CMC?", "그림에서 볼 것", [
            "왼쪽 single cell은 다루기 쉽다(practical).",
            "오른쪽 spheroid는 기능이 좋다(functional).",
        ], [25]),
        P("셋째, **경로**다. 환자들은 인공관절 수술을 두려워한다. 그래서 수술이 아니라 주사로 넣는 접근성이 중요하다. "
          "{g|수술하는 의사(surgeon)에 따라 결과가 갈리고, 수술이 잘 안 된 환자들의 하소연이 두려움을 키운다는 이야기도 있었다.}", [26, 27]),
        P("세 가지를 합친 개념이 ‘뭉치면 살고 흩어지면 죽는다’다. 연골세포를 하나씩 넣으면 취약하지만, "
          "여러 세포(multicellular, cell aggregation)와 ECM을 함께 넣으면 강력해진다. 교수님 연구팀이 세계 최초로 제시한 개념이다. "
          "{g|제품은 입셀(YiPSCELL)의 MIUChon(뮤콘), Newer formula + Stronger cell source + Easier access.}", [27, 28]),
        FS("s13.png", "United we stand, divided we fall", "그림에서 볼 것", ["한 마리보다 뭉친 새들이 살아남는다."], [28]),
        P("국내 회사들도 같은 방향으로 움직이고 있다. auto에서 allo로, single cell에서 조직을 모사(mimic)하는 제형으로 전환(turn)하고, MSC에서 pluripotent 세포로 바꾸고 있다. "
          "{g|경쟁사: 카티스템, 조인트스템, 카틸로이드, 카티큐어, 인보사 등}", [23, 24]),
        CHK("연골세포는 기질에서 떼어 단독으로 배양할 때 가장 안정적이고 기능이 좋다.", "X", [25, 28], why="1주일 안에 죽거나 fibroblast로 변한다."),
    ]))
    top.append(Q("iPSC spheroid가 연골을 재생한다는 증거는?", CH5,
                 "토끼, 비글, 돼지에서 연골이 개선되었고, 비글에서는 채워진 연골이 사람 단백질이었다.", [
        P("교수님 연구팀은 iPSC 유래 연골 spheroid {g|(약 200 µm)}를 동물에 투여했다. 토끼에서 연골이 개선되었다.", [28]),
        P("비글(beagle dog)에서는 퇴행성 모델을 만들어 1년 동안 보았다. 위약군은 연골이 망가지고 osteophyte가 생겼지만, "
          "투여군은 기능이 회복되고 연골 결손이 채워졌다. 핵심은 채워진 연골이 개가 아니라 **사람 단백질**이었다는 점이다. "
          "{g|약 7, 8년 전부터 진행했다. 비글 8마리, 십자인대 절단과 반월판(meniscus) 찢김(tearing) 손상 모델.}", [28]),
        P("돼지에서도 결손 충전과 부피 변화가 대조군보다 컸고, 연골이 많이 망가지는 zone 1, 2에서 개선이 확실했다 {g|(4마리 vs 4마리)}. "
          "즉 투여한 세포가 직접 연골을 재생할 가능성을 보였다.", [29]),
        CHK("비글 실험에서 새로 채워진 연골은 개의 단백질이었다.", "X", [28], why="사람 단백질이었다."),
    ]))
    top.append(Q("왜 iPSC를 allo로 쓰는가?", CH5,
                 "auto는 한 사람에 약 10억 원과 2년이 들어 상업화가 불가능하므로, bank를 만든 off-the-shelf allo가 필요하다.", [
        P("세포 종류와 이식 방식을 조합하면 네 가지가 나온다. MSC auto는 쉽지만 의료 기술에 그친다. MSC allo는 치료제가 되지만 규제로 어려워진다.", [30]),
        P("iPSC는 pluripotent라 규제 기관이 더 까다롭게 본다. 그중 iPSC auto는 맞춤 의학적으로는 이상적이다. "
          "그러나 한 사람의 피를 뽑아 iPSC를 만들고 다시 넣는 데 **약 10억 원과 2년**이 든다. 그래서 상업화가 불가능하다.", [30]),
        P("결국 iPSC는 bank를 만들어 누구에게나 줄 수 있는 **off-the-shelf allo**여야 한다. "
          "교수님 연구팀은 여기에 spheroid 제형과 주사 경로까지 더해, 식약처가 다뤄 보지 못한 가장 어려운 길을 택했다.", [30]),
        FS("s14.png", "Part 1 Summary: MSC, iPSC × auto, allo", "그림에서 볼 것", ["오른쪽으로 갈수록 어렵고(달고나 모양), 맨 오른쪽이 교수님 연구팀의 선택이다."], [30]),
        CHK("iPSC를 자기 세포로 만들어 자신에게 넣는 방식은 비용 약 10억 원과 2년이 들어 상업화가 어렵다.", "O", [30]),
    ]))

    # ================================================================ 6. 임상과 전망
    top.append(Q("임상에서는 어디까지 왔나?", CH6,
                 "IND 허가 후 1상(3명)에서 안전성을 확인했고, 2상(30명) 투여가 거의 끝났다.", [
        MEMO("Part 2(식약처 허가 과정)는 교수님께서 3분 만에 빠르게 넘어간 부분입니다.", [31]),
        P("{b|IND(Investigational New Drug) 허가는 임상시험용으로 투여하기 위해 규제기관(식약처)에서 받는 초기 허가이다}.", [31, 1001], effort="이해"),
        P("{p|확인 필요: 스크립트(음성 변환)는 허가 2023년 8월 1일, 투여 2025년. 사람이 쓴 정리본은 IND 허가를 2024년 8월로 적었다.}", [31]),
        P("1상(Phase 1)의 목적은 효과가 아니라 **안전성**이다. 3명에게 투여했고 부작용은 없었다. {g|샘플 1개에 1억 원이 들었지만 지금은 약 2, 300만 원 수준이다.}", [31, 32]),
        P("그런데 MRI에서 흥미로운 신호가 보였다. 연골 결손(defect size)이 줄었고, 세 번째 환자는 연골 두께(cartilage thickness)가 연속 MRI에서 늘었다. "
          "{g|MRI에서 검정은 뼈, 하양은 synovial fluid, 회색은 연골이다.} "
          "다만 위약 대조가 없으므로 효과라고 말할 수는 없고 탐색적 신호다.", [32]),
        P("그래서 지금 2상이 진행 중이다. 30명(뮤콘 15명, 위약 15명)이며 다음 주 마지막 투여다.", [32]),
        CHK("1상 임상시험은 유효성이 아니라 안전성(부작용)을 보는 단계이다.", "O", [31, 32]),
    ]))
    top.append(Q("앞으로 재생 치료는 어디로 가는가?", CH6,
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
