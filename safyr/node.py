
class NumberNode:
    def __init__(self, tok):
        self.tok = tok

        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end

    def __repr__(self):
        return f'{self.tok}'


class StringNode:
    def __init__(self, tok):
        self.tok = tok

        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end

    def __repr__(self):
        return f'"{self.tok}"'


class CapsuleNode:
    def __init__(self, element_nodes, pos_start, pos_end):
        self.elements = element_nodes

        self.pos_start = pos_start
        self.pos_end = pos_end


class ListNode:
    def __init__(self, element_nodes, pos_start, pos_end):
        self.elements = element_nodes

        self.pos_start = pos_start
        self.pos_end = pos_end


class MapNode:
    def __init__(self, elements, pos_start, pos_end):
        self.elements = elements

        self.pos_start = pos_start
        self.pos_end = pos_end


class UseNode:
    def __init__(self, fname):
        self.fname = fname

        self.pos_start = self.fname.pos_start
        self.pos_end = self.fname.pos_end

    def __repr__(self):
        return f'<{self.fname}>'


class DeleteNode:
    def __init__(self, name):
        self.name = name

        self.pos_start = self.name.pos_start
        self.pos_end = self.name.pos_end

    def __repr__(self):
        return f'<delete {self.name}>'


class VarAccessNode:
    def __init__(self, var_name_tok):
        self.var_name_tok = var_name_tok

        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.var_name_tok.pos_end

    def __repr__(self):
        return f'{self.var_name_tok}'


class ReferenceAccessNode:
    def __init__(self, head):
        self.head = head

        self.pos_start = self.head.value_node.pos_start
        self.pos_end = self.head.value_node.pos_end

    def __repr__(self):
        return f'{self.head}'


class ReferenceAssignNode:
    def __init__(self, target_node, op_tok, value_node):
        self.target_node = target_node
        self.op_tok = op_tok
        self.value_node = value_node


class VarAssignNode:
    def __init__(self, var_name_tok, op_tok, value_node,
                 const=False, statictype=None):
        self.var_name_tok = var_name_tok
        self.op_tok = op_tok
        self.value_node = value_node
        self.const = const
        self.statictype = statictype

        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.value_node.pos_end

    def __repr__(self):
        return f'({self.var_name_tok} {self.op_tok} {self.value_node})'


class BinOpNode:
    def __init__(self, left_node, op_tok, right_node):
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node

        self.pos_start = self.left_node.pos_start
        self.pos_end = self.right_node.pos_end

    def __repr__(self):
        return f'({self.left_node}, {self.op_tok}, {self.right_node})'


class UnaryOpNode:
    def __init__(self, op_tok, node):
        self.op_tok = op_tok
        self.node = node

        self.pos_start = self.op_tok.pos_start
        self.pos_end = node.pos_end

    def __repr__(self):
        return f'({self.op_tok}, {self.node})'


class IfNode:
    def __init__(self, cases, else_case):
        self.cases = cases
        self.else_case = else_case

        self.pos_start = self.cases[0][0].pos_start
        self.pos_end = (self.else_case or self.cases[len(self.cases) - 1])[0].pos_end


class ForNode:
    def __init__(self, var_name_tok, start_value_node, end_value_node, step_value_node, body_node, should_return_null):
        self.var_name_tok = var_name_tok
        self.start_value_node = start_value_node
        self.end_value_node = end_value_node
        self.step_value_node = step_value_node
        self.body_node = body_node
        self.should_return_null = should_return_null

        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.body_node.pos_end


class ForEachNode:
    def __init__(self, var_name_tok, container_node, body_node, should_return_null):
        self.var_name_tok = var_name_tok
        self.container_node = container_node
        self.body_node = body_node
        self.should_return_null = should_return_null

        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.body_node.pos_end


class WhileNode:
    def __init__(self, condition_node, body_node, should_return_null):
        self.condition_node = condition_node
        self.body_node = body_node
        self.should_return_null = should_return_null

        self.pos_start = self.condition_node.pos_start
        self.pos_end = self.body_node.pos_end


class WhenNode:
    def __init__(self, condition_node, body_node, should_return_null):
        self.condition_node = condition_node
        self.target = condition_node.left_node.var_name_tok.value

        self.body_node = body_node
        self.should_return_null = should_return_null

        self.pos_start = self.condition_node.pos_start
        self.pos_end = self.body_node.pos_end


class DeferNode:
    def __init__(self, body_node, should_return_null):
        self.body_node = body_node
        self.should_return_null = should_return_null

        self.pos_start = self.body_node.pos_start
        self.pos_end = self.body_node.pos_end


class ContinueNode:
    def __init__(self, pos_start, pos_end):
        self.pos_start = pos_start
        self.pos_end = pos_end


class BreakNode:
    def __init__(self, pos_start, pos_end):
        self.pos_start = pos_start
        self.pos_end = pos_end


class OnceNode:
    def __init__(self, pos_start, pos_end):
        self.pos_start = pos_start
        self.pos_end = pos_end


class ReturnNode:
    def __init__(self, return_node, pos_start, pos_end):
        self.return_node = return_node
        self.pos_start = pos_start
        self.pos_end = pos_end


class InterfaceDefinitionNode:
    def __init__(self, var_name_tok, body_node, auto_return):
        self.var_name_tok = var_name_tok
        self.body_node = body_node
        self.auto_return = auto_return

        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.body_node.pos_end


class FunctionDefinitionNode:
    def __init__(self, var_name_tok, arg_name_toks, body_node, auto_return):
        self.var_name_tok = var_name_tok
        self.arg_name_toks = arg_name_toks
        self.body_node = body_node
        self.auto_return = auto_return

        if self.var_name_tok:
            self.pos_start = self.var_name_tok.pos_start
        elif len(self.arg_name_toks) > 0:
            self.pos_start = self.arg_name_toks[0].pos_start
        else:
            self.pos_start = self.body_node.pos_start

        self.pos_end = self.body_node.pos_end


class CallNode:
    def __init__(self, node_to_call, arg_nodes):
        self.node_to_call = node_to_call
        self.arg_nodes = arg_nodes

        self.pos_start = self.node_to_call.pos_start

        if len(self.arg_nodes) > 0:
            self.pos_end = self.arg_nodes[len(self.arg_nodes) - 1].pos_end
        else:
            self.pos_end = self.node_to_call.pos_end


class StructDefinitionNode:
    def __init__(self, var_name_tok, arg_name_toks, body_node, auto_return):
        self.var_name_tok = var_name_tok
        self.arg_name_toks = arg_name_toks
        self.body_node = body_node
        self.auto_return = auto_return

        self.interfaces = []

        if self.var_name_tok:
            self.pos_start = self.var_name_tok.pos_start
        elif len(self.arg_name_toks) > 0:
            self.pos_start = self.arg_name_toks[0].pos_start
        else:
            self.pos_start = self.body_node.pos_start

        self.pos_end = self.body_node.pos_end


class ErrorHandlerNode:
    def __init__(self, try_tok, try_node, catch_node, auto_return=True):
        self.try_node = try_node
        self.catch_node = catch_node
        self.auto_return = auto_return

        self.pos_start = try_tok.pos_start

        self.pos_end = try_tok.pos_end
