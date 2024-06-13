'''Direct Test 定点测试
- 🎯精确指定测试范围，不修改`constants.py`运行少量测试
- 📌基于「测试运行」系列方法
'''

from os.path import basename, isfile, abspath
from constants import CONFIG_NAL
from run_tests import ALL_NARS_TYPES, ALL_TEST_FILES, show_test_result, main_store, main_test
from toolchain import *
from util import *


def generate_hjson_config(test_name: str, nal_file_path: str = '') -> str:
    '''生成配置文件内容（字符串）'''
    nal_file_path = (
        nal_file_path
        if nal_file_path
        # * 🚩↓默认的文件路径
        else f'./../../nal/single_step/{test_name}.nal'
    )
    return f'''
#hjson
// * 🎯测试nal {test_name}
// * ℹ️测试环境交由`prelude_test.hjson`加载
// * 📌原则：每个配置文件中引用的相对路径，均基于「配置文件自身」的路径
{{
    preludeNAL: {{
        // 预置的NAL测试文件（相对配置文件自身）
        file: {nal_file_path}
    }}
}}
'''.strip()


def to_temp_config_path(test_name: str) -> str:
    '''从`.nal`文件路径，生成临时配置文件路径
    - 🚩【2024-06-07 21:17:29】目前使用文件名在固定路径config/nal生成
    - 📄"**/*/<file_name>.nal" => "config/nal/<file_name>.hjson"
    '''
    return CONFIG_NAL + test_name + '.hjson'


def try_generate_temp_hjson_config(nal_file_path: str):
    '''为`.nal`测试文件生成临时hjson配置文件'''
    try:
        test_name = trim_right(basename(nal_file_path), '.nal')
        config_file_path = to_temp_config_path(test_name)
        if not isfile(config_file_path):
            # * 🚩无配置文件⇒生成临时配置文件
            with open(config_file_path, 'w+', encoding='utf-8') as f:
                content = generate_hjson_config(
                    test_name,  # * 🚩↓取绝对路径，避免路径问题
                    nal_file_path=abspath(nal_file_path))
                f.write(content)
                print(f'未找到已有配置文件，已生成临时配置文件：{config_file_path}')
    except BaseException as e:
        print(f'生成临时配置文件时出现错误：{e}')


def query_hit(file: Union[TestFile, NARSType], query: str) -> bool:
    '''测试查询是否命中指定测试用例'''
    return query.lower() in file.name.lower()


def find_nars_types_in_constants(query: str) -> List[NARSType]:
    '''在具体的`.nal`文件中搜索测试用例'''
    return collect(filter(lambda nars_type: query_hit(nars_type, query), ALL_NARS_TYPES))


def query_nars_types(queries: Iterable[str], print_feedback: bool = True) -> Optional[List[NARSType]]:
    '''请求要测试的测试集
    - 🚩通过请求用户输入，从已有测试中搜索出相应的测试用例
    - ⚠️在测试输入被中断时，返回`None`表示空值
        - 🎯用于避免非必要的「未找到任何测试」提示
    '''
    types: List[NARSType] = []

    # 请求输入 | 此处可以是特殊的「用户输入迭代器」，只要能迭代字符串即可
    try:
        for query in queries:
            # 查询、去重、添加
            found = find_nars_types_in_constants(query)
            new_types = collect(
                filter(
                    lambda nars_type: nars_type not in types,
                    found
                ))
            if is_empty(new_types):
                print_feedback and print(f'未根据关键词{repr(query)}找到任何新推理器！')
            else:
                if print_feedback:
                    print(f'现有推理器：{len(types)+len(new_types)}')
                    for nars_type in types:  # 已有推理器
                        print(f'    * {nars_type.name}')
                    for nars_type in new_types:  # 新推理器
                        print(f'    + {nars_type.name}')
                types.extend(new_types)
    # Ctrl+C中断填充 | 🎯应对「误增加推理器」的情况
    except KeyboardInterrupt:
        if is_empty(types):  # 若推理器列表为空，则重新抛出异常
            raise KeyboardInterrupt()
        print_feedback and print('\n输入中断，推理器列表已清空！')
        return None  # 此时迭代器可能损坏，无法继续复用
    # * 🚩空列表⇒使用全部推理器 | 📝没有推理器 测试无意义
    if is_empty(types):
        types.extend(ALL_NARS_TYPES)
        print_feedback and print('默认加载所有推理器：')
        for nars in types:  # 已有测试
            print(f'    * {nars.name}')
    # 返回推理器列表
    return types


def find_tests_in_constants(query: str) -> List[TestFile]:
    '''在具体的`.nal`文件中搜索测试用例'''
    return collect(filter(lambda file: query_hit(file, query), ALL_TEST_FILES))


def find_tests_in_file(query_file_path: str) -> List[TestFile]:
    '''在具体的`.nal`文件中搜索测试用例
    - 🎯实现「任意处NAL脚本均能参与测试」
    '''
    from os.path import isfile
    file_path = (
        query_file_path
        # * 🚩统一斜杠
        .replace('\\', '/')
        # * 🚩删去前后空格、引号
        .strip(' &\\/"\'')
    )
    # * 🚩若有文件⇒自动生成临时hjson配置，返回
    if isfile(file_path) and file_path.endswith('.nal'):
        try_generate_temp_hjson_config(file_path)
        return [TestFile.from_file_path(file_path)]
    else:
        return []


def find_tests(query: str) -> List[TestFile]:
    '''根据一个关键词搜索测试文件（结果可能为空）'''
    return (
        # * 🚩测试名是一个路径⇒按照路径查找文件，自动生成临时「测试文件」
        find_tests_in_file(query)
        if '/' in query or '\\' in query else
        find_tests_in_constants(query)
    )


def query_tests(queries: Iterable[str], print_feedback: bool = True, fill_when_empty: bool = True) -> Optional[List[TestFile]]:
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
        return None  # 此时迭代器可能损坏，无法继续复用
    # * 🚩空列表&没查过⇒使用全部测试用例 | 📝没有测试用例 测试无意义
    if fill_when_empty and is_empty(tests):
        tests.extend(ALL_TEST_FILES)
        print_feedback and print('默认加载所有测试用例：')
        for test in tests:  # 已有测试
            print(f'    * {test.name}')
        print_feedback and input('按下回车以确认。。。')
    # 返回测试用例列表
    return tests


def main_one(nars_types: Optional[List[NARSType]], tests: Optional[List[TestFile]], *, print_feedback: bool = True):
    '''根据指定的一个/多个测试用例，运行测试并返回部分化的结果'''
    '''主函数（仅直接执行时）'''

    # 提前检验
    if tests is None or nars_types is None:
        return  # 空值⇒静默结束（不论是否print）
    if is_empty(nars_types):
        print_feedback and print(f'未找到任何可以开始的推理器！')
        return  # 没推理器⇒提前结束
    if is_empty(tests):
        print_feedback and print(f'未找到任何可以开始的测试！')
        return  # 没测试⇒提前结束

    # 计算结果 #

    if print_feedback:
        print(f'测试开始，共{len(tests)}个测试用例，将进行{len(tests)*len(nars_types)}次测试')
        for file in tests:
            for nars_type in nars_types:
                print(f'- 测试 @ {file.name} × {nars_type.name}')

    # 开始运行
    results, total_time = main_test(nars_types=nars_types, test_files=tests)

    # 展示结果 #
    show_test_result(
        results, total_time,
        show_diff=len(nars_types) > 1  # 只在2个以上推理器时才分析差异
    )

    # 询问是否保存测试结果
    if input('是否保存结果？（非空→保存，空行→不保存）：'):
        main_store(results)


def main():

    # 先尝试从命令行参数中提取内容，以便自动化测试
    from sys import argv
    tests = query_tests(argv, print_feedback=False, fill_when_empty=False)
    main_one(ALL_NARS_TYPES, tests, print_feedback=False)

    # 正常交互
    try:  # 不断执行单个测试
        while True:
            print(f'---- 定点测试 ----')
            print(f'提示：若在没有任何 推理器/测试用例 时开始测试，将自动填充所有 推理器/测试用例')
            print(f'现有推理器：{[nars.name for nars in ALL_NARS_TYPES]}')
            inputs = InputIterator('请输入要测试的推理器名（留空以继续）: ')
            nars_types = query_nars_types(inputs)
            # * 🚩输入中断⇒重新开始
            if nars_types is None:
                print()  # 断行
                continue
            inputs = InputIterator('请输入要测试的测试用例（或输入已配置的`.nal`文件路径；输入空行以启动）: ')
            tests = query_tests(inputs)
            main_one(nars_types, tests)
            # 空行分隔
            print()
    except KeyboardInterrupt:
        print('\n主程序退出')


if __name__ == '__main__':
    main()
