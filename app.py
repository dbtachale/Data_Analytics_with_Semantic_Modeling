# app.py
import streamlit as st
from without_semantic import ask_without_semantic
from with_semantic import ask_with_semantic

st.set_page_config(page_title="Semantic Layer POC", layout="wide")
st.title("Semantic Layer POC — With vs Without")
st.caption("Ask the same question both ways. Watch how the semantic layer changes everything.")

# Test questions that are deliberately tricky
DEMO_QUESTIONS = [
    "What is the total revenue?",
    "Show me revenue by region",
    "What is our gross profit margin?",
    "Which customer segment generates the most revenue?",
    "What was revenue last quarter?",
    "Compare revenue across product categories",
]

question = st.selectbox("Choose a question (or type your own):", DEMO_QUESTIONS)
custom    = st.text_input("Or ask your own:")
final_q   = custom if custom else question

if st.button("Run comparison", type="primary"):
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### ❌ Without semantic layer")
        st.caption("LLM sees raw tables — guesses joins and metric definitions")
        with st.spinner("Querying..."):
            res_a = ask_without_semantic(final_q)

        st.markdown("**Generated SQL:**")
        st.code(res_a["sql"], language="sql")

        if res_a["error"]:
            st.error(f"Query failed: {res_a['error']}")
        else:
            st.markdown("**Result:**")
            st.dataframe(res_a["result"])

    with col2:
        st.markdown("### ✅ With semantic layer")
        st.caption("LLM uses governed concepts — metric definitions enforced")
        with st.spinner("Querying..."):
            res_b = ask_with_semantic(final_q)

        st.markdown("**Generated SQL:**")
        st.code(res_b["sql"], language="sql")

        if res_b["error"]:
            st.error(f"Query failed: {res_b['error']}")
        else:
            st.markdown("**Result:**")
            st.dataframe(res_b["result"])

    # Highlight the key difference
    st.divider()
    st.markdown("### What to observe")
    st.info("""
    **Without semantic layer:** The LLM likely used `gross_amount` instead of `net_amount`,
    forgot to filter `status = 'completed'`, or produced incorrect joins.

    **With semantic layer:** The LLM always uses `fct_revenue`, always uses `net_amount`,
    and joins are pre-resolved. The result is correct and reproducible.
    """)