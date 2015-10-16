"""
Matlab consists of various legal start and end characters depending on context.
This module is a small collection of constants available to ensure that context
is defined correctly.
"""

import string

letters = string.letters
digits = string.digits

# start and end of expression
e_start = letters + digits + "[({~-+:@.'"
e_end = "%])},;\n"

# start and end of lists
l_start = "[({"
l_end = "]})"

# end of keyword
k_end = " \t(,;\n%"

prefixes = "-+~"
postfix1 = "'"
postfix2 = ".'"

# operators with one character
op1 = r"^\/*+-:<>&|"

# operators using two characters
op2 = (
    ".^", ".\\", "./", ".*",
    "<=", ">=", "==", "~=",
    "&&", "||")

# start of string
s_start = " \t\n=><"