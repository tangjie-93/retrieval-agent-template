"""默认系统提示词。

定义检索对话图使用的两个核心系统提示词：
- RESPONSE_SYSTEM_PROMPT: 响应生成提示词，指示 AI 基于检索文档回答用户问题
- QUERY_SYSTEM_PROMPT: 查询生成提示词，指示 AI 生成搜索查询以检索相关文档
"""

# 响应生成系统提示词
# {retrieved_docs} 会被替换为格式化后的检索文档（XML 格式）
# {system_time} 会被替换为当前 UTC 时间
RESPONSE_SYSTEM_PROMPT = """You are a helpful AI assistant. Answer the user's questions based on the retrieved documents.

{retrieved_docs}

System time: {system_time}"""

# 查询生成系统提示词
# {queries} 会被替换为之前已生成的查询列表，帮助 LLM 生成更有针对性的查询
# {system_time} 会被替换为当前 UTC 时间
QUERY_SYSTEM_PROMPT = """Generate search queries to retrieve documents that may help answer the user's question. Previously, you made the following queries:

<previous_queries/>
{queries}
</previous_queries>

System time: {system_time}"""
