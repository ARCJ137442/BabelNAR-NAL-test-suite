'''Direct Test 直接测试
- 🎯精确指定测试范围，不修改`constants.py`运行少量测试
- 📌基于「测试运行」系列方法
'''

from run_tests import ALL_NARS_TYPES, ALL_TEST_FILES, group_test, main_show, main_store
from toolchain import *
from util import *


def query_hit(file: TestFile, query: str) -> bool:
    '''测试查询是否命中指定测试用例'''
    return query.lower() in file.name.lower()


def find_tests(query: str) -> List[TestFile]:
    '''根据一个关键词搜索测试文件（结果可能为空）'''
    return collect(filter(lambda file: query_hit(file, query), ALL_TEST_FILES))


def query_tests(queries: Iterable[str], print_feedback: bool = True) -> Optional[List[TestFile]]:
    '''请求要测试的测试集
    - 🚩通过请求用户输入，从已有测试中搜索出相应的测试用例
    - ⚠️在测试输入被中断时，返回`None`表示空值
        - 🎯用于避免非必要的「未找到任何测试」提示
    '''
    tests: List[TestFile] = []

    # 请求输入 | 此处可以是特殊的「用户输入迭代器」，只要能迭代字符串即可
    try:
        for query in queries:
            # 查询、去重、添加
            found = find_tests(query)
            new_tests = collect(filter(lambda test: test not in tests, found))
            if is_empty(new_tests):
                print_feedback and print(f'未根据关键词{repr(query)}找到任何新测试！')
            else:
                if print_feedback:
                    print(f'现有测试数目：{len(tests)+len(new_tests)}')
                    for test in tests:  # 已有测试
                        print(f'    * {test.name}')
                    for test in new_tests:  # 新测试
                        print(f'    + {test.name}')
                tests.extend(new_tests)
    # Ctrl+C中断填充 | 🎯应对「误增加测试」的情况
    except KeyboardInterrupt:
        if is_empty(tests):  # 若测试列表为空，则重新抛出异常
            raise KeyboardInterrupt()
        print_feedback and print('\n输入中断，测试列表已清空！')
        return None
    # 返回测试
    return tests


def main_one(tests: Optional[List[TestFile]], print_feedback: bool = True):
    '''根据指定的一个/多个测试用例，运行测试并返回部分化的结果'''
    '''主函数（仅直接执行时）'''

    # 提前检验
    if tests is None:
        return  # 空值⇒静默结束（不论是否print）
    if is_empty(tests):
        print_feedback and print(f'未找到任何可以开始的测试！')
        return  # 没测试⇒提前结束

    # 计算结果 #
    nars_types = ALL_NARS_TYPES

    if print_feedback:
        print(f'测试开始，共{len(tests)}个测试用例，将进行{len(tests)*len(nars_types)}次测试')
        for file in tests:
            for nars_type in nars_types:
                print(f'- 测试 @ {file.name} × {nars_type.name}')

    # 计时开始 #
    now = time()

    # 开始运行
    # * 🚩【2024-05-09 20:28:22】现在直接测试所有的「NARS类型×测试文件」组合
    result = group_test(nars_types=nars_types, test_files=tests)

    # 计算实际总耗时 #
    total_time = time() - now

    # 展示结果 #
    main_show(result, total_time)

    # 询问是否保存测试结果
    if input('是否保存结果？（非空→保存，空行→不保存）：'):
        main_store(result)


def main():

    from sys import argv

    tests = query_tests(argv, print_feedback=False)
    main_one(tests, print_feedback=False)

    try:  # 不断执行单个测试
        while True:
            inputs = InputIterator('请输入要测试的测试用例（输入空行以启动）: ')
            tests = query_tests(inputs)
            main_one(tests)
    except KeyboardInterrupt:
        print('\n主程序退出')

    # 结束 #
    exit(0)


if __name__ == '__main__':
    main()
