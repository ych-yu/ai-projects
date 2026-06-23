# 使用python+streamlit实现AI周报生成器网页
# 导入相应的库和包
import streamlit as st
import dashscope
from dashscope import Generation

# 侧边栏手动输入API密钥，彻底避开secrets读取报错
with st.sidebar:
    st.subheader("API密钥配置")
    DASHSCOPE_API_KEY = st.text_input("通义千问 DASHSCOPE_API_KEY", type="password", placeholder="粘贴sk开头的密钥")

# 校验密钥是否填写
if not DASHSCOPE_API_KEY:
    st.warning("请在左侧侧边栏输入你的通义千问API密钥后，才能使用生成功能！")
    st.stop()
dashscope.api_key = DASHSCOPE_API_KEY

# 创建侧边栏让页面布局更清晰明了
with st.sidebar:
    st.divider()
    job_type = st.selectbox("请选择你的工作类型：",["开发","产品","销售"])
    mode = st.radio("请选择模式：",["快速模式","对话模式"])

    st.divider()
    if st.button(" 清空全部历史"):
        st.session_state.quick_history = []
        st.session_state.chat_history = []
        st.session_state.memory = []
        st.rerun()

# 页面标题
st.title("AI周报生成器")

# 初始化所有需要跨页面保留的状态变量
if "memory" not in st.session_state:
    st.session_state.memory = []
if "quick_history" not in st.session_state:
    st.session_state.quick_history = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "input_key" not in st.session_state:
    st.session_state.input_key = 0

# 模式选择
if mode == "快速模式":
    st.write("输入你本周的工作内容，AI帮你生成一份格式清晰的周报。")

    user_input = st.text_area("请输入本周的工作内容：", height=200)

    if st.button("生成周报"):
        if user_input:
            if job_type == "开发":
                system_prompt = "你是一个专业的AI周报生成助手，面向开发岗位。请直接根据用户输入的工作内容，生成一份周报，格式如下：\n\n【本周工作】 \n- 开发进度\n- Bug修复\n\n 【下周计划】 \n- "
            elif job_type == "产品":
                system_prompt = "你是一个专业的AI周报生成助手，面向产品岗位。请直接根据用户输入的工作内容，生成一份周报，格式如下：\n\n【本周工作】 \n- 需求分析\n- 原型设计\n\n 【下周计划】 \n- "
            else:
                system_prompt = "你是一个专业的AI周报生成助手，面向销售岗位。请直接根据用户输入的工作内容，生成一份周报，格式如下：\n\n【本周工作】 \n- 客户拜访\n- 签单金额\n\n 【下周计划】 \n- "

            # 将系统提示词和用户输入拼接成完整的消息，发送给大模型API
            messages = [
                {"role": "system", "content": system_prompt},
                {"role":"user","content":user_input}
            ]
            with st.spinner("正在为您生成周报，请稍后..."):
                response = Generation.call(
                    model="qwen-plus",
                    messages=messages
                )
            if response.status_code == 200:
                st.success("周报生成成功！")
                st.write(response.output.text)
                # 追加到快速模式历史记录
                st.session_state.quick_history.append({"role": "user", "content": user_input})
                st.session_state.quick_history.append({"role": "assistant", "content": response.output.text})
            else:
                st.error(f"生成失败：{response.message}")
        else:
            st.warning("请输入本周工作内容后再生成。")

    # 快速模式历史记录展示区
    if st.session_state.quick_history:
        with st.expander("快速模式历史记录", expanded=False):
            for idx, msg in enumerate(st.session_state.quick_history):
                if msg["role"] == "user":
                    st.markdown(f"**你：** {msg['content']}")
                else:
                    st.markdown(f"**AI周报：** {msg['content']}")
                if st.button("删除", key=f"quick_del_{idx}"):
                    del st.session_state.quick_history[idx]
                    st.rerun()
                st.divider()

elif mode == "对话模式":
    st.write("逐条输入你的工作内容，输入'生成周报'后AI帮你汇总。")

    # 显示已保存的内容
    if st.session_state.memory:
        st.write("已保存的工作内容：")
        for i, item in enumerate(st.session_state.memory):
            st.write(f"{i+1}. {item}")

    # 输入框和提交按钮
    user_input = st.text_input("请输入一条工作内容（输入'生成周报'结束）：", key=f"input_{st.session_state.input_key}")

    if st.button("提交") and user_input:
        if user_input == "生成周报":
            # 把所有内容拼接起来
            work_content = "、".join(st.session_state.memory)

            # 根据用户选择的岗位类型，切换不同的 System Prompt
            if job_type == "开发":
                system_prompt = "你是一个专业的AI周报生成助手，面向开发岗位。请直接根据用户输入的工作内容，生成一份周报，格式如下：\n\n【本周工作】 \n- 开发进度\n- Bug修复\n\n 【下周计划】 \n- "
            elif job_type == "产品":
                system_prompt = "你是一个专业的AI周报生成助手，面向产品岗位。请直接根据用户输入的工作内容，生成一份周报，格式如下：\n\n【本周工作】 \n- 需求分析\n- 原型设计\n\n 【下周计划】 \n- "
            else:
                system_prompt = "你是一个专业的AI周报生成助手，面向销售岗位。请直接根据用户输入的工作内容，生成一份周报，格式如下：\n\n【本周工作】 \n- 客户拜访\n- 签单金额\n\n 【下周计划】 \n- "

            # 将系统提示词和用户输入拼接成完整的消息，发送给大模型API
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": work_content}
            ]

            with st.spinner("正在为您生成周报，请稍后..."):
                response = Generation.call(
                    model="qwen-plus",
                    messages=messages
                )

            if response.status_code == 200:
                st.success("周报生成成功！")
                st.write(response.output.text)
                # 追加到对话模式历史记录
                st.session_state.chat_history.append({"role": "assistant", "content": response.output.text})
                st.session_state.memory = []
            else:
                st.error(f"生成失败：{response.message}")
        else:
            st.session_state.memory.append(user_input)
            st.session_state.input_key += 1
            st.rerun()

    # 对话模式历史记录展示区
    if st.session_state.chat_history:
        with st.expander("对话模式历史记录", expanded=False):
            for idx, msg in enumerate(st.session_state.chat_history):
                if msg["role"] == "user":
                    st.markdown(f"**你：** {msg['content']}")
                else:
                    st.markdown(f"**AI周报：** {msg['content']}")
                if st.button("删除", key=f"chat_del_{idx}"):
                    del st.session_state.chat_history[idx]
                    st.rerun()
                st.divider()