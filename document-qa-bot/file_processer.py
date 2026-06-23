# 文件处理
import PyPDF2
def read_file(uploaded_file):
    """
    读取上传的文件内容。
    输入:Streamlit的upload_file对象
    输出:文件内容的字符串
    """
    # 获取文件名，判断后缀
    filename = uploaded_file.name.lower()

    if filename.endswith(".txt"):
        # txt文件：直接读取字节，用utf-8解码成文字
        return uploaded_file.read().decode("utf-8")
    elif filename.endswith(".pdf"):
        # PDF文件：用PyPDF逐页提取文字
        text = ""
        reader = PyPDF2.PdfReader(uploaded_file)
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    else:
        # 不支持的文件格式，抛出异常让调用方处理
        raise ValueError(f"不支持的文件格式：{filename}。请上传txt或者pdf文件。")