# 줄기세포를 이용한 맞춤의학 기술 개발 및 임상 적용

## 1. 요약 정리 · 시험 정리
*PPT p.1,3,9,12,24,31*

### 
- 이 한 쪽이 시험 대비용이다. 파랑은 기출(PAD)에 나온 내용이고 본문에서 다시 근거와 함께 나온다.
![강의 전체 흐름 — 본문 6개 장](outputs/stemcell/diagrams/diagram_01.png)

| 주제 | 핵심 |
|---|---|
| 치료제 발전 | small chemical → 단백질 → **항체** → **세포 치료제**(CAR-T) → 다음은 **재생 의학**(최종적으로 rejuvenation) |
| ESC vs MSC | ESC: 무한 증식, pluripotent, **윤리 문제**(학교에서 연구 불가). MSC: 지방, 골수, 제대혈 유래, multipotent, 안전. {b|ESC는 blastocyst의 inner cell mass를 배양한 세포} |
| 분화능 위계 | {b|totipotent > pluripotent(ESC, iPSC) > multipotent(MSC). 분화능이 가장 높은 것은 ESC와 iPSC}. {b|iPSC = 체세포에 야마나카 인자 4가지를 넣는 reprogramming}, {b|맞춤의학에 응용} |
| 연골 재생 방식 | **auto**(내 세포, 의료 기술, 상업화 불가) vs **allo**(치료제, 식약처 허가 필요). 카티스템(제대혈 MSC), 인보사(암세포 혼입으로 허가 취소) |
| 세포 유래 치료제 | ① **ECM**(연골 기질) ② **small molecule**(secretome, exosome, mitochondria) ③ {b|organoid(3D 세포 덩어리)} |
| MSC 임상 | 골수 MSC 무릎 주사 RCT(12 vs 12): 9개월째 통증 점수만 유의, MRI 연골 재생은 유의하지 않음 |
| 한국·미국 MSC | 한국: 2010년대 초 4개 허가 → 카티스템만 생존. 미국: {b|Ryoncil = 골수 유래 MSC, GVHD, 2024년 12월 FDA 최초 허가} |
| iPSC spheroid | 교수님 연구팀의 3가지 전략: **재료**(MSC → iPSC), **제형**(single cell → spheroid), **경로**(수술 → 주사). 제품명 MIUChon(뮤콘) |
| 임상 단계 | {b|IND 허가 = 임상시험용 초기 허가} → 1상 3명(안전성, MRI 연골 결손 감소) → 2상 30명(뮤콘 15, 위약 15). 일본: iPSC 치료제 조건부 허가 |


## 2. 치료제의 발전과 다음 단계
*PPT p.1,2,3,4,5,6*

### 
- (오늘 수업은 줄기세포의 종류, 골관절염과 재생 치료, 전임상과 임상 연구의 순서로 진행된 50분 강의입니다.)
![치료제 모달리티의 발전: 케미컬 → 단백질 → 항체 → 세포 → 재생](inputs/stemcell_figs/s01.png)
**치료제는 점점 짧은 간격으로 바뀌었다**
- small chemical(아스피린)에서 시작했다.
- 이후 **단백질**(인슐린, 백신)을 약으로 쓰게 되었다.
- 다음은 **항체**다. 특이성(specificity)으로 표적을 정확히 겨냥한다.
- 그다음이 **세포 치료제**(CAR-T)다.
- 1890년경 케미컬 → 약 100년 뒤 단백질 → 약 30년 뒤 항체 → 약 15년 뒤 세포
- CAR-T는 ‘유도 미사일’처럼 특정 물질을 강력하게 제거한다
- 아카데미아(의대), 클리닉(병원), 인더스트리의 연결이 바이오에서 중요하다
- 간격은 짧아지고 정확도와 파괴력은 높아졌다.
- 다음 단계는 파괴가 아니라 재생이다.
- 부족한 부분을 메우고 없는 장기를 새로 만드는 치료다.
- 최종 목표는 **rejuvenation**, 장기를 젊은 상태로 되돌리는 것이다.
- 즉 다음 세대 치료제는 재생 의학이 될 것이다.
- **개념 Check** 치료제 모달리티의 발전 순서는 small chemical → 단백질 → 항체 → 세포 치료제이다. (O, X) → O


## 3. ESC와 MSC
*PPT p.7,8,9,1009*

### 
![한국에서 쓸 수 있는 줄기세포: iPSC(역분화), ESC, MSC](inputs/stemcell_figs/s02.png)
**배아줄기세포(ESC)와 윤리**
- 정자와 난자가 만나(fertilization) **blastocyst**가 된다.
- 그 안의 **inner cell mass**를 꺼내 배양하면 ESC(Embryonic stem cell)다.
- 천주교는 수정 순간부터 생명으로 본다.
- 그래서 **학교에서는 ESC를 연구할 수 없다**.
- ESC는 blastocyst의 inner cell mass에서 분리해 배양한 세포이다
- ESC와 성체줄기세포(adult stem cell), 즉 MSC(Mesenchymal stem cell)를 비교하면 다음과 같다.
| ESC (배아줄기세포) | MSC (성체줄기세포) |
|---|---|
| 유래: blastocyst의 inner cell mass<br>분화능: pluripotent<br>증식: 무한 증식<br>장점: 상업적으로 유용<br>한계: **윤리 문제** | 유래: 지방(adipose tissue), 골수(bone marrow), 제대혈(cord blood)<br>분화능: multipotent<br>증식: 계대 배양하면 능력을 잃는다<br>장점: **윤리적이고 안전하다**<br>한계: 상업적으로 부족 |
- 즉 ESC는 강력하지만 윤리 문제가 있고, MSC는 약하지만 안전하다.
- 따라서 각각의 한계 때문에 교수님 연구팀은 iPSC에 집중한다.
- **개념 Check** MSC는 모든 세포 계통으로 분화할 수 있는 pluripotent 세포이다. (O, X) → X — MSC는 몇 개 계통으로만 가는 multipotent이다.


## 4. 분화능의 위계와 iPSC
*PPT p.8,9,10,30,1005,1007,1008,1011*

### 
- 줄기세포를 분화능에 따라 나누면 다음과 같다.
> **개념 정리** 분화능의 위계
> - **totipotent cell**: 세포 하나가 생명 개체가 된다
> - **pluripotent stem cell(PSC)**: 모든 계통으로 분화한다 (ESC, iPSC = Induced pluripotent stem cell)
> - **multipotent**: 몇 개 계통으로만 분화한다 (MSC)
> - totipotent는 ‘신의 영역’이라 연구자들이 부담스러워한다
- 분화능이 가장 높은 것은 pluripotent인 ESC와 iPSC이다
- 성체줄기세포(MSC)는 그보다 등급이 낮은 multipotent이다
- iPSC는 체세포에 야마나카 인자 4가지를 넣어 reprogramming(역분화)해 만든다
- iPSC는 개인의 체세포에서 만들 수 있어 맞춤의학에 응용된다
- iPSC는 개인별 약제 독성평가와 재생 치료에 응용될 수 있다
- MSC는 지방, 골수, 제대혈 유래 성체줄기세포다. iPSC는 MSC와 같은 분류가 아니다
- 야마나카 신야: 2006년 Cell에 reprogramming factor 논문, 2012년 노벨상(정형외과 의사)
- Nature에 ‘Stem cell therapy to the clinic’ 기사가 실리며 줄기세포가 임상에 들어오기 시작했다
- (외우는 법: toti(개체) > pluri(모든 계통) > multi(몇 계통).)


## 5. 퇴행성 골관절염
*PPT p.11,12*

### 
- 퇴행성 골관절염은 **연골세포의 노화**, 질적·양적 하락이다.
- 20대에 연골 상태가 가장 좋고 이후 내리막이다
- **초기**: 내과에서 진통제와 소염제로 지켜본다.
- **말기**: 정형외과에서 **인공관절 수술**을 한다.
- 그 사이 약 **20년** 동안은 다룰 방법이 없다.
- 즉 줄기세포로 이 과정을 늦추거나 되돌릴 수 있다면 혁명적 치료가 된다.
- **개념 Check** 퇴행성 골관절염의 초기에는 인공관절 수술이 일차 치료이다. (O, X) → X — 초기는 진통제와 소염제, 인공관절은 말기이다.


## 6. 연골 재생 치료의 방식: auto vs allo
*PPT p.12,13,14*

### 
![기존 연골 재생 치료: auto와 allo, 모두 한계가 있다](inputs/stemcell_figs/s03.png)
**치료제인가, 의료 기술인가**
- 내 몸의 성체줄기세포나 연골세포를 꺼낸다.
- 확장 배양한 뒤 다시 넣는다.
- 안전하고 만들기 쉽다.
- 이식 방식에 따라 나누면 다음과 같다.
| auto-transplantation | allo-transplantation |
|---|---|
| 내 세포를 꺼내 내게 다시 넣는다<br>**의료 기술**(치료제 아님)<br>규제가 적고 의사의 영역이다<br>상업화는 불가능하다 | 다른 사람의 세포를 여러 환자에게<br>**치료제** 영역이다<br>식약처 허가가 필요하다 |
- 카티스템(Cartistem): 메디포스트의 제대혈 유래 세포 치료제 — 수술로 주입하며 현재 쓰인다
- 인보사(Invossa): 품질 관리 실패로 암세포가 섞여 **품목허가가 취소**되었다 — 2017년경 허가, 식약처와 코오롱티슈진의 소송이 이어지고 있다
- 한계: 재생되어도 연골의 **품질이 낮거나 섬유화**된다.
- 또 실제로 재생되었다는 **과학적 증거**가 부족하다.
- 이렇게 세포 자체는 규제와 근거의 벽이 높아서 세포 유래 물질을 치료제로 쓰는 시도가 이루어졌다.
- **개념 Check** 자신의 세포를 꺼내 다시 넣는 auto 방식은 치료제가 아니라 의료 기술로 분류된다. (O, X) → O


## 7. 세포 유래 치료제의 세 범주
*PPT p.14,23,28,1003,1004,1006,1010*

### 
![줄기세포 유래 치료제 후보: ECM, small molecule, 3D organoid](inputs/stemcell_figs/s04.png)
**세포 치료제의 범위가 넓어졌다**
- 예전에는 single cell 치료제만 생각했다.
- 지금은 세포 유래 물질도 포함한다.
- ① **ECM**(Extracellular matrix, 세포외기질)
- ② **small molecule**(secretome, exosome, mitochondria)
- ③ **organoid**(세포 덩어리)
- organoid는 줄기세포에서 분화한 3D 세포 덩어리이다
- organoid는 장기의 구조와 기능을 모사해 약제 독성평가와 재생치료에 응용된다
- spheroid와 organoid를 구분하면 다음과 같다.
> **개념 정리** spheroid vs organoid
> - **spheroid**: 3D 세포 집합체. 교수님 연구팀의 연골 spheroid를 수업에서 강조했다
> - **organoid**: 줄기세포에서 분화한 장기 유사 3D 구조. 장기의 구조와 기능을 모사하는 3D 모사체
> - 기출 해설(2023 Q2)도 ‘organoid보다 spheroid를 강조했다’고 적었다
- 수업에서 직접 다루지 않았지만 기출에 나온 개념: 환자 유래 줄기세포로 환자의 병적 상태를 흉내 내는 기술 = recapitulation, 신장 organoid는 혈관세포 분화가 제한적이다


## 8. ECM
*PPT p.15,16*

### 
![ECM(세포외기질): 줄기세포 유래 치료제 후보](inputs/stemcell_figs/s05.png)
**ECM: 세포가 만든 기질이 세포를 돌본다**
- 연골세포는 **hyaline cartilage**(연골 기질)를 만든다.
- 이 기질이 연골세포를 오래 살게 한다.
- 연골세포의 기능도 촉진한다.
- 교수님 연구팀은 iPSC로 연골세포 덩어리를 만든 뒤 세포를 제거해 ECM만 남겼다.
- 분화 중인 연골세포에 처리했더니 연골세포 marker 발현이 증가했고
- 연골 결손에 넣었더니 결손이 잘 메꿔졌다.
- 즉 ECM 자체도 연골 재생 치료제가 될 수 있다.
- ECM을 택한 이유: 살아 있는 세포는 규제 기관이 까다롭게 본다.
- ECM은 무생물이라 규제 부담이 작다.
- 이미 연골 기질 제품이 쓰인다 — 히루안, 시노비안, 콘드란
- MegaCARTI: 기증받은 사체 연골 제품 — 국내는 법률상 불가능해 수입 연골로 개발
- **개념 Check** ECM은 살아 있는 세포가 아니므로 규제 기관이 세포 치료제보다 편하게 본다. (O, X) → O


## 9. Small molecule과 mitochondria
*PPT p.17,18*

### 
- secretome, exosome, mitochondria(미토콘드리아)처럼 세포에서 떨어져 나온 물질도 후보다.
- 세포를 넣기 어려워 차선책으로 시작했다.
- 그러나 규제 기관이 원재료 기준까지 요구해 쉽지 않다.
- mitochondria의 기능 저하는 골관절염, 알츠하이머 같은 만성 퇴행성 질환(chronic degenerative disease)과 연관된다(원인이 아니라 연관 요인).
- 교수님 연구팀은 mitochondria를 분리해 골관절염 동물 모델(MIA)의 무릎에 투여했다.
- 대조군보다 연골이 많이 개선되었고
- 성체줄기세포보다 iPSC에서 분리한 mitochondria의 효과가 더 좋았다.
- 즉 젊은 mitochondria(충전된 건전지)를 넣어 주는 것 자체가 치료가 될 수 있다.
- mitochondria 이식은 근육병증(inflammatory myopathy)에서도 효과가 보고되어 임상 연구 중이다
- **개념 Check** iPSC에서 분리한 mitochondria가 성체줄기세포 유래보다 연골 개선 효과가 좋았다. (O, X) → O


## 10. MSC 골관절염 RCT
*PPT p.19,20*

### 
- 교수님 연구팀은 골수 유래 MSC를 골관절염 환자 무릎에 주사하는 RCT(Randomized controlled trial)를 수행했다.
- 약 10년 전, 2018년부터 식약처와 협의해 2019년 첫 투여(sono-guided injection)
- 대조군 12명과 MSC군 12명을 1년 동안 관찰했다.
- 통증은 **9개월째에만** WOMAC pain과 VAS pain 점수가 유의했다.
- MRI상 연골 재생은 유의하지 않았다.
- T2 mapping으로 본 연골의 질적 변화는 약간 유리했다.
- 다만 **medial compartment에서만** p < 0.05였고 lateral compartment는 차이가 없었다.
- 즉 통증은 일부 줄었지만 연골 재생은 증명하지 못한 **절반의 성공**이었다.
- 환자를 대상으로 한 교수님의 첫 translational research였다
- **개념 Check** MSC RCT에서 MRI상 연골 재생은 통계적으로 유의했다. (O, X) → X — 통증 점수만 9개월째 유의했고 MRI 연골 재생은 유의하지 않았다.


## 11. 한국의 MSC 치료제와 Ryoncil
*PPT p.21,22,1002*

### 
![한국 줄기세포 치료제: 허가와 허가 거부](inputs/stemcell_figs/s06.png)
**한국은 MSC 강국이었다**
- 2010년대 초 MSC 치료제 **4개**가 허가되었다.
- 효과가 부족해 **카티스템만** 살아남았다.
- 이후 국가는 허가를 내주지 않는다.
- 황우석 퇴출 뒤 국가가 성체줄기세포 치료제를 밀어 주었다
- Neuronata-R: 루게릭병 MSC 치료제, 3상 마지막에 실패했다 — 코아스템켐온 주가 10분의 1, 2,000억 원 이상 투입
- 1회 주사에 약 2,000만 원인데 근거가 없으면 앞날이 불투명하다.
- 단순 MSC 치료의 미래는? “It’s a dead end”라고 볼 수 있다.
- Ryoncil은 GVHD 치료제로 미국 FDA가 허가한 최초의 줄기세포(simple MSC) 치료제이다 [참고]
- Ryoncil은 골수(bone marrow) 유래 MSC이고 2024년 12월에 승인되었다 [참고]
- 그래도 지금까지의 MSC 치료제는 ‘도토리 키재기’라고 본다.
- **개념 Check** 한국에서 허가된 MSC 치료제 중 현재까지 살아남은 것은 카티스템이다. (O, X) → O


## 12. 조직 치료제로의 이동과 경쟁사
*PPT p.23,24*

### 
![줄기세포 유래 치료제 후보: 3D organoid(세포 덩어리)](inputs/stemcell_figs/s07.png)
**single cell의 한계**
- single cell은 efficacy가 제한적이다.
- 그래서 세포 덩어리 형태의 조직 치료제로 발전한다.
- 교수님 연구팀의 제품은 연골 **spheroid**다.
- 회사 입셀(YiPSCELL), 제품명 MIUChon(뮤콘)
![연골치료제 개발 후보: MSC, 연골세포, iPSC](inputs/stemcell_figs/s08.png)
**경쟁사도 같은 방향으로 이동한다**
- auto에서 **allo**로 바꾸고 있다.
- single cell에서 **조직 제형**으로 바꾸고 있다.
- MSC에서 **pluripotent 세포**로 바꾸고 있다.
- 카티스템, 조인트스템, 카틸로이드, 카티큐어, 인보사 등
- 연골세포는 기질 안에 있을 때만 안정적인 shy한 세포다.
- ‘벌집 속 애벌레’ 비유
- 즉 국내 회사들도 교수님 연구팀이 처음 제시한 방향을 따라가고 있다.
- **개념 Check** 경쟁사들도 single cell에서 조직(spheroid) 제형으로 방향을 바꾸고 있다. (O, X) → O


## 13. 세 가지 전략: 재료, 제형, 경로
*PPT p.25,26,27,28*

### 
- 교수님 연구팀의 전략은 다음 세 가지다.
![For better cell therapy… change cell origin?](inputs/stemcell_figs/s09.png)
**① 재료: MSC → iPSC**
- multipotent한 MSC 대신 pluripotent한 iPSC를 쓴다.
- ‘5G 시대에 2G 폰’ 비유로 설명한다.
- 국내에서 iPSC를 환자에게 투여한 곳은 교수님 연구팀이 거의 유일하다.
- ESC는 파킨슨병 치료제 회사 1~2곳, 연세대 카리스바이오가 1명 투여, 국내 31명 중 30명
![For better cell therapy… different CMC?](inputs/stemcell_figs/s10.png)
**② 제형(CMC): single cell vs spheroid**
- single cell은 다루기 편하고 주사할 수 있다.
- 하지만 기질 없이 배양하면 1주일 안에 죽거나
- fibroblast로 변성된다.
- spheroid는 조직을 모사해 기능적으로 우수하다.
- 대신 다루기 어렵다.
- 즉 제형은 spheroid로, 투여는 주사로 하는 **중용**이 필요하다.
![Distinguished approaches: new cell, CMC, route](inputs/stemcell_figs/s11.png)
**③ 경로: 수술 → 주사**
- 환자들은 인공관절 수술을 두려워한다.
- 그래서 수술이 아니라 **주사**라는 접근성이 중요하다(injectable spheroid).
- 수술이 잘 안 된 환자들의 하소연이 두려움을 키운다
![United we stand, divided we fall](inputs/stemcell_figs/s13.png)
**‘뭉치면 살고 흩어지면 죽는다’**
- 연골세포를 하나씩 넣으면 취약하다.
- multicellular(cell aggregation)와 ECM을 함께 넣으면 강력해진다.
- 교수님 연구팀이 세계 최초로 개발한 개념이다.
![MIUChon = Newer formula + Stronger cell source + Easier access](inputs/stemcell_figs/s12.png)
**MIUChon(뮤콘)의 개념**
- Newer formula: spheroid
- Stronger cell source: iPSC
- Easier access: 주사
- (세 가지는 ‘재료, 제형, 경로’ 세 단어로 외웁니다.)
- **개념 Check** 연골세포는 기질에서 떼어 단독으로 배양할 때 가장 안정적이고 기능이 좋다. (O, X) → X — 기질 없이 배양하면 1주일 안에 죽거나 fibroblast로 변한다.


## 14. Spheroid 전임상 연구
*PPT p.28,29*

### 
- 교수님 연구팀은 iPSC 유래 연골 spheroid를 토끼, 비글, 돼지에 투여했다.
- spheroid 크기는 약 200 µm
- 토끼: 연골이 개선되었다.
- 비글(beagle dog): 기능이 회복되고 연골 결손이 채워졌다.
- 위약군에서는 연골 손상과 osteophyte가 나타났다.
- 채워진 연골은 개가 아니라 **사람 단백질**이었다.
- 돼지: 결손 충전과 부피 변화가 대조군보다 컸다.
- 특히 연골이 많이 망가지는 zone 1, 2에서 개선이 확실했다.
- 약 7, 8년 전부터 진행. 비글 8마리(십자인대 절단, 반월판(meniscus) 손상 모델, 1년 관찰), 돼지 4마리 vs 4마리
- 즉 투여한 세포가 직접 연골을 재생할 가능성을 보였다.
- **개념 Check** 비글 실험에서 새로 채워진 연골은 개의 단백질이었다. (O, X) → X — 사람 단백질이어서 투여한 세포가 직접 재생에 기여했음을 보여 준다.


## 15. 정리: auto/allo × MSC/iPSC
*PPT p.30*

### 
![Part 1 Summary: MSC, iPSC × auto, allo](inputs/stemcell_figs/s14.png)
**네 가지 조합**
- 교수님 연구팀은 iPSC allo, spheroid, 주사를 택했다.
- 식약처가 다뤄 보지 못한 제형이라 매우 어려웠다.
- 현재 1상 허가를 받았고 2상 30명 투여가 거의 끝났다.
- 세포 종류와 이식 방식으로 나누면 다음과 같다.
| MSC auto | MSC allo | iPSC auto | iPSC allo |
|---|---|---|---|
| 매우 쉽다<br>**의료 기술**<br>상업화 불가 | 치료제가 된다<br>규제로 난이도 상승 | 규제가 더 까다롭다<br>**약 10억 원, 2년**<br>상업성 없음 | 뱅크로 아무에게나 투여<br>**off-the-shelf**<br>상업성 있음 |
- 즉 맞춤 의학적으로는 auto가 좋지만 상업화는 allo가 맞다.
- **개념 Check** iPSC를 자기 세포로 만들어 자신에게 넣는 방식은 비용 약 10억 원과 2년이 들어 상업화가 어렵다. (O, X) → O


## 16. IND와 임상시험 결과
*PPT p.31,32,1001*

### 
- (Part 2(식약처 허가 과정)는 교수님께서 3분 만에 빠르게 넘어간 부분입니다.)
- IND(Investigational New Drug) 허가는 임상시험용으로 투여하기 위해 규제기관(식약처)에서 받는 초기 허가이다 [이해]
- IND 허가 후 3명에게 투여했다.
- 확인 필요: 스크립트(음성 변환)는 허가 2023년 8월 1일, 투여 2025년. 사람이 쓴 정리본은 IND 허가를 2024년 8월로 적었다
- 샘플 1개에 1억 원이 들었고 지금은 약 2, 300만 원 수준이다
- 1상(Phase 1)은 효과가 아니라 **부작용(안전성)**을 본다.
- 3명 모두 부작용이 없었다.
- MRI에서 연골 결손(defect size)이 줄었고
- 세 번째 환자는 연골 두께(cartilage thickness)가 연속 MRI에서 늘었다.
- MRI에서 검정 = 뼈, 하양 = synovial fluid, 회색 = 연골
- 위약 대조가 없어 효과는 말할 수 없고 탐색적 신호만 확인했다.
- 2상은 30명(뮤콘 15명, 위약 15명)이며 다음 주 마지막 투여다.
- **개념 Check** 1상 임상시험은 유효성이 아니라 안전성(부작용)을 보는 단계이다. (O, X) → O — 1상은 부작용 확인이 목적이고 위약 대조가 없어 효과는 평가하지 않는다.


## 17. 일본의 iPSC와 전망
*PPT p.33*

### 
![Break News: World 1st conditional approval for iPSC therapy](inputs/stemcell_figs/s15.png)
**일본의 iPSC 치료제 첫 허가**
- 일본은 10년 이상 iPSC에 투자했다.
- 올해 iPSC 치료제가 **품목 허가(조건부)**를 받았다.
- 심근세포 치료제와 파킨슨병 치료제로 세계 최초다.
- 척수 손상(spinal cord injury, 오카노, 게이오대), 망막변성(타카하시 마사요), 파킨슨병 연구가 진행 중
- 결론: pluripotent 줄기세포 기반 재생 치료가 여러분이 의사가 될 때 처방 목록에 들어올 것이다


## 18. QUIZ
*PPT p.12,27,30*

### 
- 다음 중 연골 재생 치료의 auto-transplantation에 대한 설명으로 가장 알맞은 것은?
- 교수님 연구팀이 더 좋은 세포 치료제를 위해 바꾼 세 가지가 아닌 것은?

