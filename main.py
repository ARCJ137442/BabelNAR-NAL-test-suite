'''BabelNAR CLI 测试套件 主程序
- 🎯提供一站式程序导引
'''

from typing import List

from run_tests import main as main_run_tests
from direct_test import main as main_direct_test
from result_loader import main as main_result_loader
from diff_analyze import main as main_diff_analyze
from constants import TEST_SUITE_PROGRAM_DESCRIPTION, TEST_SUITE_PROGRAM_NAME
from util import VoidFunction, find_first, is_in_or_contains


class TestProgram:
    '''测试用程序
    - 📌一个脚本算一个「程序」
    - 📌具有可被检索的「名称」
    '''
    name: str
    main: VoidFunction

    def __init__(self, name: str, main: VoidFunction) -> None:
        self.name = name
        self.main = main

    def execute(self) -> None:
        return self.main()


PROGRAMS = [
    TestProgram('run_tests 运行所有NAL测试', main_run_tests),
    TestProgram('direct_test 定点测试', main_direct_test),
    TestProgram('result_loader 加载测试结果', main_result_loader),
    TestProgram('diff_analyze 差异分析', main_diff_analyze),
]
'''现有的所有测试用程序'''


def main(extra_programs: List[TestProgram] = []):
    '''主程序'''
    # * 🚩先与外部传入的「附加测试用程序」混合，产生一个新数组
    programs = PROGRAMS + extra_programs
    print(f'==== {TEST_SUITE_PROGRAM_NAME} ====')
    print(TEST_SUITE_PROGRAM_DESCRIPTION)
    while True:
        try:
            # * 🚩打印现有程序的信息
            print('现有如下程序可供选择：')
            for program in programs:
                print(f'* {program.name}')
            # * 🚩获取输入、选择并查找
            query = input('\n输入名称以选择: ')
            selected = find_first(
                programs, lambda p: is_in_or_contains(p.name, query))
            # * 🚩执行选中的程序
            if selected is None:
                print(f'没有找到与{repr(query)}有关的程序！')
                continue
            # * 🚩执行选中的程序
            print(f'\n== 开始执行 {repr(selected.name)} ==\n')
            selected.execute()
            print(f'\n== 程序 {repr(selected.name)} 终止 ==\n')
        except KeyboardInterrupt:
            print('\n程序退出。。。')
            return
        except BaseException as e:
            print(f'程序出错：{e}')


if __name__ == '__main__':
    main()
