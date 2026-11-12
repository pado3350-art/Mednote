# T림프구 항원제시: MHC 유전자와 T세포 인식

**작성자 코멘트**

- 면역학 ‘T림프구 항원제시: MHC 유전자의 구성과 기능, 비전형적 T세포 인식’입니다. 스크립트 ¶1~40을 4장 11개 소절로 정리했고, 슬라이드 그림은 정리본 PDF에서 이미지만 가져왔습니다. 파랑 글씨 = 기출(PAD)에 나온 내용이고, 보라색은 검증이 필요한 부분입니다.

**먼저 볼 내용**

- 기출 18문항(2009~2022)은 MHC class 구분, 다형성 순서(B>A>C, DRB>DQB>DPB), NK세포와 class Ib, MHC restriction의 예외, CD1c에서 반복해서 나왔습니다. 앞쪽 요약의 표를 먼저 보세요.
- 교수님은 이름 암기보다 ‘왜 다른 역할을 하는가’의 연결을 강조했습니다. 다양성은 곧 peptide 결합의 기능적 다양성이라는 점입니다.

**강조점**

- MHC class 구분 = **class I은 HLA-A, B, C / class II는 HLA-DR, DP, DQ**
- - 다형성 순서: class I B > A > C, class II DRB > DQB > DPB
- 일반 T세포 반응 = **peptide + 자기 MHC**
- - 예외: alloresponse, 이식, superantigen
- NK세포와 class Ib = **HLA-C는 KIR, HLA-E는 억제 신호**
- - CD1c는 lipid 항원으로 invariant NKT cell 활성화

| 구분 | 분자 | 다형성(다양성) 순서 |
|---|---|---|
| class I | HLA-A, HLA-B, HLA-C | **[기출]** HLA-B > HLA-A > HLA-C |
| class II | HLA-DR, HLA-DP, HLA-DQ | **[기출]** DRB > DQB > DPB<br>**[기출]** beta chain 쪽에 다형성 집중 |
| class Ib | HLA-E, HLA-F, HLA-G 등 | 상대적으로 **제한적** |
| 구분 | 해당 |
|---|---|
| **[기출]** MHC restriction 적용 | **[기출]** peptide와 자기 MHC를 함께 인식하는 일반적인 T세포 반응 |
| **[기출]** **예외** | **[기출]** **alloresponse, transplantation(이식), superantigen** |
| 구분 | MHC class I | MHC class II |
|---|---|---|
| 분자 | **[기출]** HLA-A, HLA-B, HLA-C | **[기출]** HLA-DR, HLA-DP, HLA-DQ |
| 구조 | alpha chain 1개 + beta-2 microglobulin<br>→ ‘다리 하나짜리’(교수님 표현) | alpha chain과 beta chain이 짝<br>→ ‘다리 두 개짜리’(교수님 표현) |
| T세포 | **[기출]** CD8 T세포에 항원 제시 | CD4 T세포에 항원 제시 |
| 구분 | polygeny (polygenic) | polymorphism (polymorphic) |
|---|---|---|
| 뜻 | 한 개체가 서로 다른 MHC 유전자를 **여러 개** 가짐 | 같은 유전자 자리라도 집단 안에 **여러 형태의 allele**이 있음 |
| 예 | HLA-A와 HLA-B는 서로 다른 유전자 | HLA-A에도, HLA-B에도 다양한 allele |
| 수준 | 한 개체 안 | 집단 전체 |
| 분자 | 기능 | 단서 |
|---|---|---|
| **[기출]** HLA-C | **[기출]** NK세포 수용체(KIR)와 상호작용 → NK세포 억제 | **[기출]** class I이면서 class Ib로도 분류 |
| **[기출]** HLA-E | **[기출]** NK세포 억제 신호 | **[기출]** **T세포에 항원 제시 안 함** |
| HLA-F | class Ib의 중심 분자 중 하나 |  |
| HLA-G | 모체와 태아 사이의 면역 조절 |  |
## 목차

- [1. 요약 강의 지도와 기출 포인트](#topic-1)
- [1장. MHC(HLA) 유전자 영역의 구성](#chapter-1)
- [2장. MHC의 다양성: polymorphism과 polygeny](#chapter-2)
- [3장. MHC restriction, 예외 반응과 다양성의 의미](#chapter-3)
- [4장. Class Ib 분자와 비전형적 T세포](#chapter-4)
- [12. Take home messages](#topic-12)

<a name="topic-1"></a>

## 1. 요약 강의 지도와 기출 포인트

- 앞 시간에는 항원이 세포 안에서 처리되어 MHC에 올라가는 과정을 봤습니다. 이번 강의는 MHC 유전자의 구성과 기능을 먼저 보고, 끝에서 조금 특이한 T세포 인식을 다룹니다. 초점은 두 가지입니다. MHC는 왜 여러 종류인지, T세포는 실제로 무엇을 인식하는지입니다.
- 감염원의 입장에서 생각해 봅니다. 자기 단백질 조각이 MHC에 얹혀 T세포에 보이면 면역계가 자신을 알아보게 되니, 감염원은 그 경로를 피하고 싶어 합니다. 사람에게 MHC가 한 종류뿐이라면 그 결합을 피하는 돌연변이 하나가 모든 사람에게 통할 것입니다.
- 실제로는 한 사람 안에서도 여러 MHC 유전자가 발현되고(polygenic), 사람 사이에는 같은 유전자 자리의 allele 종류가 아주 다양합니다(polymorphic). 한쪽 염색체 위에 모여서 물려받는 allele의 조합은 haplotype이라고 합니다. 즉, 다양한 MHC → 감염원이 모두를 피하기 어려움이 오늘의 출발점입니다.

![강의 전체 지도: 네 부분](diagrams/diagram_01.png)


**(1) 다형성 순서 = class I은 B > A > C, class II는 DRB > DQB > DPB★ (파드)**


**(2) MHC restriction의 예외 = alloresponse, transplantation, superantigen★ (파드)**

- **[기출]** 2009학번 Q1은 시험지 스캔 이미지라 문항 내용을 읽을 수 없고, 정답은 3번이며 ‘짤’(재탕 문제)로 표시되어 있습니다.


<a name="chapter-1"></a>

## 1장. MHC(HLA) 유전자 영역의 구성

<a name="topic-2"></a>

### 1. MHC 유전자 영역의 구성: class I, II, III

**핵심 답**

- 6번 염색체의 HLA 영역이고, class I, II, III로 나눕니다.


인간의 MHC 유전자는 6번 염색체에 있습니다. 사람에서는 흔히 HLA(human leukocyte antigen)라고 부릅니다. 이 영역에 여러 유전자가 밀집해 있어서 class I, II, III 영역으로 나누어 봅니다.


![인간 HLA와 생쥐 H-2의 유전자 구조 (슬라이드)](../../inputs/tcell_figs/f_gene.png)


위 그림이 인간(HLA, 6번 염색체), 아래 그림이 생쥐(H-2, 17번 염색체)의 MHC 영역입니다. 생쥐의 class I에는 H-2D, H-2L이, class II에는 H-2A, H-2E 등이 있습니다. 나중에 실험 그림을 읽을 때 이 차이가 필요합니다.


**(1) 분자 = class I은 HLA-A, B, C / class II는 HLA-DR, DP, DQ★**


고전적 MHC class I과 class II를 견주면 아래와 같습니다. 이름을 외우기에 앞서 유전자 영역과 실제 분자의 기능을 구분해야 합니다.


> **[한 줄 구분]**
> **[기출]** 이름이 한 글자(A, B, C)면 class I, 두 글자(DR, DP, DQ)면 class II입니다(파드).


class II 영역에는 DR, DQ, DP만 있는 것이 아닙니다. 앞 시간에 본 HLA-DM과 HLA-DO도 이 영역과 관련이 있습니다. 고전적인 항원제시 class II와는 구분되지만 peptide editing과 항원제시 조절에 관여합니다. TAP처럼 항원 처리에 참여하는 분자도 MHC 영역 안에 있습니다.


문제가 ‘MHC class II 분자’를 묻는지 ‘class II region에 존재하는 유전자’를 묻는지 구분해서 읽어야 한다고 강조하셨습니다.

- **개념 Check** HLA-DR은 MHC class II에 해당한다. (O, X) → O — class II는 HLA-DR, DP, DQ이다.
- **개념 Check** HLA-E는 CD8 T세포에 바이러스 항원을 제시하는 고전적 class I 분자이다. (O, X) → X — 고전적 class I은 HLA-A, B, C이고 HLA-E, F, G는 class Ib이다.

**(2) 확대한 유전자 지도 = 사이사이에 항원 가공 유전자**


![확대한 MHC 유전자 지도: class II, III, I 영역 (슬라이드)](../../inputs/tcell_figs/f_map.png)


위 그림(슬라이드)은 유전자 지도를 확대한 것입니다. 위아래로 나뉘어 있지만 길게 이어진 하나의 영역입니다. class I, class II 유전자만 모여 있는 것이 아니라 그 사이사이에 항원을 가공하고 제시하는 유전자가 있습니다. TAP, proteasome 관련 성분, TNF가 그 예입니다.


class I 영역에는 고전적인 A, B, C 외에 HLA-E, HLA-F, HLA-G가 있습니다. 이들은 class Ib 또는 비고전적 class I이라고 하며 뒤에서 다시 나옵니다.


class III 영역에는 **[기출]** MIC-A, MIC-B가 있습니다. 면역 관련 유전자가 이렇게 한 영역에 모여 있어서, 뒤에서 나올 면역 반응의 공동 조절이 자연스럽게 이해됩니다.



<a name="topic-3"></a>

### 2. MHC 유전자 발현의 조절

**핵심 답**

- interferon이 발현을 조절하고, class II는 CIITA가 중요합니다.


감염이 생기면 여러 면역 관련 유전자의 발현이 달라집니다. interferon alpha, beta, gamma가 MHC 관련 유전자의 발현을 조절합니다(자료). 그 결과 감염된 세포가 바이러스 단백질에서 나온 peptide를 제시할 기회가 늘어납니다.


class II의 전사는 **CIITA**라는 co-activator가 조절합니다. interferon-gamma는 class II 관련 유전자 발현과 연결됩니다.


모든 조절 경로를 외울 필요는 없습니다. 항원제시 분자만 따로 만들어지는 것이 아니라 가공과 제시에 필요한 구성요소가 함께 조절된다는 큰 흐름이면 됩니다.



<a name="chapter-2"></a>

## 2장. MHC의 다양성: polymorphism과 polygeny

<a name="topic-4"></a>

### 1. polygeny와 polymorphism의 구분, 다형성의 순서

- 여기서 제일 중요한 두 단어가 polymorphism과 polygeny입니다. 앞에서 본 두 용어를 정확히 구분합니다.

![polymorphism, polygeny, 그리고 둘이 함께 있는 경우 (슬라이드)](../../inputs/tcell_figs/f_poly_types.png)


> **[한 줄 구분]**
> polygeny는 한 사람이 가진 유전자의 ‘개수’, polymorphism은 집단의 ‘버전 수’입니다.

- 이 두 층위의 다양성이 함께 작동합니다. 발현은 **codominant**여서 어머니와 아버지에게서 받은 allele이 둘 다 발현됩니다. 그러면 한 개체가 만드는 MHC 분자의 종류가 늘어나고, 한 사람의 조합이 다른 사람과 같기 어려워집니다.
- ‘한 개체의 유전자 수가 많다’와 ‘집단 전체의 allele 종류가 많다’를 바꿔 쓰지 말고 반드시 구분해서 이해하라고 강조하셨습니다.

**(1) 다형성의 순서 = class I은 B > A > C, class II는 DRB > DQB > DPB★**


![인간 MHC 분자별 다형성: 유전자 자리마다 allele 수가 다릅니다 (슬라이드)](../../inputs/tcell_figs/f_poly_bars.png)

- **[기출]** 그림에서 가장 다양한 것은 class I의 HLA-B, class II의 DRB입니다(파드, 순서는 앞쪽 요약 표).
- 다형성은 모든 MHC 분자에서 똑같이 큰 것이 아닙니다. 고전적 class I 쪽이 크고, class Ib는 상대적으로 제한적입니다. allele 개수는 시점과
- class II에서는 다형성이 **beta chain** 쪽에 집중됩니다. 이 다형성은 peptide가 들어가는 결합 부위와 관련이 있습니다. 같은 감염원의 peptide라도 사람의 MHC 종류에 따라 결합 가능성이 달라집니다.
- **개념 Check** Class I 중 다형성이 가장 높은 유전자좌는 HLA-A이다. (O, X) → X — HLA-B이다 (B > A > C).
- **개념 Check** Class II 중 가장 polymorphic한 것은 HLA-DR(DRB)이다. (O, X) → O — DRB > DQB > DPB이다.


<a name="topic-5"></a>

### 2. 다양성의 기전과 peptide 결합

**핵심 답**

- gene conversion으로 생기고, peptide 결합 부위를 바꿉니다.


이 다양성은 어디서 왔을까요? 중요한 기전은 **gene conversion**입니다. 서로 비슷한 서열의 유전자 사이에서 유전정보 일부가 바뀌면 원래와 조금 다른 형태가 만들어집니다. 감수분열 과정에서 유사 서열 사이에 일어난 변화가 MHC 다양성에 기여했다고 봅니다(자료).


![gene conversion(왼쪽)과 class I, class II의 변이 위치(오른쪽) (슬라이드)](../../inputs/tcell_figs/f_gene_var.png)


어디가 달라지는지는 그림 오른쪽에 있습니다. class I은 alpha-1, alpha-2 영역이, class II는 beta-1 영역이 peptide 결합과 관련된 다양성을 보입니다. 결합 홈의 구조가 달라지면 결합하는 peptide의 종류도 달라집니다.


그러니 MHC polymorphism은 이름의 다양성이 아닙니다. 어떤 항원을 T세포에 보여 줄 수 있는지와 직결된 기능적 다양성입니다.


즉, 결합 부위의 변이 → 결합 홈 구조 변화 → 제시하는 peptide 종류 변화 → T세포가 볼 수 있는 항원의 범위가 달라집니다.


다양성이 곧 기능적 다양성이라는 연결이 오늘의 핵심이라고 강조하셨습니다.


**(1) peptide 결합 = 전체 서열이 아니라 anchor residue와 motif**


![MHC에 결합하는 peptide의 서열 비교 (슬라이드)](../../inputs/tcell_figs/f_anchor.png)


여러 peptide가 하나의 MHC에 결합한다고 해서 전체 아미노산 서열이 같아야 하는 것은 아닙니다. 특정 위치에 비슷한 성질의 아미노산이 반복해서 나옵니다. 2번, 5번, 8번 위치가 그 예이고(자료), 이 위치에서 MHC와 중요한 접촉을 만드는 잔기를 **anchor residue**라고 합니다.


외워야 할 것은 번호가 아니라 결합의 원리입니다. MHC allele마다 선호하는 peptide motif가 있고, 같은 motif를 가진 서로 다른 peptide가 결합합니다. MHC 종류가 바뀌면 잘 결합하는 peptide의 집합도 달라집니다.


이 원리는 종양 항원 예측이나 백신 후보 peptide 선택에도 응용됩니다.



<a name="chapter-3"></a>

## 3장. MHC restriction, 예외 반응과 다양성의 의미

<a name="topic-6"></a>

### 1. MHC restriction의 개념과 발견

**핵심 답**

- peptide와 자기 MHC가 함께 맞아야 인식합니다.


T세포는 외래 peptide만 인식하지 않습니다. TCR이 맞는 peptide를 알아보아야 합니다. 그 peptide를 제시하는 MHC도 T세포가 인식하도록 교육받은 종류여야 반응합니다.


![MHC restriction: 세 가지 조합 (슬라이드)](../../inputs/tcell_figs/f_restriction.png)


위 그림(슬라이드)은 MHC restriction의 세 조합을 비교한 것입니다. 왼쪽은 자기 MHC에 맞는 peptide가 올라가 인식되는 경우입니다. 가운데는 peptide가 같아도 MHC가 달라 인식되지 않습니다. 오른쪽은 자기 MHC여도 TCR이 알아보지 못하는 peptide라 반응하지 않습니다.


그래서 T세포 인식의 대상은 분리된 peptide 하나가 아니라 peptide-MHC 복합체입니다.


지금은 기본 지식처럼 들리지만 처음 밝혀졌을 때는 중요한 발견이었습니다. 대표적인 것이 **Doherty와 Zinkernagel**의 연구입니다. 특정 항원에 반응하는 T세포는 어떤 세포에서나 반응하지 않고, 적절한 자기 MHC 환경에서 항원이 제시되어야 반응한다는 사실을 보여 주었습니다.


Doherty와 Zinkernagel의 실험도 위 그림과 같은 세 조합으로 나눠 비교한 것입니다. 항원은 같고 MHC가 다르면 반응이 없고, MHC는 같고 항원이 다르면 반응이 없으며, 둘 다 맞을 때만 반응합니다.


즉, T세포 반응은 항원과 자기 MHC 두 조건이 함께 결정합니다.



<a name="topic-7"></a>

### 2. MHC restriction의 예외: 이식 반응

**핵심 답**

- TCR의 교차 반응성 때문에 alloreactive T세포가 약 1~10%나 됩니다.


여기서 의문이 하나 생깁니다. 자기 MHC에 제한되어 반응한다면 왜 장기 이식 때는 타인의 MHC에 엄청난 반응이 나타날까요? 이 예외처럼 보이는 현상이 이식 반응과 superantigen입니다(앞쪽 요약의 예외 표, 파드).


alloresponse는 다른 개체의 MHC에 일어나는 강한 T세포 반응입니다. 같은 종 사이의 이식은 **allogeneic**, 서로 다른 종 사이의 이식은 **xenogeneic**(xenograft)이라고 합니다.


> **[한 줄 구분]**
> **[기출]** 같은 종끼리면 allogeneic, 다른 종이면 xenogeneic입니다.


자기 MHC에 반응하도록 교육받은 T세포가 왜 타인의 MHC에도 반응할까요? T세포 수용체에는 어느 정도 교차 반응성(cross-reactivity)이 있습니다. 그래서 자기 MHC와 구조가 비슷한 다른 MHC에 예기치 않게 강하게 결합할 수 있습니다.


alloreactive T cell은 전체 T세포의 약 1~10%라고 합니다.


![TCR의 CDR 부위와 MHC-peptide 복합체의 상호작용, alloresponse (슬라이드)](../../inputs/tcell_figs/f_alloresponse.png)


흉선(thymus)에서는 positive selection과 negative selection으로 자기 MHC에 적절히 반응하는 세포가 남습니다. 하지만 타인의 MHC에 대한 반응까지 모두 없어지지는 않습니다. 이식 거부반응을 이해할 때 이 점이 중요합니다.


즉, 흉선에서 자기 MHC 기준으로 교육 → TCR의 교차 반응성은 남음 → 구조가 비슷한 타인 MHC에 강하게 반응 → 이식 거부반응.


이 반응을 보는 고전적인 실험이 mixed lymphocyte reaction(MLR)입니다. MHC가 다른 두 개체의 림프구를 섞어 반응을 봅니다. 양쪽이 모두 증식하면 어느 쪽 반응인지 구별하기 어렵습니다.


그래서 한쪽은 irradiation이나 mitomycin C로 증식하지 못하게 합니다. 그러면 처리하지 않은 쪽의 반응을 볼 수 있습니다.

- **개념 Check** MHC restriction이 적용되는 것은 alloresponse이다. (O, X) → X — alloresponse, transplantation, superantigen은 MHC restriction의 예외이다.
- **개념 Check** 유전적으로 동일하지 않은 같은 종의 개체 사이의 이식은 allogeneic transplantation이다. (O, X) → O — 다른 종 사이의 이식은 xenogeneic이다.


<a name="topic-8"></a>

### 3. Superantigen

**핵심 답**

- peptide 처리 없이 MHC class II와 TCR을 연결해 많은 T세포를 활성화합니다.


정상적인 항원 제시는 peptide가 만들어져 MHC의 결합 홈에 자리하고, 특정 TCR이 그 복합체를 인식하는 과정입니다. superantigen은 다릅니다. 일반적인 peptide 처리와 결합 없이 MHC class II와 TCR을 연결해서 많은 T세포를 동시에 활성화합니다.


![bacterial superantigen과 viral superantigen (슬라이드)](../../inputs/tcell_figs/f_superantigen.png)


많은 T세포가 한꺼번에 자극되면 염증성 신호가 크게 생기고 숙주에 심한 부담이 됩니다. 특정 항원을 가진 병원체를 정교하게 없애는 반응과는 다릅니다. 핵심은 비특이적인 대규모 활성화이고, superantigen이 TCR과 MHC에 붙는 위치도 일반적인 peptide-MHC-TCR 인식과 다릅니다.


즉, peptide 처리 없이 MHC class II와 TCR을 직접 연결 → 많은 T세포가 한꺼번에 활성화 → 염증성 신호가 커져 숙주에 부담.


대표적인 예로는 **staphylococcal enterotoxin(SE)**과 **TSST-1**이 있습니다. SE는 식중독과 관련된 독소이고, TSST-1은 toxic shock syndrome과 관련된 독소입니다.



<a name="topic-9"></a>

### 4. 다시 보는 MHC 다양성의 의미

**핵심 답**

- 감염 방어 범위와 흉선에서의 T세포 선택 부담이 균형을 이룹니다.


강의 처음에 본 MHC polymorphism으로 돌아가 봅니다. 사람 집단에서 MHC가 다양하면 모든 사람이 같은 감염원 회피 전략에 취약해질 가능성이 줄어듭니다. 사례로는 EBV의 면역 회피, 특정 인구집단의 HLA 분포, 서아프리카에서 HLA-B53과 중증 말라리아의 관련성이 나옵니다(자료).


사례의 수치보다 중요한 메시지는 병원체와 숙주의 유전적 다양성이 서로 영향을 주고받는다는 점입니다.


그렇다면 MHC는 종류가 많을수록 좋을 텐데 왜 무한정 늘어나지 않을까요? 다양한 MHC는 더 많은 peptide를 제시하지만, 흉선(thymus)에서 T세포가 선택되는 조건도 그만큼 복잡해집니다. 자가 반응성과 적절한 면역 반응 사이에 균형이 필요하기 때문입니다.


즉, MHC 종류가 많을수록 제시할 수 있는 peptide는 늘지만 흉선 선택의 부담도 커져서, 둘 사이의 균형에서 멈춥니다.



<a name="chapter-4"></a>

## 4장. Class Ib 분자와 비전형적 T세포

<a name="topic-10"></a>

### 1. Class Ib 분자: HLA-E, F, G

**핵심 답**

- HLA-E, F, G가 중심이고 NK세포와 모체-태아 면역에 관여합니다.


지금까지는 고전적 MHC와 peptide 항원을 다뤘습니다. 이 틀로 설명하기 어려운 인식 방식도 있습니다. 거기에 연결된 분자를 class Ib, nonclassical MHC 또는 MHC-like molecule이라고 부릅니다. 분류 용어는 자료마다 조금 다르게 쓰이므로 기능을 함께 봅니다.


아래 네 분자를 묶는 이유는 하나입니다. 고전적 class I과 형태가 비슷하지만 다형성이 제한적인 경우가 많고, 기능이 다양하다는 점입니다. HLA-E, HLA-F, HLA-G를 중심으로 보라고 되어 있습니다(자료).


![class Ib 분자와 수용체, 생물학적 기능 (슬라이드)](../../inputs/tcell_figs/f_classIb.png)


> **[한 줄 구분]**
> **[기출]** HLA-C는 class I이면서 Ib이고, HLA-E는 Ib일 뿐 T세포에 항원을 제시하지 않습니다.

- **개념 Check** HLA-C는 NK세포의 KIR과 결합해 NK세포를 억제한다. (O, X) → O — HLA-C는 class I이면서 NK세포 수용체와 상호작용한다.


<a name="topic-11"></a>

### 2. 비전형적 T세포와 CD1

**핵심 답**

- peptide-MHC 밖 항원을 인식하는 T세포와 lipid 항원의 CD1입니다.


이 소절의 분자와 세포는 공통점이 하나 있습니다. 고전적인 peptide-MHC 틀 밖에서 항원을 다루거나 인식한다는 점입니다.


unconventional T cell로는 gamma-delta T cell, 점막과 관련된 MAIT cell, invariant NKT cell을 듭니다. 이름이 다른 만큼 인식하는 표적과 역할도 같지 않습니다.


**(1) CD1 = lipid 또는 glycolipid 항원 제시★**


> **[한 줄 구분]**
> 고전적 MHC는 peptide를, **[기출]** CD1은 lipid를 T세포에 보여 줍니다.


**[기출]** CD1은 peptide가 아니라 lipid 또는 glycolipid 항원을 제시합니다. 그래서 병원체에서 온 지질 항원을 인식하는 경로와 연결됩니다. CD1a부터 CD1e까지 여러 유형이 있습니다. **[기출]** CD1c는 invariant NKT cell을 활성화합니다.


CD1은 국가시험에 자주 나온다고 강조하셨다고 자료에 적혀 있으니, ‘CD1은 지질 항원제시’를 확실히 기억합니다.


(작성자 생각) 자료는 CD1c와 invariant NKT cell을 연결합니다. 하지만 일반적으로 invariant NKT cell의 대표 인식 분자는 CD1d이므로, 복습할 때 검증이 필요합니다.


![CD1c(왼쪽)와 CD1d(오른쪽)에 지질이 결합한 모습 (슬라이드)](../../inputs/tcell_figs/f_cd1.png)


FcRn은 MHC와 닮은 분자이지만 항원제시보다 모체의 IgG 전달과 관련된 역할을 합니다.

- **개념 Check** CD1c는 invariant NKT cell을 활성화한다. (O, X) → O — CD1은 lipid 항원을 제시한다.

**(2) gamma-delta T cell과 MAIT cell**


![gamma-delta T cell을 활성화하는 ligand (슬라이드)](../../inputs/tcell_figs/f_gdT.png)


gamma-delta T cell은 그림의 표에 나온 여러 ligand를 인식합니다. 고전적인 peptide-MHC 인식과 달리 다양한 신호를 직접 감지합니다. 수업에서는 종류가 다양하다는 정도로 넘어갔습니다.


MAIT cell은 점막 면역과 관계가 있고 미생물 유래 물질을 인식합니다. 선천면역과 적응면역 사이를 잇는 세포로 설명합니다.

- (스크립트 끝의 [검증참고] 다섯 문단(¶41–45)은 강의 내용이 아니라 자료 재구성에 대한 설명이어서 노트에 넣지 않았습니다.)


<a name="topic-12"></a>

## 12. Take home messages


**1. MHC는 polygenic + polymorphic = 항원제시 범위를 넓힘★**


**2. **[기출]** 다형성 순서: class I B > A > C, class II DRB > DQB > DPB★**


**3. **[기출]** class I은 HLA-A, B, C, class II는 HLA-DR, DP, DQ★**


**4. 일반 T세포 반응 = peptide + 자기 MHC, **[기출]** 예외는 alloresponse, 이식, superantigen★**


**5. **[기출]** HLA-C는 KIR로 NK세포 억제, CD1c는 lipid 항원으로 iNKT 활성화★**


