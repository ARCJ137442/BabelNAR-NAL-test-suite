'''加载先前保存的「测试结果」
- 🎯从JSON中恢复并打印其中的测试结果

## JSON文件的结构

- 🕒最后更新时间：【2024-05-26 21:28:20】
- 📄所参考文件：`group_result-20240526202227.test.json`

文件结构：

```json
{
    组名: {
        测试名: {
            推理器名: 测试结果
        }
    }
}
```
'''

from typing import Dict, List, Optional, Set, Tuple
from toolchain import NARSType, TestFile, TestResult, show_result
from run_tests import GroupTestResultToShow, cross_test_str_table, ALL_NARS_TYPES, ALL_TEST_FILES
from json import loads

CrossTestResult = Dict[Tuple[str, str], TestResult]
'''测试结果中有关「交叉测试」的返回值
- 🎯无需从「常量」`constants.py`中获取「推理器类型」与「测试文件」
    - 📌【2024-05-27 10:39:21】目前展示测试数据只需其中的字符串信息，并无需求和已有推理器、测试用例关联
'''


def get_nars_type_from_name(name: str, types_not_found: Set[str] = set()) -> Optional[NARSType]:
    '''根据推理器名获取推理器对象
    - ✨可选的「只提示一次」：根据「已找不到的名称集合」只会提示一次（加入&提示 or 不理）
    - ℹ️仅用于「结合现有常量」提供附加信息
    '''
    for nars_type in ALL_NARS_TYPES:
        if nars_type.name == name:
            return nars_type

    # 找不到⇒警告并返回`None` | 且仅有一次警告
    if name not in types_not_found:
        print(f'找不到推理器：{name}')
        types_not_found.add(name)
    return None


def get_test_file_from_name(name: str, types_not_found: Set[str] = set()) -> Optional[TestFile]:
    '''根据测试名获取测试对象
    - ✨可选的「只提示一次」：根据「已找不到的名称集合」只会提示一次（加入&提示 or 不理）
    - ℹ️仅用于「结合现有常量」提供附加信息
    '''
    for test_file in ALL_TEST_FILES:
        if test_file.name == name:
            return test_file

    # 找不到⇒警告并返回`None` | 且仅有一次警告
    if name not in types_not_found:
        print(f'找不到测试：{name}')
        types_not_found.add(name)
    return None


def load_json_object(path: str) -> dict:
    '''从JSON文件中加载对象'''
    with open(path, 'r', encoding='utf-8') as f:
        return dict(loads(f.read()))


def load_group_results(path: str) -> GroupTestResultToShow:
    '''从JSON文件路径路径加载测试结果'''
    # 加载JSON对象
    json = load_json_object(path.strip())
    return load_group_results_json(json)


def load_group_results_json(json: dict) -> GroupTestResultToShow:
    '''从JSON对象中加载测试结果'''

    # 重建测试结果
    results = {}

    for group_name, group_result in json.items():
        # 重建单个测试组的测试结果
        cross_result: CrossTestResult = {}
        for test_name, nars_results in group_result.items():
            for nars_name, test_result in nars_results.items():
                # * 🚩【2024-05-27 11:00:31】现在展示只需名称，不再需要反查现有常量
                # * 📄因为有时会「在修改常量后操作」如「关闭部分测试」，此时仍需保证加载结果（和所存数据）一致
                # nars_type = get_nars_type_from_name(nars_name)
                # test_file = get_test_file_from_name(test_name)
                # if nars_type is None or test_file is None:
                #     continue
                # key = (nars_type, test_file)
                key = (nars_name, test_name)
                cross_result[key] = TestResult.from_json(test_result)
        # 装填
        results[group_name] = cross_result

    # 返回结果
    return results


def main_path(path: str) -> None:
    '''处理单个「测试结果文件路径」'''

    # 解析测试结果
    results = load_group_results(path)

    # 处理（&展示）测试结果
    return main_one(results)


def main_one(results: GroupTestResultToShow) -> None:
    '''处理单个解析好了的「测试结果」'''

    # 打印测试结果
    for group_name, group_result in results.items():
        table = cross_test_str_table(group_result)
        print(f'组名：{group_name}\n{table}')

    print('分组测试结果加载完毕！')

    # 终端循环
    while True:
        try:
            test_name = input('请输入需要查询的具体测试名称：')
            query_single_test(results, test_name)
        except KeyboardInterrupt:
            return print('\n退出单文件查询……')


def query_single_test(results: GroupTestResultToShow, query: str) -> None:
    '''展示单个测试结果'''
    print(f'正在查询 {repr(query)}……')

    def q() -> List[Tuple[str, str, str, TestResult]]:
        '''真正的查询逻辑
        - 🚩返回值语义：
            - 1.测试组名
            - 2.测试用例名
            - 3.推理器名
            - 4.测试结果
        '''
        result = []
        for group_name, group_result in results.items():
            for (nars_name, test_name), nars_results in group_result.items():
                # * 🚩模糊查询，忽略大小写，但容易同时匹配'1'与'11'
                found = (
                    test_name.lower() == query.lower()
                    or query.lower() in test_name.lower()
                )
                if found:
                    print(
                        f'在测试组 {repr(group_name)} 中查找到测试 {repr(test_name)} @ {repr(nars_name)}')
                    result.append(
                        (group_name, test_name, nars_name, nars_results))
        return result

    test_results = q()
    if len(test_results) > 0:
        return show_single_test(test_results)
    print(f'未找到测试 {repr(query)}！')


def show_single_test(nars_results: List[Tuple[str, str, str, TestResult]]) -> None:
    '''展示单个「测试用例」的结果'''
    print()
    while True:
        try:
            query_name = input('请输入需要查询的推理器名称：')
            not_found = True
            for group_name, test_name, nars_name, test_result in nars_results:
                if nars_name == query_name or query_name in nars_name:
                    print(f'\n# {test_name} @ {nars_name}')
                    show_result(test_result, verbose=True)
                    print()
                    not_found = False
            if not_found:
                print(f'未找到推理器 {repr(query_name)}！')
        except KeyboardInterrupt:
            return print('\n退出单测试查询……')


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
