"""Mixed-style note for 'T림프구 항원제시: MHC 유전자의 구성과 기능, 비전형적 T세포 인식' - written by the make-lecture-note workflow
(docs/WORKFLOW.md): script -> storyline.md -> this file -> build.

Inputs (nothing else is used):
  * script   inputs/tcell_script.docx   (40 speech paragraphs + 5 [검증참고] notes)
  * pictures inputs/tcell_figs/         (slide images from the 정리본 PDF - pictures only, no text from it)
  * PAD      inputs/tcell_pad.pdf       (18 questions) - used ONLY to decide what is blue.
Run:  python -m examples.tcell_wf_note > outputs/wf_tcell/note_authored.json
"""
from app.models import Diagram, Group, Statement
from examples.abx_note import B, DFULL, EX, LS, P, ROWS
from examples.authoring import T, dump
from examples.stemcell_note import CHK, MEMO

FIG_DIR = "inputs/tcell_figs/"
CH1 = "MHC(HLA) 유전자 영역의 구성"
CH2 = "MHC의 다양성: polymorphism과 polygeny"
CH3 = "MHC restriction과 예외적 T세포 반응"
CH4 = "Class Ib 분자와 비전형적 T세포"

# PAD units (parse order of inputs/tcell_pad.pdf)
(Q22_1, Q21_CD1c, Q21_cls2, Q20_alle, Q19_cls2poly, Q19_KIR, Q18_MICA, Q18_CD8, Q18_cls2div,
 Q16_allo, Q16_cls1b, Q16_NKG2D, Q16_restr, Q15_KIR, Q15_HLAE, Q11_restr, Q10_noAg, Q09_scan) = range(1001, 1019)
PAD_POLY = [Q22_1, Q20_alle, Q19_cls2poly, Q18_cls2div]
PAD_CLASS = [Q21_cls2, Q18_CD8, Q16_cls1b, Q10_noAg]
PAD_NK = [Q19_KIR, Q15_KIR, Q15_HLAE, Q18_MICA, Q16_NKG2D, Q16_cls1b, Q10_noAg]
PAD_RESTR = [Q16_restr, Q11_restr]


def FIG(img, caption, g=()):
    return Statement(text=caption, kind="figure", image=FIG_DIR + img, slide_refs=list(g))


# ---- the exam tables: SAME object on the front page and in the body
POLY = ROWS([
    ["class I", "HLA-A, HLA-B, HLA-C", "{b|HLA-B > HLA-A > HLA-C}"],
    ["class II", "HLA-DR, HLA-DP, HLA-DQ", "{b|DRB > DQB > DPB}\n{b|beta chain 쪽에 다형성 집중}"],
    ["class Ib", "HLA-E, HLA-F, HLA-G 등", "상대적으로 제한적"],
], col_titles=["구분", "분자", "다형성(다양성) 순서"], col_widths=[2.6, 5.6, 9.2], g=[6, 15, 16] + PAD_POLY)

EXCEPT = ROWS([
    ["{b|MHC restriction 적용}", "{b|peptide와 자기 MHC를 함께 인식하는 일반적인 T세포 반응}"],
    ["{b|예외}", "{b|alloresponse, transplantation(이식), superantigen}"],
], col_titles=["구분", "해당"], col_widths=[4.6, 12.8], g=[24, 25, 29] + PAD_RESTR + [Q16_allo])


def build():
    top = []
    # ================================================================ 앞쪽: 전체 지도 + 기출 두 유형 표
    top.append(T("요약 ① MHC 분자와 다형성 [기출]", "", [], [
        P("이번 강의는 MHC 유전자의 구성과 기능을 먼저 보고, 마지막에 조금 특이한 형태의 T세포 인식을 다룹니다. MHC가 왜 여러 종류인지, T세포가 실제로 무엇을 인식하는지가 초점입니다.", [1, 4]),
        DFULL("강의 전체 지도: 네 부분", Diagram(kind="tree", root="T세포 항원제시", groups=[
            Group(title="1. MHC 유전자 영역", color="teal", items=["6번 염색체", "class I, II, III", "HLA-A, B, C / DR, DP, DQ"]),
            Group(title="2. 다양성", color="blue", items=["polygeny + polymorphism", "B>A>C, DRB>DQB>DPB", "gene conversion, anchor"]),
            Group(title="3. MHC restriction", color="salmon", items=["peptide + 자기 MHC", "예외: alloresponse, superantigen"]),
            Group(title="4. 비전형적 인식", color="amber", items=["class Ib (HLA-E, F, G)", "CD1: lipid 항원", "gamma-delta T, MAIT, iNKT"]),
        ]), [1, 4, 40]),
        FIG("f_poly_bars.png", "인간 MHC 분자별 다형성: 유전자 자리마다 allele 수가 다릅니다 (슬라이드)", [15]),
        POLY,
    ], role="front"))
    top.append(T("요약 ② class Ib와 MHC restriction [기출]", "", [], [
        P("기출은 NK세포와 class Ib 분자, MHC restriction의 예외, CD1c를 묻습니다.", [34, 35, 24, 37]),
        EXCEPT,
        P("{b|2009학번 Q1은 시험지 스캔 이미지라 문항 내용을 읽을 수 없고, 정답은 3번이며 ‘짤’(재탕 문제)로 표시되어 있습니다.}", [Q09_scan]),
        FIG("f_classIb.png", "class Ib 분자와 수용체, 생물학적 기능 (슬라이드)", [35]),
        ROWS([
            ["{b|HLA-C}", "{b|NK세포 수용체(KIR)와 상호작용 → NK세포 억제}", "{b|class I이면서 class Ib로도 분류}"],
            ["{b|HLA-E}", "{b|NK세포 억제 신호}", "{b|T세포에 항원 제시 안 함}"],
            ["HLA-G", "모체와 태아 사이의 면역 조절", ""],
            ["{b|CD1c}", "{b|lipid 항원 제시 → invariant NKT cell 활성화}", ""],
        ], col_titles=["분자", "기능", "단서"], col_widths=[2.8, 9.0, 5.6], g=[35, 37, 38] + [Q19_KIR, Q15_KIR, Q15_HLAE, Q16_cls1b, Q10_noAg, Q21_CD1c]),
    ], role="front"))

    # ================================================================ 1장 MHC 유전자 영역 (¶5-12)
    top.append(EX("MHC 유전자는 어디에 있고 어떻게 나뉘나?", CH1, "6번 염색체의 HLA 영역이고, class I, II, III로 나눕니다.", [
        P("사람의 MHC 유전자는 6번 염색체에 있고, 흔히 HLA(human leukocyte antigen)라고 부릅니다. 이 영역에 여러 유전자가 밀집해 있어 class I, class II, class III 영역으로 구분해서 봅니다.", [5]),
        FIG("f_gene.png", "인간 HLA와 생쥐 H-2의 유전자 구조 (슬라이드)", [5, 8]),
        P("위의 그림이 인간(HLA, 6번 염색체), 아래 그림이 생쥐(H-2, 17번 염색체)의 MHC 영역입니다.", [5, 8]),
    ]))
    top.append(LS("class I과 class II에는 어떤 분자가 있나?", CH1, [
        ROWS([
            ["class I", "{b|HLA-A, HLA-B, HLA-C}\nalpha chain 1개 + beta-2 microglobulin → ‘다리 하나짜리’"],
            ["class II", "{b|HLA-DR, HLA-DP, HLA-DQ}\nalpha chain과 beta chain이 짝 → ‘다리 두 개짜리’"],
            ["class II region의 다른 분자", "HLA-DM, HLA-DO: peptide editing과 항원제시 조절에 관여 (고전적 class II와 구분)\nTAP 등 항원 처리 분자도 MHC 영역 안에 있음"],
            ["생쥐 H-2", "class I: H-2D, H-2L / class II: H-2A, H-2E 등 (17번 염색체)"],
        ], col_titles=["구분", "분자와 구조 단서"], col_widths=[4.6, 12.8], g=[6, 7, 8] + [Q21_cls2, Q18_CD8]),
        P("{r|‘MHC class II 분자’를 묻는지 ‘class II region에 있는 유전자’를 묻는지 구분해서 읽어야 하고, 이름을 외우기보다 유전자 영역과 실제 분자의 기능을 구분하는 것이 중요하다고 강조하셨습니다.}", [6, 8]),
        CHK("HLA-DR은 MHC class II에 해당한다.", "O", [6], why="class II는 HLA-DR, DP, DQ이다."),
        CHK("HLA-E는 CD8 T세포에 바이러스 항원을 제시하는 고전적 class I 분자이다.", "X", [6, 10], why="고전적 class I은 HLA-A, B, C이고 HLA-E, F, G는 class Ib이다."),
    ]))
    top.append(LS("유전자 영역 안에는 또 무엇이 있나?", CH1, [
        FIG("f_map.png", "확대한 MHC 유전자 지도: class II, III, I 영역 (슬라이드)", [9, 10]),
        P("그림은 위아래로 나뉘어 있지만 길게 연결된 하나의 영역입니다. class I, class II 유전자만 모여 있는 것이 아니라, 사이사이에 항원을 가공하고 제시하는 유전자가 있습니다.", [9]),
        ROWS([
            ["class I 영역", "고전적 HLA-A, B, C 외에 HLA-E, HLA-F, HLA-G (class Ib 또는 비고전적 class I, 뒤에서 다시 나옴)"],
            ["class III 영역", "{b|MIC-A, MIC-B}"],
            ["사이사이", "TAP, proteasome 관련 성분, TNF 등 항원 가공과 면역 관련 유전자"],
        ], col_titles=["영역", "분자"], col_widths=[4.0, 13.4], g=[9, 10] + [Q18_MICA, Q16_NKG2D]),
        P("하나의 영역에 면역 관련 유전자가 함께 모여 있다는 점이 뒤에서 면역 반응이 함께 조절된다는 설명으로 이어집니다.", [10]),
    ]))
    top.append(EX("면역 반응에서 MHC 유전자 발현은 어떻게 조절되나?", CH1, "interferon이 발현을 조절하고, class II는 CIITA가 중요합니다.", [
        P("감염이 생기면 여러 면역 관련 유전자의 발현이 변합니다. 강의 자료는 interferon alpha, beta, gamma가 MHC 관련 유전자 발현을 조절한다고 제시하고, 그 결과 감염된 세포가 바이러스 단백질 유래 peptide를 제시할 기회가 늘어납니다.", [11]),
        P("class II의 전사 조절에는 CIITA라는 co-activator가 중요하고, interferon-gamma는 class II 관련 유전자 발현과 연결해 기억합니다.", [12]),
        P("{g|모든 조절 경로를 외울 필요는 없고, 항원제시 분자만 따로 만들어지는 것이 아니라 가공과 제시에 필요한 구성요소가 함께 조절된다는 큰 흐름을 잡으면 됩니다.}", [12]),
    ]))

    # ================================================================ 2장 다양성 (¶2, 3, 13-20, 32-33)
    top.append(EX("MHC는 왜 여러 종류가 있어야 하나?", CH2, "한 종류면 회피 돌연변이가 모든 사람에게 통하기 때문입니다.", [
        P("감염원의 입장에서 보면, 자기 단백질 조각이 MHC에 얹혀 T세포에 보이면 면역계가 자신을 알아보게 되므로 그 경로를 피하고 싶어 합니다.", [2]),
        P("그런데 사람에게 MHC가 한 종류뿐이라면, 그 결합을 피하는 돌연변이가 생겼을 때 모든 사람에게 통할 가능성이 커집니다. 실제로는 한 사람 안에서도 여러 MHC 유전자가 발현되고, 사람 사이에는 allele의 종류가 아주 다양합니다. 이 두 가지가 오늘의 중요한 출발점입니다.", [2]),
    ]))
    top.append(LS("polygeny와 polymorphism은 무엇이 다른가?", CH2, [
        FIG("f_poly_types.png", "polymorphism, polygeny, 그리고 둘이 함께 있는 경우 (슬라이드)", [13]),
        ROWS([
            ["polygeny\n(polygenic)", "한 개체가 서로 다른 MHC 유전자를 여러 개 가짐\n예: HLA-A와 HLA-B는 서로 다른 유전자"],
            ["polymorphism\n(polymorphic)", "같은 유전자 자리라도 집단 안에 여러 형태의 allele이 존재함\n예: HLA-A에도, HLA-B에도 다양한 allele"],
            ["codominant 발현", "어머니와 아버지에게서 받은 allele이 둘 다 발현됨 → 한 사람이 만드는 MHC 분자의 종류가 늘어남"],
            ["haplotype", "한쪽 염색체 위에 모여서 물려받는 MHC allele의 조합"],
        ], col_titles=["용어", "뜻"], col_widths=[4.0, 13.4], g=[3, 13, 14]),
        P("{r|‘한 개체의 유전자 수가 많다’와 ‘집단 전체의 allele 종류가 많다’를 바꿔 쓰지 말고 반드시 구분해서 이해하라고 강조하셨습니다.}", [14]),
    ]))
    top.append(LS("어느 MHC 분자가 가장 다양한가?", CH2, [
        POLY,
        P("다형성은 모든 MHC 분자에서 똑같이 큰 것이 아니라 고전적 class I 쪽이 크고 class Ib에서는 상대적으로 제한적입니다. 최신 allele 개수까지 외우기보다 상대적인 경향과 기능을 먼저 이해합니다.", [15]),
        P("class II에서는 다형성이 beta chain 쪽에 집중되어 있습니다. 다형성이 peptide가 들어가는 결합 부위와 관련되어 있어서, 같은 감염원의 peptide라도 사람의 MHC 종류에 따라 결합 가능성이 달라집니다.", [16]),
        CHK("Class I 중 다형성이 가장 높은 유전자좌는 HLA-A이다.", "X", [15], why="HLA-B이다 (B > A > C)."),
        CHK("Class II 중 가장 polymorphic한 것은 HLA-DR(DRB)이다.", "O", [15, 16], why="DRB > DQB > DPB이다."),
    ], new_page=False))
    top.append(EX("다양성은 어디서 생기고 무엇을 바꾸나?", CH2, "gene conversion으로 생기고, peptide 결합 부위를 바꿉니다.", [
        P("다양성의 중요한 기전은 gene conversion입니다. 서로 비슷한 서열의 유전자 사이에서 유전정보 일부가 바뀌면 원래와 조금 다른 형태가 만들어지고, 정리본은 감수분열 과정에서 유사 서열 사이의 변화가 MHC 다양성에 기여했다고 설명합니다.", [17]),
        FIG("f_gene_var.png", "gene conversion(왼쪽)과 class I, class II의 변이 위치(오른쪽) (슬라이드)", [17, 18]),
        P("class I에서는 alpha-1, alpha-2 영역이, class II에서는 beta-1 영역이 peptide 결합과 관련된 다양성을 보입니다.", [18]),
        P("결합 홈의 구조가 달라지면 결합하는 peptide의 종류도 달라집니다. 그래서 MHC polymorphism은 이름의 다양성이 아니라 어떤 항원을 T세포에 보여 줄 수 있는가와 직결되는 기능적인 다양성입니다.", [18]),
        P("{r|이 연결, 즉 다양성이 곧 기능적 다양성이라는 점이 오늘의 핵심이라고 강조하셨습니다.}", [18]),
    ]))
    top.append(LS("peptide는 어떻게 MHC에 결합하나?", CH2, [
        FIG("f_anchor.png", "MHC에 결합하는 peptide의 서열 비교 (슬라이드)", [19, 20]),
        P("여러 peptide가 하나의 MHC에 결합한다고 해서 전체 아미노산 서열이 같아야 하는 것은 아닙니다. 특정 위치에 비슷한 성질의 아미노산이 반복해서 나오고, 정리본은 2번, 5번, 8번 위치를 예로 듭니다.", [19]),
        ROWS([
            ["anchor residue", "2번, 5번, 8번 같은 위치에서 MHC와 중요한 접촉을 만드는 잔기"],
            ["결합의 원리", "MHC allele마다 선호하는 peptide motif가 있음\n같은 motif를 가진 서로 다른 peptide가 결합\nMHC 종류가 바뀌면 잘 결합하는 peptide 집합도 달라짐"],
            ["응용", "종양 항원 예측, 백신 후보 peptide 선택 전략"],
        ], col_titles=["구분", "내용"], col_widths=[4.0, 13.4], g=[19, 20]),
        P("표를 볼 때는 전체 서열보다 공통된 위치와 성질을 먼저 찾아봅니다. 외워야 할 것은 번호가 아니라 결합의 원리입니다.", [20]),
    ]))
    top.append(EX("MHC 종류는 왜 무한정 늘어나지 않나?", CH2, "감염 방어 범위와 흉선에서의 T세포 선택 부담이 균형을 이룹니다.", [
        P("사람 집단에서 MHC가 다양하면 모든 사람이 같은 감염원 회피 전략에 취약해질 가능성이 줄어듭니다. 자료는 EBV의 면역 회피, 특정 인구집단의 HLA 분포, 서아프리카에서 HLA-B53과 중증 말라리아의 관련성을 사례로 듭니다.", [32]),
        P("사례의 수치보다 중요한 메시지는 병원체와 숙주의 유전적 다양성이 서로 영향을 주고받는다는 것입니다.", [32]),
        P("그렇다면 MHC 종류가 많을수록 좋을 텐데 왜 무한정 늘어나지 않을까요? 다양한 MHC는 더 많은 peptide를 제시할 수 있지만 흉선(thymus)에서 T세포가 선택되는 조건도 더 복잡해지기 때문입니다. 자가 반응성과 적절한 면역 반응 사이의 균형이 필요합니다.", [33]),
    ]))

    # ================================================================ 3장 MHC restriction (¶21-31)
    top.append(EX("T세포는 peptide와 MHC를 어떻게 함께 인식하나?", CH3, "peptide와 자기 MHC가 함께 맞아야 인식합니다.", [
        P("T세포는 외래 peptide만 인식하지 않습니다. TCR이 맞는 peptide를 인식해야 하고, 그 peptide를 제시하는 MHC도 자신이 인식하도록 교육받은 종류여야 반응합니다. 이 두 조건을 같이 생각해야 합니다.", [21]),
        FIG("f_restriction.png", "MHC restriction: 세 가지 조합 (슬라이드)", [22]),
        P("왼쪽은 자기 MHC에 맞는 peptide가 올라가 인식되고, 가운데는 peptide가 같아도 MHC가 달라 인식되지 않으며, 오른쪽은 자기 MHC여도 TCR이 인식하지 못하는 peptide라 반응하지 않습니다.", [22]),
        P("따라서 T세포 인식의 대상은 분리된 peptide 하나가 아니라 peptide-MHC 복합체입니다.", [22]),
    ]))
    top.append(LS("MHC restriction은 어떻게 밝혀졌나?", CH3, [
        P("지금은 기본 지식처럼 들리지만 처음 밝혀졌을 때는 중요한 발견이었고, Doherty와 Zinkernagel의 연구가 대표적입니다. 특정 항원에 반응하는 T세포는 어떤 세포에서나 반응하는 것이 아니라 적절한 자기 MHC 환경에서 항원이 제시되어야 반응합니다.", [23]),
        P("실험의 세부사항을 따라가기보다, 항원은 같고 MHC가 다른 경우, MHC는 같고 항원이 다른 경우, 두 조건이 모두 맞는 경우로 나눠 무엇이 T세포 반응을 결정하는지 비교하는 사고방식을 익힙니다. 앞의 그림이 그 세 조합입니다.", [23, 24]),
    ]))
    top.append(EX("MHC restriction의 예외에는 무엇이 있나?", CH3, "alloresponse, 이식(transplantation), superantigen입니다.", [
        P("자기 MHC에 제한되어 반응한다면 왜 장기 이식 때는 타인의 MHC에 엄청난 반응이 나타날까요? 이 예외처럼 보이는 현상이 이식 반응과 superantigen입니다.", [24]),
        EXCEPT,
        CHK("MHC restriction이 적용되는 것은 alloresponse이다.", "X", [24, 25], why="alloresponse, transplantation, superantigen은 MHC restriction의 예외이다."),
    ], refs=PAD_RESTR, mark="기출"))
    top.append(EX("이식에서는 왜 타인의 MHC에 강하게 반응하나?", CH3, "TCR의 교차 반응성 때문에 alloreactive T세포가 약 1~10%나 됩니다.", [
        P("alloresponse는 다른 개체의 MHC에 대해 일어나는 강한 T세포 반응입니다. 같은 종 사이의 이식은 allogeneic, 서로 다른 종 사이의 이식은 xenogeneic(xenograft)이라고 합니다.", [25]),
        P("T세포 수용체는 어느 정도 교차 반응성(cross-reactivity)이 있어서, 자기 MHC와 구조가 비슷한 다른 MHC에 예기치 않게 강하게 결합할 수 있습니다. 정리본은 alloreactive T cell이 전체 T세포의 약 1~10%라고 소개합니다.", [26, 28]),
        FIG("f_alloresponse.png", "TCR의 CDR 부위와 MHC-peptide 복합체의 상호작용, alloresponse (슬라이드)", [28]),
        P("흉선(thymus)의 positive selection과 negative selection은 자기 MHC에 적절히 반응하는 세포를 남기지만, 타인의 MHC에 대한 반응까지 모두 없애 주지는 않습니다. 이식 거부반응을 이해할 때 이 점이 중요합니다.", [28]),
        P("이 반응을 보는 고전적인 실험이 mixed lymphocyte reaction(MLR)입니다. MHC가 다른 두 개체의 림프구를 섞어 반응을 보는데, 양쪽이 모두 증식하면 구별하기 어렵기 때문에 한쪽은 irradiation이나 mitomycin C로 증식하지 못하게 해서 처리하지 않은 쪽의 반응을 봅니다.", [27]),
        CHK("유전적으로 동일하지 않은 같은 종의 개체 사이의 이식은 allogeneic transplantation이다.", "O", [25], why="다른 종 사이의 이식은 xenogeneic이다."),
    ], refs=[Q16_allo], mark="기출"))
    top.append(EX("superantigen은 일반 항원과 무엇이 다른가?", CH3, "peptide 처리 없이 MHC class II와 TCR을 연결해 많은 T세포를 활성화합니다.", [
        P("정상적인 항원 제시는 peptide가 만들어져 MHC의 결합 홈에 자리하고, 특정 TCR이 그 복합체를 인식하는 과정입니다. superantigen은 일반적인 peptide 처리와 결합 방식과 다르게 MHC class II와 TCR을 연결해 많은 T세포를 동시에 활성화합니다.", [29]),
        FIG("f_superantigen.png", "bacterial superantigen과 viral superantigen (슬라이드)", [29]),
        P("많은 T세포가 한꺼번에 자극되면 염증성 신호가 크게 발생해 숙주에 심한 부담이 됩니다. 핵심은 ‘비특이적인 대규모 활성화’이고, 그림에서도 결합 위치가 일반적인 peptide-MHC-TCR 인식과 다른 점을 먼저 봅니다.", [30]),
        ROWS([
            ["staphylococcal enterotoxin (SE)", "식중독과 관련된 독소"],
            ["TSST-1", "toxic shock syndrome과 관련된 독소"],
        ], col_titles=["대표 superantigen", "관련"], col_widths=[7.0, 10.4], g=[31]),
    ]))

    # ================================================================ 4장 class Ib와 비전형적 T세포 (¶34-40)
    top.append(EX("비전형적 MHC(class Ib)에는 무엇이 있나?", CH4, "HLA-E, F, G가 중심이고 NK세포와 모체-태아 면역에 관여합니다.", [
        P("지금까지는 고전적 MHC와 peptide 항원을 다뤘고, 이 틀로 설명하기 어려운 인식 방식과 연결된 분자를 class Ib, nonclassical MHC 또는 MHC-like molecule이라고 부릅니다. 분류 용어는 자료마다 조금 다르므로 기능을 함께 봅니다.", [34]),
        ROWS([
            ["{b|HLA-E}", "{b|NK세포에 억제 신호}를 주는 경로와 연결\nT세포에 항원을 제시하는 분자는 아님"],
            ["HLA-F", "class Ib 중심 분자 중 하나"],
            ["HLA-G", "모체와 태아 사이의 면역 조절"],
            ["{b|HLA-C}", "{b|NK세포 수용체(KIR)와 상호작용 → NK세포 억제}\n{b|class I이면서 class Ib로도 분류할 수 있음}"],
        ], col_titles=["분자", "기능"], col_widths=[3.0, 14.4], g=[35] + PAD_NK),
        P("class Ib는 고전적 class I과 형태가 비슷하지만 다형성이 제한적인 경우가 많고 기능이 다양합니다. 자료는 HLA-E, F, G를 중심으로 보라고 강조합니다.", [35]),
        CHK("HLA-C는 NK세포의 KIR과 결합해 NK세포를 억제한다.", "O", [35], why="HLA-C는 class I이면서 NK세포 수용체와 상호작용한다."),
    ], refs=PAD_NK, mark="기출"))
    top.append(EX("Unconventional T cell은 무엇을 인식하나?", CH4, "peptide-MHC 밖의 항원을 인식하는 gamma-delta T, MAIT, iNKT입니다.", [
        P("unconventional T cell로 정리본은 gamma-delta T cell, 점막과 관련된 MAIT cell, invariant NKT cell을 듭니다. 인식하는 표적과 생리적 역할은 서로 같지 않습니다.", [36]),
        P("먼저 고전적인 alpha-beta T세포의 peptide-MHC 인식과 다른 항원 인식 경로가 있다는 것을 잡습니다.", [36]),
        FIG("f_gdT.png", "gamma-delta T cell을 활성화하는 ligand (슬라이드)", [39]),
        P("표에는 gamma-delta T cell이 인식하는 ligand가 여러 가지로 제시되어 있습니다. 항목을 모두 암기하기보다 고전적인 peptide-MHC 인식과 다른 방식으로 다양한 신호를 감지한다는 점이 중요합니다.", [39]),
        P("MAIT cell은 점막 면역과 관계가 있고 미생물 유래 물질을 인식하며, 선천면역과 적응면역 사이를 연결하는 성격으로 설명됩니다.", [40]),
    ]))
    top.append(LS("CD1과 FcRn은 무엇을 제시하나?", CH4, [
        ROWS([
            ["CD1", "{b|lipid 또는 glycolipid 항원 제시} → 병원체 유래 지질 항원 인식\nCD1a부터 CD1e까지 여러 유형\n{b|CD1c → invariant NKT cell 활성화}"],
            ["FcRn", "MHC 유사 분자, 항원제시보다 모체의 IgG 전달과 관련"],
        ], col_titles=["분자", "기능"], col_widths=[3.0, 14.4], g=[37, 38, Q21_CD1c]),
        P("{r|CD1은 국가시험에 자주 나온다고 강조하셨다고 정리본에 적혀 있으니 ‘CD1—지질 항원제시’를 확실히 기억합니다.}", [37]),
        P("{p|정리본은 CD1c와 invariant NKT cell을 연결하지만, 일반적으로 invariant NKT cell의 대표 인식 분자는 CD1d입니다. 이 연결은 복습할 때 검증이 필요합니다.}", [38]),
        FIG("f_cd1.png", "CD1c(왼쪽)와 CD1d(오른쪽)에 지질이 결합한 모습 (슬라이드)", [37, 38]),
        CHK("CD1c는 invariant NKT cell을 활성화한다.", "O", [37, 38], why="CD1은 lipid 항원을 제시한다."),
        MEMO("스크립트 끝의 [검증참고] 다섯 문단(¶41–45)은 강의 내용이 아니라 자료 재구성에 대한 설명이어서 노트에 넣지 않았습니다.", [41, 42, 43, 44, 45]),
    ]))
    return top


if __name__ == "__main__":
    import sys

    topics = build()
    for t in topics:
        t.slide_numbers = sorted({r for sts in t.sections.values() for st in sts for r in st.slide_refs})
    dump(topics, sys.stdout)
