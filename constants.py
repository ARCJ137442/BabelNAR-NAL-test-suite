'''常量池
- 🎯功能分离：逻辑/函数 - 实例/常量
- 🚩存储可用的「NARS类型」与「NAL测试文件」
- 📝有关NAL-1各规则的中文译名，可参考<https://oss.poerlang.com/blog/nal1pic.html>
'''

from typing import Callable
from os import getcwd

from toolchain import *
from util import *

# * === 测试套件元信息 == * #
TEST_SUITE_PROGRAM_NAME = 'BabelNAR CLI 测试套件'
TEST_SUITE_PROGRAM_DESCRIPTION = '''
提示：使用 Ctrl+C 从已启动的子程序中退出，或在未启动子程序时退出主程序
'''.strip()

# * === 测试结果保存 === * #

RESULT_SAVING_ENCODING = 'utf-8'
'''存储NAL测试结果时用到的编码方式
- 🚩控制在`run_tests.py`中`open`的`encoding`参数
- 📜默认为UTF-8
'''

CSV_BOM = UTF_8_SIG
'''控制在保存CSV时是否启用BOM，以及启用后要使用的BOM字节前缀
- 📌类型为`bytes | None`，其中
    - `None`：不启用BOM
    - `bytes`：启用BOM，并指定BOM字节前缀
- 📜默认为UTF_8_SIG，即「启用BOM，并指定为UTF-8编码」
'''

TEST_RESULT_FILE_ROOT = 'test_results/'
'''控制测试生成的结果文件保存路径
- 📜默认为`test_results/`：保存到一个单独的、被Git忽略的文件夹中
'''

TEST_RESULT_FILE_NAME: Callable = lambda: f'group_result-{time_stamp()}.test'
'''控制测试生成的结果文件名（可依赖系统时间）
- 📜目前名称依赖系统时间
'''

# * === 文件路径 === * #


def __ROOT() -> str:
    '''自动获取并计算根路径
    - 🎯功能分离，常量区保持「一个常量一行定义」
    '''
    root = getcwd().replace('\\', '/')
    # # 自动修正根路径
    # if 'test/' not in root:
    # root += '/test/'
    root += '/'
    return root


ROOT = __ROOT()
'''文件夹的根路径
- 🚩【2024-04-26 09:58:03】统一反斜杠「\」为正斜杠「/」
'''

EXECUTABLES_ROOT = ROOT + 'executables/'
'''存放可执行文件的根路径'''

BABELNAR_CLI = EXECUTABLES_ROOT + 'babelnar_cli.exe'
'''BabelNAR CLI 本体路径'''

CONFIG_ROOT = ROOT + 'config/'
'''配置文件的根路径'''

CONFIG_NAL = CONFIG_ROOT + 'test_nal/'
'''存放NAL配置文件的根路径'''

CONFIG_NAL_PRELUDE = CONFIG_ROOT + 'prelude_test.hjson'
'''用于在BabelNAR CLI启动后预置NAL测试文件的配置（NAL测试环境）'''

CONFIG_LAUNCH_DEMO_158 = CONFIG_ROOT + 'launch_demo_158.hjson'
'''用于在BabelNAR CLI启动demo-158的配置文件'''

CONFIG_LAUNCH_DEMO_158_OLD = CONFIG_ROOT + 'launch_demo_158_old.hjson'
'''用于在BabelNAR CLI启动demo-158的配置文件（旧）'''

CONFIG_LAUNCH_OPENNARS_158 = CONFIG_ROOT + 'launch_opennars_158.hjson'
'''用于在BabelNAR CLI启动OpenNARS 1.5.8的配置文件'''

CONFIG_LAUNCH_OPENNARS_312 = CONFIG_ROOT + 'launch_opennars_312.hjson'
'''用于在BabelNAR CLI启动OpenNARS 3.1.2的配置文件'''

CONFIG_LAUNCH_OPENNARS_304 = CONFIG_ROOT + 'launch_opennars_304.hjson'
'''用于在BabelNAR CLI启动OpenNARS 3.0.4的配置文件'''

# * === NARS类型 === * #

DEMO_158 = NARSType(
    'demo-158',
    launch_config_path=CONFIG_LAUNCH_DEMO_158
)
'''配置/demo-158'''

DEMO_158_OLD = NARSType(
    'demo-ol8',
    launch_config_path=CONFIG_LAUNCH_DEMO_158_OLD
)
'''配置/demo-158-old'''

NARS_158 = NARSType(
    'OpenNARS 1.5.8',
    launch_config_path=CONFIG_LAUNCH_OPENNARS_158,
    # * 🚩目前定在0.8s到1.6s之间，每次失败增加0.2s再试
    global_kill_java_timeouts=f_range(0.8, 1.6, 0.2)
)
'''配置/OpenNARS 1.5.8
* ✅【2024-05-09 16:16:25】稳定性测试成功：Java残余进程问题⇒暂时通过「强行杀死Java进程」实现自动化
* ⚠️目前会杀死所有的Java进程，包括与测试无关的Java程序
  * 📄OpenNARS 3.x/1.5.x GUI程序
'''

NARS_304 = NARSType(
    'OpenNARS 3.0.4',
    launch_config_path=CONFIG_LAUNCH_OPENNARS_304,
    # * 🚩目前定在0.8s到2.0s之间，每次失败增加0.4s再试
    global_kill_java_timeouts=f_range(0.8, 2.0, 0.4)
)
'''配置/OpenNARS 3.0.4'''

NARS_312 = NARSType(
    'OpenNARS 3.1.2',
    launch_config_path=CONFIG_LAUNCH_OPENNARS_312,
    # * 🚩目前定在0.8s到2.0s之间，每次失败增加0.4s再试
    global_kill_java_timeouts=f_range(0.8, 2.0, 0.4)
)
'''配置/OpenNARS 3.1.2'''

# * === NAL测试文件 === * #

# * 🚩使用「分界线」快速调整测试范围
if False:  # ! ↓分界线之前均不开始测试
    pass
if 测试区域开始 := True:  # ! ↑ 这条线上不测试 | 这条线下开始测试 ↓ ! #

    # * NAL-1 * #

    TEST_SINGLE_1_0 = TestFile('single_step/1.0', 'NAL-1.0 修正')
    '''单步推理/1.0 修正'''

    TEST_SINGLE_1_1 = TestFile('single_step/1.1', 'NAL-1.1 演绎')
    '''单步推理/1.1 演绎'''

    TEST_SINGLE_1_2 = TestFile('single_step/1.2', 'NAL-1.2 归因')
    '''单步推理/1.2 归因'''

    TEST_SINGLE_1_3 = TestFile('single_step/1.3', 'NAL-1.3 归纳')
    '''单步推理/1.3 归纳'''

    TEST_SINGLE_1_4 = TestFile('single_step/1.4', 'NAL-1.4 举例')
    '''单步推理/1.4 举例'''

    TEST_SINGLE_1_5 = TestFile('single_step/1.5', 'NAL-1.5 转换')
    '''单步推理/1.5 转换'''

    TEST_SINGLE_1_6 = TestFile('single_step/1.6', 'NAL-1.6 一般疑问')
    '''单步推理/1.6 一般疑问'''

    TEST_SINGLE_1_7 = TestFile('single_step/1.7', 'NAL-1.7 特殊疑问')
    '''单步推理/1.7 特殊疑问'''

    TEST_SINGLE_1_8 = TestFile('single_step/1.8', 'NAL-1.8 反向推理')
    '''单步推理/1.8 反向推理'''

    # * NAL-2 * #

    TEST_SINGLE_2_0 = TestFile('single_step/2.0', 'NAL-2.0 修正')
    '''单步推理/2.0 修正'''

    TEST_SINGLE_2_1 = TestFile('single_step/2.1', 'NAL-2.1 比较同前项')
    '''单步推理/2.1 比较同前项'''

    TEST_SINGLE_2_2 = TestFile('single_step/2.2', 'NAL-2.2 反向推理')
    '''单步推理/2.2 反向推理'''

    TEST_SINGLE_2_3 = TestFile('single_step/2.3', 'NAL-2.3 比较同后项')
    '''单步推理/2.3 比较同后项'''

    TEST_SINGLE_2_4 = TestFile('single_step/2.4', 'NAL-2.4 后项类比')
    '''单步推理/2.4 后项类比'''

    TEST_SINGLE_2_5 = TestFile('single_step/2.5', 'NAL-2.5 前项类比')
    '''单步推理/2.5 前项类比'''

    TEST_SINGLE_2_6 = TestFile('single_step/2.6', 'NAL-2.6 相似传递')
    '''单步推理/2.6 相似传递'''

    TEST_SINGLE_2_7 = TestFile('single_step/2.7', 'NAL-2.7 继承转相似')
    '''单步推理/2.7 继承转相似'''

    TEST_SINGLE_2_8 = TestFile('single_step/2.8', 'NAL-2.8 结构变换套内涵')
    '''单步推理/2.8 结构变换套内涵'''

    TEST_SINGLE_2_9 = TestFile('single_step/2.9', 'NAL-2.9 相似生继承')
    '''单步推理/2.9 相似生继承'''

    TEST_SINGLE_2_10 = TestFile('single_step/2.10', 'NAL-2.10 结构变换套外延')
    '''单步推理/2.10 结构变换套外延'''

    TEST_SINGLE_2_11 = TestFile('single_step/2.11', 'NAL-2.11 继承答相似')
    '''单步推理/2.11 继承答相似'''

    TEST_SINGLE_2_12 = TestFile('single_step/2.12', 'NAL-2.12 相似答继承')
    '''单步推理/2.12 相似答继承'''

    TEST_SINGLE_2_13 = TestFile('single_step/2.13', 'NAL-2.13 实例转继承')
    '''单步推理/2.13 实例转继承'''

    TEST_SINGLE_2_14 = TestFile('single_step/2.14', 'NAL-2.14 属性转继承')
    '''单步推理/2.14 属性转继承'''

    TEST_SINGLE_2_15 = TestFile('single_step/2.15', 'NAL-2.15 实例属性转继承')
    '''单步推理/2.15 实例属性转继承'''

    TEST_SINGLE_2_16 = TestFile('single_step/2.16', 'NAL-2.16 外延集定义')
    '''单步推理/2.16 外延集定义'''

    TEST_SINGLE_2_17 = TestFile('single_step/2.17', 'NAL-2.17 内涵集定义')
    '''单步推理/2.17 内涵集定义'''

    TEST_SINGLE_2_18 = TestFile('single_step/2.18', 'NAL-2.18 外延集逆定义')
    '''单步推理/2.18 外延集逆定义'''

    TEST_SINGLE_2_19 = TestFile('single_step/2.19', 'NAL-2.19 内涵集逆定义')
    '''单步推理/2.19 内涵集逆定义'''

    # * NAL-3 * #

    TEST_SINGLE_3_0 = TestFile('single_step/3.0', 'NAL-3.0 双前提同主词组合')
    '''单步推理/3.0 双前提同主词组合'''

    TEST_SINGLE_3_1 = TestFile('single_step/3.1', 'NAL-3.1 双前提同谓词组合')
    '''单步推理/3.1 双前提同谓词组合'''

    TEST_SINGLE_3_2 = TestFile('single_step/3.2', 'NAL-3.2 双前提内涵交分解')
    '''单步推理/3.2 双前提内涵交分解'''

    TEST_SINGLE_3_3 = TestFile('single_step/3.3', 'NAL-3.3 双前提外延差分解')
    '''单步推理/3.3 双前提外延差分解'''

    TEST_SINGLE_3_4 = TestFile('single_step/3.4', 'NAL-3.4 肯定性集合操作')
    '''单步推理/3.4 肯定性集合操作'''

    TEST_SINGLE_3_5 = TestFile('single_step/3.5', 'NAL-3.5 否定性集合操作')
    '''单步推理/3.5 否定性集合操作'''

    TEST_SINGLE_3_6 = TestFile('single_step/3.6', 'NAL-3.6 双侧陈述外延交')
    '''单步推理/3.6 双侧陈述外延交'''

    TEST_SINGLE_3_7 = TestFile('single_step/3.7', 'NAL-3.7 双侧陈述外延差')
    '''单步推理/3.7 双侧陈述外延差'''

    TEST_SINGLE_3_8 = TestFile('single_step/3.8', 'NAL-3.8 单句组合内涵交')
    '''单步推理/3.8 单句组合内涵交'''

    TEST_SINGLE_3_9 = TestFile('single_step/3.9', 'NAL-3.9 单句组合外延交')
    '''单步推理/3.9 单句组合外延交'''

    TEST_SINGLE_3_10 = TestFile('single_step/3.10', 'NAL-3.10 单句组合外延差')
    '''单步推理/3.10 单句组合外延差'''

    TEST_SINGLE_3_11 = TestFile('single_step/3.11', 'NAL-3.11 单句组合内涵差')
    '''单步推理/3.11 单句组合内涵差'''

    TEST_SINGLE_3_12 = TestFile('single_step/3.12', 'NAL-3.12 单句分解外延交')
    '''单步推理/3.12 单句分解外延交'''

    TEST_SINGLE_3_13 = TestFile('single_step/3.13', 'NAL-3.13 单句分解外延差')
    '''单步推理/3.13 单句分解外延差'''

    TEST_SINGLE_3_14 = TestFile('single_step/3.14', 'NAL-3.14 单句分解内涵交')
    '''单步推理/3.14 单句分解内涵交'''

    TEST_SINGLE_3_15 = TestFile('single_step/3.15', 'NAL-3.15 单句分解内涵差')
    '''单步推理/3.15 单句分解内涵差'''

    # * NAL-4 * #

    TEST_SINGLE_4_0 = TestFile('single_step/4.0', 'NAL-4.0 外延积转像',  # * ↓以下代码供「特别调参」演示
                               local_kill_java_timeouts=f_range(1.2, 2.0, 0.4))
    '''单步推理/4.0 外延积转像'''

    TEST_SINGLE_4_1 = TestFile('single_step/4.1', 'NAL-4.1 外延像转积1')
    '''单步推理/4.1 外延像转积1'''

    TEST_SINGLE_4_2 = TestFile('single_step/4.2', 'NAL-4.2 外延像转积2')
    '''单步推理/4.2 外延像转积2'''

    TEST_SINGLE_4_3 = TestFile('single_step/4.3', 'NAL-4.3 内涵积转像',  # * ↓以下代码供「特别调参」演示
                               local_kill_java_timeouts=f_range(1.2, 2.0, 0.4))
    '''单步推理/4.3 内涵积转像'''

    TEST_SINGLE_4_4 = TestFile('single_step/4.4', 'NAL-4.4 内涵像转积1')
    '''单步推理/4.4 内涵像转积1'''

    TEST_SINGLE_4_5 = TestFile('single_step/4.5', 'NAL-4.5 内涵像转积2')
    '''单步推理/4.5 内涵像转积2'''

    TEST_SINGLE_4_6 = TestFile('single_step/4.6', 'NAL-4.6 双侧陈述组合积')
    '''单步推理/4.6 双侧陈述组合积'''

    TEST_SINGLE_4_7 = TestFile('single_step/4.7', 'NAL-4.7 双侧陈述内涵像')
    '''单步推理/4.7 双侧陈述内涵像'''

    TEST_SINGLE_4_8 = TestFile('single_step/4.8', 'NAL-4.8 双侧陈述外延像')
    '''单步推理/4.8 双侧陈述外延像'''

    # * NAL-5 * #

    TEST_SINGLE_5_0 = TestFile('single_step/5.0', 'NAL-5.0 高阶修正')
    '''单步推理/5.0 高阶修正'''

    TEST_SINGLE_5_1 = TestFile('single_step/5.1', 'NAL-5.1 高阶演绎')
    '''单步推理/5.1 高阶演绎'''

    TEST_SINGLE_5_2 = TestFile('single_step/5.2', 'NAL-5.2 高阶举例')
    '''单步推理/5.2 高阶举例'''

    TEST_SINGLE_5_3 = TestFile('single_step/5.3', 'NAL-5.3 高阶归纳')
    '''单步推理/5.3 高阶归纳'''

    TEST_SINGLE_5_4 = TestFile('single_step/5.4', 'NAL-5.4 高阶归因')
    '''单步推理/5.4 高阶归因'''

    TEST_SINGLE_5_5 = TestFile('single_step/5.5', 'NAL-5.5 分离前推后')
    '''单步推理/5.5 分离前推后'''

    TEST_SINGLE_5_6 = TestFile('single_step/5.6', 'NAL-5.6 分离后推前')
    '''单步推理/5.6 分离后推前'''

    TEST_SINGLE_5_7 = TestFile('single_step/5.7', 'NAL-5.7 高阶比较同前项')
    '''单步推理/5.7 高阶比较同前项'''

    TEST_SINGLE_5_8 = TestFile('single_step/5.8', 'NAL-5.8 高阶比较同后项')
    '''单步推理/5.8 高阶比较同后项'''

    TEST_SINGLE_5_9 = TestFile('single_step/5.9', 'NAL-5.9 高阶类比')
    '''单步推理/5.9 高阶类比'''

    TEST_SINGLE_5_10 = TestFile('single_step/5.10', 'NAL-5.10 高阶类比带分离')
    '''单步推理/5.10 高阶类比带分离'''

    TEST_SINGLE_5_11 = TestFile('single_step/5.11', 'NAL-5.11 高阶相似传递')
    '''单步推理/5.11 高阶相似传递'''

    TEST_SINGLE_5_12 = TestFile('single_step/5.12', 'NAL-5.12 蕴含转等价')
    '''单步推理/5.12 蕴含转等价'''

    TEST_SINGLE_5_13 = TestFile('single_step/5.13', 'NAL-5.13 合取析取后组合')
    '''单步推理/5.13 合取析取后组合'''

    TEST_SINGLE_5_14 = TestFile('single_step/5.14', 'NAL-5.14 合取析取前组合')
    '''单步推理/5.14 合取析取前组合'''

    TEST_SINGLE_5_15 = TestFile('single_step/5.15', 'NAL-5.15 双前提合取分解')
    '''单步推理/5.15 双前提合取分解'''

    TEST_SINGLE_5_16 = TestFile('single_step/5.16', 'NAL-5.16 单合取条件消解')
    '''单步推理/5.16 单合取条件消解'''

    TEST_SINGLE_5_17 = TestFile('single_step/5.17', 'NAL-5.17 单析取条件消解')
    '''单步推理/5.17 单析取条件消解'''

    TEST_SINGLE_5_18 = TestFile('single_step/5.18', 'NAL-5.18 单元素析取组合')
    '''单步推理/5.18 单元素析取组合'''

    TEST_SINGLE_5_19 = TestFile('single_step/5.19', 'NAL-5.19 单合取元素分解')
    '''单步推理/5.19 单合取元素分解'''

    TEST_SINGLE_5_20 = TestFile('single_step/5.20', 'NAL-5.20 否定的定义')
    '''单步推理/5.20 否定的定义'''

    TEST_SINGLE_5_21 = TestFile('single_step/5.21', 'NAL-5.21 单句答否定')
    '''单步推理/5.21 单句答否定'''

    TEST_SINGLE_5_22 = TestFile('single_step/5.22', 'NAL-5.22 逆否')
    '''单步推理/5.22 逆否'''

    TEST_SINGLE_5_23 = TestFile('single_step/5.23', 'NAL-5.23 条件演绎消合取')
    '''单步推理/5.23 条件演绎消合取'''

    TEST_SINGLE_5_24 = TestFile('single_step/5.24', 'NAL-5.24 条件演绎消条件')
    '''单步推理/5.24 条件演绎消条件'''

    TEST_SINGLE_5_25 = TestFile('single_step/5.25', 'NAL-5.25 条件演绎换条件')
    '''单步推理/5.25 条件演绎换条件'''

    TEST_SINGLE_5_26 = TestFile('single_step/5.26', 'NAL-5.26 单条件归因取条件')
    '''单步推理/5.26 单条件归因取条件'''

    TEST_SINGLE_5_27 = TestFile('single_step/5.27', 'NAL-5.27 双条件归因取条件')
    '''单步推理/5.27 双条件归因取条件'''

    TEST_SINGLE_5_28 = TestFile('single_step/5.28', 'NAL-5.28 双条件归因消条件')
    '''单步推理/5.28 双条件归因消条件'''

    TEST_SINGLE_5_29 = TestFile('single_step/5.29', 'NAL-5.29 条件归纳')
    '''单步推理/5.29 条件归纳'''

    # * NAL-6 * #

    TEST_SINGLE_6_0 = TestFile('single_step/6.0', 'NAL-6.0 统一+修正')
    '''单步推理/6.0 统一+修正'''

    TEST_SINGLE_6_1 = TestFile('single_step/6.1', 'NAL-6.1 统一+演绎举例')
    '''单步推理/6.1 统一+演绎举例'''

    TEST_SINGLE_6_2 = TestFile('single_step/6.2', 'NAL-6.2 统一+与或归纳等价',
                               local_kill_java_timeouts=f_range(1.2, 2.0, 0.4))
    '''单步推理/6.2 统一+与或归纳等价'''

    TEST_SINGLE_6_3 = TestFile('single_step/6.3', 'NAL-6.3 统一+与或归因等价')
    '''单步推理/6.3 统一+与或归因等价'''

    TEST_SINGLE_6_4 = TestFile('single_step/6.4', 'NAL-6.4 统一+蕴含演绎换条件')
    '''单步推理/6.4 统一+蕴含演绎换条件'''

    TEST_SINGLE_6_5 = TestFile('single_step/6.5', 'NAL-6.5 统一+条件归因')
    '''单步推理/6.5 统一+条件归因'''

    TEST_SINGLE_6_6 = TestFile('single_step/6.6', 'NAL-6.6 统一+蕴含归因换条件')
    '''单步推理/6.6 统一+蕴含归因换条件'''

    TEST_SINGLE_6_7 = TestFile('single_step/6.7', 'NAL-6.7 消去+分离前推后')
    '''单步推理/6.7 消去+分离前推后'''

    TEST_SINGLE_6_8 = TestFile('single_step/6.8', 'NAL-6.8 消去+分离后推前')
    '''单步推理/6.8 消去+分离后推前'''

    TEST_SINGLE_6_9 = TestFile('single_step/6.9', 'NAL-6.9 消去+等价带分离')
    '''单步推理/6.9 消去+等价带分离'''

    TEST_SINGLE_6_10 = TestFile('single_step/6.10', 'NAL-6.10 消去+单合取条件消解')
    '''单步推理/6.10 消去+单合取条件消解'''

    TEST_SINGLE_6_11 = TestFile('single_step/6.11', 'NAL-6.11 消去+条件演绎消合取')
    '''单步推理/6.11 消去+条件演绎消合取'''

    TEST_SINGLE_6_12 = TestFile('single_step/6.12', 'NAL-6.12 消去+条件演绎消条件')
    '''单步推理/6.12 消去+条件演绎消条件'''

    TEST_SINGLE_6_13 = TestFile('single_step/6.13', 'NAL-6.13 多元消去+条件演绎消合取')
    '''单步推理/6.13 多元消去+条件演绎消合取'''

    TEST_SINGLE_6_14 = TestFile('single_step/6.14', 'NAL-6.14 多元消去+分离前推后')
    '''单步推理/6.14 多元消去+分离前推后'''

    TEST_SINGLE_6_15 = TestFile('single_step/6.15', 'NAL-6.15 多元消去+单合取条件消解')
    '''单步推理/6.15 多元消去+单合取条件消解'''

    TEST_SINGLE_6_16 = TestFile('single_step/6.16', 'NAL-6.16 多元消去+单合取条件消解')
    '''单步推理/6.16 多元消去+单合取条件消解'''

    TEST_SINGLE_6_17 = TestFile('single_step/6.17', 'NAL-6.17 引入@同前项')
    '''单步推理/6.17 引入@同前项'''

    TEST_SINGLE_6_18 = TestFile('single_step/6.18', 'NAL-6.18 引入@同后项')
    '''单步推理/6.18 引入@同后项'''

    TEST_SINGLE_6_19 = TestFile('single_step/6.19', 'NAL-6.19 引入+蕴含合取')
    '''单步推理/6.19 引入+蕴含合取'''

    TEST_SINGLE_6_20 = TestFile('single_step/6.20', 'NAL-6.20 多元引入+合取条件')
    '''单步推理/6.20 多元引入+合取条件'''

    TEST_SINGLE_6_21 = TestFile('single_step/6.21', 'NAL-6.21 多元引入@合取')
    '''单步推理/6.21 多元引入@合取'''

    TEST_SINGLE_6_22 = TestFile('single_step/6.22', 'NAL-6.22 递归')
    '''单步推理/6.22 递归'''

    TEST_SINGLE_6_23 = TestFile('single_step/6.23', 'NAL-6.23 二层统一@合取')
    '''单步推理/6.23 二层统一@合取'''

    TEST_SINGLE_6_24 = TestFile('single_step/6.24', 'NAL-6.24 二层统一@蕴含')
    '''单步推理/6.24 二层统一@蕴含'''

    TEST_SINGLE_6_25 = TestFile('single_step/6.25', 'NAL-6.25 二层引入+归纳')
    '''单步推理/6.25 二层引入+归纳'''

    TEST_SINGLE_6_26 = TestFile('single_step/6.26', 'NAL-6.26 消去+演绎')
    '''单步推理/6.26 消去+演绎'''

    TEST_SINGLE_6_27 = TestFile('single_step/6.27', 'NAL-6.27 消去+归因')
    '''单步推理/6.27 消去+归因'''

    if False:  # * 📝【2024-05-24 17:35:12】这些测试不在正规测试内，仅自OpenNARS源码迁移
        # ! ⚠️【2024-05-24 17:36:13】目前除`birdClaimedByBob`能被OpenNARS 3.0.4通过外，其它推理器均在这些测试中失败
        TEST_SINGLE_6_birdClaimedByBob = TestFile(
            'single_step/6.birdClaimedByBob', 'NAL-6.birdClaimedByBob')
        '''单步推理/6.birdClaimedByBob'''

        TEST_SINGLE_6_can_of_worms = TestFile(
            'single_step/6.can_of_worms', 'NAL-6.can_of_worms')
        '''单步推理/6.can_of_worms'''

        TEST_SINGLE_6_nlp1 = TestFile('single_step/6.nlp1', 'NAL-6.nlp1')
        '''单步推理/6.nlp1'''

        TEST_SINGLE_6_nlp2 = TestFile('single_step/6.nlp2', 'NAL-6.nlp2')
        '''单步推理/6.nlp2'''

        TEST_SINGLE_6_redundant = TestFile(
            'single_step/6.redundant', 'NAL-6.redundant')
        '''单步推理/6.redundant'''

        TEST_SINGLE_6_symmetry = TestFile(
            'single_step/6.symmetry', 'NAL-6.symmetry')
        '''单步推理/6.symmetry'''

        TEST_SINGLE_6_uncle = TestFile('single_step/6.uncle', 'NAL-6.uncle')
        '''单步推理/6.uncle'''

        # ! ↓目前此测试的测试时间过长，故不纳入默认测试中
        TEST_STABILITY_1_6 = TestFile(
            '1-6.stability', 'NAL 1-6 长期稳定性')

    # * NAL-7 * #

    TEST_SINGLE_7_0 = TestFile('single_step/7.0', 'NAL-7.0 时间演绎举例')
    '''单步推理/7.0 时间演绎举例'''
    # * ✅【2024-05-14 21:31:55】↑在OpenNARS 3.1.2中成功

    TEST_SINGLE_7_1 = TestFile('single_step/7.1', 'NAL-7.1 时间归纳对比')
    '''单步推理/7.1 时间归纳对比'''
    # * ✅【2024-05-14 22:14:34】↑在OpenNARS 3.1.2中成功

    # ! 📝【2024-05-14 21:30:09】NAL-8、NAL-9 均在OpenNARS 3.1.2上表现不佳——未能完全实现功能
if 测试区域结束 := False:  # ! ↓分界线之下均不开始测试
    pass
