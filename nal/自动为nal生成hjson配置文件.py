'''根据脚本自动为nal生成hjson配置文件'''

import os
import os.path as path
from typing import List


def 生成配置(测试路径名: str):
    '''生成配置文件的内容
    📄测试路径名：`single_step/1.1` =>
    - 测试文件：[测试根路径]/single_step/1.1.nal
    - 配置文件：[配置根路径]/single_step/1.1.hjson
    '''
    return f'''
#hjson
// * 🎯测试nal {测试路径名}
// * ℹ️测试环境交由`prelude_test.hjson`加载
// * 📌原则：每个配置文件中引用的相对路径，均基于「配置文件自身」的路径
{{
    preludeNAL: {{
        // 预置的NAL测试文件（相对配置文件自身）
        file: ./../../../nal/{测试路径名}.nal
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
测试文件所在文件夹 = 脚本自身所在文件夹
'''📄test/babelnar/nal'''

# 筛选所有后缀名为 `.nal` 的文件，获取其内部路径
所有NAL测试文件: List[str] = []
'''
- 📄'single_step/1.1'
'''

for 文件夹完整路径, 所有子文件夹, 所有子文件名 in os.walk(测试文件所在文件夹):
    # 只在自身文件夹子文件夹中遍历
    if not 文件夹完整路径.startswith(测试文件所在文件夹):
        continue
    # 截断获取相对路径
    相对路径 = trim_left(文件夹完整路径, 测试文件所在文件夹)
    for 文件名 in 所有子文件名:
        if 文件名.endswith('.nal'):
            测试文件 = (
                trim_right(path.join(相对路径, 文件名), '.nal')
                .strip('\\').replace('\\', '/')
            )
            所有NAL测试文件.append(测试文件)

# 从「脚本自身所在路径」上溯两层，并获得「config/test_nal」配置存放路径
配置文件所在文件夹 = path.abspath(
    # 先上溯，再绝对化
    path.join(脚本自身所在文件夹, '..', 'config', 'test_nal'))

所有NAL测试配置文件 = []
'''
- 📄'single_step/1.1'
'''

for 文件夹完整路径, 所有子文件夹, 所有子文件名 in os.walk(配置文件所在文件夹):
    # 只在自身文件夹子文件夹中遍历
    if not 文件夹完整路径.startswith(配置文件所在文件夹):
        continue
    # 截断获取相对路径
    相对路径 = trim_left(文件夹完整路径, 配置文件所在文件夹)
    for 文件名 in 所有子文件名:
        if 文件名.endswith('.hjson'):
            测试文件 = (
                trim_right(path.join(相对路径, 文件名), '.hjson')
                .strip('\\').replace('\\', '/')
            )
            所有NAL测试配置文件.append(测试文件)

'''无扩展名'''

新增的NAL测试 = [
    测试名
    for 测试名 in 所有NAL测试文件
    if 测试名 not in 所有NAL测试配置文件
]


if __name__ == '__main__':
    print(f'共发现如下NAL测试：{[名 for 名 in 所有NAL测试文件]}')
    # 根据新增测试名生成测试
    for 新增的NAL测试名 in 新增的NAL测试:
        print(f'发现新增测试：{新增的NAL测试名}')
        配置文件名 = 新增的NAL测试名 + '.hjson'
        # 计算路径，预备创建
        新配置文件路径 = path.join(配置文件所在文件夹, 配置文件名)
        新配置文件所在文件夹 = path.dirname(新配置文件路径)
        if not path.exists(新配置文件所在文件夹):
            os.makedirs(新配置文件所在文件夹)
            # 生成内容并写入到文件
        with open(新配置文件路径, 'w+', encoding='utf-8') as 配置文件:
            配置文件.write(生成配置(新增的NAL测试名))
            print(f'已生成配置文件：{配置文件名}')
