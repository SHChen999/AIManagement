"""SSE 流式输出 API"""
import logging
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from core.llm import init_llm_service, get_llm_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/stream", tags=["流式输出"])


class ThinkRequest(BaseModel):
    question: str
    provider: str = "qianwen"
    system_prompt: str | None = None


async def sse_generator(content_generator):
    """将 AsyncIterator 转换为 SSE 格式"""
    async for chunk in content_generator:
        yield f"data: {chunk}\n\n"
    yield "data: [DONE]\n\n"


@router.get("/think")
async def stream_think(question: str, provider: str = "qianwen", system_prompt: str | None = None):
    """
    SSE 流式输出 AI 思考过程
    
    - **question**: 用户问题
    - **provider**: LLM 提供商 (qianwen/deepseek)
    - **system_prompt**: 可选的系统提示词
    """
    try:
        llm = get_llm_service()
        init_llm_service(provider)
        
        generator = llm.think_stream(question, system_prompt)
        return StreamingResponse(
            sse_generator(generator),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            }
        )
    except Exception as e:
        logger.error(f"SSE 流式调用失败: {e}")
        async def error_gen():
            yield f"data: Error: {str(e)}\n\n"
        return StreamingResponse(error_gen(), media_type="text/event-stream")


@router.post("/think")
async def stream_think_post(request: ThinkRequest):
    """POST 版本"""
    return await stream_think(
        question=request.question,
        provider=request.provider,
        system_prompt=request.system_prompt
    )
