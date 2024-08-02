from errors import *
from result import RuntimeResult
from node import VarAssignNode
import os
from random import random


class Position:
    
    def __init__(self, idx, ln, col, fn, ftxt):
        self.idx = idx
        self.ln = ln
        self.col = col
        self.fn = fn
        self.ftxt = ftxt

    def advance(self):
        self.idx += 1
        self.col += 1
        return self

    def __repr__(self):
        return f'idx: {self.idx} line: {self.ln} col: {self.col} name: {self.fn}'

    def copy(self):
        return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)


class Token:
    
    def __init__(self, type_, value=None, pos_start=None, pos_end=None):
        self.type = type_
        self.value = value

        if pos_start:
            self.pos_start = pos_start
            self.pos_end = pos_start.copy()
            self.pos_end.advance()

        if pos_end:
            self.pos_end = pos_end

    def matches(self, other):
        return self == other

    def __repr__(self):
        if self.value is not None: return f'{self.type}:{self.value}'
        return f'{self.type}'

    def __eq__(self, other):
        return self.value == other.value and self.type == other.type

class SymbolTable:
    
    def __init__(self, parent=None):
        self.symbols = {}
        self.parent = parent
        self.globals = []

    def get(self, name):
        value = self.symbols.get(name, None)
        if value == None and self.parent:
            # return self.parent.get(name)
            if name in self.parent.globals:
                return self.parent.get(name)
        return value

    def set(self, name, value):
        self.symbols[name] = value

    def remove(self, name):
        del self.symbols[name]


class Context:
    
    def __init__(self, display_name, parent=None, parent_entry_pos=None):
        self.display_name = display_name
        self.parent = parent
        self.parent_entry_pos = parent_entry_pos
        self.symbol_table = None


class Value:
    
    def __init__(self, t=None, static=False, const=False):
        self.set_pos()
        self.set_context()
        self.value = None
        self.type = t
        self.static = static
        self.const = const
        self.triggers = []

    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def set_context(self, context=None):
        self.context = context
        return self

    def add(self, other): return None, self.illegal_op(other)

    def sub(self, other): return None, self.illegal_op(other)

    def mul(self, other): return None, self.illegal_op(other)

    def div(self, other): return None, self.illegal_op(other)

    def mod(self, other): return None, self.illegal_op(other)

    def pow(self, other): return None, self.illegal_op(other)

    def eq(self, other): return None, self.illegal_op(other)

    def ne(self, other): return None, self.illegal_op(other)

    def lt(self, other): return None, self.illegal_op(other)

    def gt(self, other): return None, self.illegal_op(other)

    def le(self, other): return None, self.illegal_op(other)

    def ge(self, other): return None, self.illegal_op(other)

    def logand(self, other): return None, self.illegal_op(other)

    def logor(self, other): return None, self.illegal_op(other)

    def lognand(self, other): return None, self.illegal_op(other)

    def lognor(self, other): return None, self.illegal_op(other)

    def logxor(self, other): return None, self.illegal_op(other)

    def lognot(self): return None, self.illegal_op(self)

    def at(self, other): return None, self.illegal_op(other)

    def contains(self, other): return None, self.illegal_op(other)

    def inj(self, other): return None, self.illegal_op(other)
        
    def sliceleft(self, other): return None, self.illegal_op(other)

    def sliceright(self, other): return None, self.illegal_op(other)

    def copy(self):
        copy = Value(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def is_true(self): return self.value != 0

    def illegal_op(self, other=None):
        if other: return NotImplementedError(self.pos_start,
                                             other.pos_end,
                                             'Illegal operation',
                                             self.context)

    def __repr__(self):
        return str(self.value)


class Number(Value):
    
    def __init__(self, value, t=None):
        super().__init__(t=t if t else 'INT')
        self.value = value

    def __eq__(self, other):
        if isinstance(other, Number):
            return self.value == other.value and self.type == other.type
        return False

    def __hash__(self):
        return self.value.__hash__()

    def add(self, other):
        if isinstance(other, Number):
            ret = self.copy()
            ret.value = self.value + other.value
            return ret.set_context(self.context), None
        else: return None, Value.illegal_op(self, other)

    def sub(self, other):
        if isinstance(other, Number):
            ret = self.copy()
            ret.value = self.value - other.value
            return ret.set_context(self.context), None
        else: return None, Value.illegal_op(self, other)

    def mul(self, other):
        if isinstance(other, Number):
            ret = self.copy()
            ret.value = self.value * other.value
            return ret.set_context(self.context), None
        else: return None, Value.illegal_op(self, other)

    def div(self, other):
        if isinstance(other, Number):
            if other.value == 0: return None, RuntimeError(other.pos_start,
                                                           other.pos_end,
                                                           'Division by zero',
                                                           self.context)
            ret = self.copy()
            ret.value = self.value / other.value
            return ret.set_context(self.context), None
        else: return None, Value.illegal_op(self, other)

    def mod(self, other):
        if isinstance(other, Number):
            if other.value == 0: return None, RuntimeError(other.pos_start,
                                                           other.pos_end,
                                                           'Modulo by zero',
                                                           self.context)
            ret = self.copy()
            ret.value = self.value % other.value
            return ret.set_context(self.context), None
        else: return None, Value.illegal_op(self, other)

    def pow(self, other):
        if isinstance(other, Number):
            ret = self.copy()
            ret.value = self.value ** other.value
            return ret.set_context(self.context), None
        else: return None, Value.illegal_op(self, other)

    def eq(self, other):
        if isinstance(other, Number):
            return Number(int(self.value == other.value)).set_context(self.context), None
        else: return Number(0), None

    def ne(self, other):
        if isinstance(other, Number):
            return Number(int(self.value != other.value)).set_context(self.context), None
        else: return Number(1), None

    def lt(self, other):
        if isinstance(other, Number):
            return Number(int(self.value < other.value)).set_context(self.context), None
        else: return None, Value.illegal_op(self, other)

    def gt(self, other):
        if isinstance(other, Number):
            return Number(int(self.value > other.value)).set_context(self.context), None
        else: return None, Value.illegal_op(self, other)

    def le(self, other):
        if isinstance(other, Number):
            return Number(int(self.value <= other.value)).set_context(self.context), None
        else: return None, Value.illegal_op(self, other)

    def ge(self, other):
        if isinstance(other, Number):
            return Number(int(self.value >= other.value)).set_context(self.context), None
        else: return None, Value.illegal_op(self, other)

    def logand(self, other):
        return Number(self.is_true() and other.is_true()).set_context(self.context), None

    def logor(self, other):
        return Number(self.is_true() or other.is_true()).set_context(self.context), None

    def lognand(self, other):
        return Number(not (self.is_true() and other.is_true())).set_context(self.context), None

    def lognor(self, other):
        return Number(not (self.is_true() or other.is_true())).set_context(self.context), None

    def logxor(self, other):
        return Number(int((self.is_true() and not other.is_true()) or (not self.is_true() and other.is_true()))
                      ).set_context(self.context), None

    def lognot(self):
        return Number(1 if self.value == 0 else 0).set_context(self.context), None

    def at(self, other):
        # @ operator returns the other-th digit from the left on a Number
        myrepr = str(self.value)
        if other.type != 'INT':
            return None, InvalidSyntaxError(self.pos_start,
                                            self.pos_end,
                                            "Input to '@' must be INT")
        elif other.value >= len(myrepr):
            return None, OutOfBoundsError(self.pos_start,
                                          self.pos_end,
                                          "Index out of range",
                                          self.context)
        return Number(int(myrepr[other.value])), None

    def copy(self):
        copy = Number(self.value)
        copy.static = self.static
        copy.const = self.const
        copy.triggers = self.triggers
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def is_true(self):
        return self.value != 0


Number.null = Number(0)
Number.false = Number(0)
Number.true = Number(1)


class String(Value):
    
    def __init__(self, value):
        super().__init__(t='STR')
        self.value = value

    def __eq__(self, other):
        if isinstance(other, String):
            return self.value == other.value
        return False

    def __hash__(self):
        return self.value.__hash__()

    def add(self, other):
        if isinstance(other, String):
            return String(self.value + other.value).set_context(self.context), None
        else: return None, Value.illegal_op(self, other)

    def sub(self, other):
        if isinstance(other, String):
            return String(self.value.replace(other.value, '')).set_context(self.context), None
        else: return None, Value.illegal_op(self, other)

    def mul(self, other):
        if isinstance(other, Number):
            return String(self.value * other.value).set_context(self.context), None
        else: return None, Value.illegal_op(self, other)

    def div(self, other):
        if isinstance(other, String):
            ret = [s for s in self.value.split(other.value) if s]
            return List([String(v) for v in ret]).set_context(self.context), None
        else: return None, Value.illegal_op(self, other)

    def eq(self, other):
        if isinstance(other, String):
            return Number(int(self.value == other.value)).set_context(self.context), None
        else: return Number(0), None

    def ne(self, other):
        if isinstance(other, String):
            return Number(int(self.value != other.value)).set_context(self.context), None
        else: return Number(1), None

    def lt(self, other):
        if isinstance(other, String):
            return Number(int(self.value < other.value)).set_context(self.context), None
        else: return None, Value.illegal_op(self, other)

    def gt(self, other):
        if isinstance(other, String):
            return Number(int(self.value > other.value)).set_context(self.context), None
        else: return None, Value.illegal_op(self, other)

    def le(self, other):
        if isinstance(other, String):
            return Number(int(self.value <= other.value)).set_context(self.context), None
        else: return None, Value.illegal_op(self, other)

    def ge(self, other):
        if isinstance(other, String):
            return Number(int(self.value >= other.value)).set_context(self.context), None
        else: return None, Value.illegal_op(self, other)

    def logand(self, other):
        return Number(self.is_true() and other.is_true()).set_context(self.context), None

    def logor(self, other):
        return Number(self.is_true() or other.is_true()).set_context(self.context), None

    def lognand(self, other):
        return Number(not (self.is_true() and other.is_true())).set_context(self.context), None

    def lognor(self, other):
        return Number(not (self.is_true() or other.is_true())).set_context(self.context), None

    def logxor(self, other):
        return Number(int((self.is_true() and not other.is_true()) or (not self.is_true() and other.is_true()))
                      ).set_context(self.context), None

    def lognot(self):
        return Number(1 if self.value == "" else 0).set_context(self.context), None

    def at(self, other):
        if other.type != 'INT':
            return None, InvalidSyntaxError(self.pos_start,
                                            self.pos_end,
                                            "Input to '@' must be INT")
        elif other.value >= len(self.value):
            return None, InvalidSyntaxError(self.pos_start,
                                            self.pos_end,
                                            "Index out of range")
        return String(self.value[other.value]), None

    def sliceleft(self, other):
        val = other.value
        if other.type != 'INT': return None, InvalidSyntaxError(self.pos_start,
                                                                self.pos_end,
                                                                "Input to STR </ must be INT")
        elif other.value >= len(self.value): val = len(self.value)
        newstr = self.copy()
        newstr.value = newstr.value[:val]
        return newstr, None

    def sliceright(self, other):
        val = other.value
        if other.type != 'INT':
            return None, InvalidSyntaxError(self.pos_start,
                                            self.pos_end,
                                            "Input to STR /> must be INT")
        elif other.value >= len(self.value): val = len(self.value)
        newstr = self.copy()
        newstr.value = newstr.value[-val:]
        return newstr, None

    def contains(self, other):
        if other.type != 'STR':
            return None, InvalidSyntaxError(self.pos_start,
                                            self.pos_end,
                                            "Input to STR ~> must be STR")
        return Number(1) if other.value in self.value else Number(0), None

    def inj(self, other):
        # reserve this for format strings
        return None, self.illegal_op(other)

    def copy(self):
        copy = String(self.value)
        copy.static = self.static
        copy.const = self.const
        copy.triggers = self.triggers
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def is_true(self):
        return self.value != ''

    def __repr__(self):
        return f'"{self.value}"'


class List(Value):
    
    def __init__(self, elements):
        super().__init__(t='LST')
        self.elements = elements

    def add(self, other):
        newlist = self.copy()
        newlist.elements.append(other)
        return newlist, None

    def sub(self, other):
        newlist = self.copy()
        while other in newlist.elements:
            newlist.elements.remove(other)
        return newlist, None

    def mul(self, other):
        if other.type != 'LST':
            return None, Value.illegal_op(self, other)
        if len(other.elements) != len(self.elements):
            return None, RuntimeError(self.pos_start,
                                      self.pos_end,
                                      "Lists must be of the same size",
                                      self.context)
        return List([List(list(i)) for i in zip(self.elements, other.elements)]), None

    def div(self, other):
        if other.type != 'INT':
            return None, Value.illegal_op(self, other)

        ret = []
        curr = []
        for i in range(len(self.elements)):
            curr.append(self.elements[i])
            if i % other.value == other.value - 1:
                ret.append(curr)
                curr = []
        if curr: ret.append(curr)
        return List([List(list(i)) for i in ret]), None

    def pow(self, other):
        if other.type != 'LST':
            return None, Value.illegal_op(self, other)

        ret = []
        for i in range(len(self.elements)):
            for j in range(len(other.elements)):
                ret.append([self.elements[i], other.elements[j]])
        return List([List(list(i)) for i in ret]), None

    def at(self, other):
        if other.type != 'INT':
            return None, InvalidSyntaxError(self.pos_start, self.pos_end,
                                            "Input to '@' must be INT")
        elif other.value >= len(self.elements):
            return None, InvalidSyntaxError(self.pos_start, self.pos_end,
                                     "Index out of range")
        elem = self.elements[other.value]
        # elem = self.elements[other.value].copy()
        return elem, None

    def sliceleft(self, other):
        val = other.value
        if other.type != 'INT':
            return None, InvalidSyntaxError(self.pos_start, self.pos_end,
                                            "Input to '@' must be INT")
        elif other.value >= len(self.elements):
            val = len(self.elements)
        newlist = self.copy()
        newlist.elements = newlist.elements[:val]
        return newlist, None

    def sliceright(self, other):
        val = other.value
        if other.type != 'INT':
            return None, InvalidSyntaxError(self.pos_start, self.pos_end,
                                            "Input to '@' must be INT")
        elif other.value >= len(self.elements):
            val = len(self.elements)
        newlist = self.copy()
        newlist.elements = newlist.elements[-val:]
        return newlist, None

    def contains(self, other):
        for elem in self.elements:
            val, err = elem.eq(other)
            if val:
                if val.is_true(): return Number(1), None
        return Number(0), None

    def inj(self, other):
        if not isinstance(other, List):
            return None, InvalidSyntaxError(self.pos_start, self.pos_end,
                                            "Input to LST <~ must be LST")
        self.elements.extend(other.elements)
        return self, None

    def eq(self, other):
        if not isinstance(other, List):
            return Number(0), None
        if len(self.elements) != len(other.elements):
            return Number(0), None
        for i in range(len(self.elements)):
            if self.elements[i] != other.elements[i]:
                return Number(0), None
        return Number(1), None

    def ne(self, other):
        if not isinstance(other, List):
            return Number(1), None
        if len(self.elements) != len(other.elements):
            return Number(1), None
        for i in range(len(self.elements)):
            if self.elements[i] != other.elements[i]:
                return Number(1), None
        return Number(0), None

    def copy(self):
        copy = List(self.elements)
        copy.static = self.static
        copy.const = self.const
        copy.triggers = self.triggers
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def __repr__(self):
        return str(self.elements)

    def __eq__(self, other):
        if not isinstance(other, List):
            return False
        if len(self.elements) != len(other.elements):
            return False
        for i in range(len(self.elements)):
            if self.elements[i] != other.elements[i]:
                return False
        return True

class Map(Value):
    
    def __init__(self, elements):
        super().__init__(t='MAP')
        self.elements = elements

    def copy(self):
        copy = Map(self.elements)
        copy.static = self.static
        copy.const = self.const
        copy.triggers = self.triggers
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def __repr__(self):
        return str(self.elements)

    def add(self, other):
        if not isinstance(other, Map):
            return None, InvalidSyntaxError(self.pos_start, self.pos_end,
                                            "Input to MAP + must be MAP")
        newmap = self.copy()
        for key, val in other.elements.items():
            newmap.elements[key] = val
        return newmap, None

    def sub(self, other):
        keys = List(list(self.elements.keys()))
        present, err = keys.contains(other)
        if not present: return self, None
        elif not present.is_true(): return self, None
        newmap = self.copy()
        del newmap.elements[other]
        return newmap, None

    def contains(self, other):
        keys = List(list(self.elements.keys()))
        present, err = keys.contains(other)
        if not present: return Number(0), None
        elif present.is_true(): return Number(1), None
        return Number(0), None

    def eq(self, other):
        if not isinstance(other, Map): return Number(0), None
        if len(self.elements) != len(other.elements): return Number(0), None
        for i in self.elements:
            if i not in other.elements: return Number(0), None
            if self.elements[i] != other.elements[i]: return Number(0), None
        return Number(1), None

    def ne(self, other):
        if not isinstance(other, Map): return Number(1), None
        if len(self.elements) != len(other.elements): return Number(1), None
        for i in self.elements:
            if i not in other.elements: return Number(1), None
            if self.elements[i] != other.elements[i]: return Number(1), None
        return Number(0), None

    def at(self, other):
        if not self.contains(other)[0].is_true():
            return None, InvalidSyntaxError(self.pos_start,
                                            self.pos_end,
                                            f"Key {other.value} not found")

        elem = self.elements[other]
        return elem, None
    

# I want to get rid of this, but it gets the job done for now.
# All copying should be handled in house.
from copy import deepcopy

class Struct(Value):
    
    def __init__(self, properties, context, instance_name):
        super().__init__(t='STRC')
        self.instance_name = instance_name
        self.properties = properties
        self.context = context

        self.interfaces = []

    def dot(self, other):
        val = other.value
        if other.type != 'SYM':
            return None, InvalidSyntaxError(self.pos_start, self.pos_end,
                                            "Input to '.' must be SYM")
        if val not in self.properties:
            return None, InvalidSyntaxError(self.pos_start, self.pos_end,
                                            f"Struct has no property '{val}'.")

        return self.properties[val]

    def __repr__(self):
        return f'{self.properties}'

    def update_context(self):
        for p in self.context.symbol_table.symbols:
            if p in self.properties:
                self.properties[p] = self.context.symbol_table.symbols[p]
        # for p in self.properties:
        #     self.context.symbol_table.symbols[p] = self.properties[p]

    def copy(self):
        copy = Struct(deepcopy(self.properties), self.context, '')
        copy.static = self.static
        copy.const = self.const
        copy.triggers = self.triggers
        copy.instance_name = self.instance_name
        copy.set_pos(self.pos_start, self.pos_end)
        copy.interfaces = self.interfaces
        # copy.set_context(self.context)
        return copy


class BaseFunction(Value):
    
    def __init__(self, name):
        super().__init__(t='FNC')
        self.name = name or "<anonymous>"

    def generate_new_context(self):
        new_context = Context(self.name, self.context, self.pos_start)
        new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)
        return new_context

    def check_args(self, arg_names, args):
        res = RuntimeResult()

        if len(args) > len(arg_names):
            return res.failure(InvalidArgumentSetError(self.pos_start,
                                                       self.pos_end,
                                                       f"{len(args) - len(arg_names)} too many args passed into {self}",
                                                       self.context))
        if len(args) < len(arg_names):
            return res.failure(InvalidArgumentSetError(self.pos_start,
                                                       self.pos_end,
                                                       f"{len(arg_names) - len(args)} too few args passed into {self}",
                                                       self.context))
        return res.success(None)

    def populate_args(self, arg_names, args, exec_ctx):
        for i in range(len(args)):
            arg_name = arg_names[i]
            arg_value = args[i]
            if not isinstance(arg_value, Struct):
                arg_value.set_context(exec_ctx)
                exec_ctx.symbol_table.set(arg_name, arg_value)
            else: exec_ctx.symbol_table.set(arg_name, arg_value)

    def check_and_populate_args(self, arg_names, args, exec_ctx):
        res = RuntimeResult()
        res.register(self.check_args(arg_names, args))
        if res.should_return(): return res
        self.populate_args(arg_names, args, exec_ctx)
        return res.success(None)


class Function(BaseFunction):
    
    def __init__(self, name, body_node, arg_names, auto_return):
        super().__init__(name)
        self.body_node = body_node
        self.arg_names = arg_names
        self.auto_return = auto_return

    def execute(self, args, interpreter):
        res = RuntimeResult()
        exec_ctx = self.generate_new_context()

        exec_ctx.symbol_table.set(self.name, self.context.symbol_table.get(self.name))

        res.register(self.check_and_populate_args(self.arg_names, args, exec_ctx))
        if res.should_return(): return res

        value = res.register(interpreter.visit(self.body_node, exec_ctx))
        if res.should_return() and res.func_return_value is None: return res

        retval = (value if self.auto_return else None) or res.func_return_value or Number.null
        return res.success(retval)

    def copy(self):
        copy = Function(self.name, self.body_node, self.arg_names, self.auto_return)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy

    def __repr__(self):
        return f"<function {self.name}>"


class StructGenerator(BaseFunction):

    def __init__(self, name, body_node, arg_names, auto_return):
        super().__init__(name)
        self.body_node = body_node
        self.arg_names = arg_names
        self.auto_return = auto_return

        self.properties = {}

        self.pos_start = self.body_node.pos_start
        self.pos_end = self.body_node.pos_end

    def execute(self, args, interpreter):
        res = RuntimeResult()
        exec_ctx = self.generate_new_context()
        exec_ctx.display_name = f'struct:{exec_ctx.display_name}'

        res.register(self.check_and_populate_args(self.arg_names, args, exec_ctx))
        if res.should_return(): return res

        names = [el.var_name_tok.value for el in self.body_node.elements if isinstance(el, VarAssignNode)]
        value = res.register(interpreter.visit(self.body_node, exec_ctx))
        properties = {name: exec_ctx.symbol_table.get(name) for name in names}

        if res.should_return() and res.func_return_value is None: return res

        value = Struct(properties, exec_ctx, '')
        for key, v in exec_ctx.symbol_table.symbols.items():
            if isinstance(v, Function): value.interfaces.append(key)

        retval = (value if self.auto_return else None) or res.func_return_value or Number.null
        return res.success(retval)

    def copy(self):
        copy = StructGenerator(self.name, self.body_node, self.arg_names, self.auto_return)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.properties = self.properties
        copy.static = self.static
        copy.const = self.const
        return copy

    def __repr__(self):
        return f"<struct {self.name}>"


class BuiltInFunction(BaseFunction):
    
    def __init__(self, name):
        super().__init__(name)

    def execute(self, args, interpreter):
        res = RuntimeResult()
        exec_ctx = self.generate_new_context()

        method_name = f'execute_{self.name}'
        method = getattr(self, method_name, self.no_visit_method)

        res.register(self.check_and_populate_args(method.arg_names, args, exec_ctx))
        if res.should_return(): return res

        return_value = res.register(method(exec_ctx))
        if res.should_return(): return res
        return res.success(return_value)

    def no_visit_method(self, node, context):
        raise Exception(f'No execute_{self.name} method defined')

    def copy(self):
        copy = BuiltInFunction(self.name)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy

    def __repr__(self):
        return f"<built-in function {self.name}>"

    def execute_print(self, exec_ctx):
        print(str(exec_ctx.symbol_table.get('value')))
        return RuntimeResult().success(Number(0))

    execute_print.arg_names = ['value']

    def execute_rprint(self, exec_ctx):
        return RuntimeResult().success(String(str(exec_ctx.symbol_table.get('value'))))

    execute_rprint.arg_names = ['value']

    def execute_input(self, exec_ctx):
        text = input()
        return RuntimeResult().success(String(text))

    execute_input.arg_names = []

    def execute_input_int(self, exec_ctx):
        while True:
            text = input()
            try:
                number = int(text)
                break
            except ValueError:
                print(f"'{text}' must be an integer. Try again!")
        return RuntimeResult().success(Number(number))

    execute_input_int.arg_names = []

    def execute_clear(self, exec_ctx):
        os.system('cls' if os.name == 'nt' else 'cls')
        return RuntimeResult().success(Number(0))

    execute_clear.arg_names = []

    def execute_type(self, exec_ctx):
        t = exec_ctx.symbol_table.get("value").type
        return RuntimeResult().success(String(t))

    execute_type.arg_names = ["value"]

    def execute_is_number(self, exec_ctx):
        is_number = isinstance(exec_ctx.symbol_table.get("value"), Number)
        return RuntimeResult().success(Number.true if is_number else Number.false)

    execute_is_number.arg_names = ["value"]

    def execute_is_string(self, exec_ctx):
        is_number = isinstance(exec_ctx.symbol_table.get("value"), String)
        return RuntimeResult().success(Number.true if is_number else Number.false)

    execute_is_string.arg_names = ["value"]

    def execute_is_list(self, exec_ctx):
        is_number = isinstance(exec_ctx.symbol_table.get("value"), List)
        return RuntimeResult().success(Number.true if is_number else Number.false)

    execute_is_list.arg_names = ["value"]

    def execute_is_function(self, exec_ctx):
        is_number = isinstance(exec_ctx.symbol_table.get("value"), BaseFunction)
        return RuntimeResult().success(Number.true if is_number else Number.false)

    execute_is_function.arg_names = ["value"]

    def execute_pop(self, exec_ctx):
        list_ = exec_ctx.symbol_table.get("list")
        index = exec_ctx.symbol_table.get("index")

        if not isinstance(list_, List):
            return RuntimeResult().failure(RuntimeError(
                self.pos_start, self.pos_end,
                "First argument must be list",
                exec_ctx
            ))

        if not isinstance(index, Number):
            return RuntimeResult().failure(RuntimeError(self.pos_start,
                                                        self.pos_end,
                                                        "Second argument must be number",
                                                        exec_ctx))
            
        try: element = list_.elements.pop(index.value)
        except: return RuntimeResult().failure(OutOfBoundsError(self.pos_start,
                                                                self.pos_end,
                                                                f'Index {index.value} out of bounds',
                                                                exec_ctx))
        return RuntimeResult().success(element)

    execute_pop.arg_names = ["list", "index"]

    def execute_append(self, exec_ctx):
        list_ = exec_ctx.symbol_table.get("list")
        value = exec_ctx.symbol_table.get("value")

        if not isinstance(list_, List):
            return RuntimeResult().failure(RuntimeError(self.pos_start,
                                                        self.pos_end,
                                                        "First argument must be list",
                                                        exec_ctx))

        list_.elements.append(value)
        return RuntimeResult().success(Number.null)

    execute_append.arg_names = ["list", "value"]

    def execute_extend(self, exec_ctx):
        listA = exec_ctx.symbol_table.get("listA")
        listB = exec_ctx.symbol_table.get("listB")

        if not isinstance(listA, List):
            return RuntimeResult().failure(RuntimeError(
                self.pos_start, self.pos_end,
                "First argument must be list",
                exec_ctx))

        if not isinstance(listB, List):
            return RuntimeResult().failure(RuntimeError(
                self.pos_start, self.pos_end,
                "Second argument must be list",
                exec_ctx))

        listA.elements.extend(listB.elements)
        return RuntimeResult().success(Number(0))

    execute_extend.arg_names = ["listA", "listB"]

    def execute_keys(self, exec_ctx):
        m = exec_ctx.symbol_table.get("map")

        if not isinstance(m, Map):
            return RuntimeResult().failure(RuntimeError(
                self.pos_start, self.pos_end,
                "Invalid input to keys()",
                exec_ctx))

        return RuntimeResult().success(List(list(m.elements.keys())))

    execute_keys.arg_names = ["map"]

    def execute_values(self, exec_ctx):
        m = exec_ctx.symbol_table.get("map")

        if not isinstance(m, Map):
            return RuntimeResult().failure(RuntimeError(
                self.pos_start, self.pos_end,
                "Invalid input to values()",
                exec_ctx))

        return RuntimeResult().success(List(list(m.elements.values())))

    execute_values.arg_names = ["map"]

    def execute_open(self, exec_ctx):
        val = exec_ctx.symbol_table.get("value")
        mode = exec_ctx.symbol_table.get("mode")
        if not isinstance(val, String):
            return RuntimeResult().failure(RuntimeError(val.pos_start,
                                                        val.pos_end,
                                                        "Filename must be of type STR",
                                                        exec_ctx))
        if not isinstance(mode, String):
            return RuntimeResult().failure(RuntimeError(val.pos_start,
                                                        val.pos_end,
                                                        "File access mode must be of type STR",
                                                        exec_ctx))
        if (not os.path.exists(val.value)) and (mode == 'r'):
            return RuntimeResult().failure(RuntimeError(val.pos_start,
                                                        val.pos_end,
                                                        F"File {val} not found",
                                                        exec_ctx))

        try:
            f = File(val, mode)
            f.fobj = open(val.value, mode.value)
            return RuntimeResult().success(f)
        except:
            return RuntimeResult().failure(RuntimeError(val.pos_start,
                                                        val.pos_end,
                                                        F"Error opening file {val}",
                                                        exec_ctx))

    execute_open.arg_names = ["value", "mode"]

    def execute_read(self, exec_ctx):
        val = exec_ctx.symbol_table.get("value")
        if not isinstance(val, File):
            return RuntimeResult().failure(RuntimeError(val.pos_start,
                                                        val.pos_end,
                                                        f"{val} is not of type FILE",
                                                        exec_ctx))
        if val.mode.value != 'r':
            return RuntimeResult().failure(RuntimeError(val.pos_start,
                                                        val.pos_end,
                                                        f"{val} is not open in 'read' mode",
                                                        exec_ctx))
        try:
            return RuntimeResult().success(String(val.fobj.read()))
        except:
            return RuntimeResult().failure(RuntimeError(val.pos_start,
                                                        val.pos_end,
                                                        F"Error reading file {val}",
                                                        exec_ctx))

    execute_read.arg_names = ["value"]

    def execute_write(self, exec_ctx):
        val = exec_ctx.symbol_table.get("value")
        data = exec_ctx.symbol_table.get("data")
        if not isinstance(val, File):
            return RuntimeResult().failure(RuntimeError(val.pos_start,
                                                        val.pos_end,
                                                        f"{val} is not of type FILE",
                                                        exec_ctx))
        if not isinstance(data, String):
            return RuntimeResult().failure(RuntimeError(val.pos_start,
                                                        val.pos_end,
                                                        f"Data is not of type STR",
                                                        exec_ctx))
        if val.mode.value != 'w':
            return RuntimeResult().failure(RuntimeError(val.pos_start,
                                                        val.pos_end,
                                                        f"{val} is not open in 'write' mode",
                                                        exec_ctx))
        try:
            val.fobj.write(data.value)
            return RuntimeResult().success(Number.null)
        except:
            return RuntimeResult().failure(RuntimeError(val.pos_start,
                                                        val.pos_end,
                                                        F"Error reading file {val}",
                                                        exec_ctx))

    execute_write.arg_names = ["value", "data"]

    def execute_close(self, exec_ctx):
        val = exec_ctx.symbol_table.get("value")
        if not isinstance(val, File):
            return RuntimeResult().failure(RuntimeError(val.pos_start,
                                                        val.pos_end,
                                                        f"{val} is not of type FILE",
                                                        exec_ctx))
        try:
            val.fobj.close()
            val.fobj = None
            return RuntimeResult().success(Number.null)
        except: return RuntimeResult().failure(RuntimeError(val.pos_start,
                                                            val.pos_end,
                                                            F"Error closing file {val}",
                                                            exec_ctx))

    execute_close.arg_names = ["value"]

    def execute_range(self, exec_ctx):
        val = exec_ctx.symbol_table.get("value")
        if not isinstance(val, Number):
            return RuntimeResult().failure(RuntimeError(val.pos_start,
                                                        val.pos_end,
                                                        f"Input to range must be INT",
                                                        exec_ctx))
        nums = list(range(int(val.value)))
        return RuntimeResult().success(List([Number(i) for i in nums]))

    execute_range.arg_names = ["value"]

    def execute_rand(self, exec_ctx):
        return RuntimeResult().success(Number(random(), t='FLT'))

    execute_rand.arg_names = []

    def execute_len(self, exec_ctx):
        val = exec_ctx.symbol_table.get("container")
        if not (isinstance(val, List) or isinstance(val, String) or isinstance(val, Map)):
            return RuntimeResult().failure(RuntimeError(val.pos_start,
                                                        val.pos_end,
                                                        f"Input to len must be container",
                                                        exec_ctx))
        if isinstance(val, List) or isinstance(val, Map):
            return RuntimeResult().success(Number(len(val.elements)))
        elif isinstance(val, String):
            return RuntimeResult().success(Number(len(val.value)))

    execute_len.arg_names = ["container"]

    def execute_clear(self, exec_ctx):
        os.system('cls' if os.name == 'nt' else 'cls')
        return RuntimeResult().success(Number(0))

    execute_clear.arg_names = []


BuiltInFunction.print = BuiltInFunction("print")
BuiltInFunction.rprint = BuiltInFunction("rprint")
BuiltInFunction.input = BuiltInFunction("input")
BuiltInFunction.input_int = BuiltInFunction("input_int")
BuiltInFunction.clear = BuiltInFunction("clear")
BuiltInFunction.type = BuiltInFunction("type")
BuiltInFunction.is_number = BuiltInFunction("is_number")
BuiltInFunction.is_string = BuiltInFunction("is_string")
BuiltInFunction.is_list = BuiltInFunction("is_list")
BuiltInFunction.is_function = BuiltInFunction("is_function")
BuiltInFunction.pop = BuiltInFunction("pop")
BuiltInFunction.append = BuiltInFunction("append")
BuiltInFunction.extend = BuiltInFunction("extend")
BuiltInFunction.keys = BuiltInFunction("keys")
BuiltInFunction.values = BuiltInFunction("values")
BuiltInFunction.open = BuiltInFunction("open")
BuiltInFunction.read = BuiltInFunction("read")
BuiltInFunction.write = BuiltInFunction("write")
BuiltInFunction.close = BuiltInFunction("close")
BuiltInFunction.range = BuiltInFunction("range")
BuiltInFunction.len = BuiltInFunction("len")
BuiltInFunction.rand = BuiltInFunction("rand")


class File(Value):
    
    def __init__(self, fname, mode):
        super().__init__(t='FILE')
        self.fname = fname
        self.mode = mode
        self.fobj = None

    def __repr__(self):
        return f'<file> {self.fname}'

    def copy(self):
        copy = File(self.fname, self.mode)
        copy.fobj = self.fobj
        copy.static = self.static
        copy.const = self.const
        copy.triggers = self.triggers
        copy.set_pos(self.pos_start, self.pos_end)
        return copy
