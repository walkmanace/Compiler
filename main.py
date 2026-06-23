import argparse
from pathlib import Path
import sys

from src.backend.codegen import CodeGenerator
from src.backend.semantic import SemanticAnalyzer
from src.frontend.lexer import Lexer
from src.frontend.parser import Parser
from src.vm.cpu_emulator import VirtualMachine


def run_compiler(source_path: Path) -> None:
    source = source_path.read_text(encoding="utf-8")

    lexer = Lexer(source)
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    ast = parser.parse()

    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)

    generator = CodeGenerator()
    instructions = generator.generate(ast)

    print(f"读取源码文件: {source_path}")
    print("开始执行编译流程: Lexer -> Parser -> SemanticAnalyzer -> CodeGenerator -> VirtualMachine")
    print("\n运行结果:")

    vm = VirtualMachine()
    vm.execute(instructions)


def main() -> None:
    project_root = Path(__file__).resolve().parent
    default_source = project_root / "examples" / "test_cases.toy"

    parser = argparse.ArgumentParser(description="运行迷你编译器示例程序")
    parser.add_argument(
        "source",
        nargs="?",
        default=str(default_source),
        help="要编译运行的 .toy 源码文件路径，默认使用 examples/test_cases.toy",
    )
    args = parser.parse_args()

    source_path = Path(args.source)
    if not source_path.is_absolute():
        source_path = project_root / source_path

    try:
        run_compiler(source_path.resolve())
    except Exception as exc:
        print(f"编译失败: {exc}")
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()