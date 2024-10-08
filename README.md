# BabelNAR NAL 测试套件

![GitHub License](https://img.shields.io/github/license/ARCJ137442/BabelNAR-NAL-test-suite?style=for-the-badge&color=0288d1)
![Code Size](https://img.shields.io/github/languages/code-size/ARCJ137442/BabelNAR-NAL-test-suite?style=for-the-badge&color=0288d1)
![Lines of Code](https://www.aschey.tech/tokei/github.com/ARCJ137442/BabelNAR-NAL-test-suite?style=for-the-badge&color=0288d1)
[![Language](https://img.shields.io/badge/language-Python-blue?style=for-the-badge&color=0288d1)](https://www.python.org/)

开发状态：

![Created At](https://img.shields.io/github/created-at/ARCJ137442/BabelNAR-NAL-test-suite?style=for-the-badge)
![Last Commit](https://img.shields.io/github/last-commit/ARCJ137442/BabelNAR-NAL-test-suite?style=for-the-badge)

[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-2.0.0-%23FE5196?style=for-the-badge)](https://conventionalcommits.org)

主要信息：

- 📌最小Python版本：3.8.10（其它版本尚未验证）
- 💻操作系统：Windows（其它系统尚未验证）
- 🗺️目前所支持NAL层级：NAL-1 ~ NAL-6
- 💬程序交互语言：简体中文
- 🕒最后更新时间：【2024-06-12 20:03:19】

## 目录

- [**快速开始**](#快速开始)
- [**概要**](#概要)
- [**理论**](#理论)
- [**技术**](#技术)

## 快速开始

⚠️注意：运行前请务必查看并了解[**现存问题**](#现存问题)

### 启动

最新测试入口为`main.py`，可在终端中运行如下命令：

```shell
python main.py
```

该入口可调用其它测试用脚本，包括但不限于：

#### 批量测试

直接运行所有测试用例

```shell
python run_tests.py
```

#### 定点测试

运行指定测试用例，带有用户交互功能

```shell
python direct_test.py
```

#### 测试结果查看器

从指定的测试结果文件(JSON)中查看测试结果

```shell
python result_loader.py
```

#### 测试结果差异分析

从指定的测试结果文件(JSON)中加载测试结果，分析不同推理器的测试结果差异

```shell
python diff_analyze.py
```

#### 调试（VSCode）

若使用 [**VSCode**](https://code.visualstudio.com/)，可在`.vscode/launch.json`中添加如下调试配置：

```json
{
    "configurations": [
        {
            "name": "测试套件 主入口",
            "type": "debugpy",
            "request": "launch",
            "program": "main.py",
            "console": "integratedTerminal"
        },
        {
            "name": "运行分组NAL测试",
            "type": "debugpy",
            "request": "launch",
            "program": "run_tests.py",
            "console": "integratedTerminal"
        },
        {
            "name": "运行精确NAL测试",
            "type": "debugpy",
            "request": "launch",
            "program": "direct_test.py",
            "console": "integratedTerminal"
        },
        {
            "name": "测试结果加载器",
            "type": "debugpy",
            "request": "launch",
            "program": "result_loader.py",
            "console": "integratedTerminal"
        },
        {
            "name": "差异分析",
            "type": "debugpy",
            "request": "launch",
            "program": "diff_analyze.py",
            "console": "integratedTerminal"
        }
    ]
}
```

在添加该配置之后，可直接在VSCode中通过"调试"启动测试。

### 配置

测试套件的所有"NARS版本"与"测试用例"均在`constants.py`中定义，可通过修改该文件来调整测试套件的配置。

- 启用/禁用 NARS版本：注释/取消注释 相应常量的定义
- 启用/禁用 测试用例：注释/取消注释 相应常量的定义

### 结果查看

在运行入口脚本`run_tests.py`后，测试结果会即刻在终端中输出。

除了终端中输出，测试结果也会被存储在`test_results`文件夹中（一般在项目根目录）。

其中的JSON文件可通过`result_loader.py`加载回看：在控制台输入路径，直接从JSON中加载并展示测试结果。

亦可通过`diff_analyze`对测试进行差异分析，比对相同用例中不同推理器的表现

1. 部分成功 ⇒ 哪些成功，哪些失败
2. 推理步数 ⇒ 各推理器通过测试所用的推理步数
3. 运行耗时 ⇒ 各推理器在推理步数相同时，通过测试所用的时间

#### 测试结果的存储方式

JSON格式：

- 主要用途：详尽、全面的信息存储，便于细节分析与漏洞溯因
- 文件名：`group_results-【时间戳】.test.json`
- 所存数据：
  - 所有测试指标
  - 产生这些指标的程序输出（标准输出`stdout`与标准错误`stderr`）

CSV格式：

- 主要用途：提供数据支持，便于直观而快速地规范化分析
- 文件名：`group_results-【时间戳】.test.csv`
- 所存数据：
  - 所有测试指标：测试用NARS、测试用例、测试通过与否、推理步数、程序运行时间等
  - **不包括程序输出**

## 概要

BabelNAR 测试套件主要包括：

- NAL测试用例：涵盖NAL（Non-Axiomatic Logic，非公理逻辑）

测试套件的主要功能：

- 功能测试：单个推理器在各种知识处理功能上的表现
- 交叉测试：测试不同NARS实现在功能、性能上的差异

测试的主要指标

- 功能指标：
  - 是否通过测试
- 性能指标：
  - 通过测试所需程序运行时间
  - 通过测试所需的最少推理步数

## 理论

### NAL 简介

NAL是NARS运作的重要部分，旨在通过统一的"推理"实现通用化知识处理。

这些知识处理过程包括：

- 旧知识的**修正**
- 新知识的**推断**、**派生**
- 问题的**回答**

### NAL 层级、知识处理功能一览

这些以"推理"为名的知识处理功能，通过"层级"的形式组织为六个层级。

NAL-1：基础的"继承"关系，推演&问答

|测试编号|主要功能|
|:---|:---|
|1.0 | 知识修正 |
|1.1 ~ 1.5 | 三段论推理 |
|1.6 ~ 1.7 | 问答 |
|1.8 | 问题溯源 |

NAL-2：在"继承"关系上建立对称的"相似"关系，并引入新的"集合"概念

|测试编号|主要功能|
|:---|:---|
|2.0 | 知识修正|
|2.1 ~ 2.3 | "比较"推理|
|2.4 ~ 2.5 | 相似类比|
|2.6 | 相似传递|
|2.7 ~ 2.15 | 知识结构转换|
|2.16 ~ 2.19 | 新的"集合"概念|

NAL-3：在NAL-2的"集合"上引入集合操作——两交两差、组合分解

|测试编号|主要功能|
|:---|:---|
|3.0 ~ 3.3 | 双前提组合分解|
|3.4 ~ 3.5 | 集合操作|
|3.6 ~ 3.7 | 组合与分解|
|3.8 ~ 3.15 | 单句组合与分解|

NAL-4：引入与笛卡尔积类似的"积/像"，并以此实现"关系推理"

|测试编号|主要功能|
|:---|:---|
|4.0 ~ 4.5 | "积"与"像"的相互转换|
|4.6 ~ 4.8 | "积"与"像"的组合分解|

NAL-5：在"继承"之上引入"蕴含"关系，结合"合取/析取/否定"实现"高阶推理"与"条件推理"

|测试编号|主要功能|
|:---|:---|
|5.0 ~ 5.4 | 高阶三段论推理|
|5.5 ~ 5.6 | 分离前提或结论|
|5.7 ~ 5.12 | 高阶对称关系"等价"|
|5.13 ~ 5.19 | 高阶集合"合取"与"析取"|
|5.20 ~ 5.22 | 高阶差集"否定"|
|5.23 ~ 5.25 | 条件演绎|
|5.26 ~ 5.28 | 条件归因|
|5.29 | 条件归纳|

NAL-6：引入"变量"的概念，容纳并处理抽象化、符号化知识

|测试编号|主要功能|
|:---|:---|
|6.0 ~ 6.6 | 单变量统一 |
|6.7 ~ 6.12 | 单变量消去 |
|6.13 ~ 6.16 | 多变量消去 |
|6.17 ~ 6.19 | 单变量引入 |
|6.20 ~ 6.21 | 多变量引入 |
|6.22 | 递归变量消去 |
|6.23 ~ 6.24 | 深层变量统一 |
|6.25 | 深层变量引入 |
|6.26 ~ 6.27 | 部分变量消去 |

## 技术

### 安装需求

Python版本：**3.8.10+**

测试套件中已内置测试工具，且代码均基于Python内置标准库，无需安装第三方库。

### 工具链

该测试套件基于 [**BabelNAR**](https://github.com/ARCJ137442/BabelNAR.rs) 搭建，主要特性有：

- 统一的测试框架：一个测试可适配多种NARS，如OpenNARS、ONA、PyNARS
- 全自动化测试过程：可通过在`.nal`文件中插入相应命令，控制测试的"延时等待"、"结果预期"、"自动退出"等
- 基于配置的测试搭建：所有测试均可通过`hjson`文件方便配置

### 文件结构

- Python脚本
  - 入口：`run_tests.py`
  - NARS版本/测试 列表：`constants.py`
  - 测试工具链：`toolchain.py`
  - 测试结果加载工具：`result_loader.py`
- 可执行文件：`executables/`
  - OpenNARS jar文件
  - BabelNAR 可执行文件（`babelnar_cli.exe`）
- NAL测试用例：`nal/`
  - 单步推理：`single_step/*.nal`
- BabelNAR 工具链配置文件：`config/*.hjson`

### 现存问题

#### 小数精度限制问题

该自动测试默认预期的真值（`%频率;信度%`）只保留**两位小数**——若小数位数不为两位，则有可能导致测试失败

#### 对Java进程（`java.exe`）的破坏性

⚠️该自动测试目前会影响系统中的Java进程：系统会使用`taskkill`命令终止进程 `java.exe`——这**可能导致系统中的其它Java应用停止运行**

目前已被验证的、会被影响的有：

- 代码编辑器中的Java语言服务器（LSP）
- OpenNARS Shell交互式终端（立即停止运行）

在开始测试之前，请务必保护系统中依赖Java的应用，避免其意外终止给系统带来不必要的影响。

#### 全套测试运行时间较长

🕒因测试套件与Java的互操作表现不佳（依靠"强行终止"检测子进程状态），**完成全套测试的时间可能较长**

可考虑用如下方式缩短总测试时间：

- 减少使用的测试用例
  - 方法：在`constants.py`中调整"测试区域分界线"，或直接注释掉不需要的测试声明
- 减少对比用NARS版本的数量
  - 方法：直接注释掉不需要的NARS版本声明
