from typing import Callable, Dict, Tuple
from toolchain import *
import constants
from util import *

# 总是设置默认编码
configure_io_encoding()


def all_nars_types() -> List[NARSType]:
    '''获取所有可用的NARS类型'''
    return sorted([
        getattr(constants, t)
        for t in dir(constants)
        if isinstance(getattr(constants, t), NARSType)
    ], key=lambda t: t.name)


def all_test_files() -> List[TestFile]:
    '''获取所有可用的测试文件
    - 🚩【2024-05-14 22:23:13】采用「NAL第二序号补零到两位」的形式
      - 🎯解决「"10"排序反在前」的问题
      - ✅基本不会对后面「非数字字符串」产生影响（英文名均超过两位）
    '''
    return sorted([
        getattr(constants, t)
        for t in dir(constants)
        if isinstance(getattr(constants, t), TestFile)
    ], key=lambda t: f'{t.nal_order():>04}')


ALL_NARS_TYPES = all_nars_types()
'''所有可用的NARS类型'''

ALL_TEST_FILES = all_test_files()
'''所有可用的测试文件'''

CrossTestResult = Dict[Tuple[NARSType, TestFile], TestResult]
'''交叉测试的返回类型
- 🎯复用
'''


def perform_cross_tests(
    nars_types: List[NARSType] = ALL_NARS_TYPES,
    test_files: List[TestFile] = ALL_TEST_FILES,
    *,
    verbose_on_success: bool = True,
    verbose_on_fail: bool = True,
) -> CrossTestResult:
    '''开展交叉测试
    - 🚩对所有「NARS类型」与所有「测试文件」进行交叉测试
    - 🚩测试顺序：在每个「测试文件」上对每个「NARS类型」测试
        - 🎯方便看到**同一测试在不同NARS上的表现**
    - 🚩返回在所有NARS上所有测试的结果

    Args:
        nars_types: NARS类型列表
        test_files: 测试文件列表
        verbose_on_fail: 测试失败时是否打印详细日志
    '''

    def test_one(nars_type: NARSType, test_file: TestFile) -> TestResult:
        '''测试一个NARS类型与一个测试文件'''
        # 测试（静音）
        result = nars_type.test_nal(test_file, silent=True)
        # 成功：提示
        if result.success:
            print(
                f'✅ {nars_type.name} @ {test_file.name} in {result.success_cycles} steps')
            if verbose_on_success:
                show_result(result, verbose=True)
        # 失败且开启了「失败时打印详细日志」 ⇒ 打印详细日志
        else:
            print(f'❌ {nars_type.name} @ {test_file.name}')
            if verbose_on_fail:
                show_result(result, verbose=True)
        # print(f'JSON: {result.to_json()}')
        # 返回
        return result

    # 生成结果并返回
    return {
        (nars_type, test_file): test_one(nars_type, test_file)
        for test_file in test_files  # 优先遍历测试文件
        for nars_type in nars_types  # 然后才是NARS类型
    }


CrossTestResultToShow = Dict[Tuple[str, str], TestResult]
'''交叉测试结果的展示格式
- 🚩只需要「推理器名」和「测试名」
- 🎯用于在「读取结果JSON文件」时 无需存储名
- 🎯其结果可与JSON实现完全互转
'''


def result_to_show(results: Union[CrossTestResult, CrossTestResultToShow]) -> CrossTestResultToShow:
    '''将交叉测试结果转换为展示格式
    - 🚩已经是「展示格式」⇒直接返回；并非「展示结果」⇒取其中的「推理器名」「测试名」
    '''
    is_result_to_show: bool = any(
        isinstance(nars, NARSType) or isinstance(test, TestFile)
        for (nars, test), _ in results.items()
    )
    '''是否为「展示格式」
    - ⚠️不可直接用`isinstance(results, CrossTestResult)
    '''

    if is_result_to_show:  # 输入为「交叉测试结果」
        return {
            (nars_type.name, test_file.name): result  # type: ignore
            for (nars_type, test_file), result in results.items()
        }
    else:  # 输入为「展示格式」
        return results  # type: ignore


def cross_test_str_table(results: Union[CrossTestResult, CrossTestResultToShow]) -> str:
    '''呈现交叉测试结果
    - 🚩返回交叉测试的结果，不产生副作用
    '''
    results = result_to_show(results)

    # 构建表格 #

    table: List[List[str]] = []
    '''表格：字符串二维数组'''

    # 表头
    table.append(["推理器类型", "推理测试名称", "🎯", "步数", "运行耗时(秒)"])

    # 表格
    for (nars_name, test_name), result in results.items():
        # 成功与否
        success = '✅' if result.success else '❌'
        # 成功步数/失败（不显示）
        steps = str(result.success_cycles) if result.success_cycles else ''
        # 添加一行
        table.append([
            nars_name,
            test_name,
            success,
            steps,
            f'{result.time_diff:.3f}'])

    # 折叠
    return fold_table(table)


# 折叠
def fold_table(rows: List[List[str]]) -> str:
    '''折叠一行
    - 🚩折叠到「max_num_full_scale_chars」
    '''

    # 预先返回与检验 #
    if is_empty(rows):  # 啥都没有
        return ''

    if not is_same(map(len, rows)):
        raise Exception('表格列数不一致')

    table = ''
    # 先计算「最大显示长度」
    row_max_display_len = [
        max(
            len_display(row[i_col])  # 获取当前列的「显示长度」
            for row in rows  # 遍历每一列
        )
        for i_col in range(len(rows[0]))  # 遍历每一行
    ]

    # 然后开始构造表格
    for row in rows:
        table += '    | '
        for col_i, col in enumerate(row):
            table += pad_display_spaces(col, row_max_display_len[col_i])
            # join逻辑
            if col_i != len(row) - 1:  # 不是最后一列
                table += '\t| '
            else:  # 最后一列
                table += '|'
        table += '\n'

    # 返回
    return table


def default_group_name(file: TestFile):
    '''默认的「NAL-层级」分类函数'''
    return f'NAL-{file.nal_level()}'


GroupTestResult = Dict[str,  CrossTestResult]
'''分组测试的返回类型'''

GroupTestResultToShow = Dict[str, CrossTestResultToShow]
'''分组测试的返回类型（展示用）'''


def group_test(
    nars_types: List[NARSType] = ALL_NARS_TYPES,
    test_files: List[TestFile] = ALL_TEST_FILES,
    group_name: Callable[[TestFile], str] = default_group_name,
    *,
    verbose_on_success: bool = True,
    verbose_on_fail: bool = True,
) -> GroupTestResult:
    '''分组测试
    - 🎯分「NAL层级」等标准，展示时可按照组别展示
    '''
    groups: Dict[str, List[TestFile]] = {}

    for file in test_files:
        name = group_name(file)
        if name in groups:
            groups[name].append(file)
        else:
            groups[name] = [file]

    sorted_groups = sorted(groups.items(), key=lambda t: t[0])

    # 分组开展测试
    return {
        name: perform_cross_tests(
            nars_types=nars_types,
            test_files=files,
            verbose_on_success=verbose_on_success,
            verbose_on_fail=verbose_on_fail,
        )
        for (name, files) in sorted_groups
    }


def jsonify_group_test(result: GroupTestResult) -> dict:
    '''存储分组测试结果
    - 🎯持久化完整地存储「分组测试」的结果
    - 🎯方便后续分析
    - 🚩目前转换为一个字典，此举无需依赖`json`标准库
    '''

    # 构造数据 #
    data = {}

    # 注入数据 #
    for (group_name, cross_result) in result.items():
        group_data: Dict[str, Dict[str, dict]] = {}
        # Dict[Tuple[NARSType, TestFile], TestResult]
        # 分两层：测试文件→推理器类型
        for ((nars_type, test_file), test_result) in cross_result.items():
            if test_file.name not in group_data:
                group_data[test_file.name] = {}
            file_test_data: Dict[str, dict] = group_data[test_file.name]
            if nars_type.name not in file_test_data:
                file_test_data[nars_type.name] = {}
            file_test_data[nars_type.name] = test_result.to_json()
        data[group_name] = group_data

    # 返回数据 #
    return data


def test_results_to_csv(group_results: GroupTestResult) -> Union[str, bytes]:
    '''将分组测试结果转换为CSV文件（内容字节串）
    - 🚩现在将字符串转换为UTF-8编码的字节串并前缀UTF-8-SIG
        - ✅【2024-05-26 19:48:43】目前已成功解决「Windows系统下Excel打开CSV乱码」问题
    '''

    csv = ''
    '''表格字符串'''
    line_num = 0
    '''自增行号（序号）'''

    def add_row(group_name: str, nars: str, test: str, success: str, steps: str, time_diff: str, line_num_header: Optional[str] = None):
        '''打印一行'''
        nonlocal csv, line_num
        # 序号/表头
        n_line: str
        if line_num_header is None:  # 是测试用例⇒序号自增
            line_num += 1
            n_line = str(line_num)
        else:
            n_line = line_num_header
        # 直接加进一行
        csv += ','.join([
            n_line,
            group_name,
            nars,
            test,
            success,
            steps,
            time_diff,
        ]) + '\n'

    # 表头 | ⚠️【2024-05-26 17:30:02】此处全英文：避免中文编码问题
    add_row(
        "测试组",
        "推理器类型",
        "推理测试名称",
        "是否成功",
        "步数",
        "运行耗时(秒)",
        line_num_header='序号',
    )

    # 表格
    for group_name, cross_result in group_results.items():
        for (nars, test), result in cross_result.items():
            # 成功与否
            success = '是' if result.success else '否'
            # 成功步数/失败（不显示）
            steps = (
                '，'.join(map(str, result.success_cycles))
                if result.success_cycles
                else '')
            time_diff = str(result.time_diff)
            add_row(group_name,
                    nars.name,
                    test.name,
                    success,
                    steps,
                    time_diff)

    # 返回 | 根据启用的编码决定
    if constants.CSV_BOM is None:
        return csv
    else:  # 启用BOM
        encoded = csv.encode(encoding=constants.RESULT_SAVING_ENCODING)
        return constants.CSV_BOM + encoded


def store_group_test(group_results: GroupTestResult, file_root: str, file_name: str):
    '''存储分组测试结果
    - 🎯持久化完整地存储「分组测试」的结果
    - 🎯方便后续分析
    '''
    def try_save(generator: Callable[[GroupTestResult], Union[str, bytes]], file_name: str):
        '''尝试从函数生成并保存数据
        Args:
            - generator: 接收测试组结果，返回字符串或字节串 的生成函数
            - file_path: 保存路径
        '''
        # 决定路径
        file_path = file_root + file_name
        # 生成数据
        try:
            data = generator(group_results)
        except BaseException as e:
            print(f'生成测试结果到 {file_name} 失败：{e}')

        # 保存数据
        try:
            print(f'正在保存测试结果到 {file_path} ……')
            if isinstance(data, bytes):
                with open(file_path, 'wb') as f:
                    f.write(data)
            else:
                with open(file_path, 'w', encoding=constants.RESULT_SAVING_ENCODING) as f:
                    f.write(data)
            print(f'测试结果已成功保存到 {file_path}')
        except BaseException as e:
            print(f'存储测试结果到 {file_name}失败：{e}')

    # 保存JSON
    from json import dumps
    try_save(
        lambda results: dumps(jsonify_group_test(results), indent=4),
        f'{file_name}.json')

    # 保存CSV
    try_save(test_results_to_csv, f'{file_name}.csv')

# 主程序


def main():
    '''主函数（仅直接执行时）'''
    from time import time

    # 计时开始 #
    now = time()

    # 计算结果 #
    # * 🚩【2024-05-09 20:28:22】现在直接测试所有的「NARS类型×测试文件」组合
    result = group_test()

    # 计算实际总耗时 #
    total_time = time() - now

    # 展示结果 #
    print(f'所有NAL测试完毕，总耗时 {total_time:.2f} 秒。')
    for (group_name, results) in result.items():

        # 计算总耗时
        d_time = sum(
            result.time_diff
            for result in results.values()
        )

        # 生成展示用表格
        table = cross_test_str_table(results)

        # 展示
        name = f"测试组 {group_name}" if group_name else "所有NAL测试"
        print(f'  {name} 运行完毕，总运行耗时 {d_time:.2f} 秒：\n{table}')

    # 存储结果 #
    file_root = constants.TEST_RESULT_FILE_ROOT
    file_name = constants.TEST_RESULT_FILE_NAME()
    '''文件名（不含扩展名）'''
    store_group_test(result, file_root=file_root, file_name=file_name)

    # 结束 #
    exit(0)


if __name__ == '__main__':
    main()
