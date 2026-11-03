from typing import Literal, Optional
from pydantic import BaseModel, Field

TicketCategory = Literal["退款申请", "技术支持", "客户投诉", "产品咨询"]
UrgencyLevel = Literal["低", "中", "高"]

class TicketAnalysis(BaseModel):
    """客服工单分析结果。"""
    category: TicketCategory = Field(description="工单的主要诉求类别")
    summary: str = Field(description="用简洁中文概括用户的主要问题")
    order_id: Optional[str] = Field(default=None, description="文本中明确出现的订单号；未提及时为 null")
    amount: Optional[float] = Field(default=None, description="文本中明确提及的人民币金额；未提及时为 null")
    urgency: UrgencyLevel = Field(description="处理紧急程度：低、中、高")
    needs_human_review: bool = Field(description="是否存在多意图、信息不足或判断不确定等需要人工复核的情况")
    review_reason: Optional[str] = Field(default=None, description="需要人工复核时说明原因")
