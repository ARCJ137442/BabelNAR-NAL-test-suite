'''BabelNAR工具链
- 🚩调用BabelNAR CLI，启动、运行与自动测试NARS
    - 📄使用Python`subprocess`：https://docs.python.org/3/library/subprocess.html
'''
import subprocess
from subprocess import CompletedProcess, Popen
from typing import Iterable, List, Optional, Union
import re
from util import *
from time import time, sleep


class ProcessResult:
    '''进程结果
    - 📄CompletedProcess | Popen
    - 🎯兼容并预处理`CompletedProcess`与`Popen`的内容
      - 退出码
      - 标准输入/标准输出/标准错误
    '''

    args: str
    '''子进程启动命令（一个字符串）'''

    returncode: int
    '''子进程终止码
    - 📝`CompletedProcess`与`Popen`均有
    '''

    stdout: bytes
    '''子进程的标准输出（必须有）'''

    stderr: bytes
    '''子进程的标准错误（必须有）'''

    def from_popen(self, process: Popen) -> None:
        '''从`Popen`初始化对象
        - 🎯【2024-05-09 15:54:49】现在主要使用**可并行运行**的`subprocess.Popen`而不再使用`subprocess.run`
        - ⚠️对标准输出、标准错误的`read`会造成主进程阻塞：Java进程未关闭导致整体被阻塞
        '''
        # 命令行参数
        if isinstance(process.args, str):
            self.args = process.args
        if isinstance(process.args, list):
            self.args = ' '.join(process.args)
        else:
            self.args = str(process.args)

        # 退出码
        self.returncode = process.returncode

        # 标准输出/标准错误
        assert process.stdout is not None
        assert process.stderr is not None
        self.stdout = process.stdout.read()
        process.stdout.close()
        self.stderr = process.stderr.read()
        process.stderr.close()

    def from_completed_process(self, process: CompletedProcess):
        '''从`CompletedProcess`初始化对象
        - 🎯适配旧的`subprocess.CompletedProcess`类型
        '''
        # 命令行参数
        self.args = str(process.args)

        # 退出码
        self.returncode = process.returncode

        # 标准输出/标准错误 | 🚩【2024-05-09 15:57:53】此环境下直接赋值
        self.stdout = process.stdout
        self.stderr = process.stderr

    def __init__(self, process: Union[CompletedProcess, Popen]) -> None:
        '''从一个`subprocess`的「子进程」对象转换
        - 🎯将外部模块结果进行检验、转换，变为更易处理的结果
        '''
        if isinstance(process, Popen):
            return self.from_popen(process)
        elif isinstance(process, CompletedProcess):
            return self.from_completed_process(process)


class TestResult:
    '''NAL测试结果'''

    success: bool
    '''测试是否成功
    - 🚩标准：启动并预置`.nal`的BabelNAR CLI是否正常终止
      - 正常终止 ⇒ exe退出码0 ⇒ success = True
      - CLI panic ⇒ exe退出码非0 ⇒ success = False
    '''

    success_cycles: List[int]
    '''测试成功时，推理了多少步
    - 🚩标准：搜索BabelNAR CLI标准输出中的`expected-cycle(【步数】)`模式
      - 执行成功 ⇒ 内含多个数值
      - 执行失败 ⇒ 往往没有数值
    '''

    launch_cmd_args: str
    '''测试的启动命令
    - 🚩直接对应子进程的`args`属性
    '''

    output_std: Optional[str]
    '''测试程序的输出
    - 🎯用于检查测试程序输出
      - 📄检查「推理了多少步才推出结果」
    - 🚩直接对应子进程的`stdout`属性
    '''

    output_err: Optional[str]
    '''测试程序的输出，但一般对应「错误」
    - 🎯用于检查测试程序输出（错误）
      - 📄用于程序调试
    - 🚩直接对应子进程的`stderr`属性
    '''

    time_diff: float
    '''测试程序的总体运行时间（秒）
    - 🎯用于测量程序的整体运行时间
      - **⚠️相比「推理步数」不具有普遍意义**
        - 📌不同计算机运行的不同NARS实现，可能有不同的运行时间
        - ❌对于一些【只能通过「超时杀进程」方式结束运行】的NARS实现 **无效**
    '''

    class TryDecodeException(Exception):
        '''尝试解码的错误
        - 📌包含所有解码错误
        - 🎯在最终解码导致错误后，能追溯并追踪每个编码的解码错误
        - 📄UTF-8、GBK均未能解码 ⇒ 报错 ⇒ 由此回溯两个解码错误的信息（无效字符 等）
        '''

        exceptions: List[BaseException]
        '''收集的所有错误对象'''

        def __init__(self, exceptions: List[BaseException]) -> None:
            self.exceptions = exceptions

    @ staticmethod
    def try_decode(text: bytes, encodings: List[str]) -> str:
        '''尝试为文本解码
        - 🚩尝试按顺序为文本解码，遇到错误则向下跳转
          - 📄UTF-8解码错误 ⇒ 尝试GBK
        - 🎯尽可能兼容并解决编码问题，同时将错误封闭在程序中（而非抛给用户）
        '''
        errors = []
        for encoding in encodings:
            try:
                # 尝试解码并返回
                return text.decode(encoding)
            except BaseException as e:
                # 报错⇒追加（方便后续追踪）
                errors.append(e)
        # 若均未能解码 ⇒ 抛异常
        raise TestResult.TryDecodeException(errors)

    def __init__(
        self,
        success: bool,
        success_cycles: List[int],
        launch_cmd_args: str,
        output_std: Optional[str],
        output_err: Optional[str],
        time_diff: float,
    ):
        '''从纯参数中构造
        - 🎯【2024-05-26 23:29:14】用于从JSON中重建结果
        '''
        self.success = success
        self.success_cycles = success_cycles
        self.launch_cmd_args = launch_cmd_args
        self.output_std = output_std
        self.output_err = output_err
        self.time_diff = time_diff

    @staticmethod
    def __default__() -> 'TestResult':
        '''构造默认「结果」
        - 🎯全空值
        - 构造全空值，以便后续覆盖属性
        '''
        return TestResult(
            success=False,
            success_cycles=[],
            launch_cmd_args='',
            output_std=None,
            output_err=None,
            time_diff=0,
        )

    @staticmethod
    def from_process_result(process: ProcessResult, time_diff: float, *, encodings: List[str] = ['utf-8', 'gbk']) -> 'TestResult':
        '''构造函数，直接从进程得来
        - 🚩从子进程获取测试结果

        Args:
            process(ProcessResult): 待转换的进程结果
            encodings(str, optional): 输出编码，默认值 = 'utf-8'
        '''

        # 退出码 ⇒ 是否成功
        success = process.returncode == 0

        # 转换命令行参数
        launch_cmd_args = process.args

        # 转换输出，标准输出&标准错误
        # * 📌【2024-04-26 11:32:49】有可能遇到编码问题：`stderr`还是GBK编码
        # * 📄转换「标准错误」时出现：`\r\nprogram exited with EOF\xb4\xed\xce\xf3: \xc3\xbb\xd3\xd0\xd5\xd2\xb5\xbd\xbd\xf8\xb3\xcc "4008"\xa1\xa3\r\n`
        try:
            output_std = TestResult.try_decode(process.stdout, encodings)
        except BaseException as e:
            print(f'转换「标准输出」时出现错误：{e}\n标准错误：{repr(process.stdout)}')
            output_std = None
        try:
            output_err = TestResult.try_decode(process.stderr, encodings)
        except BaseException as e:
            print(f'转换「标准错误」时出现错误：{e}\n标准错误：{repr(process.stderr)}')
            output_err = None

        # 从标准输出中提取「成功步数」
        success_cycles = [
            int(num_str)
            for num_str in re.findall(r'expect-cycle\(([0-9]+)\)', output_std)
        ] if output_std else []

        # 耗时
        time_diff = time_diff

        # 构造 & 返回
        return TestResult(
            success=success,
            success_cycles=success_cycles,
            launch_cmd_args=launch_cmd_args,
            output_std=output_std,
            output_err=output_err,
            time_diff=time_diff,
        )

    @ staticmethod
    def from_process(process: Popen, *args, **kwargs) -> 'TestResult':
        '''从子进程获取测试结果
        - 🚩直接转发到构造函数
        '''
        process_result = ProcessResult(process)
        return TestResult.from_process_result(process_result, *args, **kwargs)

    def __str__(self) -> str:
        '''字符串格式化
        - 🚩使用简体中文格式化测试结果信息
        '''
        cycles_head = (
            f'在{self.success_cycles[0]}步后'
            if len(self.success_cycles) == 1 else '')
        cycles_term = (
            '- 成功的步数：分别为' + "、".join(map(str, self.success_cycles))
            if len(self.success_cycles) > 1 else '')
        return f'''\
测试结果：{cycles_head}{'✅成功' if self.success else '❌失败'}
- 运行耗时：{self.time_diff:.2f}s
- 输出：{repr(TestResult.__str__long_str(self.output_std) if self.output_std else '无')}
- 错误输出：{repr(TestResult.__str__long_str(self.output_err) if self.output_err else '无')}
{cycles_term}
        '''.strip()

    @ staticmethod
    def __str__long_str(s: str, max_len: int = 50) -> str:
        '''展示长字符串'''
        if len(s) > max_len:
            return s[:max_len] + '...'
        else:
            return s

    def to_json(self) -> dict:
        '''将测试数据转换为JSON字符串
        - 🎯后续可将其存储
        - 🚩【2024-05-14 15:13:44】目前只将其转换为字典
          - 📌后续要转换为字符串时再转换为字符串
        - 🔗参考：https://stackoverflow.com/questions/11637293/iterate-over-object-attributes-in-python
        '''
        o = {
            # 键值对
            key: value
            # 只在「变量列表」中
            for (key, value) in self.__dict__.items()
            # 获取「全小写」「非内部」「不可调用」的属性
            if (
                key.lower() == key and  # 全小写（筛掉内部类）
                not key.startswith('_') and  # 键的开头不是下划线（筛掉内部属性）
                not callable(value)  # 不可调用（筛掉方法）
            )
        }
        return o

    @staticmethod
    def from_json(json: dict) -> 'TestResult':
        '''将JSON字符串转换为测试数据
        - ⚠️不稳定：容易解析出异常情况
          - 📄多余/缺少键值对
          - 📄字段值类型错误
        - 🚩【2024-05-11 16:52:32】目前直接使用「批量遍历键值对⇒设置值」的方法
        '''
        # 构造默认空对象
        self = TestResult.__default__()
        # 填充字段
        for (key, value) in json.items():
            self.__setattr__(key, value)
        # 返回
        return self

    def process_invalid(self) -> bool:
        '''是否进程无效
        - 🎯用于判断「测试OpenNARS时，进程是否意外终止」
            - 📌【2024-05-30 10:01:40】现象：有些测试实际上是「Java环境不稳定，导致OpenNARS提前终止」导致的测试失败
            - 🚩【2024-05-30 10:02:32】目前处理办法：遇到此类情况，直接重做
        '''
        return (
            self.output_std is not None
            and '子进程已关闭' in self.output_std  # 🚩判断标准输出是否意外终止（⚠️仅中文）
        ) or (
            self.output_err is not None
            and 'SendError' in self.output_err  # 🚩判断BabelNAR CLI是否存在「消息发送失败」情况
        )


KillJavaTimeouts = Optional[Iterable[float]]
'''杀Java超时时间（迭代器）
- 🔧值含义
      - `None` ⇒ 不杀Java
      - 迭代器 ⇒ 超时时间（秒）的迭代器，每次尝试中迭代出一个浮点作为「超时时间」
- 🚩使用逻辑：不断从中迭代出浮点数作为「超时杀Java时间」，若迭代完则视作「失败」
- ℹ️配合`f_range`使用，以灵活控制测试时间
'''


class TestFile:
    '''测试文件的名称
    - 🎯提供统一、语义明确的字符串常量池
    '''

    name: str
    '''测试被人所称呼的名称
    - 📄"NAL-1 演绎规则"
    - 📄示例："单步推理 NAL-1.0 修正"
    '''

    nal_index_name: str
    '''用于链接NAL测试文件的「内部名称」
    - 📄BabelNAR CLI配置`【名称】.hjson`
    - 📄`.nal`测试文件的名称
    - 📄示例："1.0"
    '''

    local_kill_java_timeouts:  KillJavaTimeouts
    '''局部「限时杀Java」超时时间范围
    - 📌现在作为一个「范围」工作
      - 🚩逐个遍历其中的浮点数
    - 🎯测试时间分配的灵活性
      - ⚠️在耗时长的特殊测试中，对OpenNARS放宽时间要求
    - 📌与[`NARSType.global_kill_java_timeouts`]的「限时杀Java」含义类似
    - 🚩**具体生效逻辑**：
      - 全局「不杀Java」 ⇒ 不杀
      - 全局「杀Java」 + 此项为负 ⇒ 仍杀Java
      - 均「杀Java」 ⇒ 覆盖「全局超时时间」继续杀Java
    '''

    def __init__(
        self,
        nal_index_name: str,
        name: Optional[str] = None,
        *,
        local_kill_java_timeouts: KillJavaTimeouts = None
    ):
        self.nal_index_name = nal_index_name
        self.name = name if name else 'NAL测试'
        self.local_kill_java_timeouts = local_kill_java_timeouts

    @staticmethod
    def from_file_path(
        file_path: str,
        *,
        local_kill_java_timeouts: KillJavaTimeouts = None
    ) -> 'TestFile':
        '''从文件路径获取测试文件'''
        from os.path import basename
        nal_index_name = (
            '.'.join(basename(file_path).split('.')[:-1])
            if '.' in file_path
            else file_path
        )
        name = f'NAL测试 {nal_index_name}'
        return TestFile(
            nal_index_name,
            name,
            local_kill_java_timeouts=local_kill_java_timeouts
        )

    def nal_level(self) -> str:
        '''获取NAL层级
        - 🎯后续按层级分组测试
        - 🚩直接按中间的「.」拆分取首个
        - 📄"1.0" => "1"
        - 📄"123" => "123"
        '''
        return self.nal_index_name.split('.')[0]

    def nal_order(self) -> str:
        '''获取NAL顺序
        - 🎯后续在分组中用于排序
        - 🚩直接按中间的「.」拆分取末个
        - 📄"1.0" => "0"
        '''
        return self.nal_index_name.split('.')[-1]

    def actual_kill_java_timeouts(self, global_timeout: KillJavaTimeouts) -> KillJavaTimeouts:
        '''计算「实际Java超时时长」
        - 📌结合「全局Java超时时长」与自身的「局部Java超时时长」
        - 🚩**具体生效逻辑**：
          - 全局「不杀Java」 ⇒ 不杀
          - 全局「杀Java」 + 此项为空 ⇒ 仍杀Java
          - 均「杀Java」 ⇒ 覆盖「全局超时时间」继续杀Java
        '''
        # 全局「不杀Java」 ⇒ 不杀
        if global_timeout is None:
            return global_timeout
        # 全局「杀Java」 + 此项为空 ⇒ 仍杀Java
        elif self.local_kill_java_timeouts is None:
            return global_timeout
        # 均「杀Java」 ⇒ 覆盖「全局超时时间」继续杀Java
        else:
            return self.local_kill_java_timeouts


class NARSType:
    '''可用于启动「交互式脚本」「NAL测试」的NARS类型
    - 🎯用于调用侧快捷使用
        - 📄如`self.shell()`
        - 📄如`self.test_nal('1.0')`
    '''

    name: str
    '''NARS类型名称
    - 📄OpenNARS
    - 📄ONA
    - 📄PyNARS
    '''

    launch_config_path: str
    '''启动用配置文件的路径'''

    global_kill_java_timeouts: KillJavaTimeouts
    '''全局「超时杀Java」时长
    - 🎯决定「是否需要在每次测试时杀死Java进程」以及测试时的超时时间
    - 🔧参数含义：见[`KillJavaTimeouts`]
    - 📌会被具体测试覆盖（若有）
      - 📄参见[`TestFile.local_kill_java_timeouts`]
    '''

    def __init__(self, name: str, *,
                 launch_config_path: str,
                 global_kill_java_timeouts:     KillJavaTimeouts = None) -> None:
        self.name = name
        self.launch_config_path = launch_config_path
        self.global_kill_java_timeouts = global_kill_java_timeouts

    def shell(self):
        '''使用`类型.shell()`调用shell脚本
        - 🎯方便使用者调用
        `'''
        return run_shell(self.launch_config_path)

    def test_nal(self, test_file: TestFile, *,
                 silent: bool = False,
                 show_verbose: bool = False,
                 show_interactive: bool = False,
                 ) -> TestResult:
        '''使用`类型.test_nal()`调用nal测试
        - 🎯方便使用者调用

        Args:
            test_name (str): 测试文件名
            silent (bool, optional): 是否静默运行（默认否）
            show_verbose (bool, optional): 是否显示详细测试信息（默认否）
            show_interactive (bool, optional): 是否交互显示测试信息（默认否）
        `'''

        # 准备 #

        # 计算得到「超时杀Java」配置
        kill_java_timeouts = test_file.actual_kill_java_timeouts(
            self.global_kill_java_timeouts)

        # 准备「测试结果」变量
        result: Optional[TestResult] = None

        # 测试 #

        # 若为空⇒直接开始一次性测试
        if kill_java_timeouts is None:
            result = run_test_nal(self.launch_config_path,
                                  test_file.nal_index_name)
        # 不为空⇒遍历其中所有「超时杀Java」时长，只要一个成功，即退出——否则失败
        else:
            # 遍历其中所有「超时杀Java」时长
            for timeout in kill_java_timeouts:
                avoid_timeout = 1
                while True:
                    result = run_test_nal(self.launch_config_path,
                                          test_file.nal_index_name,
                                          kill_java_timeouts=timeout)
                    # 只返回「进程有效」的结果
                    if result.process_invalid():
                        print(f'测试进程意外终止！指数退避{avoid_timeout}s，重新组织测试中……')
                        sleep(avoid_timeout)
                        avoid_timeout *= 2
                    else:
                        break
                # 只要一个成功，即退出——否则失败
                if result.success:
                    break
        assert result is not None  # 检验非空（一般不会发生）

        # 展示结果 #

        # 非静默 ⇒ 展示结果（附加传参）
        if not silent:
            show_result(result,
                        verbose=show_verbose,
                        user_interactive=show_interactive)

        # 返回结果 #
        return result


def __build_cli_launch_cmd(*config_paths: str) -> List[str]:
    '''构建BabelNAR CLI启动命令
    - ✨可以同时引入多个配置文件
        - 📌按**从先往后**的顺序覆盖其中的配置项
    - ⚠️需要自行输入「启动」配置
    '''
    # exe前缀
    from constants import BABELNAR_CLI
    cmd = [BABELNAR_CLI]
    # 加入路径
    for config_path in config_paths:
        cmd.extend(['-c', config_path])
    # 返回
    return cmd


def __run_cli_with_configs(*config_paths: str, interactive: bool = False, kill_java_timeouts: float = -1) -> Union[CompletedProcess, Popen]:
    '''通过配置文件启动BabelNAR CLI
    - 🚩构建启动命令，启动BabelNAR CLI子进程，通过配置调用NARS，最终输出结果
    - ⚠️会阻塞整个程序运行
    '''
    # 构建启动命令
    cmd = __build_cli_launch_cmd(*config_paths)

    # 启动 & 获取结果
    # * 📝使用`capture_output`参数捕获子进程的输出，并保存到`stdout`和`stderr`属性中
    # print(f'已使用命令启动BabelNAR CLI：`{" ".join(cmd)}`') # * 🚩【2024-05-09 16:47:45】太长，不用
    # * 🚩【2024-05-09 15:08:59】自动杀死Java
    # subprocess.Popen(KILL_JAVA_CMD)
    if not interactive:
        # * 🚩「超时杀死Java进程」逻辑
        # * ⚠️若需强制杀死Java进程以避免程序阻塞，则需要`kill_java_timeouts`>=0
        # * 🎯【2024-05-09 15:52:41】目前仍然无法从BabelNAR CLI避免「Java残留进程阻塞工具链」的问题
        if kill_java_timeouts >= 0:
            # 并行启动，然后间隔一段时间杀死Java进程
            process = subprocess.Popen(cmd,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
            # * ⚠️【2024-05-09 16:43:34】`process.poll()`也会造成主进程阻塞，不用
            # * 🚩【2024-05-09 16:44:19】现在无论如何都要kill掉Java进程
            sleep(kill_java_timeouts)
            process.kill()
            subprocess.Popen(['taskkill', '-f', '-im', 'java.exe'])

            # 返回结束了的子进程（Popen形式）
            return process
        # * 🚩正常逻辑：直接调用`subprocess.run`，返回一个`CompletedProcess`对象
        # * ⚠️【2024-05-09 17:02:28】若对Python版本（直接用`python.exe`启动）使用`Popen`，在「失败情形」下会导致主进程阻塞
        #   * 📝能成功运行并得到「测试失败」结果，但子进程结束时卡在stdout上（去掉`stdout=`反而可以正常结束）
        else:
            completed_process = subprocess.run(
                cmd, shell=True, capture_output=True)
            # 若无需特别处理「超时杀Java」逻辑，直接等待即可
            return completed_process
    else:
        # 创建并返回结束了的子进程
        process = subprocess.Popen(cmd)
        process.wait()
        return process
        # return subprocess.run(cmd, capture_output=not interactive)


def run_shell(launch_config_path: str):
    '''运行交互式命令行
    - 🚩运行BabelNAR CLI，并启动相应NARS版本的交互式终端
    '''
    # 只传入一个「启动」配置，并且是交互式的
    __run_cli_with_configs(launch_config_path, interactive=True)


def run_test_nal(
        launch_hjson_path: str,
        nal_hjson_name: str,
        kill_java_timeouts: float = -1) -> TestResult:
    '''运行指定的NAL测试文件，并返回结果
    - 🎯灵活方便地调用各类测试

    Args:
        launch_hjson_path(str): 启动的配置文件路径（用于启动CIN）
        nal_hjson_name(str): NAL测试配置名，如`1.0`
        kill_java_timeouts(float): 是否启用「超时杀Java进程」机制，及超时时间；默认为-1，表示不等待
    Returns:
        TestResult: 测试结果
    '''
    # 构建完整的「NAL预加载」配置文件路径
    from constants import CONFIG_NAL, CONFIG_NAL_PRELUDE
    NAL_HJSON_PATH = CONFIG_NAL + f'{nal_hjson_name}.hjson'

    # 计时器准备
    now = time()

    # 启动BabelNAR CLI，获取进程运行结果
    run_result = __run_cli_with_configs(
        launch_hjson_path, CONFIG_NAL_PRELUDE, NAL_HJSON_PATH,
        kill_java_timeouts=kill_java_timeouts
    )

    # 计算时间差（秒）
    dt = time() - now

    # 将运行结果转换为「进程结果」
    process_result = ProcessResult(run_result)

    # 返回测试结果
    return TestResult.from_process_result(process_result, dt)


def configure_io_encoding():
    '''配置输入输出编码
    - 🚩强制规定输入输出使用UTF-8
    - 🎯避免GBK编码进程IO导致的「中文乱码」问题
    '''
    from sys import stdin, stdout
    stdin.reconfigure(encoding='utf-8')  # type: ignore
    stdout.reconfigure(encoding='utf-8')  # type: ignore


def show_result(result: TestResult, verbose: bool = False, user_interactive: bool = False, n_paging: int = 0):
    '''展示NAL测试结果
    - 🚩【2024-06-07 20:01:32】现在对过长的输出采用「分页翻页」的方式

    Args:
        result(TestResult): 测试结果
        verbose(bool): 是否详细展示输出（可能会过于冗长）
        user_interactive(bool): 是否与用户交互，默认为False（不与用户交互）
    Returns:
        None
    '''
    # 总是展示结果概要
    show(result)
    # 若启用「详细」则开始详细展示
    if verbose:
        if user_interactive:
            input('按下回车键查看详细结果：')
        if result.output_std:
            print(f'标准输出 = """\n')
            _show_output(result.output_std.strip(), n_paging=n_paging)
            print('\n"""')
        if result.output_err:
            print(f'错误输出 = """\n')
            _show_output(result.output_err.strip(), n_paging=n_paging)
            print('\n"""')


def _show_output(output: str, n_paging: int = 100):
    '''展示输出
    - 📝【2024-06-07 20:17:43】Python的print对长字符串会限制输出长度
    - 🎯展示长字符串输出，当行数过多时分页呈现
    - 📜0表示不分页
    '''
    lines = output.splitlines()
    paging_counter = 0
    n_lines = len(lines)
    for i, line in enumerate(lines):
        paging_counter += 1
        if paging_counter == n_paging:  # `0`表示不分页
            paging_counter = 0
            input(
                f'---- 第 {(i+1)//n_paging}/{n_lines//n_paging} 页 按下回车键以继续({i+1}/{len(lines)}) ----')
        print(line)
