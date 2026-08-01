# definitions of AST nodes


class Node:
    """Base class for all visitable nodes.
    
    :: INPUT ::
     - pos_start : Position
         The position of the beginning token.
     - pos_end   : Position
         The position of the ending token.
    """
    def __init__(self, pos_start, pos_end):

        self.pos_start = pos_start
        self.pos_end   = pos_end


class NumberNode(Node):
    """Class representing numerical values.
    
    :: INPUT ::
    -- tok : Token
         Current object token.

    :: ATTRS ::
    -- tok : Token (<~ INPUT)
    """
    def __init__(self, tok):

        super().__init__(tok.pos_start, tok.pos_end)
        self.tok = tok

    def __repr__(self):
        return f'{self.tok}'


class StringNode(Node):
    """Class representing string values.
        
        :: INPUT ::
        -- tok : Token
             Current object token.
    
        :: ATTRS ::
        -- tok : Token (<~ INPUT)
        """
    def __init__(self, tok):

        super().__init__(tok.pos_start, tok.pos_end)
        self.tok = tok

    def __repr__(self):
        return f'"{self.tok}"'


class CapsuleNode(Node):
    def __init__(self,
                 element_nodes,
                 pos_start,
                 pos_end):

        super().__init__(pos_start, pos_end)
        self.elements = element_nodes


class ListNode(CapsuleNode):
    def __init__(self,
                 element_nodes,
                 pos_start,
                 pos_end):

        super().__init__(element_nodes, pos_start, pos_end)


class MapNode(CapsuleNode):
    def __init__(self,
                 elements,
                 pos_start,
                 pos_end):

        super().__init__(elements, pos_start, pos_end)


class ReferenceAssignNode(Node):
    def __init__(self,
                 target_node,
                 op_tok,
                 value_node):

        super().__init__(target_node.pos_start, value_node.pos_end)

        self.target_node = target_node
        self.op_tok = op_tok
        self.value_node = value_node


class VarAssignNode(Node):
    def __init__(self,
                 var_name_tok,
                 op_tok,
                 value_node,
                 constvar=False,
                 globalvar=False,
                 statictype=None):

        super().__init__(var_name_tok.pos_start, var_name_tok.pos_end)

        self.var_name_tok = var_name_tok
        self.op_tok = op_tok
        self.value_node = value_node
        self.constvar = constvar
        self.globalvar = globalvar
        self.statictype = statictype

    def __repr__(self):
        return f'({self.var_name_tok} {self.op_tok} {self.value_node})'


class BinOpNode(Node):
    def __init__(self,
                 left_node,
                 op_tok,
                 right_node):

        super().__init__(left_node.pos_start, right_node.pos_end)

        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node

    def __repr__(self):
        return f'({self.left_node}, {self.op_tok}, {self.right_node})'


class UnaryOpNode(Node):
    def __init__(self,
                 op_tok,
                 node):

        super().__init__(op_tok.pos_start, node.pos_end)

        self.op_tok = op_tok
        self.node = node

    def __repr__(self):
        return f'({self.op_tok}, {self.node})'


class IfNode(Node):
    def __init__(self,
                 cases,
                 else_case):

        super().__init__(cases[0][0].pos_start,
                         (else_case or cases[len(cases) - 1])[0].pos_end)

        self.cases = cases
        self.else_case = else_case


class ForNode(Node):
    def __init__(self,
                 var_name_tok,
                 start_value_node,
                 end_value_node,
                 step_value_node,
                 body_node,
                 should_return_null):

        super().__init__(var_name_tok.pos_start, body_node.pos_end)

        self.var_name_tok = var_name_tok
        self.start_value_node = start_value_node
        self.end_value_node = end_value_node
        self.step_value_node = step_value_node
        self.body_node = body_node
        self.should_return_null = should_return_null


class ForEachNode(Node):
    def __init__(self,
                 var_name_tok,
                 container_node,
                 body_node,
                 should_return_null):

        super().__init__(var_name_tok.pos_start, body_node.pos_end)

        self.var_name_tok = var_name_tok
        self.container_node = container_node
        self.body_node = body_node
        self.should_return_null = should_return_null


class WhenNode(Node):
    def __init__(self,
                 condition_node,
                 body_node,
                 should_return_null):

        super().__init__(condition_node.pos_start, body_node.pos_end)

        self.condition_node = condition_node
        self.target = condition_node.left_node.var_name_tok.value

        self.body_node = body_node
        self.should_return_null = should_return_null


class WhileNode(Node):
    def __init__(self,
                 condition_node,
                 body_node,
                 should_return_null):

        super().__init__(condition_node.pos_start, body_node.pos_end)

        self.condition_node = condition_node
        self.body_node = body_node
        self.should_return_null = should_return_null
        

class InterfaceDefinitionNode(Node):
    def __init__(self,
                 var_name_tok,
                 body_node,
                 auto_return):

        super().__init__(var_name_tok.pos_start, body_node.pos_end)

        self.var_name_tok = var_name_tok
        self.body_node = body_node
        self.auto_return = auto_return


class StructDefinitionNode(Node):
    def __init__(self,
                 var_name_tok,
                 arg_name_toks,
                 body_node,
                 auto_return):

        if var_name_tok:
            start = var_name_tok.pos_start
        elif arg_name_toks:
            start = arg_name_toks[0].pos_start
        else:
            start = body_node.pos_start
        super().__init__(start, body_node.pos_end)

        self.var_name_tok = var_name_tok
        self.arg_name_toks = arg_name_toks
        self.body_node = body_node
        self.auto_return = auto_return

        self.interfaces = []


class FunctionDefinitionNode(Node):
    def __init__(self,
                 var_name_tok,
                 arg_name_toks,
                 body_node,
                 auto_return):

        if var_name_tok:
            start = var_name_tok.pos_start
        elif arg_name_toks:
            start = arg_name_toks[0].pos_start
        else:
            start = body_node.pos_start
        super().__init__(start, body_node.pos_end)

        self.var_name_tok = var_name_tok
        self.arg_name_toks = arg_name_toks
        self.body_node = body_node
        self.auto_return = auto_return


class ReturnNode(Node):
    def __init__(self,
                 return_node,
                 pos_start,
                 pos_end):

        super().__init__(pos_start, pos_end)

        self.return_node = return_node


class CallNode(Node):
    def __init__(self,
                 node_to_call,
                 arg_nodes):

        end = arg_nodes[-1].pos_end if arg_nodes else node_to_call.pos_end
        super().__init__(node_to_call.pos_start, end)

        self.node_to_call = node_to_call
        self.arg_nodes = arg_nodes


class ErrorHandlerNode(Node):
    """Organizes error logic branches.

    ::INPUT::

    - try_tok     : Token
        The token object

    - try_node    : Node
        Node containing `try` block.

    - catch_node  : Node
        Node containing `catch` block.

    - auto_return : bool (optional)

    """
    def __init__(self,
                 try_tok,
                 try_node,
                 catch_node,
                 auto_return=True):

        super().__init__(try_tok.pos_start, try_tok.pos_end)

        self.try_node = try_node
        self.catch_node = catch_node
        self.auto_return = auto_return


class VarAccessNode(Node):
    def __init__(self, var_name_tok):
        super().__init__(var_name_tok.pos_start, var_name_tok.pos_end)
        self.var_name_tok = var_name_tok

    def __repr__(self):
        return f'{self.var_name_tok}'


class ReferenceAccessNode(Node):
    def __init__(self, head):
        super().__init__(head.pos_start, head.pos_end)
        self.head = head

    def __repr__(self):
        return f'{self.head}'


class DeferNode(Node):
    def __init__(self,
                 body_node,
                 should_return_null):

        super().__init__(body_node.pos_start, body_node.pos_end)

        self.body_node = body_node
        self.should_return_null = should_return_null


class UseNode(Node):
    def __init__(self, fname):
        super().__init__(fname.pos_start, fname.pos_end)
        self.fname = fname

    def __repr__(self):
        return f'<{self.fname}>'


class DeleteNode(Node):
    def __init__(self, name):
        super().__init__(name.pos_start, name.pos_end)
        self.name = name

    def __repr__(self):
        return f'<delete {self.name}>'


class ContinueNode(Node):
    def __init__(self, pos_start, pos_end):
        super().__init__(pos_start, pos_end)


class BreakNode(Node):
    def __init__(self, pos_start, pos_end):
        super().__init__(pos_start, pos_end)


class OnceNode(Node):
    def __init__(self, pos_start, pos_end):
        super().__init__(pos_start, pos_end)
