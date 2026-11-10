"""COMPACT note for '유전체 정밀의학 Introduction' (맞춤의학, 2026-10-12) - template templates/mom_compact.yaml.

Rebuilt after the review outputs/precision/review_vs_MOM.md:
  * two layers: 시험 정리 (2-3 pages, exam table + key summary) -> body (5 chapters, no per-§ page breaks)
  * body in 개조식 bullets / -> chains, figure + text side by side (figure_side), parallel items in columns
  * lecture logistics only as one gray line; each fact at most twice (exam layer + body)
  * factual fixes: RS <18 / 18-30 / >=31, WGS is mainly used now, cetuximab = anti-EGFR mAb,
    bevacizumab = anti-VEGF, CYP = liver metabolism, imatinib (ATP site) flagged purple
Sources: script paragraphs (발화 ¶n, kept in note.json - hidden in print) + figures cropped from the
handout screenshots (inputs/precision_figs). The drug-biomarker table is transcribed from the PMC report
table images in the handout (t01, t02); the lecture (¶89-90) says the front of that report can appear in exams.

Run:  python -m examples.precision_compact_note > outputs/precision_compact/note_authored.json
"""
from app.models import Statement
from examples.authoring import Arrow, Diagram, Group, SlideTable, T, dump

FIG = "inputs/precision_figs/"
CH1 = "Precision Medicine (정밀의료)"
CH2 = "정밀의학의 발전과 연구 기반"
CH3 = "암 정밀의학과 표적치료"
CH4 = "주요 기술"
CH5 = "임상 적용"


def _st(kind, text, g, **kw):
    kw.setdefault("origin", "both")
    return Statement(text=text, slide_refs=list(g), kind=kind, **kw)


def P(text, g=(), effort=""):
    return _st("para", text, g, effort=effort)


def B(text, g=(), level=0, effort=""):
    return _st("bullet", text, g, level=level, effort=effort)


def AUTH(text):
    """작성자 추가분(비유·암기 팁): 회색 괄호로 나온다. 사실 주장에는 쓰지 않는다."""
    return Statement(text=text, origin="author", kind="bullet")


def CHK(text, answer, g, summary="", why=""):
    """개념 Check: 같은 §의 내용만으로 풀리는 O/X. 정답은 § 끝 정답 상자에 찍힌다."""
    return _st("check", text, g, answer=answer, left_title=summary, explanations=[why] if why else [])


def CONCEPT(title, lines, g):
    return _st("concept", "", g, left_title=title, left=["- " + x for x in lines])


def H(text, g=()):
    return _st("star", text, g)


def FS(img, caption, title, lines, g=()):
    """figure + bullet box side by side; img=None -> bullet box only."""
    return _st("figure_side", caption, g, image=(FIG + img) if img else "", left_title=title,
               left=["- " + x if not x.startswith(("- ", "  ")) else x for x in lines])


def COLS(title, groups, g=()):
    return _st("columns", title, g, diagram=Diagram(kind="compare", groups=[
        Group(title=t, color=c, items=list(items)) for t, c, items in groups]))


def FIGURE(img, caption, g=()):
    return _st("figure", caption, g, image=FIG + img)


def build():
    top = []

    # ================================================================ 시험 정리 (front, 2-3 pages)
    exam_table = SlideTable(
        caption="PMC(Personalized Medicine Coalition) 리포트 표에서 옮김 (원본은 아래 그림). ★ = 강의에서 직접 설명한 약. "
                "강의: “앞에 있는 것 정도는 엄청 유명해서 시험에도 많이 나올 수 있다.”",
        col_widths_cm=[3.3, 3.6, 9.4, 1.1],
        rows=[
            ["약물(상품명)", "바이오마커", "적응증 · 의미", "강의"],
            ["Cetuximab (Erbitux)", "EGFR, **KRAS** / BRAF", "**전이성 대장암**: EGFR 발현 + **RAS 변이 없음(wild-type)** 일 때. BRAF 변이도 무반응 → {r|동반진단 후 처방}. 세포 밖 EGFR에 붙는 mAb", "★"],
            ["Imatinib (Gleevec)", "**BCR-ABL** (Ph 염색체) / PDGFR / c-KIT", "**CML**(만성기) / MDS·MPD(PDGFR 재배열) / **GIST**(c-KIT). 첫 표적치료제", "★"],
            ["Gefitinib (Iressa) · Erlotinib (Tarceva)", "**EGFR activating mutation** / KRAS", "**비소세포폐암**(EGFR 변이: 백인 약 10%, 아시아인 최대 50%). 세포 안 EGFR kinase를 막는 TKI. KRAS 변이 대장암에는 효과 없음", "★"],
            ["Crizotinib (Xalkori)", "**ALK** (EML4-ALK)", "비소세포폐암 ALK 양성 (NSCLC의 1–7%)", ""],
            ["Dabrafenib (Tafinlar)", "**BRAF V600E**", "흑색종 (절제 불가·전이)", ""],
            ["Dasatinib (Sprycel)", "Ph 염색체 / BCR-ABL", "Ph+ ALL (기존 치료 내성·불내성)", ""],
            ["Trastuzumab (Herceptin)", "**HER2 (ERBB2) 증폭**", "유방암. HER2를 막는 mAb", "★"],
            ["Bevacizumab (Avastin)", "VEGF", "**VEGF에 결합해 혈관신생 억제**", "★"],
            ["Irinotecan (Camptosar)", "**UGT1A1＊28** / ERCC1", "대장암: UGT1A1＊28 동형접합이면 호중구감소 위험 → 시작 용량 감량", ""],
            ["Warfarin", "**CYP2C9** (+ VKORC1)", "항응고(스텐트 후). 유전형에 따라 용량 결정 = **geno-dosing**", "★"],
            ["Tamoxifen", "**CYP2D6**", "유방암: CYP2D6가 활성형 **endoxifen**으로 전환 → 기능 allele이 있어야 효과", "★"],
            ["(그 밖의 표 항목)", "CD25 / HR / ER / TS·RRM1", "Denileukin diftitox(T세포 림프종) · Everolimus·Exemestane(호르몬 수용체 양성 유방암) · Gemcitabine(췌장암·폐암)", ""],
        ])
    summary_table = SlideTable(
        caption="주제별 핵심 요약 — 본문 5개 장의 순서",
        col_widths_cm=[3.6, 13.8],
        rows=[
            ["주제", "핵심"],
            ["정밀의료", "**Right treatment, right patient, right time.** 개발 측면과 **적용(선택) 측면** — 의사에게는 적용이 더 중요. 잣대 = 유전자(가장 객관적)"],
            ["바이오마커", "Clinical(GOT·GPT, 혈당, HbA1c) → Protein(IHC, ELISA) → Genetic(전좌, PCR) → **시퀀싱(NGS)** 으로 정밀의료 수준 도달"],
            ["치료제 세대", "1세대 small molecule → 2세대 바이오 신약(항체) → 3세대 **living drug**(세포·유전자 치료, 한국이 해 볼 만함)"],
            ["임상시험", "**Basket** = 약 하나·여러 질병 / **Umbrella** = 질병 하나·여러 약 / **N-of-1** = 희귀병 환자 한 명(약 ↔ 위약)"],
            ["게놈·데이터", "HGP(2003) → 사람 사이 차이 발견. UK Biobank(100만) · All of Us(50만, 다인종) · 국가통합 바이오 빅데이터(최대 100만, 구축 중)"],
            ["동반진단(CDx)", "표적치료제 처방 전 효과·내성을 가려내는 검사. 예: **RAS 변이 없음 확인 후 cetuximab**"],
            ["기술", "AI(해석 보조) · WGS/WES/패널 · single cell → **spatial** · organoid(아바타 마우스 대체) · liquid biopsy(재발 추적)"],
            ["Oncotype DX", "유방암 21-유전자 재발 점수: **RS < 18 low**(타목시펜만) · 18–30 intermediate · **≥ 31 high**(항암제 병용)"],
            ["약물유전체학", "CYP2C9 ＊1/＊1 대사 빠름 → warfarin 5–6 mg / ＊3/＊3 느림 → 1/3–1/4로 감량. Tamoxifen–CYP2D6"],
        ])
    top.append(T("요약 정리 · 시험 정리", "", [], [
        P("이 2~3쪽이 시험 대비용이다. 강의에서 시험과 연결한 것은 국시 한두 문제 수준이라는 말, 그리고 PMC 리포트 앞쪽 표(아래)이다. "
          "본문은 막히는 부분만 찾아 보면 된다.", g=[1, 89, 90]),
        DIA_FLOW(),
    ], tables=[exam_table, summary_table], role="front"))
    top.append(T("PMC 리포트 원본 표", "", [], [
        FIGURE("t01.png", "PMC 리포트 표 (1) — Cetuximab, Crizotinib, Dabrafenib, Dasatinib, Erlotinib 등", g=[89, 90]),
        FIGURE("t02.png", "PMC 리포트 표 (2) — Gefitinib, Gemcitabine, Imatinib, Irinotecan", g=[89, 90]),
    ], role="front"))

    # ================================================================ 1. Precision Medicine
    top.append(T("정밀의료의 개념", CH1, [], [
        B("{g|수업 안내: 맞춤의학 일주일 코스의 인트로덕션. 국시에는 나와도 한두 문제 수준이지만 앞으로 환자를 보려면 개념이 필요하다. 자료는 개인 학습용으로만.}", g=[1, 2, 3, 4]),
        FS("p03.png", "기존 의학(One Treatment Fits All) vs 정밀의료(More Personalized Diagnostics)",
           "정밀의료 = Right treatment, right patient, right time", [
               "치료가 들을 것으로 **정의된 환자**에게, 효과가 있을 **시점**에 치료를 제공한다",
               "동서양 모두 예전부터 추구했다: 히포크라테스 **4체액설**(체액 균형), 한국의 **체질(사상의학)**",
               "그런데도 다시 필요한 이유 = 아직 잘 안 되기 때문 → **객관화**가 핵심",
               "현실(기존 의학): 증상별 치료가 하나로 고정, 변형은 몸무게·나이 정도",
               "정밀의료: 환자 개개인의 유전자 변이·단백질 발현·바이오마커로 치료를 고른다",
           ], g=[5, 6, 7, 8, 9]),
        COLS("정밀의료의 두 측면", [
            ("① 개발", "teal", ["환자 특성에 맞는 약을 계속 만들어 낸다", "전문가 집단이 함께 하는 영역"]),
            ("② 적용(선택)", "salmon", ["이미 있는 많은 약·치료법 중 환자에게 줄 것을 고른다", "{r|의사에게 현실적으로 더 중요}", "AI 시대에 환자를 납득시키려면 필요 (‘족보’로는 부족)"]),
        ], g=[10, 11]),
        FS("p05.png", "질병 감수성 → 표적치료, GWAS로 환자별 치료 선택",
           "왜 하필 유전자인가", [
               "유전자로 환자를 그룹핑하는 것이 현재 **가장 객관적**이고, 많은 환자가 오는 병원에서 **실현 가능**해졌다",
               "그래서 강의 제목도 ‘유전자 정밀의료’. 학자가 될 필요는 없고 개념을 가지고 잘 쓰면 된다",
           ], g=[12, 13]),
        FS(None, "", "Precision Medicine Initiative (2015년, 오바마)", [
            "현대 의학 = **one-size-fits-all**(기성복) → 각자에게 맞춘 **tailoring** 치료를 하자는 정책, 코호트 구축",
            "이중나선 모형을 옆에 둔 발표 = 정책을 뒷받침할 **근거(evidence)** 가 이미 있었다는 뜻",
            "한국은 그때까지 쌓은 근거(EBM 기여)가 적어 같은 선언을 할 수 없었다",
        ], g=[41, 42]),
        CHK("정밀의료에서 의사에게 현실적으로 더 중요한 것은 새 약을 개발하는 측면이다.", "X", [10, 11],
            summary="정밀의료 = 적합한 환자에게, 적절한 시점에, 적합한 치료. 의사에게는 ‘적용(선택)’이 더 중요하다.",
            why="의사는 이미 있는 많은 약 중 환자에게 줄 것을 고른다(적용 측면)."),
    ]))
    top.append(T("바이오마커", CH1, [], [
        FS("p04.png", "바이오마커 3가지", "Biomarker: 환자를 객관적으로 가려내는 지표", [
            "① **Clinical marker**: GOT·GPT, 공복혈당, 당화혈색소 — 보편적이지만 한계 → +α 필요",
            "② **Protein marker**(주로 암): IHC, ELISA — 병리과 전문의의 판정 필요(AI가 대체 중), 대량 처리에 한계",
            "③ **Genetic marker**: CML의 염색체 전좌 → 서로 다른 염색체에 primer를 디자인한 **PCR**",
            "{r|여기까지는 정밀의료에 필요한 수준에 도달하지 못했다} → 시퀀싱이 혁명",
        ], g=[14, 15, 16, 17]),
        CHK("Clinical marker에는 GOT·GPT, 공복혈당, 당화혈색소가 있다.", "O", [14],
            summary="바이오마커 3단계: clinical → protein → genetic. 여기까지는 정밀의료에 필요한 수준에 도달하지 못했다."),
    ]))

    # ================================================================ 2. 발전과 연구 기반
    top.append(T("시퀀싱과 표적 발굴", CH2, [], [
        FS("p06.png", "Genomic sequencing → biomarker testing → pharmacogenomics", "시퀀싱의 혁명", [
            "NGS를 넘어선 시퀀싱 → 질병을 **genetic variant / mutation**으로 이해 → 처방·신약 개발·표적 발굴",
            "환자 조직·혈액에서 **전체 게놈(WGS)** 또는 **엑솜(WES)** 을 읽고, 사람 간 차이는 **GWAS**로 찾는다",
        ], g=[18, 19]),
        FS("p07.png", "유전학적 방법으로 찾은 약물 표적과 접근 방법", "표적을 찾은 뒤 막는 방법", [
            "**small molecule**(먹는 약) / **CRISPR genome editing** / **항체** / **RNA block**",
            "RNA **전달 기술**도 필요 — 코로나19 **mRNA 백신**(모더나)이 예",
            "의사가 다 개발할 수는 없다 → 전문가들의 일을 알고 **협력하는 인사이트**",
        ], g=[19, 20]),
        CHK("표적을 찾은 뒤 막는 방법에는 small molecule, CRISPR, 항체, RNA block이 있다.", "O", [19, 20],
            summary="시퀀싱 → genetic variant 이해 → 표적 발굴 → 막는 기술(약·편집·항체·RNA)"),
    ]))
    top.append(T("치료제의 세 세대", CH2, [], [
        FS("p09.png", "치료제의 세대별 발전과 세포·유전자 치료 시대", "1세대 → 2세대 → 3세대", [
            "**1세대 합성신약**: small molecule(아스피린 등). 한국 존재감 거의 없음",
            "**2세대 바이오 신약**: 항체, 재조합 단백질 → 표적치료. 아시아는 일본(빅5)만",
            "**3세대 living drug**: 세포 치료·유전자 치료 — 앞 세대는 정체기(plateau)",
            "{r|3세대는 한국이 해 볼 만하다} — CMC는 세포 치료, genome editing·mRNA 나노파티클 전달에서 리딩 그룹",
        ], g=[21, 22, 23, 24]),
        B("CMC가 세포·유전자 치료에서 강점이라는 점은 참고로만 알면 된다.", g=[24], effort="참고"),
        CHK("3세대 치료제는 항체 의약품이다.", "X", [21, 22, 23],
            summary="1세대 small molecule → 2세대 항체·재조합 단백질 → 3세대 living drug(세포·유전자 치료)",
            why="항체는 2세대이고, 3세대는 세포·유전자 치료(living drug)이다."),
    ]))
    top.append(T("정밀의료 임상시험", CH2, [], [
        COLS("Basket vs Umbrella vs N-of-1 trial (상식 차원)", [
            ("Basket trial", "teal", ["**약물이 주인공**", "표적치료제 하나가 들을 질병 A·B·C·D의 환자를 한 바구니에 모아 효과 검증", "유전자 변이를 표적으로 만든 약 중심"]),
            ("Umbrella trial", "blue", ["**환자(질병)가 주인공**", "폐암 하나의 주요 변이 5가지에 각각 약을 적용해 비교", "우산 아래 여러 약 중 잘 맞는 것 찾기"]),
            ("N-of-1 trial", "salmon", ["**희귀병 환자 한 명**", "환자를 모으기 힘들 때 한 사람에게 약 ↔ 위약을 번갈아 주어 비교", "자기 자신이 대조군"]),
        ], g=[25, 26, 27, 28, 29]),
        B("{g|이번 코스: 세포 치료(상용화·스핀오프), 나노 메디슨(RNA 전달), AI, 암 유전체, 임상 검사, 통계, 퇴행성 신경질환, AI 신약 개발·virtual screening, genome editing, ELSI.}", g=[30, 31]),
        B("임상시험 3종은 상식 차원에서 설명했다 — 개념 구분만 알면 된다.", g=[25], effort="참고"),
        AUTH("바구니(basket) = 약 하나에 여러 질병, 우산(umbrella) = 질병 하나에 여러 약, N-of-1 = 환자 한 명으로 외우면 편하다."),
        CHK("Basket trial은 하나의 약을 여러 질병의 환자에게 적용해 효과를 검증한다.", "O", [27],
            summary="Basket = 약 중심 / Umbrella = 질병 중심 / N-of-1 = 환자 한 명"),
    ]))
    top.append(T("인간 게놈 프로젝트와 바이오 빅데이터", CH2, [], [
        FS("p08.png", "99.9% 같고 일부가 다르다 — 개인별 차이와 정밀의료", "Human Genome Project (2003)", [
            "사람의 유전자는 같지만 **100%는 아니다** — 이것을 알게 된 것이 HGP",
            "2003년 미·영 정상이 해독 발표(99%~99.5%)",
            "가장 큰 소득 = **사람 사이의 차이**를 안 것 → personalized medicine의 출발",
            "{p|차이의 크기는 강의에서 0.5%, 그림에서 0.1%로 다르게 제시됨 — 자료마다 다름}",
        ], g=[32, 33, 34, 35]),
        COLS("나라별 바이오 빅데이터", [
            ("UK Biobank (영국)", "teal", ["**100만 명**, 한국보다 약 20년 앞섬", "NHS(국가 100% 책임) 덕분에 모집 수월", "유전체 + 대사체·단백질체(멀티 오믹스) + 임상·라이프로그", "전 세계 연구자가 가장 많이 쓰는 리소스"]),
            ("All of Us (미국)", "blue", ["약 **50만 명**", "오믹스 + 라이프스타일 + 의무기록·환경", "**다인종(multi-race)**"]),
            ("국가통합 바이오 빅데이터 (한국)", "salmon", ["3~4년 전 시작, **최대 100만 명**", "이유: 영·미 자료에 **동아시아인 데이터가 부족**", "지금은 ‘곳간을 채우는 시기’, 앞으로 활용"]),
        ], g=[36, 37, 38, 39, 40]),
        CHK("UK Biobank는 약 100만 명 규모이고, 한국은 동아시아인 데이터가 부족해 국가 사업을 시작했다.", "O", [36, 39, 40],
            summary="나라별 바이오 빅데이터: 영국 100만, 미국 50만(다인종), 한국 최대 100만(구축 중)"),
    ]))

    # ================================================================ 3. 암 정밀의학과 표적치료
    top.append(T("암 치료의 발전", CH3, [], [
        FS("p13.png", "암 치료 유형: 점점 더 정밀한 표적치료로", "Chemotherapy에서 표적치료까지", [
            "① **Chemotherapy**(5-FU, 백금): 정밀하지 않음 — 암과 환자가 함께 손상(탈모 등)",
            "② **Hormone therapy**: 비뇨생식기암에서 호르몬 차단",
            "③ **Epigenetic modifiers**: 혈액암의 후성유전 조절 차단",
            "④ **Immune checkpoint inhibitor**: 면역감시 회피(체크포인트)를 부순다",
            "⑤ **Angiogenesis inhibitor**: 암으로 가는 혈관을 막는다",
            "⑥ **Adoptive immunotherapy**: CAR-T",
            "⑦ **Therapeutic antibodies** · ⑧ **Cell signaling inhibitors**(imatinib, gefitinib)",
        ], g=[43, 44, 45]),
    ]))
    top.append(T("3-1. Philadelphia chromosome → Gleevec", CH3, [], [
        FS("p14.png", "Philadelphia chromosome과 Gleevec — 첫 표적치료제", "CML과 imatinib", [
            "**23쌍** 염색체를 중기(metaphase)로 고정해 보다가 약 40년 전 발견: **9번·22번 long arm 전좌**(필라델피아 염색체)",
            "전좌 → **BCR–ABL** 융합 → BCR 프로모터가 **ABL kinase** 자극 → 과활성 → **CML**",
            "**Gleevec(imatinib)**: kinase에 먼저 붙어 기질 결합을 막는 경쟁 물질 → 활성 소실",
            "표적치료의 문을 연 **첫 breakthrough**",
            "{p|강의는 ‘기질이 붙는 자리와 경쟁’이라고 설명. 교과서에서 imatinib은 ATP 결합 부위를 막는 억제제 — 확인 필요}",
        ], g=[46, 47]),
        AUTH("Gleevec은 기질이 앉을 자리를 먼저 차지해 버리는 ‘자리 선점’ 약으로 기억하면 쉽다."),
        CHK("필라델피아 염색체는 9번과 22번 염색체의 전좌로 BCR–ABL이 생긴 것이다.", "O", [46, 47],
            summary="BCR–ABL 과활성 → CML → Gleevec(imatinib)이 첫 표적치료제"),
    ]))
    top.append(T("3-2. EGFR → cetuximab, gefitinib · erlotinib", CH3, [], [
        FS("p17.png", "EGF·VEGF 신호와 downstream pathway(RAS, RAF …)", "EGFR과 두 종류의 약", [
            "위장관·폐·유선 등 몸을 덮는 **상피세포**의 EGFR 변이 → downstream 활성 → 과증식 → 암",
            "상피세포는 계속 떨어지고 새로 나야 함 → 이를 돕는 수용체가 과발현·증폭되면 암",
            "**Cetuximab(Erbitux)**: 세포 밖 **EGFR에 붙는 mAb** — 전이성 대장암",
            "**Gefitinib · Erlotinib**: 세포 안 **EGFR kinase를 막는 TKI** — 비소세포폐암",
        ], g=[48, 49]),
        FS(None, "", "그런데 왜 재발할까? → 동반진단의 출발", [
            "EGFR을 막았더니 드라마틱하게 듣다가 **환자의 절반 정도에서 재발**",
            "원인: **downstream(RAS, RAF)** 에 처음부터 변이가 있으면 위를 막아도 신호가 핵으로 계속 전달",
            "그래서 비싼 약을 마구 쓰지 않고 **downstream이 clear한지 확인(verify)한 뒤** 처방",
            "실제로 진단검사의학과에서 **RAS·BRAF 변이**를 먼저 스크리닝 → indication이 되는 환자만 처방",
            "{p|강의는 cetuximab·gefitinib을 함께 말했지만, RAS 검사는 대장암 cetuximab의 조건이고 gefitinib은 폐암의 EGFR 변이가 조건(위 표 참고)}",
        ], g=[51, 52, 53, 54, 55, 56]),
        CONCEPT("Cetuximab vs Gefitinib·Erlotinib", [
            "**Cetuximab**: 세포 밖 EGFR에 붙는 항체(mAb) — 전이성 대장암",
            "**Gefitinib · Erlotinib**: 세포 안 EGFR kinase를 막는 TKI — 비소세포폐암"], [48, 56]),
        AUTH("수도꼭지(EGFR)를 잠가도 아래 배관(RAS·RAF)이 이미 터져 있으면 물은 계속 흐른다."),
        CHK("EGFR을 막아도 downstream(RAS, RAF)에 변이가 있으면 신호가 계속 전달되어 효과가 없다.", "O", [53],
            summary="EGFR 차단제는 downstream이 정상(변이 없음)일 때만 듣는다"),
    ]))
    top.append(T("동반진단 (Companion Diagnostics)", CH3, [], [
        FS("p16.png", "동반진단(CDx)과 약물 공동 개발", "Companion Diagnostics (CDx)", [
            "처방과 **동시에** 시행해 효과 있을 환자, 나중에 효과가 없어질 환자를 **미리 가려내는 검사**",
            "임상 표현: “○○ 검사의 동반진단 결과 변이가 없어 처방 indication이 되었습니다”",
            "{r|대표 예: 전이성 대장암 — RAS 변이 음성이어야 cetuximab}",
        ], g=[57, 58]),
        FS("p20.png", "Paradigm shift in oncology — 장기(anatomy)에서 분자 경로로", "종양학의 패러다임 전환", [
            "예전: chest PA, mammography, CT, endoscopy 중심",
            "지금: 여기에 **BCR-ABL, EGFR, HER2, BRAF, EML4-ALK** 등 유전자 검사를 더해 indication을 확인한 뒤 치료",
        ], g=[59]),
        B("동반진단이 무엇을 뜻하는지 임상에서 듣고 알아볼 수 있으면 된다.", g=[57], effort="이해"),
        CHK("동반진단은 치료제 처방이 끝난 뒤에 효과를 확인하는 검사이다.", "X", [57, 58],
            summary="동반진단 = 처방과 동시에 시행해 처방 대상을 가려내는 검사. 예: RAS 변이 음성 → cetuximab",
            why="처방과 동시에 시행해 효과가 있을 환자, 나중에 효과가 없어질 환자를 미리 가려낸다."),
    ]))
    top.append(T("3-3. HER2 → Herceptin · 3-4. VEGF → Bevacizumab", CH3, [], [
        FS("p18.png", "HER2 증폭 유방암", "HER2 → Herceptin(trastuzumab)", [
            "유전자가 100배·1000배로 늘어나는 **증폭(amplification)** → HER2 과발현 → 유방암",
            "단백질·유전자 검사로 확인 → HER2를 막는 mAb **Herceptin**",
        ], g=[49]),
        FS("p19.png", "Bevacizumab과 VEGF 신호", "VEGF → Avastin(bevacizumab)", [
            "암이 자라려면 혈관이 필요 → **VEGF에 결합해 혈관신생을 억제**",
        ], g=[50]),
    ]))
    top.append(T("CAR-T (참고 수준)", CH3, [], [
        FS("p21.png", "CAR-T 치료: 채혈 → 제작 → 주입", "CAR-T", [
            "T cell에 **CAR**(chimeric antigen receptor)를 넣어 **종양 특이 항원**을 공격하게 함 — 혈액내과에서 자주 듣는 치료",
            "CAR는 인공 설계물 → genetic engineering, CRISPR, 전달 기술이 필요",
            "한국 현황: 환자 T cell을 **미국 회사로 air shipping** → 제작 후 받아서 주입. 번거로워서 국내 제작(construct 기술 도입)을 추진 중",
        ], g=[45, 60, 61]),
        B("CAR-T는 참고하는 수준으로 알면 된다.", g=[60], effort="참고"),
        AUTH("CAR-T는 환자의 T cell에 ‘표적 탐지기’(CAR)를 달아 되돌려 보내는 치료로 기억하면 된다."),
    ]))

    # ================================================================ 4. 주요 기술
    top.append(T("AI와 멀티 오믹스", CH4, [], [
        FS("p24.png", "AI가 정밀의료를 바꾸는 방식", "AI-assisted medicine", [
            "one-fit-all 시대는 갔지만, 지놈·메타볼롬·마이크로바이옴·프로테옴을 의사가 **직접 통합 해석하기는 어렵다**",
            "예전: 바이오인포매티션과 협업(시간이 걸림) → 지금: **AI**가 해석을 돕는다",
            "쓰임: **약물 표적 탐색**, 환자 **모니터링**(혈압·혈당, 집 PC·의사 데스크탑에서), **조기 발견**, **원인 유전자**, **이질성**",
            "지금은 이행기 — 앞으로는 AI를 안 쓰면 이상한 시대, 잘 쓰는 현명함이 필요",
        ], g=[62, 63, 64, 65, 66]),
        CHK("AI는 해석을 직접 할 필요가 없도록 의사를 대체한다.", "X", [63, 64, 66],
            summary="AI는 방대한 데이터의 해석을 돕는 도구 — 잘 쓰는 판단은 의사의 몫",
            why="AI가 해석을 돕지만, 이를 잘 쓰는 현명함이 의사에게 필요하다."),
    ]))
    top.append(T("NGS의 세 방식", CH4, [], [
        FS("p25.png", "Whole genome · whole exome · targeted sequencing", "얼마나 읽을 것인가", [
            "**WGS**: 30억 쌍 전체 — {r|요즘은 시퀀싱이 빨라 엑솜을 골라내는 것이 더 번거로워져 그냥 다 읽는다}",
            "**WES**: 엑솜만 골라 읽기 (예전 연구에서 주로 사용)",
            "**Targeted(패널)**: 암 치료에 필요한 일부만, 엑솜의 약 1/1000",
        ], g=[67]),
        B("NGS 세 방식의 구분은 참고로 알면 된다.", g=[67], effort="참고"),
        CHK("요즘은 시퀀싱이 빨라져 엑솜만 골라내기보다 전체 게놈을 읽는 방식을 주로 쓴다.", "O", [67]),
    ]))
    top.append(T("Single cell → Spatial transcriptomics", CH4, [], [
        FS("p26.png", "Single-cell transcriptome", "Single cell — 평균값의 한계를 넘다", [
            "침생검 조직 = 여러 세포의 합집합 → **평균값(mean data)** 만 알 수 있음",
            "**fluidics** 기술로 세포를 하나씩 띄워 특성 파악",
            "비유: ‘베리 주스가 맛있다’ → ‘딸기·블랙베리가 맛있다’를 구분",
            "한계: 떠 있는 세포라 **조직 안 위치를 모른다**",
        ], g=[68, 69, 70]),
        FS("p27.png", "Spatial transcriptomics", "Spatial transcriptomics — 위치까지", [
            "조직의 **2·3차원 상태를 유지**한 채 세포 하나하나를 본다",
            "각 세포가 조직의 어느 부위인지 알 수 있다 (세미나에 자주 나오는 이름)",
        ], g=[71]),
        B("Spatial transcriptomics는 이름을 알아보는 정도면 된다.", g=[71], effort="참고"),
        CHK("Single-cell transcriptome는 세포가 조직의 어느 위치에 있는지도 알려 준다.", "X", [70, 71],
            summary="single cell: 세포별 특성(평균값의 한계 극복) → spatial: 조직 안 위치까지",
            why="위치 정보를 더한 것이 spatial transcriptomics이다."),
    ]))
    top.append(T("Organoid · Liquid biopsy", CH4, [], [
        FS("p28.png", "Patient-derived organoid (3D culture)", "Organoid", [
            "투여 전 인체를 모사한 모델에서 약을 먼저 스크리닝해야 한다",
            "5년·10년 전 주목받은 **아바타 마우스**는 반응이 느려 실패 (환자를 기다리게 할 수 없음)",
            "장기·조직 일부를 **배양**한 유사 장기(-oid = 모사)로 약효 확인",
        ], g=[72, 73]),
        FS("p29.png", "Liquid biopsy", "Liquid biopsy", [
            "병소에서 떨어져 나와 **혈액**을 떠도는 미세한 변화를 검출 (기술은 약 98% 준비)",
            "아직 루틴은 아니지만, 수술 후 재발 확인을 **CT·침생검 대신 피검사**로 하게 될 것",
        ], g=[74]),
    ]))

    # ================================================================ 5. 임상 적용
    top.append(T("Oncotype DX", CH5, [], [
        FS("p30.png", "Oncotype DX 21-gene recurrence score (Paik et al., NEJM 2004)", "유방암 재발 점수(RS)", [
            "임상 적용 예는 데이터가 충분히 쌓인 10~15년 전 것들이다. **백순명 교수** 등(연세대 졸업, MD 앤더슨 병리과): 유방암에서 알려진 유전자(증식·호르몬 수용체·침윤)의 발현에 가중치를 주어 **공식(formula)** 을 만듦(NEJM, 2004년) → 상용화",
            "{r|RS < 18 low · 18–30 intermediate · ≥ 31 high} (그림 기준. 강의는 ‘18 이하’로 말함)",
            "low: 항암제를 세게 쓰지 않고 관찰 + 최소 치료(호르몬제)로 10년 이상 생존",
            "검증(JCO): low RS는 tamoxifen 단독 ≈ tamoxifen + chemo(95% 이상 생존)",
            "high RS는 tamoxifen 단독이면 생존율 50% 이하 → **항암제 병용**의 이득이 큼",
        ], g=[75, 76, 77, 78, 79, 80]),
        AUTH("RS는 재발 위험 점수표 — 낮으면 약을 덜고, 높으면 더한다."),
        CHK("Oncotype DX에서 RS 31 이상은 high risk이다.", "O", [77], summary="RS < 18 low · 18–30 intermediate · ≥ 31 high"),
    ]))
    top.append(T("약물유전체학 — CYP450과 warfarin, tamoxifen", CH5, [], [
        FS("p32.png", "CYP2C9 유전형별 warfarin 하루 용량", "Warfarin과 CYP2C9 (geno-dosing)", [
            "타고난 유전형이 임상에서 가장 많이 쓰이는 곳 = **약 처방(pharmacogenomics)**",
            "**CYP450**: 몸에 들어온 수천 가지 물질을 **간에서 대사**해 배출 → 형태가 수백~수천 가지",
            "Warfarin: 스텐트 시술 후 혈소판·적혈구가 붙어 다시 좁아지는 것을 막는 항응고제",
            "체중(예: 70kg)만 보고 같은 용량을 줬는데 어떤 사람은 **출혈**, 어떤 사람은 **다시 막힘** → 원인은 CYP2C9",
            "**＊1/＊1** 대사 빠름 → 5–6 mg / **＊3/＊3** 대사 느림·체내 잔류 → **1/3–1/4로 감량** (VKORC1도 함께)",
            "FDA: 유전형을 보고 용량을 정하라 = **geno-dosing**",
        ], g=[81, 82, 83, 84, 85, 86, 87]),
        FS("p33.png", "Tamoxifen 대사: CYP2D6 → endoxifen", "Tamoxifen과 CYP2D6", [
            "Tamoxifen은 **CYP2D6**에 의해 활성형 **endoxifen**으로 바뀌어 작용 (그림)",
            "그래서 유전형에 따라 쓸지 말지가 정해질 수 있다(indication)",
        ], g=[88]),
        AUTH("＊3/＊3은 배수구가 느린 싱크대 — 같은 양을 부어도 물이 차오른다."),
        CHK("CYP2C9 ＊3/＊3형은 warfarin 대사가 느려 용량을 줄인다.", "O", [86, 87],
            summary="같은 체중·같은 용량인데 반응이 다르다 → 유전형(CYP2C9)으로 용량을 정한다(geno-dosing)"),
    ]))
    top.append(T("참고자료", CH5, [], [
        B("**PMC 리포트**(Personalized Medicine Coalition, 무료 PDF): 현장에서 쓰는 제품과 indication 정리 — 앞쪽 표는 시험 정리에 옮김", g=[89, 90]),
        B("더 공부하려면 **EMM**(Experimental & Molecular Medicine) 스페셜 이슈", g=[91]),
        B("{g|마지막 출석 확인(개인정보라 생략), 질문은 따로.}", g=[92]),
    ]))
    top.append(T("QUIZ", CH5, [], [
        _st("quiz", "전이성 대장암 환자에게 cetuximab을 처방하기 전에 시행하는 동반진단으로 가장 알맞은 것은?", [56, 57, 58],
            options=["① RAS 변이가 없는지 확인한다", "② HER2 증폭을 확인한다", "③ BCR–ABL 전좌를 확인한다",
                     "④ CYP2C9 유전형을 확인한다", "⑤ Oncotype DX 재발 점수를 계산한다"],
            answer="① RAS 변이가 없는지 확인한다",
            explanations=["① RAS 변이가 없어야 cetuximab이 듣는다 (정답)", "② HER2 증폭은 유방암의 Herceptin 대상이다",
                          "③ BCR–ABL은 CML과 Gleevec이다", "④ CYP2C9는 warfarin 용량 결정에 쓴다",
                          "⑤ Oncotype DX는 유방암의 재발 점수이다"]),
        _st("quiz", "warfarin을 체중에 맞춰 투여했는데 출혈이 멈추지 않는 환자의 CYP2C9 유전형으로 가장 알맞은 것은?", [84, 85, 86, 87],
            options=["① ＊1/＊1", "② ＊3/＊3", "③ 유전형과 무관하다"],
            answer="② ＊3/＊3",
            explanations=["① ＊1/＊1은 대사가 빨라 체내에 남는 양이 적다", "② ＊3/＊3은 대사가 느려 체내 농도가 높게 유지된다 (정답)",
                          "③ 같은 용량에도 반응이 다른 원인이 유전형이다"]),
    ]))
    return top


def DIA_FLOW():
    return _st("diagram", "강의 전체 흐름 — 본문 5개 장", [1, 5, 14, 43, 62, 75], diagram=Diagram(
        kind="flow", arrows=[Arrow(src=i, dst=i + 1, label="") for i in range(4)], groups=[
            Group(title="① 정밀의료", color="teal", items=["right patient · drug · time", "적용(선택)이 핵심"]),
            Group(title="② 발전·기반", color="blue", items=["마커 → 시퀀싱", "약 3세대 · 임상시험", "바이오뱅크"]),
            Group(title="③ 암 표적치료", color="salmon", items=["Gleevec · EGFR", "HER2 · VEGF", "{r|동반진단}"]),
            Group(title="④ 기술", color="amber", items=["AI · NGS", "single cell · spatial", "organoid · liquid"]),
            Group(title="⑤ 임상 적용", color="violet", items=["Oncotype DX", "CYP2C9 · CYP2D6"]),
        ]))



if __name__ == "__main__":
    import sys

    topics = build()
    for t in topics:  # script-only: the topic cites every paragraph its statements cite
        t.slide_numbers = sorted({r for sts in t.sections.values() for st in sts for r in st.slide_refs})
    dump(topics, sys.stdout)
