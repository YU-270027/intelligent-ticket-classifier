import os
import re
from typing import Iterable

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from src.schemas import TicketAnalysis

load_dotenv()

SYSTEM_PROMPT = """你是一个严谨的中文客服工单分析助手。请阅读工单并输出符合结构要求的分析结果。

分类只能从以下四类中选择：
- 退款申请：退款、退货、取消订单、退款进度等
- 技术支持：无法登录、功能故障、支付失败、系统报错等
- 客户投诉：服务态度、配送体验、服务质量或明确表达不满并要求投诉
- 产品咨询：产品功能、规格、价格、使用方式等咨询

判断要求：
1. 以用户最主要、最需要处理的诉求作为分类依据。
2. 不要根据情绪强烈程度直接判断为高紧急程度。
3. 只有文本明确提供时才提取订单号和金额，不要猜测或补全。
4. 如果包含多个互相冲突的诉求、关键信息不足或无法确定主要意图，将 needs_human_review 设为 true，并说明原因。
5. 摘要应忠实于原文，不添加原文没有的信息。
6. 紧急程度结合明确时效要求、服务中断或实际风险判断；普通询问通常为低。
"""

def build_chain():
    """创建 DeepSeek 结构化输出 Chain。"""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError("未检测到 DEEPSEEK_API_KEY，请检查 .env 配置。")
    from langchain_openai import ChatOpenAI
    model_name = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    llm = ChatOpenAI(
        model=model_name,
        api_key=api_key,
        base_url="https://api.deepseek.com",
        temperature=0,
        timeout=30,
        max_retries=2,
    )
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "请分析以下客服工单：\n\n{ticket_text}"),
    ])
    return prompt | llm.with_structured_output(TicketAnalysis)

def analyze_ticket(ticket_text: str) -> TicketAnalysis:
    """调用 DeepSeek 分析单条工单。"""
    if not ticket_text or not ticket_text.strip():
        raise ValueError("工单内容不能为空。")
    return build_chain().invoke({"ticket_text": ticket_text.strip()})

def analyze_tickets_batch(ticket_texts: Iterable[str]) -> list[TicketAnalysis]:
    """批量分析工单。"""
    texts = [str(text).strip() for text in ticket_texts]
    if any(not text for text in texts):
        raise ValueError("批量数据中存在空工单，请先检查 CSV 文件。")
    chain = build_chain()
    return chain.batch(
        [{"ticket_text": text} for text in texts],
        config={"max_concurrency": 3},
    )

def analyze_ticket_offline(ticket_text: str) -> TicketAnalysis:
    """不调用模型的关键词规则模式，仅用于演示流程。"""
    text = (ticket_text or "").strip()
    if not text:
        raise ValueError("工单内容不能为空。")
    rules = [
        ("退款申请", ["退款", "退货", "退钱", "取消订单", "返还款"]),
        ("技术支持", ["无法登录", "登录不了", "报错", "闪退", "无法使用", "支付失败", "故障"]),
        ("客户投诉", ["投诉", "态度差", "服务差", "非常不满", "欺骗"]),
        ("产品咨询", ["咨询", "多少钱", "价格", "规格", "怎么使用", "功能"]),
    ]
    scores = [(category, sum(keyword in text for keyword in keywords)) for category, keywords in rules]
    category, score = max(scores, key=lambda item: item[1])
    needs_review = score == 0 or sum(value > 0 for _, value in scores) > 1
    order_match = re.search(r"(?:订单号|订单编号|订单)\s*[:：#]?\s*([A-Za-z0-9-]{5,})", text)
    amount_match = re.search(r"(?:人民币)?\s*([0-9]+(?:\.[0-9]{1,2})?)\s*元", text)
    urgency = "高" if any(word in text for word in ["立即", "马上", "无法正常营业", "紧急"]) else "中" if any(word in text for word in ["尽快", "今天"]) else "低"
    return TicketAnalysis(
        category=category,
        summary=text[:80] + ("…" if len(text) > 80 else ""),
        order_id=order_match.group(1) if order_match else None,
        amount=float(amount_match.group(1)) if amount_match else None,
        urgency=urgency,
        needs_human_review=needs_review,
        review_reason="离线关键词模式无法可靠判断复杂语义，建议人工复核。" if needs_review else None,
    )
