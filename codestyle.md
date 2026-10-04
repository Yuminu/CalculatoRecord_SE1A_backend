本代码规范参考自：PEP 8 -- Style Guide for Python Code（https://peps.python.org/pep-0008/）

# 后端代码规范（Python / Flask）

本仓库的 Python 代码遵循 [PEP 8](https://peps.python.org/pep-0008/) 官方风格指南，
并结合 Flask 项目实践做如下约定。所有提交的代码必须满足这些规则。

## 1. 命名规范

- 变量名、函数名、模块名：`snake_case`（如 `validate_expression`）。
- 类名：`PascalCase`（如 `Calculation`、`CalculatorError`）。
- 常量：全大写 `UPPER_SNAKE_CASE`（如 `MAX_HISTORY_RECORDS`）。
- 私有函数 / 变量：以单下划线开头（如 `_check_operators`）。

## 2. 格式

- 每行不超过 79 个字符。
- 使用 4 个空格缩进，禁止使用 Tab。
- 顶层定义之间空两行，类内方法之间空一行。
- 二元运算符两侧各留一个空格。
- 文件末尾保留一个空行。

## 3. 注释与文档字符串

- 每个模块顶部必须有模块说明注释（module docstring）。
- 每个公开函数、类和公共方法必须有 docstring，说明用途、
  参数（Args）与返回值（Returns）；可能抛错时说明 Raises。
- 注释使用英文，保持简洁，解释"为什么"而非"做了什么"。

## 4. 导入

- 导入语句按 **标准库 → 第三方库 → 本地模块** 三组排列，
  组间空一行。
- 每组内部按字母顺序排列。
- 禁止使用通配符导入（`from x import *`）。

## 5. 安全与错误处理

- **禁止**使用 `eval()`、`exec()`、`__import__()` 或任何等效的
  任意代码执行方法处理用户输入；表达式解析使用 `ast` 安全求值。
- 所有 API 路由必须使用 `try-except` 捕获异常，记录日志后返回
  标准 JSON 错误响应，禁止将 traceback 直接返回给前端。
- 使用标准 HTTP 状态码表达结果（200 / 204 / 400 / 404 / 500）。

## 6. 数据库

- 使用 Flask-SQLAlchemy 的会话（`db.session`）进行增删改查，
  修改后显式 `commit()`。
- 模型方法返回可 JSON 序列化的字典，字段名与接口契约保持一致。
