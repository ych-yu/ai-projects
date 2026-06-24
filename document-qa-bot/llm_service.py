import requests

def generate_answer(question,context,api_key="YOUR-API-KEY"):
    """
    调用通义千问大模型，基于文档内容生成回答。

    参数:
        question: 用户提问的字符串
        context: 从文档中检索到的相关文本块拼接成的上下文字符串
        api_key: 阿里云百炼的API Key，默认占位符，部署时替换为真实Key

    返回:
        AI生成的回答字符串，如果调用失败则返回错误信息
    """
    api_url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    headers = {
        "Authorization": "Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "qwen-plus",
        "messages": [
            {"role": "system", "content": "你是一个严格基于文档内容回答问题的助手。请根据用户提供的文档内容组织回答。如果文档中没有相关信息，请如实说'文档中未提及'，不要编造任何信息。"},
            {"role": "user", "content": f"请根据以下文档内容，回答用户的问题。\n\n文档内容：\n{context}\n\n用户问题：{question}"}
        ]
    }
    response = requests.post(api_url, headers=headers, json=payload)


    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"生成失败，状态码：{response.status_code},错误信息：{response.text}"

