export interface SearchResult {
  id: string
  score: number
  snippet: string
  difficulty?: number
  tags?: string
}

export interface SearchResponse {
  query: string
  results: SearchResult[]
  total_time_ms: number
  k: number
}

export interface Choice {
  id: number
  label: string
  body: string
  is_correct: boolean
}

export interface Problem {
  id: number
  question: string
  answer: string
  explanation?: string
  difficulty: number
  tags?: string
  choices: Choice[]
  created_at: string
}

export interface ExamGenerateRequest {
  num_questions: number
  difficulty_ratio: Record<string, number>
  tags?: string[]
  time_limit_min: number
}

export interface ExamQuestion {
  id: number
  question: string
  choices: Choice[]
  difficulty: number
  tags?: string
}

export interface ExamResponse {
  exam_id: string
  questions: ExamQuestion[]
  time_limit_min: number
  total_questions: number
  difficulty_distribution: Record<string, number>
}

export interface ParaphraseRequest {
  text: string
  creativity: number
}

export interface ParaphraseResponse {
  original: string
  paraphrased: string
  processing_time_ms: number
}