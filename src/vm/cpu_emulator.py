class VirtualMachine:
    def __init__(self) -> None:
        self.stack: list[int | bool] = []
        self.environment: dict[str, int | bool] = {}
        self.labels: dict[str, int] = {}

    def execute(self, instructions: list[str]) -> None:
        self.stack = []
        self.environment = {}
        self.labels = self._collect_labels(instructions)
        instruction_pointer = 0

        while instruction_pointer < len(instructions):
            instruction = instructions[instruction_pointer].strip()
            if not instruction:
                instruction_pointer += 1
                continue

            parts = instruction.split(maxsplit=1)
            opcode = parts[0]
            operand = parts[1] if len(parts) > 1 else None

            if opcode == "LABEL":
                instruction_pointer += 1
                continue
            if opcode == "PUSH":
                self.stack.append(int(operand))
            elif opcode == "LOAD":
                if operand not in self.environment:
                    raise RuntimeError(f"变量未定义: {operand}")
                self.stack.append(self.environment[operand])
            elif opcode == "STORE":
                self.environment[operand] = self._pop_stack()
            elif opcode == "ADD":
                self._binary_operation(lambda left, right: left + right)
            elif opcode == "SUB":
                self._binary_operation(lambda left, right: left - right)
            elif opcode == "MUL":
                self._binary_operation(lambda left, right: left * right)
            elif opcode == "DIV":
                self._binary_operation(self._safe_divide)
            elif opcode == "LT":
                self._binary_operation(lambda left, right: left < right)
            elif opcode == "GT":
                self._binary_operation(lambda left, right: left > right)
            elif opcode == "LE":
                self._binary_operation(lambda left, right: left <= right)
            elif opcode == "GE":
                self._binary_operation(lambda left, right: left >= right)
            elif opcode == "EQ":
                self._binary_operation(lambda left, right: left == right)
            elif opcode == "NE":
                self._binary_operation(lambda left, right: left != right)
            elif opcode == "AND":
                self._binary_operation(lambda left, right: bool(left) and bool(right))
            elif opcode == "OR":
                self._binary_operation(lambda left, right: bool(left) or bool(right))
            elif opcode == "NOT":
                self.stack.append(not bool(self._pop_stack()))
            elif opcode == "JMP":
                instruction_pointer = self._jump_to_label(operand)
                continue
            elif opcode == "JMP_IF_FALSE":
                condition = self._pop_stack()
                if not condition:
                    instruction_pointer = self._jump_to_label(operand)
                    continue
            elif opcode == "PRINT":
                print(self._pop_stack())
            else:
                raise RuntimeError(f"未知指令: {instruction}")

            instruction_pointer += 1

    def _collect_labels(self, instructions: list[str]) -> dict[str, int]:
        labels: dict[str, int] = {}
        for index, instruction in enumerate(instructions):
            parts = instruction.split(maxsplit=1)
            if parts and parts[0] == "LABEL":
                if len(parts) != 2:
                    raise RuntimeError(f"非法标签指令: {instruction}")
                labels[parts[1]] = index
        return labels

    def _jump_to_label(self, label: str | None) -> int:
        if label is None or label not in self.labels:
            raise RuntimeError(f"跳转目标不存在: {label}")
        return self.labels[label] + 1

    def _binary_operation(self, operation) -> None:
        right = self._pop_stack()
        left = self._pop_stack()
        self.stack.append(operation(left, right))

    def _safe_divide(self, left: int | bool, right: int | bool) -> int:
        if right == 0:
            raise RuntimeError("除零错误")
        return int(left) // int(right)

    def _pop_stack(self):
        if not self.stack:
            raise RuntimeError("数据栈为空，无法继续执行")
        return self.stack.pop()


StackVM = VirtualMachine