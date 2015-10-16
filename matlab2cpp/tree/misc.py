"""
Interpretors that didn't fit other places

Functions
~~~~~~~~~
number          Verbatim number
string          Verbatim string
list            A list (both comma or space delimited)
comment         Comments on any form
matrix          Verbatim matrices
cell            Verbatim cells
"""

import matlab2cpp
import constants as c
import findend


def number(self, node, start):
    """
Verbatim number

Args:
    self (Builder): Code constructor
    node (Node): Parent node
    start (int): Current position in code

Returns:
	int : End of number

Example:
    >>> builder = mc.Builder(True)
    >>> builder.load("unnamed", "42.")
    loading unnamed
         Program     functions.program
       0 Main        functions.main
       0 Codeblock   codeblock.codeblock 
       0   Statement     codeblock.codeblock  '42.'
       0     Expression  expression.create    '42.'
       0     Float       misc.number          '42.'
    >>> print mc.qtree(builder, core=True)
      1   1 Block      code_block   TYPE    
      1   1 Statement  code_block   TYPE    
      1   1 | Float      double       double  
    """

    if not (self.code[start] in c.digits or\
            self.code[start] == "." and self.code[start+1] in c.digits):
        self.syntaxerror(start, "number")

    k = start

    while self.code[k] in c.digits:
        k += 1
    last = k-1

    integer = True
    if self.code[k] == ".":
        integer = False

        k += 1
        while self.code[k] in c.digits:
            k += 1
        last = k-1

    if self.code[k] in "eEdD":

        exp = k

        k = k+1
        if self.code[k] in "+-":
            k += 1

        while self.code[k] in c.digits:
            k += 1

        number = self.code[start:exp] + "e" + self.code[exp+1:k]

        last = k-1

        if self.code[k] in "ij":

            k += 1
            node = matlab2cpp.collection.Imag(node, number, cur=start,
                    code=self.code[start:last+1])
            if self.disp:
                print "%4d     Imag       " % (start),
                print "%-20s" % "misc.number",
                print repr(self.code[start:last+1])

        else:
            node = matlab2cpp.collection.Float(node, number, cur=start,
                    code=self.code[start:last+1])
            if self.disp:
                print "%4d     Float      " % (start),
                print "%-20s" % "misc.number",
                print repr(self.code[start:last+1])

    elif integer:

        number = self.code[start:k]

        if self.code[k] in "ij":

            node = matlab2cpp.collection.Imag(node, self.code[start:k], cur=start,
                    code=self.code[start:last+1])
            k += 1
            if self.disp:
                print "%4d     Imag       " % (start),
                print "%-20s" % "misc.number",
                print repr(self.code[start:last+1])

        else:
            node = matlab2cpp.collection.Int(node, self.code[start:k], cur=start,
                    code=self.code[start:last+1])
            if self.disp:
                print "%4d     Int        " % (start),
                print "%-20s" % "misc.number",
                print repr(self.code[start:last+1])

    else:

        if self.code[k] in "ij":

            node = matlab2cpp.collection.Imag(node, self.code[start:k], cur=start,
                    code=self.code[start:last+1])
            k += 1
            if self.disp:
                print "%4d     Imag       " % (start),
                print "%-20s" % "misc.number",
                print repr(self.code[start:last+1])

        else:
            node = matlab2cpp.collection.Float(node, self.code[start:k], cur=start,
                    code=self.code[start:k])
            if self.disp:
                print "%4d     Float      " % (start),
                print "%-20s" % "misc.number",
                print repr(self.code[start:last+1])

    return k-1


def string(self, parent, cur):
    """
Verbatim string

Args:
    self (Builder): Code constructor
    parent (Node): Parent node
    start (int): Current position in code

Returns:
	int : End of string

Example:
    >>> builder = mc.Builder(True)
    >>> builder.load("unnamed", "'abc'")
    loading unnamed
         Program     functions.program
       0 Main        functions.main
       0 Codeblock   codeblock.codeblock 
       0   Statement     codeblock.codeblock  "'abc'"
       0     String  misc.string          "'abc'"
    >>> print mc.qtree(builder, core=True)
      1   1 Block      code_block   TYPE    
      1   1 Statement  code_block   TYPE    
      1   1 | String     string       string  
    """

    end = findend.string(self, cur)

    if  "\n" in self.code[cur:end]:
        self.syntaxerror(cur, "no line-feed character in string")

    matlab2cpp.collection.String(parent, self.code[cur+1:end], cur=cur,
            code=self.code[cur:end+1])

    if self.disp:
        print "%4d     String " % cur,
        print "%-20s" % "misc.string",
        print repr(self.code[cur:end+1])

    return end


def list(self, parent, cur):
    """
A list (both comma or space delimited)

Args:
    self (Builder): Code constructor
    parent (Node): Parent node
    cur (int): Current position in code

Returns:
	int : End of list

Example:
    >>> builder = mc.Builder(True)
    >>> builder.load("unnamed", "[2 -3]")
    loading unnamed
         Program     functions.program
       0 Main        functions.main
       0 Codeblock   codeblock.codeblock 
       0   Statement     codeblock.codeblock  '[2 -3]'
       0     Expression  expression.create    '[2 -3]'
       0     Matrix      misc.matrix          '[2 -3]'
       1     Vector      misc.matrix          '2 -3'
       1     Expression  expression.create    '2'
       1     Int         misc.number          '2'
       3     Expression  expression.create    '-3'
       4     Int         misc.number          '3'
    >>> print mc.qtree(builder, core=True)
      1   1 Block      code_block   TYPE    
      1   1 Statement  code_block   TYPE    
      1   1 | Matrix     matrix       TYPE    
      1   2 | | Vector     matrix       TYPE    
      1   2 | | | Int        int          int     
      1   4 | | | Neg        expression   TYPE    
      1   5 | | | | Int        int          int     
    """

    if  self.code[cur] not in "({":
        self.syntaxerror(cur, "start of list character")

    end = cur
    for vector in self.iterate_comma_list(cur):
        for start,end in vector:
            self.create_expression(parent, start, end)

    end += 1
    while self.code[end] in " \t":
        end += 1

    if  self.code[end] not in ")}":
        self.syntaxerror(cur, "end of list character")

    return end


def comment(self, parent, cur):
    """
Comments on any form

Args:
    self (Builder): Code constructor
    parent (Node): Parent node
    cur (int): Current position in code

Returns:
	int : End of comment

Example:
    >>> builder = mc.Builder(True, comments=True)
    >>> builder.load("unnamed", "4 % comment")
    loading unnamed
         Program     functions.program
       0 Main        functions.main
       0 Codeblock   codeblock.codeblock 
       0   Statement     codeblock.codeblock  '4'
       0     Expression  expression.create    '4'
       0     Int         misc.number          '4'
       2   Comment       misc.comment         '% comment'
    >>> print mc.qtree(builder, core=True)
      1   1 Block      code_block   TYPE    
      1   1 Statement  code_block   TYPE    
      1   1 | Int        int          int     
      1   3 Ecomment   code_block   TYPE    
    """

    assert parent.cls == "Block"

    if  self.code[cur] != "%":
        self.syntaxerror(cur, "comment")

    end = findend.comment(self, cur)

    if not self.comments:
        return end

    if self.disp:
        print "%4d   Comment      " % cur,
        print "%-20s" % "misc.comment",
        print repr(self.code[cur:end])

    if self.code[cur+1] == "{":
        comment = matlab2cpp.collection.Bcomment(parent, self.code[cur+2:end-1], cur=cur)
    else:
        k = cur-1
        while self.code[k] in " \t":
            k -= 1
        if self.code[k] == "\n":
            comment = matlab2cpp.collection.Lcomment(parent, self.code[cur+1:end], cur=cur)
        else:
            comment = matlab2cpp.collection.Ecomment(parent, self.code[cur+1:end], cur=cur)

    comment.code = self.code[cur:end+1]

    return end


def matrix(self, node, cur):
    """
Verbatim matrices

Args:
    self (Builder): Code constructor
    node (Node): Parent node
    cur (int): Current position in code

Returns:
	int : End of matrix

Example:
    >>> builder = mc.Builder(True)
    >>> builder.load("unnamed", "[[1 2] [3 4]]")
    loading unnamed
         Program     functions.program
       0 Main        functions.main
       0 Codeblock   codeblock.codeblock 
       0   Statement     codeblock.codeblock  '[[1 2] [3 4]]'
       0     Expression  expression.create    '[[1 2] [3 4]]'
       0     Matrix      misc.matrix          '[[1 2] [3 4]]'
       1     Vector      misc.matrix          '[1 2] [3 4]'
       1     Expression  expression.create    '[1 2]'
       1     Matrix      misc.matrix          '[1 2]'
       2     Vector      misc.matrix          '1 2'
       2     Expression  expression.create    '1'
       2     Int         misc.number          '1'
       4     Expression  expression.create    '2'
       4     Int         misc.number          '2'
       7     Expression  expression.create    '[3 4]'
       7     Matrix      misc.matrix          '[3 4]'
       8     Vector      misc.matrix          '3 4'
       8     Expression  expression.create    '3'
       8     Int         misc.number          '3'
      10     Expression  expression.create    '4'
      10     Int         misc.number          '4'
    >>> print mc.qtree(builder, core=True)
      1   1 Block      code_block   TYPE    
      1   1 Statement  code_block   TYPE    
      1   1 | Matrix     matrix       TYPE    
      1   2 | | Vector     matrix       TYPE    
      1   2 | | | Matrix     matrix       TYPE    
      1   3 | | | | Vector     matrix       TYPE    
      1   3 | | | | | Int        int          int     
      1   5 | | | | | Int        int          int     
      1   8 | | | Matrix     matrix       TYPE    
      1   9 | | | | Vector     matrix       TYPE    
      1   9 | | | | | Int        int          int     
      1  11 | | | | | Int        int          int     
    """

    if  self.code[cur] != "[":
        self.syntaxerror(cur, "bracket start")

    end = findend.matrix(self, cur)
    if self.disp:
        print "%4d     Matrix     " % cur,
        print "%-20s" % "misc.matrix",
        print repr(self.code[cur:end+1])

    L = self.iterate_list(cur)
    matrix = matlab2cpp.collection.Matrix(node, cur=cur, code=self.code[cur:end+1])

    for array in L:

        if array:
            start = array[0][0]
            end = array[-1][-1]
        else:
            start = cur

        vector = matlab2cpp.collection.Vector(matrix, cur=start,
                code=self.code[start:end+1])

        if self.disp:
            print "%4d     Vector     " % (start),
            print "%-20s" % "misc.matrix",
            print repr(self.code[start:end+1])

        for start,end in array:

            self.create_expression(vector, start, end)

    if not L:

        if self.disp:
            print "%4d     Vector     " % cur,
            print "%-20s" % "misc.matrix",
            print repr("")
        vector = matlab2cpp.collection.Vector(matrix, cur=cur, code="")


    return findend.matrix(self, cur)


def cell(self, node, cur):
    """
Verbatim cells

Args:
    self (Builder): Code constructor
    node (Node): Parent node
    cur (int): Current position in code

Returns:
	int : End of cell

Example:
    >>> builder = mc.Builder(True)
    >>> builder.load("unnamed", "{1, 2}")
    loading unnamed
         Program     functions.program
       0 Main        functions.main
       0 Codeblock   codeblock.codeblock 
       0   Statement     codeblock.codeblock  '{1, 2}'
       0     Expression  expression.create    '{1, 2}'
       0     Cell        misc.cell            '{1, 2}'
       1     Expression  expression.create    '1'
       1     Int         misc.number          '1'
       4     Expression  expression.create    '2'
       4     Int         misc.number          '2'
    >>> print mc.qtree(builder, core=True)
      1   1 Block      code_block   TYPE    
      1   1 Statement  code_block   TYPE    
      1   1 | Cell       cell         TYPE    
      1   2 | | Int        int          int     
      1   5 | | Int        int          int     
    """

    if  self.code[cur] != "{":
        self.syntaxerror(cur, "curly braces")

    end = findend.cell(self, cur)
    if self.disp:
        print "%4d     Cell       " % cur,
        print "%-20s" % "misc.cell",
        print repr(self.code[cur:end+1])

    L = self.iterate_list(cur)
    cell = matlab2cpp.collection.Cell(node, cur=cur, code=self.code[cur:end+1])

    for array in L:

        if array:
            start = array[0][0]
            end = array[-1][-1]
        else:
            start = cur

        for start,end in array:

            self.create_expression(cell, start, end)


    return findend.cell(self, cur)


if __name__ == "__main__":
    import matlab2cpp as mc
    import doctest
    doctest.testmod()