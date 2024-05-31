'''Diff Analyze 差异分析
- 🎯分析相同测试中不同推理器之间的差异
    1. 部分成功⇒展示「成功/失败」的差异
    2. 成功所用步数不同⇒展示步数之差
    3. 运行时间不同⇒展示时间之差
- 🚩不运行测试，仅分析保存的测试结果
'''


from typing import Dict, Tuple, Union
from result_loader import load_group_results
from run_tests import CrossTestResultToShow, GroupTestResult, GroupTestResultToShow, result_to_show
from toolchain import TestResult
from util import *


GroupedResultByNARS = List[Tuple[str, List[Tuple[str, TestResult]]]]
'''分组后结果
- 📌与字典的区别：内部项可排序

## 📄示例
```
[
    (测试名称, [
        (推理器名称, 测试结果),
        (推理器名称1, 测试结果),
    ]),
]
```
'''


def groupby_nars_test(results: CrossTestResultToShow) -> GroupedResultByNARS:
    '''将测试结果按层级「测试名称→推理器名称」分组
       - 🎯便于后续「同测试不同推理器」对比
    '''
    # 最开始用字典是为了去重
    d: Dict[str, Dict[str, TestResult]] = {}
    for (nars, test), result in results.items():
        if test not in d:
            d[test] = {}
        d[test][nars] = result

    # 将字典整理成列表，并在其中排序
    l = []
    for test, nars_results in d.items():
        l.append((test, sorted(nars_results.items(), key=lambda x: x[0])))
    l.sort(key=lambda x: x[0])
    return l


def nars_diff_one(nars_results: List[Tuple[str, TestResult]], show_level: int, indent=' '*4) -> str:
    '''对比单个测试中不同NARS的表现差异'''
    result = ''

    def print(obj='', n_indent=0, end='\n'):
        nonlocal result, indent
        result += (indent * n_indent) + obj + end

    # 分析 & 追加 #
    # 1. 部分成功⇒展示「成功/失败」的差异
    if show_level > 0 and not_same(
            r.success
            for _, r in nars_results):
        print('- ⚠️ 部分成功：', 1)
        for nars_name, r in nars_results:
            mark = '✅' if r.success else '❌'
            print(f'{nars_name} => {mark}', 2)
    # 2. 成功所用步数不同⇒展示步数之差
    elif show_level > 1 and not_same(
            r.success_cycles  # 📝Python对数组的`==`判等是按值判等
            for _, r in nars_results):
        print(f'- ℹ️ 所用步数：', 1)
        # 此处直接列举
        for nars_name, r in nars_results:
            print(f'{nars_name} => {r.success_cycles}', 2)
    # 3. 运行时间不同⇒展示时间之差
    elif show_level > 2 and not_same(
            r.time_diff
            for _, r in nars_results):
        print(f'- 🕒 运行耗时：', 1)
        # 此处直接列举
        for nars_name, r in nars_results:
            print(f'{nars_name} => {r.time_diff}', 2)

    # 返回 #
    return result


def nars_diff(results: CrossTestResultToShow, show_level: int) -> str:
    '''呈现交叉测试结果
    - 🚩返回交叉测试的结果，不产生副作用
    '''

    result = ''

    def print(obj='', end='\n'):
        nonlocal result
        result += obj + end

    # 预先分组
    grouped = groupby_nars_test(results)

    # 逐个测试追加
    for test, nars_results in grouped:
        diff = nars_diff_one(nars_results, show_level)
        # 若有内容⇒追加标题并呈现
        if diff:
            print(f'- 测试 {test}\n{diff}', end='')

    # 返回
    return result


def request_show_level() -> int:
    while True:
        try:
            level_str = input('请输入对比等级（0-3，留空默认为2）：')
            return int(level_str) if level_str else 2  # 默认为2
        except ValueError:
            print('输入错误！请重新输入！')


def show_group_diffs(results: Union[GroupTestResult, GroupTestResultToShow], show_level: Optional[int] = None) -> None:
    '''展示单个解析好了的「分组测试结果」'''

    # 未指定「对比等级」⇒靠用户输入请求
    level = show_level if show_level else request_show_level()

    # 逐组打印测试结果
    print()
    for group_name, cross_result in results.items():
        # 计算结果
        group_result = result_to_show(cross_result)
        table = nars_diff(group_result, level)
        # 打印结果
        if table.strip():
            print(f'# 组名 {group_name}\n\n{table}')
        else:
            print(f'# 组名 {group_name} 无差异')
    print()

    print('分组测试差异分析完毕！')


def main_path(path: str) -> None:
    '''处理单个「测试结果文件路径」'''

    # 解析测试结果
    results = load_group_results(path)

    # 处理（&展示）测试结果
    return show_group_diffs(results)


def main():
    '''主函数'''
    print('==== 测试结果加载器 ====')
    print('提示：使用Ctrl+C退出各级查询')
    while True:
        try:
            # 获取测试结果路径
            PATH = input('请输入保存的测试记录JSON文件路径：')
            # 处理单个路径
            main_path(PATH)
        except FileNotFoundError:
            print('路径错误！请重新输入！')
            continue
        # 手动退出
        except KeyboardInterrupt:
            print('\n程序退出……')
            return


if __name__ == '__main__':
    main()
