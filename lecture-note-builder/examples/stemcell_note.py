"""Compact note for '줄기세포를 이용한 맞춤의학 기술 개발 및 임상 적용' (맞춤의학, 2026-10-12, 주지현 교수님).

Inputs of this run (nothing else is used):
  * script   inputs/stemcell_script.txt   (33 paragraphs = the 33 time blocks of the transcript)
  * pictures inputs/stemcell_figs/        (the 15 slide images taken from the user's 정리본 DOCX - pictures only, no text)
  * PAD      the PAD DOCX (11 questions) - used ONLY to decide what is blue. Blue = content that appears in a PAD
             question/answer, with the PAD unit cited (1001...). There is no 기출 section.

Template templates/mom_compact.yaml. Techniques: check boxes, effort tags, author additions (grey parentheses).
Run:  python -m examples.stemcell_note > outputs/stemcell/note_authored.json
"""
from app.models import Statement
from examples.authoring import Arrow, Diagram, Group, SlideTable, T, dump

FIG = "inputs/stemcell_figs/"
CH1 = "치료제의 역사와 재생 의학"
CH2 = "줄기세포의 종류와 특성"
CH3 = "퇴행성 골관절염과 연골 재생 치료"
CH4 = "MSC 임상시험과 한계"
CH5 = "iPSC 유래 연골 스페로이드"
CH6 = "임상 개발 현황과 전망"


def _st(kind, text, g, **kw):
    kw.setdefault("origin", "both")
    return Statement(text=text, slide_refs=list(g), kind=kind, **kw)


def B(text, g=(), effort=""):
    return _st("bullet", text, g, effort=effort)


def AUTH(text):
    return Statement(text=text, origin="author", kind="bullet")


def CHK(text, answer, g, summary="", why=""):
    return _st("check", text, g, answer=answer, left_title=summary, explanations=[why] if why else [])


def CONCEPT(title, lines, g):
    return _st("concept", "", g, left_title=title, left=["- " + x for x in lines])


def FS(img, caption, title, lines, g=()):
    return _st("figure_side", caption, g, image=(FIG + img) if img else "", left_title=title,
               left=["- " + x if not x.startswith(("- ", "  ")) else x for x in lines])


def COLS(title, groups, g=()):
    return _st("columns", title, g, diagram=Diagram(kind="compare", groups=[
        Group(title=t, color=c, items=list(items)) for t, c, items in groups]))


# PAD units (see parse_exam_docx): 1001 IND, 1002 Ryoncil, 1003 kidney organoid, 1004 organoid = 3D model,
# 1005 iPSC = reprogramming, 1006 recapitulation, 1007 highest potency = ESC, 1008 iPSC for personalised medicine,
# 1009 ESC from blastocyst, 1010 organoid for toxicity / regeneration, 1011 iPSC is not an MSC.


def build():
    top = []

    # ================================================================ 시험 정리 (front)
    summary_table = SlideTable(
        caption="주제별 핵심 요약 — 파랑 = 기출(PAD)에 나온 내용",
        col_widths_cm=[3.4, 14.0],
        rows=[
            ["주제", "핵심"],
            ["치료제 발전", "small chemical(1890년경, 아스피린) → 단백질(인슐린, 백신) → **항체** → **세포 치료제**(CAR-T) → 다음은 **재생 의학**(최종적으로 rejuvenation)"],
            ["ESC vs MSC", "ESC: blastocyst의 inner cell mass, 무한 증식·pluripotent, **윤리 문제**(학교에서 연구 불가) / MSC: 지방·골수·제대혈, multipotent, 증식 한계, 윤리적·안전. {b|ESC는 blastocyst의 inner cell mass를 배양한 세포}"],
            ["분화능 위계", "{b|totipotent > pluripotent(ESC, iPSC) > multipotent(MSC). 분화능이 가장 높은 것은 ESC·iPSC}. {b|iPSC = 체세포에 야마나카 인자 4가지를 넣는 reprogramming}, {b|맞춤의학에 응용}"],
            ["연골 재생 방식", "**auto**(내 세포 → 의료 기술, 쉽지만 상업화 불가) vs **allo**(치료제 → 식약처 허가 필요, 어려움). 카티스템(제대혈 MSC), 인보사(암세포 혼입 → 품목허가 취소)"],
            ["세포 유래 치료제", "① **ECM**(연골 기질) ② **small molecule**(secretome, exosome, 미토콘드리아) ③ {b|오가노이드(3D 세포 덩어리, 독성평가·재생치료에 응용)}"],
            ["MSC 임상", "골수 MSC 무릎 주사 RCT(12 vs 12): 9개월째 통증 점수만 유의, MRI 연골 재생은 유의하지 않음(T2 mapping 질적 변화는 약간 유리)"],
            ["한국·미국 MSC", "한국: 2010년대 초 4개 허가 → 카티스템만 생존. 미국: {b|Ryoncil = 골수 유래 MSC, GVHD, 2024년 12월 FDA 최초 허가}"],
            ["iPSC 스페로이드", "연자팀 전략 3가지: **재료**(MSC → iPSC) · **제형**(single cell → 스페로이드) · **경로**(수술 → 주사). 뮤콘(MIUChon) = 동종 iPSC 유래 연골 스페로이드"],
            ["임상 단계", "{b|IND 허가 = 임상시험용 초기 허가}(참고 수준) → 1상 3명(안전성, MRI 연골 결손 감소) → 2상 30명(뮤콘 15 · 위약 15). 일본: iPSC 치료제 조건부 허가"],
        ])
    top.append(T("요약 정리 · 시험 정리", "", [], [
        _st("para", "이 한 쪽이 시험 대비용이다. 파랑은 기출(PAD)에 나온 내용이고 본문에서 다시 근거와 함께 나온다.", [1]),
        _st("diagram", "강의 전체 흐름 — 본문 6개 장", [1, 3, 9, 12, 24, 31], diagram=Diagram(
            kind="flow", arrows=[Arrow(src=i, dst=i + 1, label="") for i in range(5)], groups=[
                Group(title="① 역사·재생 의학", color="teal", items=["케미컬 → 단백질 → 항체 → 세포", "다음은 재생"]),
                Group(title="② 줄기세포 종류", color="blue", items=["ESC · MSC · iPSC", "분화능 위계"]),
                Group(title="③ 연골 재생", color="salmon", items=["auto vs allo", "ECM · 미토콘드리아"]),
                Group(title="④ MSC의 한계", color="amber", items=["RCT 결과", "한국 MSC · Ryoncil"]),
                Group(title="⑤ iPSC 스페로이드", color="violet", items=["재료 · 제형 · 경로", "전임상"]),
                Group(title="⑥ 임상·전망", color="teal", items=["IND · 1상 · 2상", "일본 iPSC"]),
            ])),
    ], tables=[summary_table], role="front"))

    # ================================================================ 1. 치료제의 역사와 재생 의학
    top.append(T("치료제의 발전과 다음 단계", CH1, [], [
        B("{g|오늘의 내용: 줄기세포의 종류와 특성 / 퇴행성 골관절염의 병태생리와 재생 치료의 필요성 / 재생 치료 전략과 전임상 연구(환자에게 투여하기 전 동물 대상 연구) / 임상 연구 결과의 해석. 50분 강의.}", g=[1, 2]),
        FS("s01.png", "치료제 모달리티의 발전: 케미컬 → 단백질 → 항체 → 세포 → 재생", "치료제는 점점 짧은 간격으로 바뀐다", [
            "아카데미아(의대) → 클리닉(서울성모병원) → 인더스트리로 이어지는 연결 고리가 현재 바이오에서 중요하다",
            "**1890년경 small chemical**(아스피린) → 약 100년 뒤 **단백질**(인슐린, 백신) → 약 30년 뒤 **항체** → 약 15년 뒤 **세포 치료제**(CAR-T)",
            "**항체**: 특이성(specificity)으로 타겟을 정확히 겨냥한다",
            "**CAR-T**: 혈액내과·종양 치료에서 ‘유도 미사일’처럼 특정 물질을 강력하게 제거한다",
            "간격은 짧아지고 정확도·파괴력은 높아졌다 → {r|다음 단계는 파괴보다 재생}: 부족한 부분을 메우고 없는 장기를 새로 만드는 치료, 최종적으로 **rejuvenation**(역노화, 장기를 젊은 상태로)",
        ], g=[3, 4, 5, 6]),
        CHK("치료제 모달리티의 발전 순서는 small chemical → 단백질 → 항체 → 세포 치료제이다.", "O", [3, 4, 5],
            summary="케미컬 → 단백질 → 항체 → 세포 치료제 → (다음) 재생 의학"),
    ]))

    # ================================================================ 2. 줄기세포의 종류와 특성
    top.append(T("ESC와 MSC", CH2, [], [
        FS("s02.png", "한국에서 쓸 수 있는 줄기세포: iPSC(역분화), ESC, MSC", "배아줄기세포(ESC)와 윤리", [
            "정자·난자 → **blastocyst** → 안의 **inner cell mass**를 꺼내 배양하면 배아줄기세포",
            "천주교는 수정(fertilization) 순간부터 생명으로 보므로 inner cell mass를 꺼내는 것이 윤리적으로 어렵다 → **학교에서 ESC는 연구할 수 없다**",
        ], g=[7]),
        B("{b|ESC는 blastocyst의 inner cell mass에서 분리해 배양한 세포이다}", g=[7, 1009]),
        COLS("ESC vs MSC(성체줄기세포)", [
            ("ESC (배아줄기세포)", "salmon", ["유래: blastocyst의 inner cell mass", "분화능: 모든 세포로 분화(pluripotent)", "증식: 무한 증식", "장점: 여러 조직으로 분화, 상업적으로 유용", "한계: **윤리 문제**"]),
            ("MSC (성체줄기세포)", "teal", ["유래: 지방 · 골수 · 제대혈", "분화능: 제한된 분화능(multipotent)", "증식: 계대 배양하면 줄기세포 능력을 잃는다", "장점: **윤리적으로 유리, 안전**(강력할수록 부작용도 강하다)", "한계: 상업적으로 부족"]),
        ], g=[7, 8]),
        CHK("MSC는 모든 세포 계통으로 분화할 수 있는 pluripotent 세포이다.", "X", [8, 9],
            summary="ESC = 강력하지만 윤리 문제 / MSC = 약하지만 안전하고 윤리적",
            why="MSC는 몇 개 계통으로만 가는 multipotent이다."),
    ]))
    top.append(T("분화능의 위계와 iPSC", CH2, [], [
        CONCEPT("분화능의 위계", [
            "**totipotent**: 세포 하나가 생명 개체가 될 수 있다 (‘신의 영역’이라 연구자가 부담스러워 한다)",
            "**pluripotent**: 모든 계통으로 분화 — ESC, iPSC (등급이 같다)",
            "**multipotent**: 몇 개 계통으로만 분화 — 성체줄기세포(MSC)"], [9]),
        B("{b|분화능이 가장 높은 것은 pluripotent인 배아줄기세포(ESC)와 유도만능줄기세포(iPSC)이고, 성체줄기세포(MSC)는 그보다 등급이 낮은 multipotent이다}", g=[9, 1007]),
        B("{b|iPSC는 체세포를 얻어 야마나카 인자 4가지를 넣어 reprogramming(역분화)시켜 만든다}", g=[9, 10, 1005]),
        B("{b|iPSC는 개인의 체세포에서 유도할 수 있어 맞춤의학(개인별 약제 독성평가, 재생 치료)에 응용된다}", g=[9, 1008]),
        B("{b|MSC는 지방·골수·제대혈 유래 성체줄기세포이므로, iPSC는 MSC와 같은 분류에 들어가지 않는다}", g=[8, 9, 1011]),
        FS(None, "", "야마나카 신야와 iPSC의 위상", [
            "reprogramming factor(야마나카 인자)를 개발해 **2006년 Cell**에 논문, **2012년 노벨상**. 정형외과 의사이다",
            "미국·유럽에서는 줄기세포가 치료 모달리티로 인정을 잘 받지 못했으나, Nature가 ‘Stem cell therapy to the clinic’ 기사를 싣는 등 **임상 단계로 들어오기 시작**했다",
            "일본에서는 iPSC 치료제 개발에 대한 기대와 압박이 야마나카에게 집중되어 있다",
        ], g=[10]),
        AUTH("외우는 법: toti(개체) > pluri(모든 계통) > multi(몇 계통) — 앞 글자가 클수록 분화능이 크다."),
    ]))

    # ================================================================ 3. 퇴행성 골관절염과 연골 재생
    top.append(T("퇴행성 골관절염", CH3, [], [
        B("20대에 연골 상태가 가장 좋고 이후 내리막이다. 퇴행성 골관절염 = **연골세포의 노화**, 질적·양적 하락", g=[11]),
        B("**초기**는 내과 영역: 진통제·소염제로 경과 관찰 / **말기**는 관절 기능이 없어져 정형외과에서 **인공관절 수술**", g=[11]),
        B("연골이 닳는 약 **20년** 동안 이 과정을 다룰 방법이 아직 없다 → 줄기세포의 재생 능력으로 **늦추거나 멈추거나 되돌릴 수 있다면** 혁명적 치료가 된다", g=[11, 12]),
        CHK("퇴행성 골관절염의 초기에는 인공관절 수술이 일차 치료이다.", "X", [11],
            summary="초기 = 진통제·소염제(내과), 말기 = 인공관절(정형외과), 그 사이 약 20년은 방법이 없다",
            why="초기는 진통제·소염제, 인공관절은 말기이다."),
    ]))
    top.append(T("연골 재생 치료의 방식: auto vs allo", CH3, [], [
        FS("s03.png", "기존 연골 재생 치료: auto-transplantation과 allo-transplantation, 모두 한계가 있다", "치료제인가, 의료 기술인가", [
            "내 몸에서 꺼낸 **성체줄기세포**(골수·지방·제대혈) 또는 쓰지 않는 부위의 **연골세포**를 확장 배양해 다시 넣는다 — 안전하고 만들기 쉽다",
            "한계: 연골이 재생되더라도 **품질이 낮거나 섬유화**되고, 실제로 재생되었다는 **과학적 증거**를 제시한 치료제가 별로 없다 → 메이저 치료 모달리티로 인정받지 못함",
        ], g=[12, 13]),
        COLS("auto vs allo", [
            ("auto-transplantation", "teal", ["내 세포를 꺼내 → 배양 → 내게 다시 투여", "**치료제가 아니라 의료 기술** → 규제를 덜 받고 병원·의사의 영역", "수술로 주입", "쉽지만 **상업화·치료제 인정은 불가**"]),
            ("allo-transplantation", "salmon", ["다른 사람의 세포를 제조해 여러 환자에게", "**치료제 영역** → 식약처 허가가 필요", "규제 기관의 허가 때문에 난이도가 높다"]),
        ], g=[12]),
        B("**카티스템(Cartistem)**: 메디포스트가 제대혈에서 개발한 세포 치료제, 수술로 주입. 현재 쓰이는 약", g=[13]),
        B("**인보사(Invossa)**: allo 치료제로 2017년경 허가 → 세포 성분의 **품질 관리 실패로 암세포가 혼입**(증식해 main population이 됨) → **품목허가 취소**, 식약처와 코오롱티슈진의 소송이 이어지고 있다", g=[13]),
        CHK("자신의 세포를 꺼내 다시 넣는 auto 방식은 치료제가 아니라 의료 기술로 분류된다.", "O", [12],
            summary="auto = 의료 기술(규제 적음, 상업화 어려움) / allo = 치료제(식약처 허가)"),
    ]))
    top.append(T("세포 유래 치료제의 세 범주", CH3, [], [
        FS("s04.png", "줄기세포 유래 치료제 후보: ECM, small molecule, 3D organoid", "세포 치료제 = 세포 + 세포 유래물 + 세포 덩어리", [
            "과거에는 stem cell therapeutics = single cell 치료제로만 인식했으나, 지금은 **세포 유래 기질·물질·세포 덩어리**도 세포 치료제의 큰 카테고리이다",
            "① **세포외기질(ECM)** ② **small molecule**(secretome, exosome, 미토콘드리아) ③ **오가노이드**(세포 덩어리)",
        ], g=[14]),
        B("{b|오가노이드는 줄기세포에서 분화한 3D 세포 덩어리로 장기의 구조와 기능을 모사하며, 약제 독성평가·재생치료에 응용된다}", g=[14, 23, 1004, 1010]),
        _st("reference", "수업에서 직접 다루지 않았지만 기출에 나온 개념: {b|환자 유래 줄기세포로 환자의 병적 세포를 만들어 병적 상태를 흉내 내는 기술 = recapitulation}, {b|신장 오가노이드는 혈관세포 분화가 제한적이다}", [1006, 1003]),
        AUTH("유래 기준으로 외우면 쉽다 — 세포가 만든 ‘집’(ECM), 세포에서 떨어진 ‘조각’(small molecule), 세포가 뭉친 ‘덩어리’(organoid)."),
    ]))
    top.append(T("ECM", CH3, [], [
        FS("s05.png", "ECM(세포외기질) — 줄기세포 유래 치료제 후보", "ECM: 세포가 만든 기질이 세포를 돌본다", [
            "연골세포가 만든 **hyaline cartilage**(연골 기질) 자체가 치료제로 인식된다 — 연골세포를 오래 살게 하고 기능을 촉진(facilitation)한다",
            "연자 실험: **iPSC로 연골세포 덩어리를 만들고 세포를 제거해 ECM만** 남김 → 분화 중인 연골세포에 처리하니 **연골세포 marker 발현 증가** → 연골 결손에 이식하니 연골이 잘 메꿔졌다",
            "이유: 살아 있는 세포는 암세포로 바뀔 우려 등으로 **규제 기관이 까다롭게** 보지만, ECM은 변하지 않는 **무생물**이라 훨씬 편하게 본다",
            "이미 쓰이는 제품: 히루안·시노비안·콘드란 같은 연골 기질 제품, **메가카티**(사체 연골 기증). 국내는 사체 이용 법률 때문에 시술이 불가능해 **수입**한 연골로 개발한다",
        ], g=[15, 16]),
        CHK("ECM은 살아 있는 세포가 아니므로 규제 기관이 세포 치료제보다 편하게 본다.", "O", [15],
            summary="ECM = 세포가 만든 기질. 무생물이라 규제 부담이 작다"),
        AUTH("ECM은 세포가 지은 ‘집’이고, 그 집이 다시 세포를 보호해 준다."),
    ]))
    top.append(T("Small molecule과 미토콘드리아", CH3, [], [
        FS(None, "", "세포에서 떨어져 나온 물질: secretome, exosome, 미토콘드리아", [
            "세포를 넣기 어려우니 **차선책**으로 시작했지만, 연자는 이것이 잘못된 생각이었음을 알았다 — 규제 기관이 **기준을 강화**하고 **원재료 기준**까지 요구하기 때문이다",
            "**미토콘드리아**: 만성 퇴행성 질환(골관절염, 알츠하이머 등)에서 기능·양의 부족이 알려져 있다 (원인이 아니라 **연관 요인**)",
            "MIA 골관절염 동물 모델 무릎에 **분리한 미토콘드리아**를 넣었더니 연골이 많이 개선(빨간색 = 연골 기질) — 세포가 에너지를 받아 분화·이동이 빨라지고, 연골 덩어리 제작에도 도움",
            "**iPSC 유래 미토콘드리아**가 성체줄기세포 유래보다 효과가 좋았다 — 리프로그래밍으로 젊어진 세포의 미토콘드리아 = **충전된 건전지**",
            "미토콘드리아 이식은 에너지가 많이 필요한 **근육병증**(inflammatory myopathy)에서도 효과가 보고되어 임상 연구가 진행 중이다",
        ], g=[17, 18]),
        CHK("iPSC에서 분리한 미토콘드리아가 성체줄기세포 유래보다 연골 개선 효과가 좋았다.", "O", [18],
            summary="미토콘드리아도 치료제 모달리티가 될 수 있다 — 젊은(iPSC 유래) 것이 더 효과적"),
    ]))

    # ================================================================ 4. MSC 임상시험과 한계
    top.append(T("MSC 골관절염 RCT", CH4, [], [
        B("연자가 약 10년 전 처음으로 **골수 유래 MSC**를 골관절염 환자 무릎에 주사하는 **RCT**를 수행했다. 실험실 세포를 환자에게 넣는 것은 난이도가 다르다 — 식약처의 **규제 과학** 기준을 맞춰야 한다 (2018년부터 협의, **2019년** 첫 투여. 성의회관 2층 세포처리시설, sono-guided injection)", g=[19]),
        B("**결과**: 대조군 12명 vs MSC 12명, 1년 관찰. 연자는 12개월 내내 p value 0.001 이하의 큰 차이를 기대했으나 **9개월째 WOMAC pain · VAS pain 점수만** 통계적으로 유의했고, 기대한 **MRI 연골 재생**은 유의하지 않았다 (골수 병변·염증 병변도 마찬가지)", g=[20]),
        B("**T2 mapping**(연골 노화·퇴행을 보는 MRI 시퀀스, 정준영 교수 도움)으로 보니 연골의 **질적 변화**는 약간 유리 — **medial compartment**에서만 p < 0.05로 ‘덜 나쁘게’ 만들었다 (lateral은 차이 없음)", g=[20]),
        B("연자 평가: 환자를 대상으로 한 첫 translational research였지만 **절반의 성공**", g=[20]),
        CHK("MSC RCT에서 MRI상 연골 재생은 통계적으로 유의했다.", "X", [20],
            summary="MSC 주사: 통증은 9개월째만 유의, 연골 재생은 유의하지 않음 (12 vs 12)",
            why="통증 점수만 9개월째 유의했고, MRI 연골 재생은 유의하지 않았다."),
    ]))
    top.append(T("한국의 MSC 치료제와 Ryoncil", CH4, [], [
        FS("s06.png", "한국 줄기세포 치료제: 초기 산업화 → 후기 상용화 → R&D 지연 (허가 vs 허가 거부)", "한국은 MSC 강국이었지만…", [
            "황우석 퇴출 후 국가가 **성체줄기세포(MSC) 치료제**를 밀어 주었고 **2010년대 초 4개**가 허가되었다 (당시 세계적으로도 드문 일)",
            "효과가 부족해 **메디포스트의 카티스템**만 살아남았고 나머지는 생산 중단, 이후 국가는 허가를 내주지 않는다 → 세포 치료제에 대한 실망",
            "**Neuronata-R**(루게릭병 MSC): 임상 2상 성공 → **3상 마지막(미국 임상)에서 실패**, 코아스템켐온 주가가 **10분의 1**로 하락 (연자 추정 2,000억 원 이상 투입)",
            "‘It’s a dead end’ 표지판 비유: 안전하더라도 **1회 주사 약 2,000만 원**인데 근거(evidence)를 못 주면 앞날이 불투명하다",
        ], g=[21]),
        B("{b|Ryoncil은 골수 유래 MSC로, GVHD에 대해 2024년 12월 미국 FDA가 최초로 허가한 줄기세포 치료제이다}", g=[22, 1002]),
        B("연자 평가: 치료제가 거의 없는 GVHD라서 허가된 것이고, 대안이 생기면 살아남을지는 의문 — 지금까지의 MSC 치료제는 **‘도토리 키재기’**", g=[22]),
        CHK("한국에서 허가된 MSC 치료제 중 현재까지 살아남은 것은 카티스템이다.", "O", [21],
            summary="한국 MSC: 2010년대 초 4개 허가 → 카티스템만 생존 / 미국: Ryoncil(GVHD)"),
    ]))

    # ================================================================ 5. iPSC 유래 연골 스페로이드
    top.append(T("조직 치료제로의 이동과 경쟁사", CH5, [], [
        FS("s07.png", "줄기세포 유래 치료제 후보 — 3D organoid(세포 덩어리)", "single cell의 한계 → 세포 덩어리", [
            "single cell이나 세포 유래물질의 **efficacy가 제한**적이라, 세포 치료제의 기능을 극대화한 **세포 덩어리(오가노이드) 형태의 조직 치료제**로 발전하고 있다",
            "연자팀의 연골 조직 제재 = **스페로이드(spheroid)**, 회사는 **입셀(YiPSCELL)**, 제품명 **뮤콘(MIUChon)**",
        ], g=[23]),
        FS("s08.png", "연골치료제 개발 후보: MSC · 연골세포 · iPSC, single cell · multi cell", "경쟁사들도 같은 방향으로 이동", [
            "카티스템, 조인트스템, 카틸로이드, 카티큐어, 인보사 등 국내에 회사가 많은 이유는 연골 재생 치료제의 **시장이 크기** 때문이다",
            "원래는 대부분 single cell이었지만 연자팀을 따라 ① **auto → allo** ② **single cell → 조직(스페로이드) 제형** ③ **MSC → pluripotent 세포**로 바꾸고 있다",
            "연골세포는 **shy**한 세포 — 연골 기질 안에서 ‘벌집 속 애벌레’처럼 있을 때만 안정적이고 기능을 잘한다",
            "{g|경쟁사 주주들의 비판, 2주일 전 국회의원의 협조 요청과 국정감사 참고인 출석 등 연자의 개인 사정은 생략}",
        ], g=[23, 24]),
        CHK("경쟁사들도 single cell에서 조직(스페로이드) 제형으로 방향을 바꾸고 있다.", "O", [24],
            summary="국내 회사들도 allo · 조직 제형 · pluripotent 세포 쪽으로 이동 중"),
    ]))
    top.append(T("세 가지 전략: 재료 · 제형 · 경로", CH5, [], [
        FS("s09.png", "For better cell therapy…change cell origin? — MSC(2G) vs iPSC/ESC(5G)", "① 재료: MSC → iPSC", [
            "‘5G 폰 시대에 2G 폰을 쓰는 것’: multipotent한 MSC보다 **pluripotent한 iPSC/ESC**(unlimited differentiation)로 옮겨 간다",
            "pluripotent 세포를 분화해 환자에게 투여한 국내 회사는 연자팀뿐 — ESC는 파킨슨병 치료제를 개발하는 회사가 1~2곳, **iPSC**는 연자팀이 유일(연세대 스핀오프 **카리스바이오**가 지난달 첫 환자 1명 투여 → 국내 총 31명 중 30명이 연자 기관)",
        ], g=[25]),
        FS("s10.png", "For better cell therapy…different CMC? — 기능은 스페로이드, 다루기는 single cell", "② 제형(CMC): single cell vs 스페로이드", [
            "**CMC**(chemistry, manufacturing, control) 제형: single cell과 spheroid",
            "**single cell**: 다루기 편하고 주사 가능(practical). 그러나 기질을 깨고 세포만 배양하면 **1주일 내 사멸하거나 fibroblast로 변성**",
            "**스페로이드**: 조직 형태를 유지해 안정적이고 **기능적으로 우수**(조직 모사), 다루기는 어렵다",
            "결론은 **중용**: 제형은 덩어리(스페로이드)로, 투여는 수술이 아니라 **injection**으로 — 내과 출신인 연자의 개발 전략",
        ], g=[25]),
        FS("s11.png", "Distinguished approaches: (1) new cell, (2) CMC & (3) route", "③ 경로: 수술 → 주사", [
            "인공관절 수술이 잘 된 환자는 만족하지만 **안 된 환자는 더 힘들어져** 하소연하고 다녀서, 수술 전 환자들이 두려워한다 → **수술이 아니라 주사**라는 접근성이 중요하다",
            "**세 가지**: ① 재료(MSC → iPSC) ② 제형(single → cell aggregation, 스페로이드) ③ 경로(수술 → injectable)",
        ], g=[26, 27]),
        FS("s13.png", "스페로이드의 의미: United we stand, divided we fall", "‘뭉치면 살고 흩어지면 죽는다’", [
            "연골세포를 하나씩 넣으면 취약하지만 **multicellular + ECM**을 함께 넣으면 강력한 제형이 된다",
            "연자팀이 **세계 최초로 개발한 개념**이고 임상 2상까지 왔으며, 이제 국내외 회사들이 따라 한다",
        ], g=[27, 28]),
        FS("s12.png", "Spheroids: MIUChon = Newer formula + Stronger cell source + Easier access", "뮤콘(MIUChon)의 개념", [
            "AS-IS: single cell(흩어진 물고기) → TO-BE: multi-cell therapeutics(뭉친 물고기)",
            "**N**ewer formula(스페로이드) + **S**tronger cell source(iPSC) + **E**asier access(주사)",
        ], g=[27, 28]),
        AUTH("세 가지는 ‘재료 · 제형 · 경로’ 세 단어로 외운다."),
        CHK("연골세포는 기질에서 떼어 단독으로 배양할 때 가장 안정적이고 기능이 좋다.", "X", [25, 28],
            summary="재료 = iPSC, 제형 = 스페로이드, 경로 = 주사 — 연골세포는 뭉쳐 있을 때 안정적",
            why="기질 없이 세포만 배양하면 1주일 내 사멸하거나 fibroblast로 변한다."),
    ]))
    top.append(T("스페로이드 전임상 연구", CH5, [], [
        B("**iPSC 유래 약 200 µm 크기 스페로이드**를 치료제로 개발했다", g=[28]),
        B("**토끼**: 연골 개선", g=[28]),
        B("**비글(beagle dog)**: 십자인대 절단 + 반월판(meniscus) 긁어냄으로 퇴행성 모델을 만들고(8마리) 1년 관찰하고, 3개월 시점에 연골 스페로이드가 보였다. **위약군**은 기능 저하·연골 손상·osteophyte(비정상 뼈 리모델링), **뮤콘군**은 기능이 회복되고 연골 결손이 많이 채워졌다", g=[28]),
        B("채워진 연골은 개의 단백질이 아니라 **사람 단백질**임을 확인 → 투여한 세포가 **직접 연골 재생**에 기여한다는 근거", g=[28]),
        B("**돼지**(4마리 vs 4마리, 연골 손상 모델): 대조군보다 결손 충전·**부피 변화**가 증가. 구역(zone)별 분석에서 연골이 많이 망가지는 **zone 1·2**에서 개선이 확실했다. 논문으로 마무리", g=[29]),
        CHK("비글 실험에서 새로 채워진 연골은 개의 단백질이었다.", "X", [28],
            summary="토끼 · 비글 · 돼지 모두 연골 개선 — 비글에서는 사람 단백질로 채워짐을 확인",
            why="채워진 연골은 사람 단백질이어서 투여한 세포가 직접 재생에 기여했음을 보여 준다."),
    ]))
    top.append(T("정리: auto/allo × MSC/iPSC", CH5, [], [
        FS("s14.png", "Part 1 Summary: MSC·iPSC × auto·allo, 새 formula, 새 route", "네 가지 조합과 연자의 선택", [
            "연자팀은 **iPSC allo-transplantation + 스페로이드 + 주사**를 택했고, 식약처가 다뤄 보지 못한 제형이라 **난이도가 매우 높았다**",
            "현재 **1상 허가 완료, 2상은 30명 투여가 거의 끝났다**",
        ], g=[30]),
        COLS("MSC · iPSC × auto · allo", [
            ("MSC auto", "teal", ["내 것을 꺼내 내가 넣는다 — 매우 쉬움", "**의료 기술**, 의사도 시행 가능", "상업화·치료제 인정 불가"]),
            ("MSC allo", "blue", ["치료제가 되기 시작", "규제 기관의 규제를 받아 난이도 ↑"]),
            ("iPSC auto", "amber", ["pluripotent라 규제 기관이 **더 까다롭게** 본다", "연세대(카리스바이오) 방식, 연자팀보다 뒤처짐", "피 채취 → iPSC 뱅킹 → 재투여 **약 10억 원 · 2년**"]),
            ("iPSC allo", "salmon", ["뱅크를 만들어 **아무에게나** 투여 = **off-the-shelf**", "**상업성**이 있고 성공 가능", "연자팀의 선택"]),
        ], g=[30]),
        CHK("iPSC를 자기 세포로 만들어 자신에게 넣는 방식은 비용 약 10억 원·2년이 들어 상업화가 어렵다.", "O", [30],
            summary="상업화는 allo(off-the-shelf), 맞춤 의학적으로는 auto가 좋지만 비용·시간이 크다"),
    ]))

    # ================================================================ 6. 임상 개발 현황과 전망
    top.append(T("IND와 임상시험 결과", CH6, [], [
        B("Part 2(식약처 허가를 받기까지 보완 요청과 갈등을 겪은 기록)는 구체적인 내용이라 연자가 **3분 동안만 발표하고 넘어갔다**", g=[31], effort="참고"),
        B("{b|IND(Investigational New Drug) 허가는 환자에게 임상시험용으로 투여하기 위해 규제기관(식약처)에서 받는 초기 허가이다}", g=[31, 1001]),
        B("IND 허가(**2023년 8월 1일**) 후 **2025년 3명** 투여 완료. 샘플 1개 제작에 1억 원이 들었으나 지금은 약 2, 300만 원 수준으로 기술이 개발되었다", g=[31]),
        B("**1상**은 효과가 아니라 **부작용(안전성)** 을 보는 단계 — 3명에서 **부작용이 없었다**", g=[31, 32]),
        B("**MRI**: 3명 모두 연골 **결손(defect) 크기 감소**, 세 번째 환자는 연골 **두께가 serial MRI에서 증가**(가장 드라마틱). 1상은 위약 대조군이 없어 efficacy를 말할 수 없고 **탐색적 유효성(signal)** 만 확인했다", g=[32]),
        B("**2상**: 30명(**뮤콘 15 · 위약 15**), 다음 주 마지막 투여", g=[32]),
        CHK("1상 임상시험은 유효성이 아니라 안전성(부작용)을 보는 단계이다.", "O", [31, 32],
            summary="IND → 1상(3명, 안전성) → 2상(30명, 뮤콘 15 vs 위약 15)",
            why="1상은 부작용 확인이 목적이고, 위약 대조가 없어 efficacy는 평가하지 않는다."),
    ]))
    top.append(T("일본의 iPSC와 전망", CH6, [], [
        FS("s15.png", "Break News: World 1st conditional approval for iPSC therapy (일본)", "일본의 도전과 iPSC 치료제의 첫 허가", [
            "일본이 **10년 이상 투자** — Nature 사설 ‘Big bets on stem-cell therapies might soon pay off’",
            "**오카노**(게이오대): 척수 손상 환자에게 투여해 2명에서 운동 개선 / **타카하시 마사요**: 망막변성증 / 파킨슨병 치료도 진행",
            "iPSC 치료제가 올해 임상 연구가 아니라 **품목 허가(조건부)** 로 인정 — **심근세포 치료제와 파킨슨병 치료제**가 세계 최초",
            "{r|결론: 플루리포텐트 줄기세포 기반 차세대 재생 치료가 의사가 되었을 때 처방 목록에 들어올 것}",
        ], g=[33]),
    ]))
    # ================================================================ QUIZ
    top.append(T("QUIZ", CH6, [], [
        _st("quiz", "다음 중 연골 재생 치료의 auto-transplantation에 대한 설명으로 가장 알맞은 것은?", [12, 30],
            options=["① 다른 사람의 세포를 제조해 여러 환자에게 공급한다", "② 치료제가 아니라 의료 기술로 분류되어 규제를 덜 받는다",
                     "③ 식약처의 품목 허가가 반드시 필요하다", "④ 상업화에 가장 유리한 방식이다", "⑤ 스페로이드 제형만 사용한다"],
            answer="② 치료제가 아니라 의료 기술로 분류되어 규제를 덜 받는다",
            explanations=["① 다른 사람의 세포는 allo이다", "② 내 세포를 꺼내 내가 다시 넣는 것은 의료 기술이다 (정답)",
                          "③ 품목 허가는 치료제(allo)에 필요하다", "④ 상업화는 allo(off-the-shelf)가 유리하다", "⑤ 제형과는 무관한 분류이다"]),
        _st("quiz", "연자팀이 ‘더 좋은 세포 치료제’를 위해 바꾼 세 가지가 아닌 것은?", [27],
            options=["① 재료: MSC → iPSC", "② 제형: single cell → 스페로이드", "③ 경로: 수술 → 주사",
                     "④ 이식 방식: allo → auto"],
            answer="④ 이식 방식: allo → auto",
            explanations=["① 재료를 pluripotent한 iPSC로 바꾸었다", "② 제형을 세포 덩어리(스페로이드)로 바꾸었다", "③ 경로를 injectable로 바꾸었다",
                          "④ 연자팀은 오히려 auto가 아니라 **allo(뱅크, off-the-shelf)** 방식이다 (정답)"]),
    ]))
    return top


if __name__ == "__main__":
    import sys

    topics = build()
    for t in topics:  # script-only: the topic cites every paragraph its statements cite (PAD units included)
        t.slide_numbers = sorted({r for sts in t.sections.values() for st in sts for r in st.slide_refs})
    dump(topics, sys.stdout)
