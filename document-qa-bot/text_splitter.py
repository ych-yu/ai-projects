# 文本分割
from langchain_text_splitters import RecursiveCharacterTextSplitter

def split_text(text, chunk_size=300, chunk_overlap=100):
    """
       以段落为基准分割文本（支持纯中文、纯英文、中英混合）。
       优先按空行（段落）切分，如果段落太长再按句子切分，保证每块大小接近 chunk_size。
       """
    # 创建递归分割器，指定中文和英文常见的段落/句子分隔符
    splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n","\n","。","."," ",""],
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        is_separator_regex=False
    )
    chunks = splitter.split_text(text)

    # 修复：清理掉每个文本块开头多余的标点和空白（如 "。"、". " 等）
    cleaned_chunks = []
    for chunk in chunks:
        # 去掉开头所有空白，然后去掉开头多余的句号或英文句点+空格
        chunk = chunk.lstrip()  # 先去左空白
        chunk = chunk.lstrip("。. ")  # 再去掉多余的句号和点号
        cleaned_chunks.append(chunk)

    return cleaned_chunks