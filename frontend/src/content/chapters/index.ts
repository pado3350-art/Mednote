// 챕터 메타데이터 레지스트리
// 새 챕터 추가 시 이 파일에만 등록하면 됩니다

export interface ChapterMeta {
  id: number
  number: number
  titleKo: string
  category: string
  categoryId: string
  /** PK 시뮬레이터 표시 여부 */
  hasPkSim?: boolean
  /** PD 시뮬레이터 표시 여부 */
  hasPdSim?: boolean
}

export const CHAPTERS: ChapterMeta[] = [
  { id: 1,  number: 1,  titleKo: '약리학 입문: 수용체와 약력학',       categoryId: 'other',          category: '기초약리학', hasPdSim: true },
  { id: 2,  number: 2,  titleKo: '약동학: 흡수, 분포, 대사, 배설',     categoryId: 'other',          category: '기초약리학', hasPkSim: true },
  { id: 3,  number: 3,  titleKo: '자율신경 약리학 개요',               categoryId: 'autonomic',      category: '자율신경계' },
  { id: 4,  number: 4,  titleKo: '콜린수용체 효능제',                  categoryId: 'autonomic',      category: '자율신경계' },
  { id: 5,  number: 5,  titleKo: '항콜린에스테라제 약물',              categoryId: 'autonomic',      category: '자율신경계' },
  { id: 6,  number: 6,  titleKo: '콜린수용체 차단제',                  categoryId: 'autonomic',      category: '자율신경계' },
  { id: 7,  number: 7,  titleKo: '아드레날린 합성, 저장, 분비',        categoryId: 'autonomic',      category: '자율신경계' },
  { id: 8,  number: 8,  titleKo: '아드레날린 효능제 및 교감신경 흥분제', categoryId: 'autonomic',    category: '자율신경계' },
  { id: 9,  number: 9,  titleKo: '아드레날린 수용체 차단제',           categoryId: 'autonomic',      category: '자율신경계' },
  { id: 10, number: 10, titleKo: '항고혈압제',                        categoryId: 'cardiovascular', category: '심혈관계' },
  { id: 11, number: 11, titleKo: '혈관확장제와 협심증 치료',           categoryId: 'cardiovascular', category: '심혈관계' },
  { id: 12, number: 12, titleKo: '심부전 약물치료',                   categoryId: 'cardiovascular', category: '심혈관계' },
  { id: 13, number: 13, titleKo: '항부정맥제',                        categoryId: 'cardiovascular', category: '심혈관계' },
  { id: 14, number: 14, titleKo: '이뇨제',                            categoryId: 'cardiovascular', category: '심혈관계' },
  { id: 15, number: 15, titleKo: '진정 수면제',                       categoryId: 'cns',            category: '중추신경계' },
  { id: 16, number: 16, titleKo: '알코올',                            categoryId: 'cns',            category: '중추신경계' },
  { id: 17, number: 17, titleKo: '항경련제',                          categoryId: 'cns',            category: '중추신경계' },
  { id: 18, number: 18, titleKo: '파킨슨병 치료제',                   categoryId: 'cns',            category: '중추신경계' },
  { id: 19, number: 19, titleKo: '마약성 진통제',                     categoryId: 'cns',            category: '중추신경계' },
  { id: 20, number: 20, titleKo: '항정신병약 및 리튬',                categoryId: 'cns',            category: '중추신경계' },
]

// Markdown 파일을 동적으로 로드하기 위한 Vite 매핑
// 새 md 파일 추가 시 여기에도 추가
export const CHAPTER_CONTENT: Record<number, () => Promise<{ default: string }>> = {
  1:  () => import('./chapter-01.md?raw') as Promise<{ default: string }>,
  2:  () => import('./chapter-02.md?raw') as Promise<{ default: string }>,
  10: () => import('./chapter-10.md?raw') as Promise<{ default: string }>,
}
