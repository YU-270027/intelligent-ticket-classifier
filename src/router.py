from src.schemas import TicketAnalysis

DEPARTMENT_BY_CATEGORY = {
    "退款申请": "售后退款组",
    "技术支持": "技术支持组",
    "客户投诉": "客户服务与质检组",
    "产品咨询": "产品咨询组",
}

def assign_department(analysis: TicketAnalysis) -> str:
    """根据结构化分类结果分配处理部门。"""
    return DEPARTMENT_BY_CATEGORY[analysis.category]
