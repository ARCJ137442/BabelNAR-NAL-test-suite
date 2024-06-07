'''根据脚本自动为nal生成hjson配置文件'''

import os
import os.path as path


def 生成配置(测试名称):
    return f'''
#hjson
// * 🎯测试nal {测试名称}
// * ℹ️测试环境交由`prelude_test.hjson`加载
// * 📌原则：每个配置文件中引用的相对路径，均基于「配置文件自身」的路径
{{
    preludeNAL: {{
        // 预置的NAL测试文件（相对配置文件自身）
        file: ./../../nal/single_step/{测试名称}.nal
    }}
}}
'''.strip()


def trim_left(s: str, prefix: str) -> str:
    '''左侧整体性裁剪'''
    while s.startswith(prefix):
        s = s[len(prefix):]
    return s


def trim_right(s: str, suffix: str) -> str:
    '''右侧整体性裁剪'''
    while s.endswith(suffix):
        s = s[:-len(suffix)]
    return s


# 获取当前目录下所有文件名
脚本自身所在文件夹 = path.dirname(path.abspath(__file__))

# 筛选所有后缀名为 `.nal` 的文件名
所有NAL测试文件名 = [
    文件
    for 文件 in os.listdir(脚本自身所在文件夹)
    if 文件.endswith('.nal')
]

# 从「脚本自身所在路径」上溯两层，并获得「config/test_nal」配置存放路径
配置文件所在文件夹 = path.abspath(
    # 先上溯，再绝对化
    path.join(脚本自身所在文件夹, '..', '..', 'config', 'test_nal'))

所有NAL测试配置文件名 = [
    # 配置文件名 = 测试文件名 + '.hjson'
    配置文件名
    for 配置文件名 in os.listdir(配置文件所在文件夹)
    if 配置文件名.endswith('.hjson')
]

所有NAL测试名称 = [
    trim_right(文件名, '.nal')
    for 文件名 in 所有NAL测试文件名
]
'''无扩展名，无前导"nal"'''

所有NAL配置名称 = [
    trim_right(文件名, '.hjson')
    for 文件名 in 所有NAL测试配置文件名
]
'''无扩展名'''

新增的NAL测试名称 = [
    测试名称
    for 测试名称 in 所有NAL测试名称
    if 测试名称 not in 所有NAL配置名称
]


if __name__ == '__main__':
    print(f'共发现如下NAL测试：{所有NAL测试名称}')
    # 根据新增测试名生成测试
    for 新增的NAL测试名 in 新增的NAL测试名称:
        print(f'发现新增测试：{新增的NAL测试名}')
        配置文件名 = 新增的NAL测试名 + '.hjson'
        with open(path.join(配置文件所在文件夹, 配置文件名), 'w', encoding='utf-8') as 配置文件:
            配置文件.write(生成配置(新增的NAL测试名))
            print(f'已生成配置文件：{配置文件名}')
