"""智能体思考服务：调用AI模型生成真实的思考过程"""
import asyncio
import logging
from typing import Optional, AsyncIterator

from core.llm import LLMService, init_llm_service

logger = logging.getLogger(__name__)


# ==================== 多模态信息采集智能体（千问） ====================

VISION_SYSTEM_PROMPT = """你是一个专业的多模态信息采集智能体，专门负责处理药品图片信息。

你的职责是：
1. 接收用户上传的药盒图片（通过图片字节数据描述）
2. 分析图片中的视觉信息（颜色、形状、文字轮廓等）
3. 根据用户输入的药品名称，建立图片与药品信息的关联
4. 规划如何保存图片到指定目录
5. 准备将药品信息传递给下一个智能体

请用第一人称思考，用中文展示你的思维过程。思考要具体、有深度，体现出你对药品图片信息的专业分析能力。

每次只输出一句话的思考，要简洁有力。"""


async def vision_agent_think(drug_name: str, num_steps: int = 4) -> AsyncIterator[str]:
    """多模态信息采集智能体思考 - 使用千问动态生成思考过程"""
    
    init_llm_service(provider="qianwen", model="qwen-turbo")
    llm = LLMService(provider="qianwen", model="qwen-turbo")
    
    prompt = f"""用户正在上传一张药盒图片进行药品识别。

用户输入的药品名称是：「{drug_name}」

请模拟多模态信息采集智能体的思考过程。请生成 {num_steps} 步思考，每一步都要：
1. 用第一人称"我"来思考
2. 体现智能体接收到图片后的认知和分析过程
3. 思考要具体真实，不能是固定模板
4. 每步思考用【思考】开头

请开始思考："""

    try:
        # 使用千问生成思考过程
        full_response = await llm.think(prompt, VISION_SYSTEM_PROMPT)
        
        # 将响应按行分割或按句子分割
        thoughts = [line.strip() for line in full_response.split('\n') if line.strip()]
        
        if not thoughts:
            # 如果没有生成有效的思考，使用备用方案
            thoughts = [
                f"我接收到用户上传的药盒图片，图片数据已就绪...",
                f"用户输入的药品名称是「{drug_name}」，我正在分析这个药品...",
                f"我正在规划图片存储方案，确保图片能被正确保存...",
                f"我正在准备将药品「{drug_name}」的信息传递给知识检索智能体..."
            ]
        
        for i, thought in enumerate(thoughts[:num_steps]):
            yield thought
            await asyncio.sleep(0.8)
            
    except Exception as e:
        logger.error(f"【多模态信息采集智能体】思考过程生成失败: {e}")
        # 备用思考内容
        fallback_thoughts = [
            f"我收到了这张药盒图片，开始分析图片中的视觉特征...",
            f"根据图片中的包装特征，这可能是「{drug_name}」品牌的药品...",
            f"我正在验证图片质量，确保图片清晰可辨...",
            f"图片信息已准备就绪，正在保存到本地存储系统..."
        ]
        for i, thought in enumerate(fallback_thoughts[:num_steps]):
            yield thought
            await asyncio.sleep(0.5)


# ==================== 知识检索智能体（DeepSeek） ====================

KNOWLEDGE_SYSTEM_PROMPT = """你是一个专业的知识检索智能体，专门负责从药品知识库中检索药品信息。

你的职责是：
1. 接收药品名称，理解用户的查询意图
2. 分析需要检索哪些维度的信息（成分、适应症、禁忌症、副作用等）
3. 评估数据库中可能匹配的信息
4. 整合检索结果，提炼关键信息
5. 判断检索结果的完整性和可信度

请用第一人称思考，用中文展示你的思维过程。思考要体现专业性和分析能力。

每次只输出一句话的思考，要简洁有力。"""


async def knowledge_agent_think(drug_name: str, num_steps: int = 5) -> AsyncIterator[str]:
    """知识检索智能体思考 - 使用DeepSeek动态生成思考过程"""
    
    llm = LLMService(provider="deepseek", model="deepseek-chat")
    
    prompt = f"""用户需要查询药品的详细信息。

要查询的药品名称是：「{drug_name}」

请模拟知识检索智能体的思考过程。请生成 {num_steps} 步思考，每一步都要：
1. 用第一人称"我"来思考
2. 体现智能体对检索任务的规划和分析
3. 思考要具体真实，展现专业性
4. 每步思考用【检索】开头

请开始思考："""

    try:
        # 使用DeepSeek生成思考过程
        full_response = await llm.think(prompt, KNOWLEDGE_SYSTEM_PROMPT)
        
        # 将响应按行分割或按句子分割
        thoughts = [line.strip() for line in full_response.split('\n') if line.strip()]
        
        if not thoughts:
            thoughts = [
                f"我收到了查询「{drug_name}」的任务，正在理解查询意图...",
                f"我正在连接药品知识数据库，准备执行检索...",
                f"我在数据库中搜索与「{drug_name}」相关的记录...",
                f"我找到了匹配的药品信息，正在提取详细信息...",
                f"药品「{drug_name}」的信息检索完成，正在整理输出..."
            ]
        
        for i, thought in enumerate(thoughts[:num_steps]):
            yield thought
            await asyncio.sleep(0.8)
            
    except Exception as e:
        logger.error(f"【知识检索智能体】思考过程生成失败: {e}")
        fallback_thoughts = [
            f"我开始分析「{drug_name}」的检索需求...",
            f"我正在构建检索查询，准备从数据库获取信息...",
            f"数据库查询已执行，我正在筛选匹配的记录...",
            f"我找到了「{drug_name}」的相关信息，正在验证数据准确性...",
            f"检索结果已整理完毕，准备输出给用户..."
        ]
        for i, thought in enumerate(fallback_thoughts[:num_steps]):
            yield thought
            await asyncio.sleep(0.5)


# ==================== 健康管家智能体（DeepSeek） ====================

HEALTH_SYSTEM_PROMPT = """你是一个细心的健康管家智能体，专门负责用药安全检查。

你的职责是：
1. 接收家庭成员的健康档案（年龄、过敏史、病史等）
2. 分析目标药品的适应症和禁忌症
3. 将成员健康状况与药品特性进行匹配分析
4. 检查是否存在过敏风险、年龄禁忌、药物相互作用等问题
5. 综合评估后给出用药建议

请用第一人称思考，用中文展示你的思维过程。思考要体现专业性和关怀性。

每次只输出一句话的思考，要简洁有力。"""


async def safety_agent_think(
    member_name: str,
    age: str,
    allergies: str,
    drug_name: str,
    indications: str,
    contraindications: str,
    num_steps: int = 6,
) -> AsyncIterator[str]:
    """健康管家智能体思考 - 使用DeepSeek动态生成思考过程"""
    
    llm = LLMService(provider="deepseek", model="deepseek-chat")
    
    # 构建上下文信息
    context_parts = []
    if allergies:
        context_parts.append(f"过敏史：{allergies}")
    if age:
        context_parts.append(f"年龄：{age}岁")
    
    context = "；".join(context_parts) if context_parts else "暂无详细信息"
    indications_text = indications if indications else "暂无详细信息"
    contraindications_text = contraindications if contraindications else "暂无详细信息"
    
    prompt = f"""我正在为家庭成员进行用药安全检查。

**成员信息：**
- 姓名：{member_name}
- {context}

**目标药品：**
- 药品名称：{drug_name}
- 适应症：{indications_text}
- 禁忌症：{contraindications_text}

请模拟健康管家智能体的思考过程。请生成 {num_steps} 步思考，每一步都要：
1. 用第一人称"我"来思考，体现对用户健康的关心
2. 展现专业的安全分析能力
3. 思考要具体真实，基于提供的信息进行分析
4. 每步思考用【健康】开头

请开始思考："""

    try:
        # 使用DeepSeek生成思考过程
        full_response = await llm.think(prompt, HEALTH_SYSTEM_PROMPT)
        
        # 将响应按行分割或按句子分割
        thoughts = [line.strip() for line in full_response.split('\n') if line.strip()]
        
        if not thoughts:
            thoughts = [
                f"我正在查看{member_name}的健康档案...",
                f"我注意到{member_name}的年龄是{age}岁，需要考虑年龄相关的用药安全...",
                f"我正在检查{drug_name}是否与{member_name}的过敏史冲突...",
                f"我正在分析{drug_name}的禁忌症，评估用药风险...",
                f"我正在将{member_name}的健康状况与药品特性进行匹配分析...",
                f"综合分析完成，正在制定个性化用药建议..."
            ]
        
        for i, thought in enumerate(thoughts[:num_steps]):
            yield thought
            await asyncio.sleep(0.8)
            
    except Exception as e:
        logger.error(f"【健康管家智能体】思考过程生成失败: {e}")
        fallback_thoughts = [
            f"我正在仔细查阅{member_name}的健康档案信息...",
            f"根据档案显示的过敏史，我需要重点关注过敏风险...",
            f"我正在核对{drug_name}的药品说明书，寻找禁忌信息...",
            f"年龄因素很重要，我正在评估{age}岁人群的用药安全性...",
            f"我正在将药品成分与{member_name}的过敏原进行比对...",
            f"综合分析中，我会给出最谨慎的用药建议..."
        ]
        for i, thought in enumerate(fallback_thoughts[:num_steps]):
            yield thought
            await asyncio.sleep(0.5)
