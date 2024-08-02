from lexer import KWDS, Lexer
from parser import (Parser, StringNode, ReferenceAssignNode,
                    VarAccessNode, NumberNode, BinOpNode)
from typedef import *
from errors import *


class Interpreter:
    def visit(self, node, context):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        val = method(node, context)
        return val

    def no_visit_method(self, node, context):
        return RuntimeResult().failure(RuntimeError(node.pos_start,
                                                    node.pos_end,
                                                    f'No visit_{type(node).__name__} method defined',
                                                    context))

    def visit_NumberNode(self, node, context):
        return RuntimeResult().success(Number(node.tok.value,
                                              t=node.tok.type
                                              ).set_context(context).set_pos(node.pos_start, node.pos_end))

    def visit_StringNode(self, node, context):
        return RuntimeResult().success(String(node.tok.value,
                                              ).set_context(context).set_pos(node.pos_start, node.pos_end))

    # CapsuleNode object shuttle results around between areas of the program
    # acts just like a ListNode, but i needed those for actual lists in the program
    def visit_CapsuleNode(self, node, context):
        res = RuntimeResult()
        elements = []
        for el in node.elements:
            ret = res.register(self.visit(el, context))
            if res.should_return(): return res
            elements.append(ret)
        if len(elements) == 1:
            if isinstance(elements[0], Struct):
                return RuntimeResult().success(elements[0].set_pos(node.pos_start, node.pos_end))
            return RuntimeResult().success(elements[0].set_context(context
                                                                   ).set_pos(node.pos_start, node.pos_end))
        return RuntimeResult().success(List(elements).set_context(context
                                                                  ).set_pos(node.pos_start, node.pos_end))

    def visit_ListNode(self, node, context):
        res = RuntimeResult()
        elements = []
        for el in node.elements:
            ret = res.register(self.visit(el, context))
            elements.append(ret)
            if res.should_return(): return res
        return RuntimeResult().success(List(elements).set_context(context
                                                                  ).set_pos(node.pos_start, node.pos_end))

    def visit_MapNode(self, node, context):
        res = RuntimeResult()
        elements = {}
        for key, val in node.elements.items():
            mykey = res.register(self.visit(key, context))
            myval = res.register(self.visit(val, context))
            elements[mykey] = myval

            if res.should_return(): return res

        return RuntimeResult().success(Map(elements).set_context(context
                                                                 ).set_pos(node.pos_start, node.pos_end))

    def visit_BinOpNode(self, node, context):
        res = RuntimeResult()

        # left might have already been evaluated when we get here
        if not isinstance(node.left_node, List):
            left = res.register(self.visit(node.left_node, context))
        else: left = node.left_node

        if res.should_return(): return res
        if isinstance(left, Struct) and node.op_tok.type == 'DOT':
            if not isinstance(node.right_node, VarAccessNode):
                return res.failure(VariableAccessError(node.pos_start,
                                                       node.pos_end,
                                                       f"DOT operator must accept identifier as input"))

            # make sure to access the right things if working on a dot operator
            right = res.register(self.visit(node.right_node, left.context))
            if res.error: return res
        else:
            right = res.register(self.visit(node.right_node, context))
            if res.error: return res
        if res.should_return(): return res

        # apply the appropriate operation
        match node.op_tok.type:
            case 'PLS' : result, error = left.add(right)
            case 'MNS' : result, error = left.sub(right)
            case 'MUL' : result, error = left.mul(right)
            case 'DIV' : result, error = left.div(right)
            case 'MOD' : result, error = left.mod(right)
            case 'POW' : result, error = left.pow(right)
            case 'EQ'  : result, error = left.eq(right)
            case 'NE'  : result, error = left.ne(right)
            case 'LT'  : result, error = left.lt(right)
            case 'GT'  : result, error = left.gt(right)
            case 'LE'  : result, error = left.le(right)
            case 'GE'  : result, error = left.ge(right)
            case 'AND' : result, error = left.logand(right)
            case 'OR'  : result, error = left.logor(right)
            case 'NAND': result, error = left.lognand(right)
            case 'NOR' : result, error = left.lognor(right)
            case 'XOR' : result, error = left.logxor(right)
            case 'AT'  : result, error = left.at(right)
            case 'LSLC': result, error = left.sliceleft(right)
            case 'RSLC': result, error = left.sliceright(right)
            case 'INJ' : result, error = left.inj(right)
            case 'IN'  : result, error = left.contains(right)
            case 'DOT' : result, error = right, None
            case _: pass

        if error: return res.failure(error)
        else: return res.success(result)

    def visit_UnaryOpNode(self, node, context):
        res = RuntimeResult()
        number = res.register(self.visit(node.node, context))
        if res.should_return(): return res

        error = None
        if node.op_tok.type == 'MNS':
            number, error = number.mul(Number(-1))
        if node.op_tok.type == 'NOT':
            number, error = number.lognot()

        if error: return res.failure(error)
        else: return res.success(number.set_pos(node.pos_start, node.pos_end))

    # this grabs a value by name from the current local table
    def visit_VarAccessNode(self, node, context):
        res = RuntimeResult()

        var_name = node.var_name_tok.value
        value = context.symbol_table.get(var_name)
        if not value:
            return res.failure(VariableAccessError(node.pos_start,
                                                   node.pos_end,
                                                   f"'{var_name}' is not defined"))

        if isinstance(value, Struct):
            value = value.copy().set_pos(node.pos_start, node.pos_end)
        elif context.display_name.startswith('struct'):
            value = value.set_pos(node.pos_start, node.pos_end)
        else:
            value = value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
        return res.success(value)

    # this assigns values to objects at the end of chained access expressions
    def visit_ReferenceAssignNode(self, node, context):
        res = RuntimeResult()

        value = res.register(self.visit(node.value_node, context))
        if res.error: return res

        childidxs = []
        parent = None
        curr_node = node.target_node
        while True:
            if isinstance(curr_node, BinOpNode):

                # go through the tree and store any access variables for children
                # e.g. if we have myvar.prop1.prop2.prop3, we need to save prop2
                # and prop3 until we know what sort of thing myvar.prop1 is
                if isinstance(curr_node.right_node, VarAccessNode):
                    val = String(curr_node.right_node.var_name_tok.value)
                elif isinstance(curr_node.right_node, NumberNode):
                    val = self.visit(curr_node.right_node, context).value
                elif isinstance(curr_node.right_node, BinOpNode):
                    val = res.register(self.visit(curr_node.right_node, context)).value
                    if res.error: return res
                elif isinstance(curr_node.right_node, StringNode):
                    val = self.visit(curr_node.right_node, context).value
                childidxs = [val] + childidxs

                if curr_node.op_tok.type in ('LSLC', 'RSLC'):
                    return res.failure(InvalidSyntaxError(curr_node.op_tok.pos_start,
                                                          curr_node.op_tok.pos_end,
                                                          'Slices not allowed on left of expression.'))

                if isinstance(curr_node.left_node, VarAccessNode):
                    parent = context.symbol_table.symbols[curr_node.left_node.var_name_tok.value]
                    break
                else: curr_node = curr_node.left_node

        c = parent
        parents = [c]
        if parent:
            for i in childidxs:
                if isinstance(c, Struct): c = c.context.symbol_table.symbols[i.value]
                elif isinstance(c, List):
                    try: c = c.elements[i.value]
                    except: c = c.elements[i]
                elif isinstance(c, Map): c = c.elements[i]
                parents.append(c)

            op_tok = node.op_tok.value
            match op_tok:
                case '=': pass
                case '+=': value = c.add(value)[0]
                case '-=': value = c.sub(value)[0]
                case '*=': value = c.mul(value)[0]
                case '/=': value = c.div(value)[0]
                case '%=': value = c.mod(value)[0]
                case '^=': value = c.pow(value)[0]
                case _: return res.failure(InvalidOperationTokenError(node.pos_start,
                                                                      node.pos_end,
                                                                      f'Expected assignment operator, got {op_tok}'))
            # change the object's value directly
            # there is still an issue here: if c is a Number, there is nothing stopping me from
            # giving that int a string value without changing it to a String object
            c.value = value.value

        # iterate back through chain of parents to update their local symbol tables
        # otherwise, property values and values references in the symbol table won't match
        for p in parents[::-1]:
            if isinstance(p, Struct): p.update_context()

        return res.success(value)

    def visit_ReferenceAccessNode(self, node, context):
        res = RuntimeResult()
        curr_node = node.head

        if isinstance(curr_node, ReferenceAssignNode):
            source = res.register(self.visit(curr_node, context))
            return res.success(source)

        # if isinstance(curr_node.root_var, VarAccessNode):
        #     val = res.register(self.visit(BinOpNode(curr_node.root_var, Token('AT', '@'), curr_node.specifier),
        #                                   context))

            if res.error: return res
            return res.success(val)

    def visit_VarAssignNode(self, node, context):
        res = RuntimeResult()
        var_name = node.var_name_tok.value
        op_tok = node.op_tok.value

        if var_name in KWDS + ['T', 'F']:
            return res.failure(BuiltinViolationError(node.pos_start,
                                                     node.pos_end,
                                                     f'Cannot overwrite keyword {var_name}.'))

        # value is the new value for the variable
        value = res.register(self.visit(node.value_node, context))
        if res.should_return(): return res

        # og_val is the current variable if it exists
        og_val = context.symbol_table.get(var_name)
        static_mode = context.symbol_table.get('static-typing').is_true()

        # handle new variable assignment
        if og_val is None:
            # if a static type is provided, check to make sure it isn't violated
            # note that float values will be truncated if cast to static int
            # this should execute no matter what type mode we are in
            if node.statictype not in ['var', 'default']:
                if value.type.lower() != node.statictype:
                    if isinstance(value, Number):
                        if node.statictype == 'int':
                            value.value = int(value.value)
                            value.type = 'INT'
                        elif node.statictype == 'flt':
                            value.value = float(value.value)
                            value.type = 'FLT'
                        else: return res.failure(StaticViolationError(node.pos_start,
                                                                      node.pos_end,
                                                                      f'Cannot convert {value.value} to {node.statictype}'))
                    else: return res.failure(StaticViolationError(node.pos_start,
                                                                  node.pos_end,
                                                                  f'Cannot convert {value.value} to {node.statictype}'))
                value.static = True

            if static_mode:
                if node.statictype == 'var': value.static = False
                else: value.static = True
            else:
                if node.statictype not in ['var', 'default']: value.static = True
                else: value.static = False

            # if const keyword is used, set new value to constant
            if node.const: value.const = True

            # can only use bare assignment to create new value
            if op_tok == '=':
                if isinstance(value, Struct):
                    value.instance_name = var_name

                    ##
                    value = value.copy()
                    ##
                context.symbol_table.set(var_name, value)
            else: return res.failure(VariableAccessError(node.pos_start,
                                                         node.pos_end,
                                                         f'Symbol {var_name} doesn\'t exist'))
            return res.success(value)

        # variable already exists
        else:
            if og_val.const:
                return res.failure(ConstantViolationError(node.pos_start,
                                                          node.pos_end,
                                                          f'Cannot change value of constant variable {var_name}'))
            if node.statictype != 'default' or node.const:
                return res.failure(InvalidSpecifierError(node.pos_start,
                                                         node.pos_end,
                                                         f'Specifiers not allowed on existing variable {var_name}.'))

            # only check number conversion if variable is static
            # if in static mode and not otherwise specified, the variable should be set to
            # static automatically
            if og_val.static:
                if value.type != og_val.type:
                    if isinstance(value, Number):
                        if og_val.type == 'INT':
                            value.value = int(value.value)
                            value.type = 'INT'
                        elif og_val.type == 'FLT':
                            value.value = float(value.value)
                            value.type = 'FLT'
                        else:
                            return res.failure(StaticViolationError(node.pos_start,
                                                                    node.pos_end,
                                                                    f'Cannot convert static {og_val.type} to {value.type}'))

                        # handle when triggers for current variable if there are any
                        rmv = []
                        for t in value.triggers:
                            condition = res.register(self.visit(node.condition_node, context))
                            if condition.is_true():
                                result = res.register(self.visit(node.body_node, context))
                                if res.error: return res
                                if res.loop_should_break: rmv.append(t)
                            if res.should_return(): return res
                        for t in rmv: value.triggers.remove(t)

                        value.static = True

                    # if the new value's inferred type is different than the original value,
                    # throw an error
                    else: return res.failure(StaticViolationError(node.pos_start,
                                                                  node.pos_end,
                                                                  f'Cannot convert {var_name} [{og_val.type}] to {value.type}'))

                value.static = True

            value.const = og_val.const
            value.triggers = og_val.triggers

        if op_tok == '=':

            ##
            if isinstance(value, Struct):
                value = value.copy()
            ##

            context.symbol_table.set(var_name, value)

            rmv = []
            for t in value.triggers:
                condition = res.register(self.visit(t.condition_node, context))
                if res.should_return(): return res

                if condition.is_true():
                    result = res.register(self.visit(t.body_node, context))
                    if res.error: return res
                    if res.loop_should_break:
                        rmv.append(t)
            for t in rmv: value.triggers.remove(t)

        match op_tok:
            case '=': pass
            case '+=': value = og_val.add(value)[0]
            case '-=': value = og_val.sub(value)[0]
            case '*=': value = og_val.mul(value)[0]
            case '/=': value = og_val.div(value)[0]
            case '%=': value = og_val.mod(value)[0]
            case '^=': value = og_val.pow(value)[0]
            case _: return res.failure(InvalidOperationTokenError(node.pos_start,
                                                                  node.pos_end,
                                                                  f'Expected assignment operator, got {op_tok}'))
        context.symbol_table.set(var_name, value)

        rmv = []
        for t in value.triggers:
            condition = res.register(self.visit(t.condition_node, context))
            if res.should_return(): return res

            if condition.is_true():
                result = res.register(self.visit(t.body_node, context))
                if res.error: return res
                if res.loop_should_break: rmv.append(t)
        for t in rmv: value.triggers.remove(t)

        return res.success(value)

    def visit_IfNode(self, node, context):
        res = RuntimeResult()

        for condition, expr, ret in node.cases:
            condition_value = res.register(self.visit(condition, context))
            if res.should_return(): return res

            if condition_value.is_true():
                expr_value = res.register(self.visit(expr, context))
                if res.should_return(): return res
                return res.success(expr_value)

        if node.else_case:
            else_value = res.register(self.visit(node.else_case[0], context))
            if res.should_return(): return res
            return res.success(else_value)

        return res.success(None)

    def visit_ForNode(self, node, context):
        res = RuntimeResult()
        elements = []

        start_value = res.register(self.visit(node.start_value_node, context))
        if res.should_return(): return res

        end_value = res.register(self.visit(node.end_value_node, context))
        if res.should_return(): return res

        if node.step_value_node:
            step_value = res.register(self.visit(node.step_value_node, context))
            if res.should_return(): return res
        else:
            if start_value.value < end_value.value: step_value = Number(1)
            else: step_value = Number(-1)

        i = start_value.value
        # go forwards or backwards depending on step
        if step_value.value >= 0: condition = lambda: i < end_value.value
        else: condition = lambda: i > end_value.value

        while condition():
            context.symbol_table.set(node.var_name_tok.value, Number(i))
            i += step_value.value

            result = res.register(self.visit(node.body_node, context))
            if res.should_return() and not res.loop_should_continue and not res.loop_should_break: return res
            if res.loop_should_continue: continue
            if res.loop_should_break: break

            elements.append(result)

        return res.success(List(elements
                                ).set_context(context).set_pos(node.pos_start, node.pos_end))

    def visit_ForEachNode(self, node, context):
        res = RuntimeResult()
        elements = []

        container = res.register(self.visit(node.container_node, context))
        if res.should_return(): return res

        for elem in container.elements:

            context.symbol_table.set(node.var_name_tok.value, elem)
            result = res.register(self.visit(node.body_node, context))
            if (res.should_return() and
                    not res.loop_should_continue and
                    not res.loop_should_break):
                return res

            if res.loop_should_continue: continue
            if res.loop_should_break: break
            elements.append(result)

        return res.success(List(elements
                                ).set_context(context).set_pos(node.pos_start, node.pos_end))

    def visit_WhileNode(self, node, context):
        res = RuntimeResult()

        elements = []
        while True:
            condition = res.register(self.visit(node.condition_node, context))
            if res.should_return(): return res
            if not condition.is_true(): break

            result = res.register(self.visit(node.body_node, context))
            if (res.should_return() and
                    not res.loop_should_continue and
                    not res.loop_should_break):
                return res

            if res.loop_should_continue: continue
            if res.loop_should_break: break
            elements.append(result)

        return res.success(List(elements
                                ).set_context(context).set_pos(node.pos_start, node.pos_end))

    def visit_WhenNode(self, node, context):
        res = RuntimeResult()
        elements = []

        val = context.symbol_table.get(node.target)
        if val is None:
            return res.failure(VariableAccessError(node.pos_start,
                                                   node.pos_end,
                                                   f'Variable {node.target} does not exist'))

        # when triggers can currently only be added to named variables
        context.symbol_table.symbols[node.target].triggers.append(node)

        return res.success(List(elements
                                ).set_context(context).set_pos(node.pos_start, node.pos_end))

    def visit_DeleteNode(self, node, context):
        res = RuntimeResult()

        name = node.name.value
        if name not in context.symbol_table.symbols:
            return res.failure(VariableAccessError(node.pos_start,
                                                   node.pos_end,
                                                   f'Variable {node.target} does not exist'))
        else: context.symbol_table.remove(name)

        return res.success(Number(0))

    def visit_ContinueNode(self, node, context):
        return RuntimeResult().success_continue()

    def visit_BreakNode(self, node, context):
        return RuntimeResult().success_break()

    def visit_OnceNode(self, node, context):
        return RuntimeResult().success_break()

    def visit_ReturnNode(self, node, context):
        res = RuntimeResult()
        if node.return_node:
            val = res.register(self.visit(node.return_node, context))
            if res.should_return(): return res
        else: val = Number.null
        return res.success_return(val)

    def visit_UseNode(self, node, context):
        res = RuntimeResult()

        name = node.fname.value
        if name == 'static':
            context.symbol_table.set('static-typing', Number(1))
            return res.success(None)

        try:
            f = open(f'C:\\Users\\pvshe\\PycharmProjects\\safyr\\{name}.sfr', 'r')
            code = f.read()
            f.close()
        except: return res.failure(ModuleNotFoundError(node.fname.pos_start,
                                                       node.fname.pos_end,
                                                       f'No module found: {name}'))
        ast = Parser(Lexer().tokenize(code).value).parse()
        if ast.error: return res.failure(ModuleImportError(node.fname.pos_start,
                                                           node.fname.pos_end,
                                                           f'Error parsing file {name}'))
        result = self.visit(ast.node, context)

        return res.success(result.value)

    def visit_InterfaceDefinitionNode(self, node, context):
        res = RuntimeResult()

        func_name = node.var_name_tok.value
        body_node = node.body_node
        func_val = Function(func_name,
                            body_node,
                            [],
                            node.auto_return
                            ).set_context(context).set_pos(node.pos_start, node.pos_end)
        if node.var_name_tok: context.symbol_table.set(func_name, func_val)

        return res.success(func_val)

    def visit_FunctionDefinitionNode(self, node, context):
        res = RuntimeResult()

        func_name = node.var_name_tok.value if node.var_name_tok else None
        body_node = node.body_node
        arg_names = [a.value for a in node.arg_name_toks]
        func_val = Function(func_name, body_node,
                            arg_names,
                            node.auto_return
                            ).set_context(context).set_pos(node.pos_start, node.pos_end)
        if node.var_name_tok: context.symbol_table.set(func_name, func_val)

        return res.success(func_val)

    def visit_CallNode(self, node, context):
        res = RuntimeResult()

        args = []
        value_to_call = res.register(self.visit(node.node_to_call, context))
        if res.should_return(): return res
        value_to_call = value_to_call.copy().set_pos(node.pos_start, node.pos_end)

        # grab values for all input arguments
        for i in range(len(node.arg_nodes)):
            arg = res.register(self.visit(node.arg_nodes[i], context))
            if res.error: return res

            # automatically append non-structs
            if not isinstance(arg, Struct):
                args.append(arg)
                if res.should_return(): return res
            else:
                # check if struct has an interface for this function
                # if so, call that and replace the struct argument with its proxy
                if value_to_call.name not in arg.interfaces:
                    args.append(arg)
                    if res.should_return(): return res
                else:
                    func = arg.context.symbol_table.get(value_to_call.name)
                    myval = res.register(self.visit(func.body_node, arg.context))
                    if res.error: return res
                    args.append(myval)

        retval = res.register(value_to_call.execute(args, self))
        if res.should_return(): return res

        # update any chained symbol tables if needed
        for i in range(len(node.arg_nodes)):
            curr = node.arg_nodes[i]
            while isinstance(curr, BinOpNode):
                if isinstance(curr.left_node, VarAccessNode):
                    p = context.symbol_table.symbols[curr.left_node.var_name_tok.value]
                    if isinstance(p, Struct):
                        p.update_context()
                        curr = None
                elif isinstance(curr.left_node, BinOpNode): curr = curr.left_node
            if isinstance(curr, VarAccessNode):
                p = context.symbol_table.symbols[curr.var_name_tok.value]
                if isinstance(p, Struct): p.update_context()

        if isinstance(retval, Struct):
            return res.success(retval.copy().set_pos(node.pos_start, node.pos_end))
        return res.success(retval.copy().set_pos(node.pos_start, node.pos_end).set_context(context))

    def visit_StructDefinitionNode(self, node, context):
        res = RuntimeResult()

        struct_name = node.var_name_tok.value if node.var_name_tok else None
        body_node = node.body_node
        arg_names = [a.value for a in node.arg_name_toks]
        struct_val = StructGenerator(struct_name,
                                     body_node,
                                     arg_names,
                                     node.auto_return
                                     ).set_context(context).set_pos(node.pos_start, node.pos_end)
        if node.var_name_tok:
            context.symbol_table.set(struct_name, struct_val)

        return res.success(struct_val)

    def visit_ErrorHandlerNode(self, node, context):
        res = RuntimeResult()

        try_block = node.try_node
        catch_block = node.catch_node
        new_context = Context('<errorhandler>', context, node.pos_start)
        new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)

        # prepare a symbol table for updated values
        for s in context.symbol_table.symbols:
            if s in context.symbol_table.globals: continue
            new_context.symbol_table.symbols[s] = context.symbol_table.symbols[s]

        # create a backup symbol table so that any changes made before an error was
        # thrown in the try block will be restored before the catch block executes
        restore = {key: val for key, val in new_context.symbol_table.symbols.items()}
        res.register(self.visit(try_block, new_context))
        if res.error:
            for key, value in restore.items():
                if key in new_context.symbol_table.symbols:
                    new_context.symbol_table.symbols[key] = restore[key]
            res.register(self.visit(catch_block, new_context))
            if res.error: return res

        # update symbol table
        for key in new_context.symbol_table.symbols:
            if key in context.symbol_table.symbols:
                context.symbol_table.symbols[key] = new_context.symbol_table.symbols[key]

        return res.success(Number(0))
