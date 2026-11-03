import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from src.classifier import analyze_ticket, analyze_ticket_offline, analyze_tickets_batch
from src.router import assign_department

load_dotenv()
st.set_page_config(page_title="智能客服工单分类与自动路由系统", page_icon="📨", layout="wide")
st.title("智能客服工单分类与自动路由系统")
st.caption("基于 LangChain 与 DeepSeek API 的中文工单分析练习项目")

with st.sidebar:
    st.header("运行设置")
    mode = st.radio("选择分析模式", ["离线规则模式", "DeepSeek API 模式"])
    if mode == "DeepSeek API 模式":
        st.success("已检测到 API Key") if os.getenv("DEEPSEEK_API_KEY") else st.warning("未检测到 API Key，请在项目根目录配置 .env 文件。")
    else:
        st.info("离线模式不调用外部 API，结果仅供流程演示。")

def run_analysis(text: str):
    return analyze_ticket_offline(text) if mode == "离线规则模式" else analyze_ticket(text)

tab_single, tab_batch = st.tabs(["单条工单分析", "CSV 批量处理"])
with tab_single:
    st.subheader("输入客服工单")
    ticket_text = st.text_area("工单内容", height=160, placeholder="例如：我的订单号是 DD20261103001，支付了 199 元，但商品一直没有发货，我想申请退款。")
    if st.button("分析工单", type="primary", key="analyze_single"):
        if not ticket_text.strip():
            st.error("请先输入工单内容。")
        else:
            try:
                with st.spinner("正在分析工单…"):
                    result = run_analysis(ticket_text)
                department = assign_department(result)
                st.subheader("分析结果")
                c1, c2, c3 = st.columns(3)
                c1.metric("工单类别", result.category)
                c2.metric("紧急程度", result.urgency)
                c3.metric("处理部门", department)
                st.write("**工单摘要：**", result.summary)
                st.write("**订单号：**", result.order_id or "未提取到")
                st.write("**涉及金额：**", f"¥{result.amount:.2f}" if result.amount is not None else "未提取到")
                if result.needs_human_review:
                    st.warning("该工单建议人工复核：" + (result.review_reason or "模型提示存在不确定性。"))
                else:
                    st.success("当前结果未触发人工复核标记。")
                with st.expander("查看结构化结果"):
                    st.json(result.model_dump())
            except Exception as exc:
                st.error(f"分析失败：{exc}")

with tab_batch:
    st.subheader("上传 CSV 文件")
    st.write("CSV 文件必须包含一列名为“工单内容”的文本列。")
    uploaded = st.file_uploader("选择 CSV 文件", type=["csv"])
    if uploaded is not None:
        try:
            df = pd.read_csv(uploaded)
            if "工单内容" not in df.columns:
                st.error("文件中未找到“工单内容”列。")
            elif df.empty:
                st.warning("文件中没有工单数据。")
            else:
                st.write(f"共读取 {len(df)} 条工单。")
                st.dataframe(df.head(10), use_container_width=True)
                if st.button("开始批量分析", type="primary"):
                    try:
                        texts = df["工单内容"].fillna("").astype(str).tolist()
                        if mode == "离线规则模式":
                            results = [analyze_ticket_offline(text) for text in texts]
                        else:
                            with st.spinner("正在调用 DeepSeek API 批量分析…"):
                                results = analyze_tickets_batch(texts)
                        output = df.copy()
                        output["工单类别"] = [r.category for r in results]
                        output["工单摘要"] = [r.summary for r in results]
                        output["订单号"] = [r.order_id for r in results]
                        output["涉及金额"] = [r.amount for r in results]
                        output["紧急程度"] = [r.urgency for r in results]
                        output["处理部门"] = [assign_department(r) for r in results]
                        output["建议人工复核"] = [r.needs_human_review for r in results]
                        output["复核原因"] = [r.review_reason for r in results]
                        st.session_state["batch_output"] = output
                    except Exception as exc:
                        st.error(f"批量分析失败：{exc}")
                if "batch_output" in st.session_state:
                    output = st.session_state["batch_output"]
                    st.subheader("批量分析结果")
                    st.dataframe(output, use_container_width=True)
                    st.download_button("下载分析结果 CSV", data=output.to_csv(index=False).encode("utf-8-sig"), file_name="工单分析结果.csv", mime="text/csv")
        except Exception as exc:
            st.error(f"读取 CSV 失败：{exc}")

st.divider()
st.caption("说明：本项目为个人练习原型，示例数据为模拟数据。模型分析结果不应未经人工审核直接用于真实业务决策。")
