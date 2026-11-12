"""Mixed-style note (v3: L27-L44, tables only for comparisons, humanized) for 'T림프구 항원제시: MHC 유전자의 구성과 기능, 비전형적 T세포 인식' - written by the make-lecture-note workflow
(docs/WORKFLOW.md): script -> storyline.md -> this file -> build.

Inputs (nothing else is used):
  * script   inputs/tcell_script.docx   (40 speech paragraphs + 5 [검증참고] notes)
  * pictures inputs/tcell_figs/         (slide images from the 정리본 PDF - pictures only, no text from it)
  * PAD      inputs/tcell_pad.pdf       (18 questions) - used ONLY to decide what is blue.
Run:  python -m examples.tcell_wf_note > outputs/wf_tcell/note_authored.json
"""
from app.models import Diagram, Group, Statement
from examples.abx_note import B, DFULL, EX, LS, P, ROWS
from examples.authoring import T as _T  # noqa: F401
from examples.authoring import T, dump
from examples.stemcell_note import CHK, MEMO, _st

FIG_DIR = "inputs/tcell_figs/"
CH1 = "MHC(HLA) 유전자 영역의 구성"
CH2 = "MHC의 다양성: polymorphism과 polygeny"
CH3 = "MHC restriction, 예외 반응과 다양성의 의미"
CH4 = "Class Ib 분자와 비전형적 T세포"

# PAD units (parse order of inputs/tcell_pad.pdf)
(Q22_1, Q21_CD1c, Q21_cls2, Q20_alle, Q19_cls2poly, Q19_KIR, Q18_MICA, Q18_CD8, Q18_cls2div,
 Q16_allo, Q16_cls1b, Q16_NKG2D, Q16_restr, Q15_KIR, Q15_HLAE, Q11_restr, Q10_noAg, Q09_scan) = range(1001, 1019)
PAD_POLY = [Q22_1, Q20_alle, Q19_cls2poly, Q18_cls2div]
PAD_CLASS = [Q21_cls2, Q18_CD8, Q16_cls1b, Q10_noAg]
PAD_NK = [Q19_KIR, Q15_KIR, Q15_HLAE, Q18_MICA, Q16_NKG2D, Q16_cls1b, Q10_noAg]
PAD_RESTR = [Q16_restr, Q11_restr]


def HOOK(text, g=()):
    """L50: a confusable, testable pair with a clear dividing point -> ONE plain sentence in a [한 줄 구분] box."""
    return Statement(text="", kind="callout", left_title="한 줄 구분", left=[text], slide_refs=list(g))


def FIG(img, caption, g=()):
    return Statement(text=caption, kind="figure", image=FIG_DIR + img, slide_refs=list(g))


# ---- tables only for real comparisons (L41); contrasts inside are marked (L42). Same object on the front page and in the body.
POLY = ROWS([
    ["class I", "HLA-A, HLA-B, HLA-C", "{b|HLA-B > HLA-A > HLA-C}"],
    ["class II", "HLA-DR, HLA-DP, HLA-DQ", "{b|DRB > DQB > DPB}\n{b|beta chain 쪽에 다형성 집중}"],
    ["class Ib", "HLA-E, HLA-F, HLA-G 등", "상대적으로 **제한적**"],
], col_titles=["구분", "분자", "다형성(다양성) 순서"], col_widths=[2.6, 5.6, 9.2], g=[6, 15, 16] + PAD_POLY)

EXCEPT = ROWS([
    ["{b|MHC restriction 적용}", "{b|peptide와 자기 MHC를 함께 인식하는 일반적인 T세포 반응}"],
    ["{b|**예외**}", "{b|**alloresponse, transplantation(이식), superantigen**}"],
], col_titles=["구분", "해당"], col_widths=[4.6, 12.8], g=[24, 25, 29] + PAD_RESTR + [Q16_allo])

CLASS_CMP = ROWS([
    ["분자", "{b|HLA-A, HLA-B, HLA-C}", "{b|HLA-DR, HLA-DP, HLA-DQ}"],
    ["구조", "alpha chain 1개 + beta-2 microglobulin\n→ {k|‘다리 하나짜리’}(교수님 표현)", "alpha chain과 beta chain이 짝\n→ {k|‘다리 두 개짜리’}(교수님 표현)"],
    ["T세포", "{b|CD8 T세포에 항원 제시}", "CD4 T세포에 항원 제시"],
], col_titles=["구분", "MHC class I", "MHC class II"], col_widths=[2.4, 7.4, 7.6], g=[6, 7, 8] + [Q21_cls2, Q18_CD8])

CLASS_IB = ROWS([
    ["{b|HLA-C}", "{b|NK세포 수용체(KIR)와 상호작용 → NK세포 억제}", "{b|class I이면서 class Ib로도 분류}"],
    ["{b|HLA-E}", "{b|NK세포 억제 신호}", "{b|**T세포에 항원 제시 안 함**}"],
    ["HLA-F", "class Ib의 중심 분자 중 하나", ""],
    ["HLA-G", "{k|모체와 태아} 사이의 면역 조절", ""],
], col_titles=["분자", "기능", "단서"], col_widths=[2.8, 9.0, 5.6], g=[35] + [Q19_KIR, Q15_KIR, Q15_HLAE, Q16_cls1b, Q10_noAg])


def build():
    top = []
    # ================================================================ 앞쪽 요약: 지도 + 기출 비교표
    top.append(T("요약 강의 지도와 기출 포인트", "", [], [
        P("앞 시간에는 항원이 세포 안에서 처리되어 MHC에 올라가는 과정을 봤습니다. 이번 강의는 MHC 유전자의 구성과 기능을 먼저 보고, 끝에서 조금 특이한 T세포 인식을 다룹니다. 초점은 두 가지입니다. MHC는 왜 여러 종류인지, T세포는 실제로 무엇을 인식하는지입니다.", [1, 4]),
        P("감염원의 입장에서 생각해 봅니다. 자기 단백질 조각이 MHC에 얹혀 T세포에 보이면 면역계가 자신을 알아보게 되니, 감염원은 그 경로를 피하고 싶어 합니다. 사람에게 MHC가 한 종류뿐이라면 그 결합을 피하는 돌연변이 하나가 모든 사람에게 통할 것입니다.", [2]),
        P("실제로는 한 사람 안에서도 여러 MHC 유전자가 발현되고(polygenic), 사람 사이에는 같은 유전자 자리의 allele 종류가 아주 다양합니다(polymorphic). 한쪽 염색체 위에 모여서 물려받는 allele의 조합은 haplotype이라고 합니다. 즉, 다양한 MHC → 감염원이 모두를 피하기 어려움이 오늘의 출발점입니다.", [2, 3]),
        DFULL("강의 전체 지도: 네 부분", Diagram(kind="tree", root="T세포 항원제시", groups=[
            Group(title="Ⅰ. MHC 유전자 영역", color="teal", items=["6번 염색체", "class I, II, III", "HLA-A, B, C / DR, DP, DQ"]),
            Group(title="Ⅱ. 다양성", color="blue", items=["polygeny + polymorphism", "B>A>C, DRB>DQB>DPB", "gene conversion, anchor"]),
            Group(title="Ⅲ. MHC restriction", color="salmon", items=["peptide + 자기 MHC", "예외: alloresponse, superantigen"]),
            Group(title="Ⅳ. 비전형적 인식", color="amber", items=["class Ib (HLA-E, F, G)", "CD1: lipid 항원", "gamma-delta T, MAIT, iNKT"]),
        ]), [1, 4, 40]),
        _st("sub", "(1) 다형성 순서 = class I은 B > A > C, class II는 DRB > DQB > DPB★ (파드)", [15, 16]),
        POLY,
        _st("sub", "(2) MHC restriction의 예외 = alloresponse, transplantation, superantigen★ (파드)", [24, 25, 29]),
        EXCEPT,
        P("{b|2009학번 Q1은 시험지 스캔 이미지라 문항 내용을 읽을 수 없고, 정답은 3번이며 ‘짤’(재탕 문제)로 표시되어 있습니다.}", [Q09_scan]),
    ], role="front"))

    # ================================================================ Ⅰ. MHC(HLA) 유전자 영역의 구성 (¶5-12)
    top.append(EX("MHC 유전자 영역의 구성: class I, II, III", CH1, "6번 염색체의 HLA 영역이고, class I, II, III로 나눕니다.", [
        P("인간의 MHC 유전자는 6번 염색체에 있습니다. 사람에서는 흔히 HLA(human leukocyte antigen)라고 부릅니다. 이 영역에 여러 유전자가 밀집해 있어서 class I, II, III 영역으로 나누어 봅니다.", [5]),
        FIG("f_gene.png", "인간 HLA와 생쥐 H-2의 유전자 구조 (슬라이드)", [5, 8]),
        P("위 그림이 인간(HLA, 6번 염색체), 아래 그림이 생쥐(H-2, 17번 염색체)의 MHC 영역입니다. 생쥐의 class I에는 H-2D, H-2L이, class II에는 H-2A, H-2E 등이 있습니다. 나중에 실험 그림을 읽을 때 이 차이가 필요합니다.", [5, 8]),
        _st("sub", "(1) 분자 = class I은 HLA-A, B, C / class II는 HLA-DR, DP, DQ★", [6]),
        P("고전적 MHC class I과 class II를 견주면 아래와 같습니다. 이름을 외우기에 앞서 유전자 영역과 실제 분자의 기능을 구분해야 합니다.", [6]),
        CLASS_CMP,
        HOOK("{b|이름이 한 글자(A, B, C)면 class I, 두 글자(DR, DP, DQ)면 class II}입니다(파드).", [6, Q21_cls2]),
        P("class II 영역에는 DR, DQ, DP만 있는 것이 아닙니다. 앞 시간에 본 HLA-DM과 HLA-DO도 이 영역과 관련이 있습니다. 고전적인 항원제시 class II와는 구분되지만 peptide editing과 항원제시 조절에 관여합니다. TAP처럼 항원 처리에 참여하는 분자도 MHC 영역 안에 있습니다.", [7]),
        P("{r|문제가 ‘MHC class II 분자’를 묻는지 ‘class II region에 존재하는 유전자’를 묻는지 구분해서 읽어야 한다고 강조하셨습니다.}", [8]),
        CHK("HLA-DR은 MHC class II에 해당한다.", "O", [6], why="class II는 HLA-DR, DP, DQ이다."),
        CHK("HLA-E는 CD8 T세포에 바이러스 항원을 제시하는 고전적 class I 분자이다.", "X", [6, 10], why="고전적 class I은 HLA-A, B, C이고 HLA-E, F, G는 class Ib이다."),
        _st("sub", "(2) 확대한 유전자 지도 = 사이사이에 항원 가공 유전자", [9, 10]),
        FIG("f_map.png", "확대한 MHC 유전자 지도: class II, III, I 영역 (슬라이드)", [9, 10]),
        P("위 그림(슬라이드)은 유전자 지도를 확대한 것입니다. 위아래로 나뉘어 있지만 길게 이어진 하나의 영역입니다. class I, class II 유전자만 모여 있는 것이 아니라 그 사이사이에 항원을 가공하고 제시하는 유전자가 있습니다. TAP, proteasome 관련 성분, TNF가 그 예입니다.", [9]),
        P("class I 영역에는 고전적인 A, B, C 외에 HLA-E, HLA-F, HLA-G가 있습니다. 이들은 class Ib 또는 비고전적 class I이라고 하며 뒤에서 다시 나옵니다.", [10]),
        P("class III 영역에는 {b|MIC-A, MIC-B}가 있습니다. 면역 관련 유전자가 이렇게 한 영역에 모여 있어서, 뒤에서 나올 면역 반응의 공동 조절이 자연스럽게 이해됩니다.", [10] + [Q18_MICA, Q16_NKG2D]),
    ], refs=PAD_CLASS, mark="기출"))
    top.append(EX("MHC 유전자 발현의 조절", CH1, "interferon이 발현을 조절하고, class II는 CIITA가 중요합니다.", [
        P("감염이 생기면 여러 면역 관련 유전자의 발현이 달라집니다. interferon alpha, beta, gamma가 MHC 관련 유전자의 발현을 조절합니다(자료). 그 결과 감염된 세포가 바이러스 단백질에서 나온 peptide를 제시할 기회가 늘어납니다.", [11]),
        P("class II의 전사는 **CIITA**라는 co-activator가 조절합니다. interferon-gamma는 class II 관련 유전자 발현과 연결됩니다.", [12]),
        P("{g|모든 조절 경로를 외울 필요는 없습니다. 항원제시 분자만 따로 만들어지는 것이 아니라 가공과 제시에 필요한 구성요소가 함께 조절된다는 큰 흐름이면 됩니다.}", [12]),
    ]))

    # ================================================================ Ⅱ. MHC의 다양성 (¶2, 3, 13-20, 32-33)
    top.append(LS("polygeny와 polymorphism의 구분, 다형성의 순서", CH2, [
        P("여기서 제일 중요한 두 단어가 polymorphism과 polygeny입니다. 앞에서 본 두 용어를 정확히 구분합니다.", [13]),
        FIG("f_poly_types.png", "polymorphism, polygeny, 그리고 둘이 함께 있는 경우 (슬라이드)", [13]),
        ROWS([
            ["뜻", "한 개체가 서로 다른 MHC 유전자를 **여러 개** 가짐", "같은 유전자 자리라도 집단 안에 **여러 형태의 allele**이 있음"],
            ["예", "HLA-A와 HLA-B는 서로 다른 유전자", "HLA-A에도, HLA-B에도 다양한 allele"],
            ["수준", "{k|한 개체 안}", "{k|집단 전체}"],
        ], col_titles=["구분", "polygeny (polygenic)", "polymorphism (polymorphic)"], col_widths=[2.4, 7.4, 7.6], g=[13, 14]),
        HOOK("polygeny는 한 사람이 가진 유전자의 ‘개수’, polymorphism은 집단의 ‘버전 수’입니다.", [13, 14]),
        P("이 두 층위의 다양성이 함께 작동합니다. 발현은 **codominant**여서 어머니와 아버지에게서 받은 allele이 둘 다 발현됩니다. 그러면 한 개체가 만드는 MHC 분자의 종류가 늘어나고, 한 사람의 조합이 다른 사람과 같기 어려워집니다.", [13, 14]),
        P("{r|‘한 개체의 유전자 수가 많다’와 ‘집단 전체의 allele 종류가 많다’를 바꿔 쓰지 말고 반드시 구분해서 이해하라고 강조하셨습니다.}", [14]),
        _st("sub", "(1) 다형성의 순서 = class I은 B > A > C, class II는 DRB > DQB > DPB★", [15, 16]),
        FIG("f_poly_bars.png", "인간 MHC 분자별 다형성: 유전자 자리마다 allele 수가 다릅니다 (슬라이드)", [15]),
        P("{b|그림에서 가장 다양한 것은 class I의 HLA-B, class II의 DRB입니다}(파드, 순서는 앞쪽 요약 표).", [15, 16] + PAD_POLY),
        P("다형성은 모든 MHC 분자에서 똑같이 큰 것이 아닙니다. 고전적 class I 쪽이 크고, class Ib는 상대적으로 제한적입니다. allele 개수는 시점과", [15]),
        P("class II에서는 다형성이 **beta chain** 쪽에 집중됩니다. 이 다형성은 peptide가 들어가는 결합 부위와 관련이 있습니다. 같은 감염원의 peptide라도 사람의 MHC 종류에 따라 결합 가능성이 달라집니다.", [16]),
        CHK("Class I 중 다형성이 가장 높은 유전자좌는 HLA-A이다.", "X", [15], why="HLA-B이다 (B > A > C)."),
        CHK("Class II 중 가장 polymorphic한 것은 HLA-DR(DRB)이다.", "O", [15, 16], why="DRB > DQB > DPB이다."),
    ], new_page=False))
    top.append(EX("다양성의 기전과 peptide 결합", CH2, "gene conversion으로 생기고, peptide 결합 부위를 바꿉니다.", [
        P("이 다양성은 어디서 왔을까요? 중요한 기전은 **gene conversion**입니다. 서로 비슷한 서열의 유전자 사이에서 유전정보 일부가 바뀌면 원래와 조금 다른 형태가 만들어집니다. 감수분열 과정에서 유사 서열 사이에 일어난 변화가 MHC 다양성에 기여했다고 봅니다(자료).", [17]),
        FIG("f_gene_var.png", "gene conversion(왼쪽)과 class I, class II의 변이 위치(오른쪽) (슬라이드)", [17, 18]),
        P("어디가 달라지는지는 그림 오른쪽에 있습니다. class I은 alpha-1, alpha-2 영역이, class II는 beta-1 영역이 peptide 결합과 관련된 다양성을 보입니다. 결합 홈의 구조가 달라지면 결합하는 peptide의 종류도 달라집니다.", [18]),
        P("그러니 MHC polymorphism은 이름의 다양성이 아닙니다. 어떤 항원을 T세포에 보여 줄 수 있는지와 직결된 {k|기능적 다양성}입니다.", [18]),
        P("즉, 결합 부위의 변이 → 결합 홈 구조 변화 → 제시하는 peptide 종류 변화 → T세포가 볼 수 있는 항원의 범위가 달라집니다.", [18]),
        P("{r|다양성이 곧 기능적 다양성이라는 연결이 오늘의 핵심이라고 강조하셨습니다.}", [18]),
        _st("sub", "(1) peptide 결합 = 전체 서열이 아니라 anchor residue와 motif", [19, 20]),
        FIG("f_anchor.png", "MHC에 결합하는 peptide의 서열 비교 (슬라이드)", [19, 20]),
        P("여러 peptide가 하나의 MHC에 결합한다고 해서 전체 아미노산 서열이 같아야 하는 것은 아닙니다. 특정 위치에 비슷한 성질의 아미노산이 반복해서 나옵니다. 2번, 5번, 8번 위치가 그 예이고(자료), 이 위치에서 MHC와 중요한 접촉을 만드는 잔기를 **anchor residue**라고 합니다.", [19]),
        P("외워야 할 것은 번호가 아니라 결합의 원리입니다. MHC allele마다 선호하는 peptide motif가 있고, 같은 motif를 가진 서로 다른 peptide가 결합합니다. MHC 종류가 바뀌면 잘 결합하는 peptide의 집합도 달라집니다.", [20]),
        P("이 원리는 종양 항원 예측이나 백신 후보 peptide 선택에도 응용됩니다.", [20]),
    ]))
    # ================================================================ Ⅲ. MHC restriction (¶21-31)
    top.append(EX("MHC restriction의 개념과 발견", CH3, "peptide와 자기 MHC가 함께 맞아야 인식합니다.", [
        P("T세포는 외래 peptide만 인식하지 않습니다. TCR이 맞는 peptide를 알아보아야 합니다. 그 peptide를 제시하는 MHC도 T세포가 인식하도록 교육받은 종류여야 반응합니다.", [21]),
        FIG("f_restriction.png", "MHC restriction: 세 가지 조합 (슬라이드)", [22]),
        P("위 그림(슬라이드)은 MHC restriction의 세 조합을 비교한 것입니다. 왼쪽은 자기 MHC에 맞는 peptide가 올라가 인식되는 경우입니다. 가운데는 peptide가 같아도 MHC가 달라 인식되지 않습니다. 오른쪽은 자기 MHC여도 TCR이 알아보지 못하는 peptide라 반응하지 않습니다.", [22]),
        P("그래서 T세포 인식의 대상은 분리된 peptide 하나가 아니라 {k|peptide-MHC 복합체}입니다.", [22]),
        P("지금은 기본 지식처럼 들리지만 처음 밝혀졌을 때는 중요한 발견이었습니다. 대표적인 것이 **Doherty와 Zinkernagel**의 연구입니다. 특정 항원에 반응하는 T세포는 어떤 세포에서나 반응하지 않고, 적절한 자기 MHC 환경에서 항원이 제시되어야 반응한다는 사실을 보여 주었습니다.", [23]),
        P("Doherty와 Zinkernagel의 실험도 위 그림과 같은 세 조합으로 나눠 비교한 것입니다. 항원은 같고 MHC가 다르면 반응이 없고, MHC는 같고 항원이 다르면 반응이 없으며, 둘 다 맞을 때만 반응합니다.", [22, 23, 24]),
        P("즉, T세포 반응은 항원과 자기 MHC 두 조건이 함께 결정합니다.", [22, 24]),
    ]))
    top.append(EX("MHC restriction의 예외: 이식 반응", CH3, "TCR의 교차 반응성 때문에 alloreactive T세포가 약 1~10%나 됩니다.", [
        P("여기서 의문이 하나 생깁니다. 자기 MHC에 제한되어 반응한다면 왜 장기 이식 때는 타인의 MHC에 엄청난 반응이 나타날까요? 이 예외처럼 보이는 현상이 이식 반응과 superantigen입니다(앞쪽 요약의 예외 표, 파드).", [24]),
        P("alloresponse는 다른 개체의 MHC에 일어나는 강한 T세포 반응입니다. 같은 종 사이의 이식은 **allogeneic**, 서로 다른 종 사이의 이식은 **xenogeneic**(xenograft)이라고 합니다.", [25]),
        HOOK("{b|같은 종끼리면 allogeneic, 다른 종이면 xenogeneic입니다.}", [25, Q16_allo]),
        P("자기 MHC에 반응하도록 교육받은 T세포가 왜 타인의 MHC에도 반응할까요? T세포 수용체에는 어느 정도 교차 반응성(cross-reactivity)이 있습니다. 그래서 자기 MHC와 구조가 비슷한 다른 MHC에 예기치 않게 강하게 결합할 수 있습니다.", [26]),
        P("alloreactive T cell은 전체 T세포의 {k|약 1~10%}라고 합니다.", [28]),
        FIG("f_alloresponse.png", "TCR의 CDR 부위와 MHC-peptide 복합체의 상호작용, alloresponse (슬라이드)", [28]),
        P("흉선(thymus)에서는 positive selection과 negative selection으로 자기 MHC에 적절히 반응하는 세포가 남습니다. 하지만 타인의 MHC에 대한 반응까지 모두 없어지지는 않습니다. 이식 거부반응을 이해할 때 이 점이 중요합니다.", [28]),
        P("즉, 흉선에서 자기 MHC 기준으로 교육 → TCR의 교차 반응성은 남음 → 구조가 비슷한 타인 MHC에 강하게 반응 → 이식 거부반응.", [26, 28]),
        P("이 반응을 보는 고전적인 실험이 mixed lymphocyte reaction(MLR)입니다. MHC가 다른 두 개체의 림프구를 섞어 반응을 봅니다. 양쪽이 모두 증식하면 어느 쪽 반응인지 구별하기 어렵습니다.", [27]),
        P("그래서 한쪽은 irradiation이나 mitomycin C로 증식하지 못하게 합니다. 그러면 처리하지 않은 쪽의 반응을 볼 수 있습니다.", [27]),
        CHK("MHC restriction이 적용되는 것은 alloresponse이다.", "X", [24, 25], why="alloresponse, transplantation, superantigen은 MHC restriction의 예외이다."),
        CHK("유전적으로 동일하지 않은 같은 종의 개체 사이의 이식은 allogeneic transplantation이다.", "O", [25], why="다른 종 사이의 이식은 xenogeneic이다."),
    ], refs=PAD_RESTR + [Q16_allo], mark="기출"))
    top.append(EX("Superantigen", CH3, "peptide 처리 없이 MHC class II와 TCR을 연결해 많은 T세포를 활성화합니다.", [
        P("정상적인 항원 제시는 peptide가 만들어져 MHC의 결합 홈에 자리하고, 특정 TCR이 그 복합체를 인식하는 과정입니다. superantigen은 다릅니다. 일반적인 peptide 처리와 결합 없이 MHC class II와 TCR을 연결해서 많은 T세포를 동시에 활성화합니다.", [29]),
        FIG("f_superantigen.png", "bacterial superantigen과 viral superantigen (슬라이드)", [29]),
        P("많은 T세포가 한꺼번에 자극되면 염증성 신호가 크게 생기고 숙주에 심한 부담이 됩니다. 특정 항원을 가진 병원체를 정교하게 없애는 반응과는 다릅니다. 핵심은 {k|비특이적인 대규모 활성화}이고, superantigen이 TCR과 MHC에 붙는 위치도 일반적인 peptide-MHC-TCR 인식과 다릅니다.", [30]),
        P("즉, peptide 처리 없이 MHC class II와 TCR을 직접 연결 → 많은 T세포가 한꺼번에 활성화 → 염증성 신호가 커져 숙주에 부담.", [29, 30]),
        P("대표적인 예로는 **staphylococcal enterotoxin(SE)**과 **TSST-1**이 있습니다. SE는 식중독과 관련된 독소이고, TSST-1은 toxic shock syndrome과 관련된 독소입니다.", [31]),
    ]))

    top.append(EX("다시 보는 MHC 다양성의 의미", CH3, "감염 방어 범위와 흉선에서의 T세포 선택 부담이 균형을 이룹니다.", [
        P("강의 처음에 본 MHC polymorphism으로 돌아가 봅니다. 사람 집단에서 MHC가 다양하면 모든 사람이 같은 감염원 회피 전략에 취약해질 가능성이 줄어듭니다. 사례로는 EBV의 면역 회피, 특정 인구집단의 HLA 분포, 서아프리카에서 HLA-B53과 중증 말라리아의 관련성이 나옵니다(자료).", [32]),
        P("사례의 수치보다 중요한 메시지는 병원체와 숙주의 유전적 다양성이 서로 영향을 주고받는다는 점입니다.", [32]),
        P("그렇다면 MHC는 종류가 많을수록 좋을 텐데 왜 무한정 늘어나지 않을까요? 다양한 MHC는 더 많은 peptide를 제시하지만, 흉선(thymus)에서 T세포가 선택되는 조건도 그만큼 복잡해집니다. 자가 반응성과 적절한 면역 반응 사이에 {k|균형}이 필요하기 때문입니다.", [33]),
        P("즉, MHC 종류가 많을수록 제시할 수 있는 peptide는 늘지만 흉선 선택의 부담도 커져서, 둘 사이의 균형에서 멈춥니다.", [33]),
    ]))

    # ================================================================ Ⅳ. Class Ib 분자와 비전형적 T세포 (¶34-40)
    top.append(EX("Class Ib 분자: HLA-E, F, G", CH4, "HLA-E, F, G가 중심이고 NK세포와 모체-태아 면역에 관여합니다.", [
        P("지금까지는 고전적 MHC와 peptide 항원을 다뤘습니다. 이 틀로 설명하기 어려운 인식 방식도 있습니다. 거기에 연결된 분자를 class Ib, nonclassical MHC 또는 MHC-like molecule이라고 부릅니다. 분류 용어는 자료마다 조금 다르게 쓰이므로 기능을 함께 봅니다.", [34]),
        P("아래 네 분자를 묶는 이유는 하나입니다. 고전적 class I과 형태가 비슷하지만 다형성이 제한적인 경우가 많고, 기능이 다양하다는 점입니다. HLA-E, HLA-F, HLA-G를 중심으로 보라고 되어 있습니다(자료).", [35]),
        FIG("f_classIb.png", "class Ib 분자와 수용체, 생물학적 기능 (슬라이드)", [35]),
        CLASS_IB,
        HOOK("{b|HLA-C는 class I이면서 Ib이고, HLA-E는 Ib일 뿐 T세포에 항원을 제시하지 않습니다.}", [35, Q16_cls1b, Q10_noAg]),
        CHK("HLA-C는 NK세포의 KIR과 결합해 NK세포를 억제한다.", "O", [35], why="HLA-C는 class I이면서 NK세포 수용체와 상호작용한다."),
    ], refs=PAD_NK, mark="기출"))
    top.append(EX("비전형적 T세포와 CD1", CH4, "peptide-MHC 밖 항원을 인식하는 T세포와 lipid 항원의 CD1입니다.", [
        P("이 소절의 분자와 세포는 공통점이 하나 있습니다. 고전적인 peptide-MHC 틀 밖에서 항원을 다루거나 인식한다는 점입니다.", [36]),
        P("unconventional T cell로는 gamma-delta T cell, 점막과 관련된 MAIT cell, invariant NKT cell을 듭니다. 이름이 다른 만큼 인식하는 표적과 역할도 같지 않습니다.", [36]),
        _st("sub", "(1) CD1 = lipid 또는 glycolipid 항원 제시★", [37, 38]),
        HOOK("고전적 MHC는 peptide를, {b|CD1은 lipid를} T세포에 보여 줍니다.", [37, Q21_CD1c]),
        P("{b|CD1은 peptide가 아니라 lipid 또는 glycolipid 항원을 제시합니다.} 그래서 병원체에서 온 지질 항원을 인식하는 경로와 연결됩니다. CD1a부터 CD1e까지 여러 유형이 있습니다. {b|CD1c는 invariant NKT cell을 활성화합니다.}", [37, 38, Q21_CD1c]),
        P("{r|CD1은 국가시험에 자주 나온다고 강조하셨다고 자료에 적혀 있으니, ‘CD1은 지질 항원제시’를 확실히 기억합니다.}", [37]),
        P("{p|(작성자 생각) 자료는 CD1c와 invariant NKT cell을 연결합니다. 하지만 일반적으로 invariant NKT cell의 대표 인식 분자는 CD1d이므로, 복습할 때 검증이 필요합니다.}", [38]),
        FIG("f_cd1.png", "CD1c(왼쪽)와 CD1d(오른쪽)에 지질이 결합한 모습 (슬라이드)", [37, 38]),
        P("FcRn은 MHC와 닮은 분자이지만 항원제시보다 모체의 IgG 전달과 관련된 역할을 합니다.", [38]),
        CHK("CD1c는 invariant NKT cell을 활성화한다.", "O", [37, 38], why="CD1은 lipid 항원을 제시한다."),
        _st("sub", "(2) gamma-delta T cell과 MAIT cell", [39, 40]),
        FIG("f_gdT.png", "gamma-delta T cell을 활성화하는 ligand (슬라이드)", [39]),
        P("gamma-delta T cell은 그림의 표에 나온 여러 ligand를 인식합니다. 고전적인 peptide-MHC 인식과 달리 다양한 신호를 직접 감지합니다. {g|수업에서는 종류가 다양하다는 정도로 넘어갔습니다.}", [39]),
        P("MAIT cell은 점막 면역과 관계가 있고 미생물 유래 물질을 인식합니다. 선천면역과 적응면역 사이를 잇는 세포로 설명합니다.", [40]),
        MEMO("스크립트 끝의 [검증참고] 다섯 문단(¶41–45)은 강의 내용이 아니라 자료 재구성에 대한 설명이어서 노트에 넣지 않았습니다.", [41, 42, 43, 44, 45]),
    ]))

    # ================================================================ Take home messages
    top.append(T("Take home messages", "", [], [
        _st("sub", "1. MHC는 polygenic + polymorphic = 항원제시 범위를 넓힘★", [2, 13]),
        _st("sub", "2. {b|다형성 순서: class I B > A > C, class II DRB > DQB > DPB}★", [15, 16] + PAD_POLY),
        _st("sub", "3. {b|class I은 HLA-A, B, C, class II는 HLA-DR, DP, DQ}★", [6] + [Q21_cls2, Q18_CD8]),
        _st("sub", "4. 일반 T세포 반응 = peptide + 자기 MHC, {b|예외는 alloresponse, 이식, superantigen}★", [21, 24] + PAD_RESTR),
        _st("sub", "5. {b|HLA-C는 KIR로 NK세포 억제, CD1c는 lipid 항원으로 iNKT 활성화}★", [35, 37] + [Q19_KIR, Q21_CD1c]),
    ], role="closing"))
    return top


if __name__ == "__main__":
    import sys

    topics = build()
    for t in topics:
        t.slide_numbers = sorted({r for sts in t.sections.values() for st in sts for r in st.slide_refs})
    dump(topics, sys.stdout)
