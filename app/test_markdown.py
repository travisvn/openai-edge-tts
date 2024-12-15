import re

def process_markdown(text):
    # 将Markdown格式中表示标题的#号去掉
    text = re.sub(r'^#+\s', '', text, flags=re.MULTILINE)
    # 将Markdown格式中表示列表的*号去掉
    text = re.sub(r'(?:^\s*\*\s|^>\s+\*\s)', '', text, flags=re.MULTILINE)
    # 把长度超过2个的连续下划线去掉（连续下划线通常为选择题填空部份）
    text = re.sub(r'_{2,}', '__', text, flags=re.MULTILINE)
    # 处理带有语言类型的代码块
    text = re.sub(r'^```(\w+).*\n[\s\S]*?^```', r'省略\1代码块', text, flags=re.MULTILINE)
    # 处理不带语言类型的代码块
    text = re.sub(r'^```.*\n[\s\S]*?^```', '省略代码块', text, flags=re.MULTILINE)
    # 处理缩进式代码块
    text = re.sub(r'(?:(?:^[ ]{4}|\t).*\n?)+', '省略代码块', text, flags=re.MULTILINE)
    return text

def test_markdown_processing():
    # 测试用例
    test_text = """# 一级标题
## 二级标题
### 三级标题

* 列表项1
* 列表项2
> * 引用中的列表项

这是一个___下划线测试____

```python
def hello():
    print("Hello")
```

```
普通代码块
多行内容
```

    这是缩进式代码块
    第二行
        更多缩进
"""

    processed = process_markdown(test_text)
    print("原始文本：")
    print("-" * 50)
    print(test_text)
    print("\n处理后文本：")
    print("-" * 50)
    print(processed)

if __name__ == "__main__":
    test_markdown_processing()
