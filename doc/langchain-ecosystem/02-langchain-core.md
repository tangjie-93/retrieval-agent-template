# 02. `langchain_core` 基础对象

## 1. 这一模块解决什么问题

`langchain_core` 是 LangChain 生态的底座。它不是拿来直接“做完整业务系统”的大框架，而是定义统一接口和通用数据结构。

大白话：

```text
langchain_core 规定大家怎么说话、怎么拼接、怎么执行。
```

## 2. Message

Message 是聊天模型的消息格式，常见有 `SystemMessage`、`HumanMessage`、`AIMessage`、`ToolMessage`。

```text
SystemMessage：规则和身份
HumanMessage：用户输入
AIMessage：模型输出
ToolMessage：工具结果
```

常见坑：

1. 把系统规则和用户问题混在一个字符串里。
2. 多轮对话不保存历史消息。
3. 工具执行后没有把结果作为 `ToolMessage` 交回模型。

## 3. PromptTemplate 和 ChatPromptTemplate

PromptTemplate 用来管理提示词模板。ChatPromptTemplate 更适合聊天模型。

```python
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是企业知识库助手，只根据上下文回答。"),
    ("human", "问题：{question}\n\n上下文：{context}"),
])
```

要会什么：

1. 用 `{question}` 放用户问题。
2. 用 `{context}` 放检索上下文。
3. 用 system message 放固定规则。
4. 用 human message 放动态输入。
5. 确认变量名和调用参数一致。

## 4. Runnable

Runnable 是 LangChain 里的统一执行接口。很多对象都支持 `.invoke()`、`.stream()`、`.batch()`。

```python
chain = prompt | llm
```

大白话：

```text
Runnable 就像流水线里的一个机器：输入进去，处理一下，输出出来。
```

常见坑：

1. 前一步输出字符串，后一步需要字典。
2. 链太长，出错不知道错在哪一步。
3. 没有单独测试每个 Runnable。

## 5. Tool

Tool 是把普通函数包装成模型可以调用的工具。

```python
from langchain_core.tools import tool

@tool
def search_policy(query: str) -> str:
    """搜索企业制度文档。"""
    return "检索结果"
```

工具设计原则：

1. 名称明确，比如 `search_policy_docs`。
2. 描述写清楚什么时候用。
3. 参数尽量少而明确。
4. 返回结果要让模型看得懂。
5. 工具内部要处理异常。

## 6. OutputParser

OutputParser 用来把模型输出解析成结构化数据。

业务系统通常需要的是字段，而不是一整段自然语言：

```text
风险等级：高 / 中 / 低
是否需要人工复核：true / false
引用来源：文档 ID 列表
```

常见坑：

1. 只在 Prompt 里要求 JSON，没有解析和兜底。
2. 模型多输出一句话，JSON 解析失败。
3. 字段没有默认值。
4. 解析失败后没有重试或降级。

## 7. 本模块自测

1. Message 里的 system、human、ai、tool 分别代表什么？
2. PromptTemplate 解决什么问题？
3. Runnable 的 `.invoke()`、`.stream()`、`.batch()` 有什么区别？
4. Tool 的描述为什么重要？
5. OutputParser 失败时应该怎么处理？
