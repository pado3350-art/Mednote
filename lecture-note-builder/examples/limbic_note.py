"""Mixed-style note for 'Limbic system' (편도체복합체, septal nuclei, nucleus accumbens) - written by the make-lecture-note workflow
(docs/WORKFLOW.md): script -> storyline.md -> this file -> build.

Inputs (nothing else is used):
  * script   inputs/limbic_script.txt   (40 speech paragraphs + 5 [검증참고] notes)
  * pictures inputs/limbic_figs/        (slide images from the 정리본 PDF - pictures only, no text from it)
  * PAD      inputs/limbic_pad.pdf      (13 questions) - used ONLY to decide what is blue.
Run:  python -m examples.limbic_note > outputs/wf_limbic/note_authored.json
"""
from app.models import Diagram, Group, Statement
from examples.abx_note import B, DFULL, EX, LS, P, ROWS
from examples.stemcell_note import CHK, MEMO, _st
from examples.authoring import T, dump

FIG_DIR = "inputs/limbic_figs/"
CH1 = "편도체(amygdala)의 구조와 연결"
CH2 = "Septal nuclei(사이막핵)의 위치와 연결"
CH3 = "Nucleus accumbens의 위치와 연결"
CH4 = "해부 실습 사진으로 보는 구조"

# PAD units (parse order of inputs/limbic_pad.pdf)
Q20_53, Q20_9, Q19_29, Q19_31, Q19_32, Q18_21, Q18_25, Q17_4, Q17_3, Q14_2, Q12_1, Q12_3, Q12_4 = range(1001, 1014)
PAD_AMY = [Q20_53, Q19_29, Q18_25, Q14_2, Q12_1, Q12_3]  # basolateral / corticomedial / central
PAD_EFF = [Q19_32, Q20_9, Q12_1]  # stria terminalis, ventral amygdalofugal
PAD_SEP = [Q18_21, Q17_3, Q12_4, Q17_4, Q14_2, Q20_9]  # septal nuclei connections


def FIG(img, caption, g=()):
    return Statement(text=caption, kind="figure", image=FIG_DIR + img, slide_refs=list(g))


# ---- the two exam tables: SAME object on the front page and in the body
AMY = ROWS([
    ["{b|basolateral}", "{b|대뇌와 광범위하게 연결 (higher-order, 고위 연합 입력)}\n여러 감각 정보와 대뇌피질 정보를 통합"],
    ["{b|corticomedial}", "{b|olfactory system와 밀접: olfactory bulb, primary olfactory cortex}"],
    ["{b|central}", "{b|brainstem과 연결 (부교감 신경핵)}\nhypothalamus와도 연결 → 자율신경·내장 반응"],
], col_titles=["group", "연결과 단서"], col_widths=[3.6, 13.8], g=[5, 6] + PAD_AMY)

SEPTAL = ROWS([
    ["{b|hippocampus}", "{b|fornix}\nprecommissural fibers"],
    ["{b|habenular nuclei}", "{b|stria medullaris thalami}"],
    ["{b|amygdala}", "{b|stria terminalis, ventral amygdalofugal pathway}"],
    ["{b|ventral tegmental area, hypothalamus}", "{b|medial forebrain bundle}\ndopamine-containing fibers 포함 → 쾌락, 충동"],
], col_titles=["연결되는 곳", "경로(섬유)"], col_widths=[6.4, 11.0], g=[23, 24, 26] + PAD_SEP)


EFF = ROWS([
            ["stria terminalis", "출발: {b|corticomedial nuclei}\n위치: caudate nucleus와 dorsal thalamus 사이, lateral ventricle 부근에서 thalamostriate vein(terminal vein)과 함께 주행\n표적: septal nuclei, hypothalamus, nucleus accumbens septi"],
            ["ventral amygdalofugal pathway", "출발: basolateral nuclei, central nucleus (더 주요한 경로)\n표적: substantia innominata, hypothalamus, septal nuclei, nucleus accumbens septi\n{b|dorsomedial nucleus of thalamus} → prefrontal cortex\nfrontal, cingulate, insular, inferior temporal cortex (entorhinal region, subiculum)"],
], col_titles=["경로", "출발, 위치, 표적"], col_widths=[4.4, 13.0], g=[14, 15, 16, 17, 18] + PAD_EFF)


def build():
    top = []
    # ================================================================ 앞쪽: 전체 지도 + 기출 두 유형 표
    top.append(T("요약 ① 편도체 group [기출]", "", [], [
        P("변연계(limbic system) 강의는 편도체복합체(amygdaloid complex), septal region, nucleus accumbens 세 구조를 다루고, 기능보다 어디서 정보를 받아 어디로 보내는지"
          "(afferent, efferent)를 구분하는 것이 핵심입니다. 세 구조는 서로 연결되어 있습니다.", [1, 2]),
        DFULL("강의 전체 지도: 세 구조와 대표 연결어", Diagram(kind="tree", root="변연계", groups=[
            Group(title="1. 편도체(amygdala)", color="teal", items=["uncus 안쪽, 두 그룹", "afferent / efferent", "대표 기능: fear"]),
            Group(title="2. septal nuclei", color="blue", items=["anterior commissure 앞", "네 곳과 연결 (기출)", "자율 행동 과정"]),
            Group(title="3. Nucleus accumbens", color="salmon", items=["caudate head, putamen 이어지는 곳", "amygdala, hippocampus, VTA 입력", "대표 기능: addiction"]),
            Group(title="4. 실습 사진", color="amber", items=["stria terminalis, uncus", "fimbria, fornix, dentate gyrus"]),
        ]), [1, 2, 37, 38]),
        FIG("f_nuclei.png", "편도체의 핵 구분(cortical, central, basolateral)과 uncus 안쪽 위치 (슬라이드)", [3, 4]),
        AMY,
    ], role="front"))
    top.append(T("요약 ② 편도체 출력과 septal nuclei [기출]", "", [], [
        P("기출은 편도체에서 나가는 경로와, septal nuclei(septal nuclei)과 연결되는 곳·경로를 짝지어 묻습니다.", [13, 24]),
        EFF,
        SEPTAL,
        FIG("f_septal.png", "septal nuclei의 위치와 연결 경로 (슬라이드)", [23, 26]),
    ], role="front"))

    # ================================================================ 1장 편도체복합체 (¶3-20)
    top.append(EX("편도체는 어디에 있고 어떻게 나뉘나?", CH1, "uncus 안쪽에 있고, 두 그룹(basolateral, corticomedial group)으로 나눕니다.", [
        P("편도체(amygdala)는 uncus 안쪽에 있고, 하나의 핵이 아니라 여러 핵으로 이루어진 복합체(complex)입니다. 그림에서 uncus를 먼저 찾으면 그 안쪽에 핵들이 모여 있습니다.", [3]),
        FIG("f_nuclei.png", "편도체의 핵 구분과 uncus 안쪽 위치 (슬라이드)", [3]),
        P("group을 나누는 방식은 책마다 조금 다릅니다. 이번 수업은 basolateral nuclei와 cortical(medial) nuclei 두 그룹으로 정리하고, "
          "central nucleus를 따로 떼어 세 그룹으로 보는 경우는 cortical-medial group에 묶습니다.", [4]),
        P("{r|시험을 위해서는 큰 분류 두 개를 먼저 가져가야 하고, 이 분류가 뒤의 연결 경로를 이해하는 기준이라고 강조하셨습니다.}", [4]),
    ]))
    top.append(LS("basolateral·corticomedial group은 무엇과 연결되나?", CH1, [
        AMY,
        P("편도체 전체의 기능은 fear, endocrine activity, sexual behavior, 음식물 섭취, emotion-related learning 등이고, 이 가운데 가장 기본인 것이 fear(공포)입니다.", [6]),
        P("{r|편도체와 공포의 연결은 졸업 뒤에도 기억해야 할 정도라고 강조하셨습니다.}", [6]),
        P("{b|기출: amygdaloid nucleus 이상과 관련된 질환으로 docility, hyperorality, hypersexuality가 나왔고, anterograde amnesia는 해마(hippocampus) 이상이라 해당하지 않습니다.}{g| 이번 강의에서는 직접 다루지 않았습니다.}", [Q19_31]),
        CHK("편도체와 고위 감각 피질 영역의 연결이 비정상이면 일차적으로 central nucleus에 문제가 생긴다.", "X", [5],
            why="higher-order 입력을 받는 것은 basolateral nuclei이다."),
    ], new_page=False))
    top.append(EX("어디서 정보가 들어오나(afferent)?", CH1, "basolateral은 대뇌 광범위한 입력, corticomedial은 후각 입력", [
        P("afferent는 들어오는 것, efferent는 나가는 것이므로 두 방향을 뒤집으면 안 됩니다.", [7]),
        ROWS([
            ["basolateral", "여러 감각 정보(somatosensory, visual, visceral)가 들어옴\n{b|cortical input}: prefrontal, cingulate, parahippocampal gyrus, temporal region, insular cortex\ndorsal thalamus\nsubiculum (hippocampus)"],
            ["corticomedial", "{b|olfactory bulb (direct olfactory pathway), primary olfactory cortex}\ndorsal thalamus\nhypothalamus (ventromedial nucleus, lateral hypothalamic area)"],
            ["central", "parabrachial nuclei, solitary nucleus, periaqueductal gray (내장 기능, 통증 조절)"],
        ], col_titles=["group", "들어오는 곳"], col_widths=[3.6, 13.8], g=[7, 8, 9, 10, Q20_53, Q19_29, Q12_1, Q12_3]),
        P("{r|‘후각’이라는 말을 들으면 바로 corticomedial group이라고 답할 수 있어야 한다고 강조하셨습니다.}", [9]),
        FIG("f_aff.png", "편도체로 들어오는 afferent 경로: 파랑 = basolateral, 빨강 = corticomedial (슬라이드)", [11]),
        P("파란 경로는 basolateral group으로, 붉은 경로는 corticomedial group으로 들어옵니다. 대뇌피질에서 뻗는 화살표는 basolateral, "
          "olfactory bulb에서 오는 경로는 corticomedial로 이어집니다. 색깔보다 어디서 출발한 정보가 어느 group에 닿는지를 봅니다.", [11, 12]),
        P("brainstem, 시상하부, 시상, 해마에서 들어오는 연결은 efferent에서도 다시 나옵니다. 핵이 입력만 받는 것이 아니라 다른 구조와 회로를 이루기 때문입니다.", [12]),
    ], refs=[Q20_53, Q19_29, Q12_1, Q12_3], mark="기출"))
    top.append(EX("어디로 나가나(efferent)?", CH1, "stria terminalis와 ventral amygdalofugal pathway 두 경로입니다.", [
        P("fugal은 밖으로 나간다는 뜻입니다. ventral amygdalofugal pathway가 주요 efferent pathway이고, stria terminalis는 위치와 연결 대상을 특히 기억해야 합니다.", [13]),
        EFF,
        P("{r|stria terminalis의 표적(septal nuclei, hypothalamus, nucleus accumbens)은 외워 두고, 경로 하나를 따로 외우지 말고 연결망으로 기억하라고 강조하셨습니다.}", [16]),
        P("central nucleus는 brainstem과 연결되어 자율신경 반응과 관련됩니다. ventral amygdalofugal pathway는 연결 범위가 넓다는 점을 먼저 기억하고, 두 경로의 출발점과 표적을 비교합니다.", [18]),
        FIG("f_eff1.png", "stria terminalis와 ventral amygdalofugal pathway (슬라이드)", [19]),
        P("왼쪽 모식도에서 stria terminalis는 caudate nucleus와 dorsal thalamus 사이를 따라 길게 휘어 지나가고, ventral amygdalofugal pathway는 다른 방향과 위치로 주행합니다. 모든 화살표를 외우는 것이 아니라 두 경로가 다르게 주행한다는 점을 확인합니다.", [19]),
        FIG("f_eff2.png", "편도체(Am)의 3차원 재구성과 단면 (슬라이드)", [20]),
        P("아래 그림의 Am이 amygdala이고, 거기서 나오는 stria terminalis와 다른 efferent 경로를 따라가 봅니다. 경로의 굴곡을 그리는 것이 아니라 amygdala에서 어디로 이어지는지 추적하는 것이 목표입니다.", [20]),
        CHK("Stria terminalis는 limbic system과 관련이 있는 corticomedial nuclei의 efferent fiber이다.", "O", [14, 15], why="corticomedial nuclei에서 나온다."),
    ], refs=PAD_EFF, mark="기출"))

    # ================================================================ 2장 septal nuclei (¶21-26)
    top.append(EX("septal nuclei는 어디에 있나?", CH2, "anterior commissure 앞, septum pellucidum 아래의 깊은 층입니다.", [
        P("septal nuclei(사이막핵)는 육안으로 관찰하기 어렵지만 limbic system의 여러 구조와 연결되어 있어 신경로 공부에서 중요합니다. 위치는 anterior commissure 앞쪽, 대뇌반구 안쪽 벽, septum pellucidum 아래입니다.", [21]),
        P("겉에서 보이는 구조는 paraterminal gyrus와 subcallosal area이고, 핵은 그보다 깊은 층에 있습니다. 실습에서 표면 구조에 핵이 그대로 노출되어 있다고 보면 안 됩니다.", [22]),
        P("편도체에서 stria terminalis와 ventral amygdalofugal pathway로 연결되는 곳이어서 앞에서 septal nuclei가 여러 번 나왔습니다.", [22]),
    ]))
    top.append(LS("연결되는 네 곳과 경로는?", CH2, [
        SEPTAL,
        P("{r|이 표가 오늘 septal nuclei에서 가장 중요한 부분이니 네 곳과 경로를 짝지어 외우라고 강조하셨습니다.}", [24]),
        FIG("f_septal.png", "septal nuclei의 위치와 연결 경로 (슬라이드)", [23, 26]),
        CHK("Retroflex fasciculus는 septal nuclei와 연결되는 신경섬유이다.", "X", [23, 24], why="fornix, stria terminalis, medial forebrain bundle, stria medullaris thalami가 해당한다."),
        CHK("Septal nuclei와 hypothalamus를 연결하는 구조는 medial forebrain bundle이다.", "O", [24], why="VTA와 hypothalamus 연결에 medial forebrain bundle이 관여한다."),
    ], new_page=False, ))
    top.append(EX("septal nuclei는 무슨 일을 하나?", CH2, "여러 변연계 구조와 reciprocal하게 연결되어 자율 행동 과정에 관여합니다.", [
        P("reciprocal은 한 방향으로만 가는 것이 아니라 서로 정보를 주고받는다는 뜻이어서, 구조를 따로 떼지 않고 limbic circuit 안에서 이해해야 합니다.", [25]),
        P("medial forebrain bundle에는 dopamine-containing fibers가 있어 쾌락, 충동과 연결해 설명합니다.", [26]),
        P("septal region은 eating, drinking, sexual behavior, reproduction, aggression 같은 autonomic behavioral process에 관여합니다. 운동을 수행하는 핵이 아니라 몸의 내부 상태와 행동을 잇는 과정에 관여한다고 이해합니다.", [26]),
    ]))

    # ================================================================ 3장 nucleus accumbens (¶27-32)
    top.append(EX("nucleus accumbens는 어디에 있고 무슨 일을 하나?", CH3, "caudate head와 putamen이 이어지는 앞쪽에 있고, 중독과 연결됩니다.", [
        P("nucleus accumbens septi(사이막곁핵)는 basal ganglia에서도 이름이 나왔고, 오늘은 limbic system의 구성 요소로 다시 나옵니다. 위치는 caudate nucleus의 head와 putamen이 이어지는 부위로, 뇌의 비교적 앞쪽입니다.", [27]),
        FIG("f_acc_loc.png", "nucleus accumbens의 위치: caudate head와 putamen 사이 (슬라이드)", [27]),
        P("그림에서 caudate head와 putamen을 먼저 찾고, 그 사이 아래쪽으로 이어지는 부분이 nucleus accumbens입니다.", [27]),
        P("{r|amygdala는 fear, nucleus accumbens는 addiction으로 연결해 반드시 가져가라고 강조하셨습니다.}", [28]),
    ]))
    top.append(LS("nucleus accumbens의 afferent와 efferent는?", CH3, [
        ROWS([
            ["입력 (afferent)", "amygdala: stria terminalis 또는 ventral amygdalofugal pathway\nhippocampus: precommissural fornix\nventral tegmental area: medial forebrain bundle"],
            ["출력 (efferent)", "hypothalamus, brainstem, globus pallidus"],
        ], col_titles=["방향", "연결"], col_widths=[3.8, 13.6], g=[29, 30]),
        P("{g|출력은 원문 자료에서 간단히 다루어, 위에 나열한 경로를 연결하는 데 집중했습니다.}", [30]),
        FIG("f_acc_path.png", "nucleus accumbens의 입력과 출력 경로 (슬라이드)", [31]),
        P("fornix, stria terminalis, medial forebrain bundle이 같은 모식도에 나오는 것은 이 경로들이 따로 외울 목록이 아니라 하나의 회로를 이루기 때문입니다.", [31]),
    ]))
    top.append(LS("amygdala와 어떻게 다른가?", CH3, [
        FIG("f_compare.png", "Limbic structures and behavior: amygdala와 nucleus accumbens 비교 (슬라이드)", [32]),
        P("표에서 amygdala는 fear, aversion과 관련된 중심이고, nucleus accumbens는 joy, pleasure, addiction과 관련된 중심입니다.", [32]),
        P("신경전달물질도 비교되어 있는데, nucleus accumbens에서는 dopamine과의 관련성을 기억합니다.", [32]),
    ]))

    # ================================================================ 4장 실습 사진 (¶33-36)
    top.append(LS("사진에서 stria terminalis와 uncus는?", CH4, [
        FIG("f_photo1.png", "실습 사진(e-neuroanatomy): stria terminalis, uncus, parahippocampal gyrus (슬라이드)", [33, 34]),
        P("stria terminalis는 안쪽에서 혈관과 함께 주행하므로 그 위치를 알아 두면 확인에 도움이 됩니다. 실습에서 보이는 구조와 보기 어려운 구조가 섞여 있습니다.", [33]),
        P("uncus 안쪽에 amygdala가 있고, parahippocampal gyrus는 해마 주변 구조를 확인할 때의 기준점입니다. 해부 사진은 모식도와 크기와 색이 달라서 상대적인 위치를 익혀야 합니다.", [34]),
    ]))
    top.append(LS("fimbria에서 dentate gyrus까지는?", CH4, [
        FIG("f_photo2.png", "parahippocampal gyrus를 젖힌 뒤 보이는 구조 (슬라이드)", [35, 36]),
        ROWS([
            ["fimbria", "alveus가 모여 형성됨, fornix와 이어지는 연속 섬유 경로"],
            ["fornix", "앞쪽으로 이어짐, postcommissural fornix는 mammillary body와 hippocampus 사이 연결"],
            ["hippocampal sulcus", "dentate gyrus와 hippocampus proper의 경계"],
            ["dentate gyrus", "sulcus 주변에 점처럼 보임"],
            ["lamina terminalis", "위치를 함께 확인"],
        ], col_titles=["구조", "확인할 점"], col_widths=[4.4, 13.0], g=[35, 36]),
        P("실습에서는 이름을 보고 실제 단면에서 위치를 찾아가는 훈련이 중요합니다.", [36]),
        MEMO("마지막에 졸업 뒤 진로(임상교실, 기초의학교실) 안내가 있었으나 신경해부학 내용이 아니어서 생략했습니다.", [39, 40]),
        MEMO("스크립트 끝의 [검증참고] 다섯 문단(¶41–45)은 강의 내용이 아니라 자료 재구성에 대한 설명이어서 노트에 넣지 않았습니다.", [41, 42, 43, 44, 45]),
    ]))
    return top


if __name__ == "__main__":
    import sys

    topics = build()
    for t in topics:
        t.slide_numbers = sorted({r for sts in t.sections.values() for st in sts for r in st.slide_refs})
    dump(topics, sys.stdout)
