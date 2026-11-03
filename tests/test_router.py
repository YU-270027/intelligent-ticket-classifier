import pytest
from src.classifier import analyze_ticket_offline
from src.router import assign_department
from src.schemas import TicketAnalysis

@pytest.mark.parametrize(
    ("category", "expected"),
    [
        ("退款申请", "售后退款组"),
        ("技术支持", "技术支持组"),
        ("客户投诉", "客户服务与质检组"),
        ("产品咨询", "产品咨询组"),
    ],
)
def test_department_routing(category, expected):
    analysis = TicketAnalysis(category=category, summary="测试工单", urgency="低", needs_human_review=False)
    assert assign_department(analysis) == expected

def test_offline_refund_ticket():
    result = analyze_ticket_offline("我的订单号是 DD20261103001，支付了 199 元，现在想申请退款。")
    assert result.category == "退款申请"
    assert result.order_id == "DD20261103001"
    assert result.amount == 199.0

def test_offline_empty_ticket():
    with pytest.raises(ValueError):
        analyze_ticket_offline("   ")
