'''实用工具函数
- 🎯内容分离：减少在「工具链」侧的代码量，拆分功能
'''


from time import strftime, localtime
from typing import Callable, Iterable, Iterator, List, Optional, TypeVar

UTF_8_SIG = b'\xEF\xBB\xBF'
'''UTF8 BOM：明确标识一个文件是UTF-8编码
- 🔗参考：https://baike.baidu.com/item/BOM/2790401
'''


def show(thing):
    '''打印值，并返回该值'''
    print(thing)
    return thing


__T = TypeVar("__T")
'''泛型参数
- 📝Python 3.1.2才在语言层面增加泛型语法
- 🔗参考：https://docs.python.org/zh-cn/3/library/typing.html
- 🚩【2024-05-27 11:34:51】不直接使用`T`以避免符号泄漏
'''


def collect(iterable: Iterable[__T]) -> List[__T]:
    '''将可迭代对象转换为列表
    - 🚩直接使用列表生成式
    '''
    return [t for t in iterable]


def __f_range(start: float, stop: float, step: float) -> Iterable[float]:
    '''浮点范围
    - 🚩类似Python内置的`range`函数，但能使用浮点
    - 🔗参考：https://stackoverflow.com/questions/7267226/range-for-floats
    - ⚠️只能用一次：迭代/遍历 完成就失效，不能被用作「常持有变量」
    '''
    result, n = start, 1
    while result <= stop:
        yield result
        result = start + n * step
        n += 1


def f_range(start: float, stop: float, step: float = 0.1) -> List[float]:
    '''浮点范围（固定数组）
    - 📌将Python内置的列表生成式进行了包装
    - 🚩每次运行均生成一个新数组，这个数组可被重复遍历
    '''
    return collect(__f_range(start, stop, step))


def time_stamp():
    '''产生视觉上连续的数值字符串作为时间戳
    - 🚩格式：年月日时分秒（按【调用时】时间算）
    - 📄"20240526191722" ⇒ 2024年05月26日 19:17:22
    '''
    return strftime('%Y%m%d%H%M%S', localtime())


def count(iter: Iterable) -> int:
    '''计算可迭代对象的元素数量
    - 🚩直接使用内置函数
    '''
    count = 0
    for _ in iter:
        count += 1
    return count


def is_empty(iter: Iterable) -> bool:
    '''判断一个可迭代对象是否为空
    - 🚩直接使用`count`计算
    - ⚠️会消耗掉迭代器
    '''
    return count(iter) == 0


def first(iterable: Iterable[__T]) -> Optional[__T]:
    '''获取可迭代对象的第一个元素（可能没有）'''
    return next(iter(iterable))


def is_same(iterable: Iterable) -> bool:
    '''判断一个可迭代对象内含元素是否相同
    - 🚩空迭代器⇒真
    '''
    iterator = iter(iterable)
    try:  # ! ❌is_empty会消耗掉迭代器
        first = next(iterator)
    except StopIteration:
        return True  # 空⇒真

    # 判断剩余元素剩余元素
    return all(t == first for t in iterator)


def not_same(iterable: Iterable) -> bool:
    '''判断一个可迭代对象内含元素是否不同
    - 🚩空迭代器⇒假
    - 📌实质上就是`is_same`的反向
    '''
    iterator = iter(iterable)
    try:  # ! ❌is_empty会消耗掉迭代器
        first = next(iterator)
    except StopIteration:
        return False  # 空⇒假

    # 判断剩余元素剩余元素
    return any(t != first for t in iterator)


char = str
'''字符类型'''


def is_full_scale_char(c: char) -> bool:
    '''判断一个字符是否为全角字符
    - 🚩【2024-05-27 11:16:07】目前仅用于判断是否中文
    '''
    return 0x4e00 < ord(c) < 0x9fff


def num_full_scale_chars(s: str) -> int:
    '''计算一个字符串中全角字符的数量
    - 🎯【2024-05-27 11:13:15】用于「最大长度补全全角空格」
    '''
    return count(filter(is_full_scale_char, s))


def pad_full_scale_spaces(s: str, max_num_full_scale_chars: int) -> str:
    '''补全字符串，使其全角字符个数恰好为max_num_full_scale_chars
    - 🎯此即「最大长度补全全角空格」，避免Python默认补全导致宽度问题
    - 🚩对长度超过的保持原样，否则补全
    '''
    n = num_full_scale_chars(s)
    if n > max_num_full_scale_chars:
        return s
    else:
        return s + '　' * (max_num_full_scale_chars - n)


def len_display(s: str) -> int:
    '''计算字符串的「显示长度」
    - 🎯对中文和英文分别计算
    - 📌【2024-05-27 11:47:24】目前以「半角空格」为单位
        - 📌全角字符算两个
    '''
    # 计算全角字符（以及剩余的「半角字符」）
    n_full_scale_chars = num_full_scale_chars(s)
    n_half_scale_chars = len(s) - n_full_scale_chars
    # 加权求和返回
    return n_half_scale_chars + n_full_scale_chars * 2


def pad_display_spaces(s: str, max_num_display_chars: int, tail: bool = True) -> str:
    '''填充字符串空格
    - 📌【2024-05-27 11:45:19】目前认为其中字符只会出现「全角字符」与「半角字符」
        - 📌不是全角字符，则为半角字符
        - 📌全角字符算两个
    '''
    # 计算显示长度
    l = len_display(s)
    pad = (
        ''
        if l > max_num_display_chars
        else ' ' * (max_num_display_chars - l)
    )
    # 用半角空格补全
    return s + pad if tail else pad + s


def InputIterator(
    prompt: str,
    *,
    end_condition: Callable[[str], bool] = is_empty,
):
    '''简单的用户输入迭代器
    - 📌在迭代时请求用户输入
    - 🚩默认为空字符串结束
    '''
    while True:
        i = input(prompt)
        if end_condition(i):
            return
        else:
            yield i
