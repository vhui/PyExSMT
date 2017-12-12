# Copyright: see copyright.txt

import logging

from pysmt.shortcuts import *

# the ABSTRACT base class for representing any expression that depends on a symbolic input
# it also tracks the corresponding concrete value for the expression (aka concolic execution)

class SymbolicObject(object):
    def __init__(self, expr, name = "se", ty=INT):
        if expr is None:
            self.expr = Symbol(name, ty)
        else:
            self.expr = expr

    # This is set up by the concolic engine to link __bool__ to PathConstraint
    SI = None
    # This is set up by the concolic engine to link the solver to the variables  
    SOLVER = None

    # this is a critical interception point: the __bool__
    # method is called whenever a predicate is evaluated in
    # Python execution (if, while, and, or). This allows us
    # to capture the path condition
    def __bool__(self):
        ret = self.get_concr_value()
        if ret == FALSE():
            ret = False
        elif ret == TRUE():
            ret = True
        else:
            raise ValueError("NOT A BOOL!")
        
        if SymbolicObject.SI != None:
            SymbolicObject.SI.whichBranch(ret, self)
        
        return ret

    def get_concr_value(self):
        if SymbolicObject.SOLVER is None:
            raise ValueError("MUST SPECIFY SOLVER")
        if not SymbolicObject.SOLVER.last_result:
            raise ValueError("SOLVER MUST HAVE A MODEL")
        val = SymbolicObject.SOLVER.get_value(self.expr)
        logging.debug("%s := %s" %(str(self), val))
        return val

    def get_vars(self):
        return self.expr.get_free_variables()

    def symbolicEq(self, other):
        if not isinstance(other,SymbolicObject):
            ret = False
        ret = str(self.expr) == str(other.expr)
        logging.debug("Checking equality of %s and %s: result is %s" %(self, other, ret))
        return ret

    def __hash__(self):
        return hash(str(self))

    def __str__(self):
        return self.expr.serialize()

    def __repr__(self):
        return self.__str__()


    ## OPERATORS
    # TODO: TYPE CHECKING AND CONVERTING
    def __eq__(self, other):
        #TODO: what if self is not symbolic and other is?
        other = wrap(other)
        if self.expr.get_type() != other.get_type():
            return False
        return SymbolicObject(Equals(self.expr, other))

    def __ne__(self, other):
        other = wrap(other)
        if self.expr.get_type() != other.get_type():
            return False
        return SymbolicObject(NotEquals(self.expr, other))

    def __lt__(self, other):
        other = wrap(other)
        if self.expr.get_type() != other.get_type():
            return False
        return SymbolicObject(LT(self.expr, other))

    def __le__(self, other):
        other = wrap(other)
        if self.expr.get_type() != other.get_type():
            return False
        return SymbolicObject(LE(self.expr, other))

    def __gt__(self, other):
        other = wrap(other)
        if self.expr.get_type() != other.get_type():
            return False
        return SymbolicObject(GT(self.expr, other))

    def __ge__(self, other):
        other = wrap(other)
        if self.expr.get_type() != other.get_type():
            return False
        return SymbolicObject(GE(self.expr, other))

    def __add__(self, other):
        other = wrap(other)
        if self.expr.get_type() != other.get_type():
            return False
        return SymbolicObject(self.expr + other)

    def __sub__(self, other):
        other = wrap(other)
        if self.expr.get_type() != other.get_type():
            return False
        return SymbolicObject(self.expr - other)

    def __mul__(self, other):
        other = wrap(other)
        if self.expr.get_type() != other.get_type():
            return False
        return SymbolicObject(self.expr * other)

    def __mod__(self, other):
        raise NotImplementedError("mod Not Implemented Yet!")

    def __div__(self, other):
        other = wrap(other)
        if self.expr.get_type() != other.get_type():
            return False
        return SymbolicObject(self.expr / other)

    def __and__(self, other):
        other = wrap(other)
        if self.expr.get_type() != other.get_type():
            return False
        return SymbolicObject(And(self.expr, other))

    def __or__(self, other):
        other = wrap(other)
        if self.expr.get_type() != other.get_type():
            return False
        return SymbolicObject(Or(self.expr, other))

    def __xor__(self, other):
        raise NotImplementedError("xor Not Implemented Yet!")

    def __lshift__(self, other):
        raise NotImplementedError("lshift Not Implemented Yet!")

    def __rshift__(self, other):
        raise NotImplementedError("rshift Not Implemented Yet!")

def wrap(val):
    if isinstance(val, SymbolicObject):
        return val.expr
    elif isinstance(val, int):
        return Int(val)
    else:
        raise NotImplementedError("Only integers supported at the moment.")
