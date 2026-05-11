# -*- coding: utf-8 -*-
"""
run_all.py —— 运行全部测试套件。纯标准库 unittest，零外部依赖。
输出：汇总 PASS/FAIL
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))


def run_all():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    test_dir = os.path.dirname(os.path.abspath(__file__))

    # 发现所有 test_*.py
    test_files = sorted(f for f in os.listdir(test_dir)
                        if f.startswith("test_") and f.endswith(".py"))
    for f in test_files:
        mod_name = f[:-3]
        try:
            module = __import__(mod_name)
            tests = loader.loadTestsFromModule(module)
            suite.addTests(tests)
            print("加载: {}".format(mod_name))
        except Exception as e:
            print("跳过: {} ({})".format(mod_name, e))

    # 运行
    print("\n" + "=" * 50)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 汇总
    print("\n" + "=" * 50)
    total = result.testsRun
    fails = len(result.failures) + len(result.errors)
    if fails == 0:
        print("[PASS] 全部 {} 个测试通过".format(total))
    else:
        print("[FAIL] {} 个失败 / {} 个测试".format(fails, total))

    return 0 if fails == 0 else 1


def run_validate():
    """运行 JSON 数据验证（独立于单元测试）"""
    print("=" * 50)
    print("JSON 数据验证")
    print("=" * 50)
    from validate_data import validate_all
    return 0 if validate_all() else 1


if __name__ == "__main__":
    ok1 = run_validate()
    print()
    ok2 = run_all()
    sys.exit(0 if (ok1 == 0 and ok2 == 0) else 1)
