"""Second example: 'Limbic system' (신경과학1) script -> note in the same MOM v2 style.

Same rules as examples/tcell_note.py (readable-note-organizer): all content kept, reorganised for
understanding; chapters with § sections, 기본정석 boxes, Advice / Reference call-outs, 핵심 어휘 and
요약 정리 pages. No PAD was provided for this lecture, so there is no blue text and no exam section.

Authoring uses the script's 20 time blocks (+ 21 = closing remarks) only as reference numbers; they are
remapped to paragraph ids (¶), so the final note carries no time-block structure.
Run:  python -m examples.limbic_note inputs/limbic_script.docx > outputs/limbic/note_authored.json
"""
import json
import sys

from app.models import SlideTable
from examples.tcell_note import ADV, B, P, REF, STAR, T, _remap, unit_ids_from_script

CH1 = "Amygdaloid nuclear complex"
CH2 = "Septal region & Nucleus accumbens"
CH3 = "해부 실습 구조"


def build(unit_ids):
    top = []

    # ---------------------------------------------------------------- 핵심 어휘
    top.append(T("핵심 어휘", "", [1, 2, 3, 4, 7, 9, 11, 13, 14, 18], [
        P("오늘 나오는 핵심 용어를 먼저 훑어보자. 뒤에서 하나씩 다시 나오니 가볍게 읽고 가도 좋다.", 1),
        B("**Limbic system (변연계)** : 감정·동기·기억과 관련된 구조들이 연결된 회로. 오늘은 편도체복합체, septal region, nucleus accumbens를 본다.", 1),
        B("**Amygdaloid nuclear complex (편도체복합체)** : uncus 안쪽에 있는 여러 핵의 집합. 대표 기능은 fear(공포).", 2, 3),
        B("**Basolateral nuclei / Cortical(medial) nuclei** : 편도체 핵군을 나누는 두 그룹. 앞은 대뇌 광범위, 뒤는 후각계와 연결.", 2, 3),
        B("**Afferent / Efferent** : 들어오는 경로 / 나가는 경로. 방향을 절대 뒤집지 말 것.", 4),
        B("**Stria terminalis (분계섬유줄)** : caudate nucleus와 dorsal thalamus 사이를 지나는 편도체의 efferent 경로.", 7, 8),
        B("**Ventral amygdalofugal pathway** : 편도체의 주요 efferent 경로. fugal = 밖으로 나가는.", 7, 9),
        B("**Septal nuclei (사이막핵)** : 변연계 여러 구조와 연결되는 핵. 육안으로 관찰하기 어렵다.", 11),
        B("**Medial forebrain bundle** : dopamine-containing fibers를 가진 다발. septal nuclei, nucleus accumbens의 VTA·hypothalamus 연결에 관여.", 12, 13),
        B("**Nucleus accumbens septi (사이막곁핵)** : caudate head와 putamen이 이어지는 곳. 기능의 핵심은 addiction(중독).", 14),
        B("**Fornix / Fimbria / Dentate gyrus** : 해마 주변의 섬유 경로와 구조. 해부 실습 사진에서 확인.", 18),
    ], role="front"))

    # ---------------------------------------------------------------- 요약 정리
    top.append(T("요약 정리", "", [1, 2, 3, 4, 7, 12, 14, 15, 16, 18, 19], [
        STAR("편도체복합체", 2, 3, 19),
        B("{r|uncus 안쪽}에 위치, 핵군은 **basolateral / corticomedial** 두 그룹", 2, 19),
        B("Basolateral : 대뇌 광범위 / Corticomedial : **후각계** / Central nucleus : hypothalamus·brainstem", 3, 19),
        B("대표 기능 {r|fear (공포)}", 3, 19),
        STAR("Afferent / Efferent", 4, 7, 19),
        B("Afferent(들어옴) : basolateral ← cortical input, dorsal thalamus, subiculum / corticomedial ← olfactory bulb·primary olfactory cortex, dorsal thalamus, hypothalamus", 4),
        B("Efferent(나감) : {r|stria terminalis} (→ septal nuclei, hypothalamus, nucleus accumbens septi), **ventral amygdalofugal pathway** (주요 경로)", 7, 19),
        STAR("Septal nuclei — 네 곳과 연결", 12, 19),
        B("Hippocampus — precommissural fornix / Habenular nuclei — stria medullaris thalami", 12),
        B("Amygdala — stria terminalis 또는 ventral amygdalofugal pathway / VTA·hypothalamus — medial forebrain bundle", 12),
        STAR("Nucleus accumbens", 14, 15, 16),
        B("위치 : caudate head와 putamen이 이어지는 앞쪽 / {r|addiction (중독)}, dopamine과 관련", 14, 16),
        B("들어옴 : amygdala, hippocampus, VTA / 나감 : hypothalamus, brainstem, globus pallidus", 15),
        B("{r|Amygdala — fear, Nucleus accumbens — addiction}", 16, 19),
        STAR("해부 실습에서 찾을 구조", 17, 18, 19),
        B("stria terminalis, uncus, parahippocampal gyrus, fimbria, fornix, mammillary body, hippocampal sulcus, dentate gyrus, lamina terminalis", 17, 18, 19),
    ], role="front"))

    # ================================================================ Ch 1 · § 1
    top.append(T("편도체복합체의 위치와 핵군", CH1, [1, 2, 3], [
        STAR("오늘의 큰 그림", 1),
        P("오늘은 변연계에서 **세 가지 구조**를 본다 : ① 편도체복합체(amygdaloid nuclear complex) ② septal region ③ nucleus accumbens. "
          "구조의 기능도 중요하지만, **어디에서 정보를 받아서 어디로 보내는지**, 즉 afferent와 efferent pathway를 구분하는 것이 핵심이다.", 1),
        P("세 구조는 따로 떨어져 움직이는 것이 아니라 서로 연결되어 있다. 먼저 큰 그림 한 줄씩만 잡아두자.", 1),
        B("편도체 → **공포(fear)**", 1),
        B("septal nuclei → 여러 변연계 구조와 연결", 1),
        B("nucleus accumbens → **중독(addiction)**", 1),
        P("{g|실습에서는 구조의 위치를 묻기도 하므로 경로가 지나가는 위치도 같이 본다. 그림을 무작정 외우기보다 이름, 출발점, 도착점, 위치를 연결해서 이해하자.}", 1),
        STAR("편도체의 위치와 구성", 2),
        P("편도체(amygdala)는 **uncus 안쪽**에 있다. 그림에서 uncus를 먼저 찾고, 그 안쪽에 핵들이 모여 있다고 보면 된다. "
          "편도체는 하나의 균일한 핵이 아니라 **여러 핵으로 이루어진 complex**라는 점을 알아두자.", 2),
        P("핵군을 이 수업에서는 **두 그룹**으로 정리한다.", 2),
        B("**Basolateral nuclei**", 2),
        B("**Cortical (medial) nuclei** — central nucleus는 따로 떼지 않고 corticomedial 쪽과 함께 묶어 생각한다.", 2),
        ADV("핵군을 나누는 방식은 책이나 학자에 따라 다르다. central nucleus를 따로 떼어 **세 그룹**으로 설명하는 경우도 있지만, 이 수업에서는 {r|두 그룹}으로 가져가자. 이 분류가 뒤의 연결 경로를 이해하는 기준이 된다.", 2),
        STAR("두 그룹은 각각 무엇과 연결될까?", 3),
        B("**Basolateral nuclei** : 대뇌의 상당히 광범위한 부분과 연결 → 다양한 감각 정보와 대뇌피질 정보를 통합하는 쪽.", 3),
        B("**Cortical (medial) nuclei** : 후각계(olfactory system)와 밀접하게 연결 — 지난 시간에 배운 olfactory bulb, primary olfactory cortex와 이어진다.", 3),
        B("**Central nucleus** : hypothalamus, brainstem nuclei와 연결 → 자율신경·내장 기능과 관련된 반응.", 3),
        STAR("편도체의 기능", 3),
        P("편도체의 기능은 fear, endocrine activity(내분비), sexual behavior, 음식물 섭취, emotion-related learning 등이 있다. 이 가운데 가장 기본이면서 꼭 기억할 것은 "
          "{r|fear(공포)}이다. 의과대학을 졸업한 뒤에도 ‘편도체 = 공포’ 연결은 기억해야 한다.", 3),
    ], basics_title="편도체복합체", basics=[
        "편도체(amygdala)는 uncus 안쪽에 있고, 하나의 핵이 아니라 여러 핵으로 이루어진 complex이다.",
        "이 수업에서는 핵군을 basolateral nuclei와 cortical(medial) nuclei 두 그룹으로 나누고, central nucleus는 corticomedial 쪽과 묶어 본다.",
        "대표 기능은 fear(공포) — endocrine activity, sexual behavior, 음식물 섭취, emotion-related learning도 담당한다.",
    ], tables=[SlideTable(rows=[
        ["핵군", "연결되는 곳", "의미"],
        ["Basolateral nuclei", "대뇌의 광범위한 부분", "감각·대뇌피질 정보를 통합"],
        ["Cortical (medial) nuclei", "후각계 (olfactory bulb, primary olfactory cortex)", "후각 정보와 밀접"],
        ["Central nucleus", "hypothalamus, brainstem nuclei", "자율신경·내장 기능 반응"],
    ], caption="편도체 핵군과 연결 (강의 설명을 표로 정리)", col_widths_cm=[4.0, 7.4, 6.0])]))

    # ================================================================ Ch 1 · § 2
    top.append(T("Afferent fibers (들어오는 경로)", CH1, [4, 5, 6], [
        STAR("먼저 방향부터 : Afferent vs Efferent", 4),
        P("**Afferent는 들어오는 것, efferent는 나가는 것**이다. 두 방향을 절대 뒤집으면 안 된다. 먼저 편도체로 들어오는 정보부터 본다.", 4),
        STAR("Basolateral group으로 들어오는 경로", 4),
        P("이 그룹은 대뇌의 여러 부분과 연결되므로 **somatosensory, visual, visceral information** 같은 여러 종류의 정보가 들어온다. 목록이 길어 보이지만 **세 덩어리**로 묶으면 외우기 쉽다.", 4),
        B("**Cortical input** : prefrontal gyrus, cingulate gyrus, parahippocampal gyrus, temporal region, insular cortex", 4),
        B("**Dorsal thalamus**", 4),
        B("**Subiculum** (hippocampus 쪽)", 4),
        STAR("Corticomedial group으로 들어오는 경로", 5),
        P("앞의 basolateral group과 **비교**하는 것이 중요하다. 여기서는 **후각계 입력**이 중심이다.", 5),
        B("**Olfactory bulb** (direct olfactory pathway)와 **primary olfactory cortex**", 5),
        B("**Dorsal thalamus**", 5),
        B("**Hypothalamus** — ventromedial nucleus, lateral hypothalamic area", 5),
        B("**Central nucleus의 연결** : 내장 기능·통증 조절과 연관된 뇌줄기 구조 — parabrachial nuclei, solitary nucleus, periaqueductal gray (지난 시간 pain control과 연결)", 5),
        ADV("‘**후각**’이라는 말을 들으면 바로 **corticomedial group**이라고 대답할 수 있어야 한다. 핵심 대비 : {r|basolateral = 광범위한 cortical input / corticomedial = olfactory input}.", 5),
        STAR("그림으로 확인하기", 6),
        P("글로만 보면 헷갈리니 그림으로 확인한다. 그림에서 **파란 쪽은 basolateral group으로 들어오는 경로**, **붉은 쪽은 corticomedial group**에 대응한다. "
          "색깔을 외우기보다 어디서 출발한 정보가 어느 핵군으로 도착하는지를 보자.", 6),
        B("대뇌피질 여러 곳에서 뻗어 들어오는 화살표 → basolateral group의 특징", 6),
        B("olfactory bulb·후각계에서 오는 경로 → corticomedial 쪽으로 연결", 6),
        B("뇌줄기, 시상하부, 시상, 해마에서 들어오는 연결도 함께 확인", 6),
        P("이 구조들은 나중에 efferent를 배울 때 상당수가 다시 나온다. 핵이 정보를 받기만 하는 것이 아니라 다른 구조와 회로를 이루며 **서로 영향을 주고받기** 때문이다. 여기까지가 들어오는 길이고, 이제 나가는 길로 넘어간다.", 6),
    ], basics_title="Afferent fibers to amygdaloid complex", basics=[
        "Afferent = 들어오는 경로, efferent = 나가는 경로. 방향을 뒤집지 말 것.",
        "Basolateral group : 대뇌 광범위 → cortical input(prefrontal, cingulate, parahippocampal, temporal, insular), dorsal thalamus, subiculum.",
        "Corticomedial group : 후각계(olfactory bulb, primary olfactory cortex) + dorsal thalamus + hypothalamus. Central nucleus는 parabrachial nuclei, solitary nucleus, periaqueductal gray와 연결.",
    ], tables=[SlideTable(rows=[
        ["", "Basolateral group", "Corticomedial group"],
        ["정보의 성격", "somatosensory, visual, visceral (광범위)", "후각 중심"],
        ["들어오는 곳", "cortical input, dorsal thalamus, subiculum", "olfactory bulb / primary olfactory cortex, dorsal thalamus, hypothalamus"],
        ["그림 색", "파란 경로", "붉은 경로"],
    ], caption="Afferent 비교 (강의 설명을 표로 정리)", col_widths_cm=[3.0, 6.8, 7.6])]))

    # ================================================================ Ch 1 · § 3
    top.append(T("Efferent fibers (나가는 경로)", CH1, [7, 8, 9, 10], [
        STAR("편도체에서 나가는 두 경로", 7),
        P("편도체에서 정보가 나가는 길은 크게 **두 가지**이다. **stria terminalis(분계섬유줄)** 와 **ventral amygdalofugal pathway**. "
          "이름이 길지만 fugal = 밖으로 나간다고 떠올리면 된다. ventral amygdalofugal pathway가 **주요(major) efferent pathway**이고, "
          "stria terminalis는 **위치와 연결 대상**을 특히 기억하자.", 7),
        B("**Stria terminalis** — corticomedial nuclei 쪽에서 나오는 길", 7),
        B("**Ventral amygdalofugal pathway** — basolateral nuclei와 central nucleus에서 나오는 주요 경로", 7),
        P("{r|먼저 두 경로의 이름부터.}  나중에 그림을 볼 때도 이 두 경로를 찾는 것이 첫 번째 목표이다.", 7),
        STAR("Stria terminalis : 위치와 표적", 8),
        P("**위치** : caudate nucleus와 dorsal thalamus **사이**를 주행한다. lateral ventricle 부근에서 **thalamostriate vein(terminal vein)** 과 같이 지나간다. "
          "글로만 외우지 말고 미상핵과 시상을 기준으로 공간적 위치를 머릿속에 잡자. 해부 실습에서 확인할 수 있는 구조이다.", 8),
        P("**표적** : {r|septal nuclei, hypothalamus, nucleus accumbens septi} — 세 곳은 외워두자. 뒤에서 septal nuclei와 nucleus accumbens를 따로 배울 때 이 경로가 다시 나온다. "
          "경로를 하나씩 따로 외우기보다 **연결망**으로 생각하면 오래 기억된다.", 8),
        STAR("Ventral amygdalofugal pathway", 9),
        P("basolateral과 central nucleus에서 나오는, 더 **주요한** efferent 경로이다. 여러 곳으로 가므로 한꺼번에 외우기보다 상대적으로 넓은 범위로 연결된다는 점을 먼저 기억하자.", 9),
        B("**substantia innominata, hypothalamus, septal nuclei, nucleus accumbens septi** 등으로 간다.", 9),
        B("**dorsomedial nucleus of thalamus**로 가고, 그 신호는 **prefrontal cortex**로 연결된다.", 9),
        B("**cortical region** : frontal, cingulate, insular, inferior temporal cortex (inferior temporal 쪽에서 entorhinal region, subiculum도 언급).", 9),
        B("**Central nucleus → brainstem** : 자율신경 반응과 관련 (앞에서 이야기한 내용).", 9),
        P("정리하면, stria terminalis와 ventral amygdalofugal pathway **두 길의 출발점과 표적을 비교**하는 것이 중요하다.", 9),
        STAR("그림과 단면으로 확인", 10),
        P("왼쪽 모식도에는 stria terminalis가 **휘어서 지나가는 경로**와 ventral amygdalofugal pathway가 나온다. 모든 화살표를 외우는 것이 아니라 "
          "두 경로가 **서로 다른 방향과 위치**로 주행한다는 점을 확인하자. 특히 stria terminalis는 미상핵과 시상 사이를 따라 길게 도는 모양이 특징이다.", 10),
        P("아래 그림은 편도체를 3차원으로 재구성한 모습과 뇌 단면이다. **Am**으로 표시된 부위가 amygdala이다. 경로의 굴곡을 그리는 것이 아니라 "
          "amygdala에서 출발해 어디로 이어지는지 추적하는 능력이 중요하다. 이 내용은 다음의 septal region과 이어진다.", 10),
        ADV("**Afferent와 efferent**, 그리고 **두 efferent 경로의 출발 핵군**(stria terminalis = corticomedial, ventral amygdalofugal = basolateral + central)을 섞지 말 것.", 7, 9),
    ], basics_title="Efferent fibers from amygdaloid complex", basics=[
        "나가는 경로는 두 가지 : stria terminalis(분계섬유줄)와 ventral amygdalofugal pathway (fugal = 밖으로, 주요 efferent).",
        "Stria terminalis : corticomedial nuclei에서 시작, caudate nucleus와 dorsal thalamus 사이로 thalamostriate vein과 함께 주행 → septal nuclei, hypothalamus, nucleus accumbens septi.",
        "Ventral amygdalofugal pathway : basolateral nuclei와 central nucleus에서 시작, 더 넓게 연결 (substantia innominata, hypothalamus, septal nuclei, nucleus accumbens septi, dorsomedial thalamus → prefrontal cortex, 여러 cortex, central nucleus → brainstem).",
    ], tables=[SlideTable(rows=[
        ["", "Stria terminalis", "Ventral amygdalofugal pathway"],
        ["출발", "corticomedial nuclei", "basolateral nuclei, central nucleus"],
        ["위치·특징", "caudate nucleus와 dorsal thalamus 사이, thalamostriate vein과 함께 주행", "더 주요한(major) efferent, 넓은 범위로 연결"],
        ["표적", "septal nuclei, hypothalamus, nucleus accumbens septi", "substantia innominata, hypothalamus, septal nuclei, nucleus accumbens septi, dorsomedial thalamus → prefrontal cortex, frontal·cingulate·insular·inferior temporal cortex, brainstem"],
    ], caption="Efferent 두 경로 비교 (강의 설명을 표로 정리)", col_widths_cm=[2.6, 6.4, 8.4])]))

    # ================================================================ Ch 2 · § 1
    top.append(T("Septal region", CH2, [11, 12, 13], [
        STAR("Septal nuclei의 위치", 11),
        P("두 번째 구조는 **septal region(septal nuclei, 사이막핵)** 이다. 육안으로 관찰하기는 쉽지 않지만 limbic system의 여러 구조와 연결되어 있어 신경로를 공부할 때 중요하다. "
          "위치는 **anterior commissure 앞쪽, 대뇌반구의 안쪽 벽, septum pellucidum의 아래쪽**이라고 정리한다.", 11),
        ADV("**paraterminal gyrus, subcallosal area**처럼 겉에서 보이는 구조가 있지만 septal nuclei는 그보다 **깊은 층**에 있다. 실습에서 표면 구조를 보며 핵이 그대로 노출되어 있다고 생각하면 안 된다. "
            "주변 구조를 기준으로 대략적인 위치를 잡고 연결 관계를 익히는 것이 현실적이다. 편도체 이야기에서 septal nuclei가 여러 번 나온 것도, 편도체와 stria terminalis·ventral amygdalofugal pathway로 연결되기 때문이다.", 11),
        STAR("Septal nuclei와 연결되는 네 곳", 12),
        P("연결되는 곳 **네 군데**와, 그 연결이 어떤 섬유로 이루어지는지를 **짝지어서** 외우자.", 12),
        B("**Hippocampus** — fornix (precommissural fibers)", 12),
        B("**Habenular nuclei** — stria medullaris thalami (실습에서도 볼 수 있으니 위치 확인)", 12),
        B("**Amygdala** — stria terminalis 또는 ventral amygdalofugal pathway (앞에서 배운 것)", 12),
        B("**Ventral tegmental area(VTA)와 hypothalamus** — medial forebrain bundle", 12),
        P("{r|이 네 쌍의 표가 septal nuclei에서 가장 중요한 부분이다.}", 12),
        STAR("Septal region의 기능", 13),
        P("이 연결들이 왜 중요할까? septal nuclei는 여러 부위와 **reciprocal**하게 연결되어 있다. reciprocal은 한 방향으로 한 번 가는 것이 아니라 **서로 정보를 주고받는** 관계라는 뜻이다. "
          "그래서 구조를 하나만 떼어 생각하지 말고 **limbic circuit 안에서** 이해해야 한다.", 13),
        B("**Medial forebrain bundle**에는 **dopamine-containing fibers**가 있다 → 쾌락·충동과 연결해서 설명할 수 있다.", 13),
        B("Septal region 자체는 eating, drinking, sexual behavior, reproduction, aggression 등 **autonomic behavioral processes**에 관여한다.", 13),
        P("운동을 수행하는 핵이라기보다 **몸의 내부 상태와 행동이 연결되는 과정**에 관여한다고 이해하자.", 13),
    ], basics_title="Septal region", basics=[
        "Septal nuclei(사이막핵)는 육안 관찰이 어렵지만 limbic system 여러 구조와 연결된다 — anterior commissure 앞쪽, 대뇌반구 안쪽 벽, septum pellucidum 아래, 표면 구조(paraterminal gyrus, subcallosal area)보다 깊은 층.",
        "연결 네 곳 : hippocampus(precommissural fornix), habenular nuclei(stria medullaris thalami), amygdala(stria terminalis / ventral amygdalofugal pathway), VTA·hypothalamus(medial forebrain bundle).",
        "Reciprocal 연결이며 medial forebrain bundle에는 dopamine-containing fibers가 있고, eating, drinking, sexual behavior, reproduction, aggression 등에 관여한다.",
    ], tables=[SlideTable(rows=[
        ["연결되는 곳", "관여하는 섬유"],
        ["Hippocampus", "fornix (precommissural fibers)"],
        ["Habenular nuclei", "stria medullaris thalami"],
        ["Amygdala", "stria terminalis 또는 ventral amygdalofugal pathway"],
        ["VTA, hypothalamus", "medial forebrain bundle"],
    ], caption="Septal nuclei의 네 가지 연결 (짝지어 암기)", col_widths_cm=[5.0, 12.4])]))

    # ================================================================ Ch 2 · § 2
    top.append(T("Nucleus accumbens", CH2, [14, 15, 16], [
        STAR("위치와 기능", 14),
        P("세 번째 구조는 **nucleus accumbens septi(사이막곁핵)** 이다. basal ganglia를 배울 때도 들은 이름이지만, 오늘은 **limbic system의 구성 요소**로 다시 만난다.", 14),
        B("**위치** : caudate nucleus의 **head**와 **putamen**이 이어지는 부위, 뇌의 비교적 앞쪽. 그림에서 caudate head, putamen을 먼저 찾고 그 아래쪽으로 이어지는 부분을 보자.", 14),
        B("**기능** : {r|중독(addiction)}. amygdala = fear, nucleus accumbens = addiction으로 연상한다.", 14),
        P("{g|하나의 핵이 한 가지 기능만 하는 것은 아니지만, 오늘 강의의 핵심 연결어를 둘로 줄이면 amygdala—fear, nucleus accumbens—addiction이다. 이 정도는 반드시 가져가자.}", 14),
        STAR("들어오는 경로와 나가는 경로", 15),
        B("**Afferent** : amygdala (stria terminalis 또는 ventral amygdalofugal pathway), hippocampus (precommissural fornix), VTA (medial forebrain bundle).", 15),
        B("**Efferent** : hypothalamus, brainstem, globus pallidus.", 15),
        P("앞에서 본 경로 이름이 반복되므로, 구조 이름 하나하나보다 **연결 관계를 묶어서** 기억하는 편이 좋다. 원자료가 이 부분을 비교적 간단히 다루었기 때문에 위에 나열한 경로를 정확히 연결하는 것을 목표로 하자.", 15),
        STAR("Amygdala와 nucleus accumbens의 대비", 16),
        P("그림을 보면 nucleus accumbens가 다른 변연계 구조와 얼마나 가까이 연결되어 있는지 알 수 있다. fornix, stria terminalis, medial forebrain bundle이 같은 모식도에 나오는 이유는 "
          "이들이 **별개의 목록이 아니라 하나의 회로**이기 때문이다.", 16),
        P("비교표에서 amygdala는 **fear 또는 aversion**의 중심, nucleus accumbens는 **joy, pleasure, addiction**의 중심으로 나온다. "
          "신경전달물질도 비교되어 있는데, 오늘은 특히 nucleus accumbens와 **dopamine**의 관련성을 기억하자.", 16),
        P("{r|Amygdala — fear, Nucleus accumbens — addiction, 그리고 dopamine-containing fibers.} 이 세 가지를 연결하면 두 부위의 기능적 차이를 이해하기 쉽다. 여기까지가 강의의 주요 이론 내용이다.", 16),
    ], basics_title="Nucleus accumbens septi", basics=[
        "위치 : caudate nucleus head와 putamen이 이어지는 부위, 뇌의 비교적 앞쪽.",
        "기능 : 중독(addiction)과 연결 — joy, pleasure와 관련되고 dopamine과의 관련성을 기억.",
        "Afferent : amygdala, hippocampus, VTA / Efferent : hypothalamus, brainstem, globus pallidus.",
    ], tables=[SlideTable(rows=[
        ["", "Amygdala", "Nucleus accumbens"],
        ["핵심 연결어", "fear (공포) / aversion", "addiction (중독) / joy, pleasure"],
        ["관련 물질", "—", "dopamine (dopamine-containing fibers)"],
        ["위치", "uncus 안쪽", "caudate head와 putamen이 이어지는 앞쪽"],
    ], caption="Amygdala vs Nucleus accumbens (강의 설명을 표로 정리)", col_widths_cm=[3.4, 6.6, 7.4])]))

    # ================================================================ Ch 3
    top.append(T("Uncus, stria terminalis, parahippocampal gyrus", CH3, [17], [
        STAR("해부 사진 1", 17),
        P("이제 실제 해부 구조를 사진으로 확인한다. 이 사진은 **e-neuroanatomy** 자료를 이용한 것이고, 실습에서 관찰할 수 있는 구조와 관찰하기 어려운 구조가 섞여 있으니 그림을 보며 방향을 잡자.", 17),
        B("**Stria terminalis** : 안쪽에서 **혈관(vein)과 같이 주행**하기 때문에 그 자국으로 위치를 알면 확인에 도움이 된다.", 17),
        B("**Uncus** : 앞에서 편도체는 uncus 안쪽에 있다고 했다. 표면 구조(uncus)와 그 안쪽의 amygdala를 연결해서 이해하자.", 17),
        B("**Parahippocampal gyrus** : 뒤에 나오는 해마 주변 구조물을 확인할 때의 기준점.", 17),
        ADV("해부 사진에서는 구조물의 크기나 색깔이 모식도와 다르다. 사진을 자주 보면서 **상대적인 위치**를 익히자.", 17),
    ], basics_title="해부 사진 (e-neuroanatomy) 1", basics=[
        "Stria terminalis는 안쪽에서 vein과 함께 주행해서 자국이 보인다.",
        "Uncus의 안쪽에 amygdala가 있다.",
        "Parahippocampal gyrus는 해마 주변 구조를 찾는 기준점이다.",
    ]))
    top.append(T("Fimbria, fornix, dentate gyrus", CH3, [18], [
        STAR("해부 사진 2 : parahippocampal gyrus를 젖힌 뒤", 18),
        P("parahippocampal gyrus를 젖힌 뒤 보이는 구조이다. 안쪽에 **튀어나온 듯한 fimbria**를 먼저 찾자.", 18),
        B("**Fimbria** : alveus가 모여 형성된 것으로 설명하며 **fornix와 이어진다.** fimbria와 fornix는 끊어진 별개 구조가 아니라 **연속되는 섬유 경로**이다.", 18),
        B("**Fornix** : 앞쪽으로 이어진다. 그중 **postcommissural fornix**는 mammillary body와 hippocampus 사이의 연결을 이해할 때 중요하다.", 18),
        B("**Hippocampal sulcus** : dentate gyrus와 hippocampus proper 사이의 **경계**.", 18),
        B("**Dentate gyrus** : 그 sulcus 주변에서 **점처럼 보이는** 형태.", 18),
        B("**Lamina terminalis** : 위치를 함께 확인.", 18),
        P("실습에서 중요한 것은 이름을 보고 실제 단면의 위치를 **찾아가는 훈련**이다. fimbria → fornix → mammillary body → hippocampal sulcus → dentate gyrus를 차례로 짚어보자.", 18),
        REF("오늘의 정리 : 어렵게 확장해서 외우기보다 {r|오늘 강조한 이름과 경로}부터 정확히 하자. (정리 내용은 앞쪽 ‘요약 정리’ 참고)", 19),
    ], basics_title="해부 사진 (e-neuroanatomy) 2", basics=[
        "Fimbria(alveus가 모인 것)는 fornix와 이어지는 연속된 섬유 경로이다.",
        "Fornix는 앞쪽으로 이어지고, postcommissural fornix는 mammillary body와 hippocampus를 연결한다.",
        "Hippocampal sulcus = dentate gyrus와 hippocampus proper의 경계, dentate gyrus는 sulcus 주변에서 점처럼 보인다.",
    ]))

    # ================================================================ appendix
    top.append(T("부록 & 검증 참고", "", [20, 21], [
        STAR("부록 : 기초의학교실과 연구자의 진로", 20),
        P("수업 내용과는 별개로, 졸업 후 진로에 대한 짧은 이야기가 있었다. 의과대학을 졸업하고 학교에 남는 경우 **임상교실**로 가는 길과 **기초의학교실**에서 연구와 교육을 중심으로 일하는 길이 있다.", 20),
        B("많은 학생이 기초의학교실에서 실제로 어떤 일을 하는지 잘 모른다 → 연구실의 일과 진로 구조에 관심을 가져보라는 취지.", 20),
        B("임상교수와 비교하면 진료 업무의 비중이 달라 연구에 더 많은 시간을 쓸 수 있는 환경이라는 점.", 20),
        B("진로의 안정성이나 군 복무와 관련한 선택지는 개인의 상황과 제도에 따라 확인이 필요하다.", 20),
        B("신경해부학 지식과는 별도의 이야기이며, 관심이 있으면 기초의학교실에 문의해도 좋다.", 20),
        STAR("검증 참고", 21),
        P("{p|이 강의록은 실제 강의 음성이나 전사가 아니라 정리본에서 역구성한 가상 40분 스크립트에서 만든 것이다. 아래 사항을 확인하고 사용하자.}", 21),
        B("원본에 반복적으로 나타나는 경로·기능·강조 지점을 중심으로 재구성한 스크립트이다.", 21),
        B("강의실 지시어(“그림을 보세요”, “외워두세요”)와 전환문은 자연스러운 전달을 위해 새로 만든 문장이다.", 21),
        B("정리본의 페이지 번호는 원본 PDF 기준이다. 표지·기출 통계 등은 교수가 실제로 말했는지 확인할 수 없어 본문에서 제외했다.", 21),
        B("진로 관련 내용은 당시 정리본의 취지만 반영했으며 현재 제도의 사실 관계를 검증하거나 보장하지 않는다.", 21),
        B("실제 40분 발화의 문자 그대로의 복원이나 정확한 음성 길이 검증 자료가 아니며, 시간 구간 표기는 구성에 사용하지 않았다.", 21),
    ]))
    return _remap(top, unit_ids, {})


if __name__ == "__main__":
    json.dump({"topics": [t.model_dump() for t in build(unit_ids_from_script(sys.argv[1]))]},
              sys.stdout, ensure_ascii=False, indent=2)
