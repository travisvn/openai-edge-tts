import re

def test_bracket_processing():
    # 测试用例
    test_cases = [
        (
            "这是一个[测试]文本",
            "这是一个文本"
        ),
        (
            "这是一个[链接文本](http://example.com)测试",
            "这是一个链接文本测试"
        ),
        (
            "多个测试：[测试1][测试2][链接](http://test.com)",
            "多个测试：链接"
        ),
        (
            "混合测试[测试1]text[链接1](link1)[测试2][链接2](link2)",
            "混合测试text链接1链接2"
        )
    ]

    def process_text(text):
        # 从server.py复制的处理逻辑
        # 1. 如果中括号后面没有紧跟小括号,则删除中括号及其内容
        text = re.sub(r'\[[^\]]*\](?!\([^\)]*\))', '', text)
        # 2. 如果中括号后面紧跟小括号,则保留中括号内容,删除小括号及其内容
        text = re.sub(r'\[([^\]]*)\](?=\([^\)]*\))\([^\)]*\)', r'\1', text)
        return text

    # 运行测试
    for i, (input_text, expected_output) in enumerate(test_cases, 1):
        result = process_text(input_text)
        success = result == expected_output
        print(f"\n测试用例 {i}:")
        print(f"输入: {input_text}")
        print(f"期望: {expected_output}")
        print(f"实际: {result}")
        print(f"结果: {'通过' if success else '失败'}")

if __name__ == '__main__':
    print("开始测试中括号处理逻辑...")
    test_bracket_processing()
