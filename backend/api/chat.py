"""
AI 챗봇 엔드포인트 — Anthropic Claude API SSE 스트리밍
한국어 전용 약리학 튜터
"""

import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import anthropic

from core.config import settings

router = APIRouter(prefix="/api/chat", tags=["chat"])

# 한국어 전용 약리학 System Prompt
SYSTEM_PROMPT = """당신은 Katzung 약리학 교재를 전문으로 하는 한국어 약리학 튜터입니다.

[역할]
- 의대생과 약대생이 약리학 개념을 깊이 이해하도록 돕습니다.
- Katzung 약리학(Basic & Clinical Pharmacology) 교재의 내용을 기반으로 정확하고 체계적인 설명을 제공합니다.
- 임상적 연관성을 항상 포함하여 실제 진료 현장과 연결합니다.

[언어 규칙]
- 모든 답변은 반드시 한국어로 작성합니다. 영어로 질문이 들어와도 한국어로 답변합니다.
- 의학 용어는 한국어 명칭을 주로 사용하고, 처음 등장할 때 괄호 안에 영문을 병기합니다.
  예: 베타 차단제(beta-blocker), 반감기(half-life), 생체이용률(bioavailability)

[답변 형식]
- 복잡한 개념은 단계적으로 번호를 매겨 설명합니다.
- 핵심 사항은 **볼드체**로 강조합니다.
- 적절한 경우 표(markdown table)를 활용합니다.
- 약물 기전 → 임상 적용 → 부작용/주의사항 순서로 구성합니다.
- 답변 마지막에 "관련 챕터: [챕터 번호와 제목]"을 명시합니다.

[안전 지침]
- 실제 환자에 대한 처방 조언은 절대 제공하지 않습니다.
- 정보는 교육 목적임을 필요 시 명시합니다.
- 불확실한 내용은 "교재를 직접 확인하시기 바랍니다"라고 안내합니다."""


class ChatRequest(BaseModel):
    messages: list[dict[str, str]]


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """SSE 스트리밍으로 AI 응답 반환"""

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    async def generate():
        try:
            with client.messages.stream(
                model=settings.anthropic_model,
                max_tokens=2048,
                system=SYSTEM_PROMPT,
                messages=request.messages,
            ) as stream:
                for text in stream.text_stream:
                    yield f"data: {json.dumps({'text': text}, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"
        except anthropic.APIError as e:
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("")
async def chat_sync(request: ChatRequest):
    """동기 방식 응답 (스트리밍 미지원 클라이언트용)"""

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    message = client.messages.create(
        model=settings.anthropic_model,
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=request.messages,
    )

    return {"content": message.content[0].text}
