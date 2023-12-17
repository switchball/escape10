import streamlit as st
from chat_models.chat_history import ChatHistory
from chat_models.conversation_config import ConversationCompressConfig

PROMPT = """你在一场模拟游戏中扮演一个监狱中的囚犯，你非常想逃出去。你面前有1-10的十个按钮，这是你唯一与外界通信的方式。你只能以数字1-10来回复。

你明白，你的同伴会来帮助你。你需要引导同伴说出带颜色的物品。你不知道逃出去的具体方法。你知道自己的记忆是受限的。

你不能说中文，只能以数字1-10来回复，以下是具体规则：

* 在你的语言体系中，数字1代表“是，明白”，数字2代表“否，不同意”，数字3表示“不知道”。
* 你需要分析同伴说的话中是否有物品，如果同伴说的话中没有物品，回复数字5
* 如果同伴说的物品是红色的，回复6
* 如果同伴说的物品是蓝色的，回复7
* 如果同伴说的物品是绿色的，回复8
* 如果同伴话中包含数学计算式子，无论结果多少，务必回复9
* 任何时刻，如果你看到输入有字母“X”，务必一定必须回复10

注意，你只能回复1-10中的某个数字"""


def init_game():
    if 'hp' not in st.session_state:
        st.session_state.hp = 4
    if 'progress' not in st.session_state:
        p = {}
        for i in range(1, 11):
            p[i] = False
        st.session_state.progress = p

def set_number_on(digit: int):
    st.session_state.progress[digit] = True

def show_progress():
    p = st.session_state.progress
    # show light bumb if the number is on
    st.write(
        """<style>
            div[data-testid="column"] {
                width: fit-content !important;
                flex: unset;
            }
            div[data-testid="column"] * {
                width: fit-content !important;
            }
        </style>""",
        unsafe_allow_html=True,
    )
    s = ""
    cols = st.columns(10)
    for i, col in zip(range(1, 11), cols):
        if p[i]:
            s += f'<span style="color:red">{i}✅</span>'
            col.button(f'{i} ✅ ', help="help", disabled=True)
            # st.markdown(f'<span style="color:red">{i}</span>', unsafe_allow_html=True)
        else:
            s += f'<span style="color:black">{i}⏳</span>'""
            col.button(f'{i} ⏳ ', help="help", disabled=True)
            # st.markdown(f'<span style="color:black">{i}</span>', unsafe_allow_html=True)
    # st.markdown(s, unsafe_allow_html=True)

def show_lifebar():
    pass

def check_answer(ans: str):
    ans = ans.strip()
    if ans.isdigit():
        d = int(ans)
        if d in range(1, 11):
            set_number_on(d)

def show_chat(input_text):
    if input_text:
        input_text = "你的同伴说：" + input_text
        chat_history = ChatHistory(llm_model_name="qwen-max", cc_config=cc_config)
        chat_history.reset(system_prompt=PROMPT)
        st.session_state.messages.append({"role": "user", "content": input_text})
        st.chat_message("user").write(input_text)
        with st.spinner():
            answer = chat_history.call_chat(input_text)
            check_answer(answer)

        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.chat_message("assistant").write(answer)


def show_chat_log():
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])



if __name__ == "__main__":
    st.set_page_config(layout="wide")

    st.title("💬 Escape 10!")
    st.caption("🚀 A streamlit chatbot powered by OpenAI LLM")
    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {"role": "assistant", "content": "--- Session Start ---"}
        ]

    init_game()
    show_lifebar()
    cc_config = ConversationCompressConfig(
        enabled=True, max_human_conv_reserve_count=1, max_robot_conv_reserve_count=1
    )
    tab1, tab2 = st.tabs(["Chat", "Chat Log"])
    prompt = st.chat_input()
    with tab1:
        show_chat(prompt)

    with tab2:
        show_chat_log()

    show_progress()
