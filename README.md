# giga-compiler

一个面向编译原理课程小组作业的迷你编译器项目。当前仓库根目录作为项目根目录使用，内部结构按 `giga-compiler` 的设计搭建。

## 团队分工表


| 模块 | 负责人 | 主要工作 |
| --- | --- | --- |
| `main.py` | 同学A | 项目主入口、串联编译流程 |
| `src/frontend/lexer.py` | 同学B | 词法分析、Token 输出 |
| `src/ast/nodes.py` | 同学C | AST 节点定义 |
| `src/frontend/parser.py` | 同学C | 语法分析、构建 AST |
| `src/backend/semantic.py` | 同学D | 语义分析、符号表检查 |
| `src/backend/codegen.py` | 同学E | 中间代码/目标代码生成 |
| `src/vm/cpu_emulator.py` | 同学F | 栈式虚拟机、运行支持 |
| `examples/test_cases.toy` | 同学F | 示例程序与测试用例维护 |

## 项目目录结构

```text
giga-compiler/
├── README.md
├── main.py
├── src/
│   ├── ast/
│   │   └── nodes.py
│   ├── frontend/
│   │   ├── lexer.py
│   │   └── parser.py
│   ├── backend/
│   │   ├── semantic.py
│   │   └── codegen.py
│   └── vm/
│       └── cpu_emulator.py
└── examples/
    └── test_cases.toy
```

## 项目目标

本项目实现一个教学演示用的迷你编译器，覆盖以下四个阶段：

- 词法分析
- 语法分析
- 语义分析
- 代码生成与简单运行支持

目标不是完整复现 C 编译器，而是完成一个范围清晰、结构完整、适合课程展示的最小可运行版本。

## 第一版语言范围

### 支持的内容

- 数据类型：`int`、`bool`
- 变量：声明、初始化、赋值
- 表达式：算术、关系、逻辑、括号
- 语句：代码块、`if-else`、`while`、`print`

示例：

```c
int a = 3;
bool keep_running = true;

while (keep_running && a > 0) {
    if (a != 2) {
        print(a);
    } else {
        print(99);
    }

    a = a - 1;
    keep_running = a >= 0;
}
```

### 第一版暂不支持

- 函数定义与普通函数调用
- 数组、字符串、浮点数
- 指针、结构体、类
- `for`、`switch`、`break`、`continue`

这样可以把难度控制在课程项目可完成的范围内。

## 语义分析最低要求

- 变量先声明后使用
- 同一作用域中不能重复声明
- 赋值语句类型匹配
- 算术运算只接受 `int`
- 逻辑运算只接受 `bool`
- `if` 和 `while` 条件必须为 `bool`

## 当前已实现功能

目前项目已经实现了一条可以直接运行的完整编译链路：

- `Lexer`：手写词法分析器，支持关键字、标识符、整数、布尔值和运算符切分
- `Parser`：递归下降语法分析器，能够构建 AST
- `SemanticAnalyzer`：支持符号表、重复声明检查、未声明变量检查、类型检查
- `CodeGenerator`：把 AST 生成为基于栈的 P-Code 指令
- `VirtualMachine`：执行 P-Code，并打印程序运行结果

### 当前支持的语法与语义能力

- 数据类型：`int`、`bool`
- 变量声明：`int a = 1;`、`bool ok = true;`
- 赋值语句：`a = a + 1;`
- 条件语句：`if ... else`
- 循环语句：`while`
- 输出语句：`print(...)`
- 算术运算：`+`、`-`、`*`、`/`
- 关系运算：`<`、`>`、`<=`、`>=`
- 相等运算：`==`、`!=`
- 逻辑运算：`&&`、`||`、`!`
- 括号表达式：`( ... )`

### 当前已实现的语义检查

- 变量重复声明检查
- 未声明变量使用检查
- 变量初始化类型检查
- 赋值类型匹配检查
- `if` / `while` 条件必须为 `bool`
- 算术运算只能作用于 `int`
- 逻辑运算只能作用于 `bool`
- 相等运算两侧类型必须一致

## 当前目标代码形式

当前项目实际输出的是基于栈的 P-Code，而不是三地址码。

已支持的核心指令包括：

- `PUSH`
- `LOAD`
- `STORE`
- `ADD`、`SUB`、`MUL`、`DIV`
- `LT`、`GT`、`LE`、`GE`、`EQ`、`NE`
- `AND`、`OR`、`NOT`
- `JMP`、`JMP_IF_FALSE`
- `LABEL`
- `PRINT`

## 如何运行项目

### 1. 进入项目目录

在终端中切换到项目根目录（也就是本 README 所在目录）：

```powershell
cd <项目根目录>
```

### 2. 运行正常示例

如果要运行默认的综合示例程序，执行：

```powershell
python main.py
```

这条命令会默认读取：

- `examples/test_cases.toy`

### 3. 运行错误示例

如果要运行专门用于展示语义分析报错的示例，执行：

```powershell
python main.py examples/error_cases.toy
```

这条命令会读取：

- `examples/error_cases.toy`

### 4. 运行流程说明

无论运行哪一个 `.toy` 文件，`main.py` 都会依次执行：

- `Lexer`
- `Parser`
- `SemanticAnalyzer`
- `CodeGenerator`
- `VirtualMachine`

如果程序合法，最后会在终端打印运行结果；如果存在语义错误，则会输出简洁错误信息。

### 5. 当前正常示例输出

当前 `examples/test_cases.toy` 的内容是：

```c
int a = 3;
bool keep_running = true;

while (keep_running && a > 0) {
    if (a != 2) {
        print(a);
    } else {
        print(99);
    }

    a = a - 1;
    keep_running = a >= 0;
}
```

运行结果为：

```text
3
99
1
```

### 6. 错误示例文件

项目还提供了一个专门用于演示语义分析报错的文件：

- `examples/error_cases.toy`

这个文件会触发语义错误，便于展示编译器能够检查的问题，例如：

- 变量重复声明
- 使用未声明变量
- 变量初始化类型不匹配
- 赋值类型不匹配
- `if` / `while` 条件不是 `bool`

当前错误示例文件默认首先触发的是“变量重复声明”错误。

运行命令：

```powershell
python main.py examples/error_cases.toy
```

当前输出示例：

```text
编译失败: 变量重复声明: 'a'
```

## 后续可扩展方向

1. 增加更完整的错误定位信息，例如具体 token 行列
2. 增加更多测试用例，覆盖 `if-else`、`bool` 和逻辑表达式
3. 继续扩展语言特性，例如函数、数组或更完整的类型系统
