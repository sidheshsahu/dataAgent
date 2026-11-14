import os
import streamlit as st
from dotenv import load_dotenv
from agents.sql_agent import sql_analyst


load_dotenv()

st.set_page_config(page_title="Blinkit Quick Commerce Intelligence", page_icon="🛒", layout="centered")
st.title("🛒 Blinkit Quick Commerce Intelligence")
st.caption("Ask questions about orders, customers, products, delivery, and inventory.")

required = ("host", "port", "user", "password", "database", "GROQ_API_KEY")
missing = [name for name in required if not os.environ.get(name)]
if missing:
    st.error("Configure the following environment variables before starting the app: " + ", ".join(missing))
    st.stop()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for item in st.session_state.chat_history:
    with st.chat_message(item["role"]):
        st.markdown(item["content"])
        if item.get("sql"):
            with st.expander("View generated SQL"):
                st.code(item["sql"], language="sql")

question = st.chat_input("For example: Which payment methods are used most often?")
if question:
    st.session_state.chat_history.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing your question..."):
            try:
                result = sql_analyst.invoke({
                    "messages": [],
                    "user_question": question,
                    "curated_ques": "",
                    "prompt_query_context": "",
                    "generated_sql_query": "",
                    "is_safe": "No",
                    "comments": "",
                    "sql_query_execution_result": "",
                    "final_answer": "",
                })
                answer = result.get("final_answer") or "The agent did not return an answer."
                st.markdown(answer)
                with st.expander("View generated SQL"):
                    st.code(result.get("generated_sql_query") or "No SQL was generated.", language="sql")
                st.session_state.chat_history.append({
                    "role": "assistant", "content": answer,
                    "sql": result.get("generated_sql_query", ""),
                })
            except Exception as exc:
                st.error(f"The request could not be completed: {exc}")

