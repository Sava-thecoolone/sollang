declare x = 10
declare y = 2
assert(x, 10)
assert(y, 2)
assert(x+y, 12)
assert(x-y, 8)
assert(x*y, 20)
assert(x^y, 100)
assert(x+y*y, 14)
assert(2^3^2, 512)
x = 11
assert(x, 11)
assert(x*x, 121)
assert(tostr(try(something=0)), "(Error line 14 - undeclared variable 'something')")
declare str = "str"
declare ing = "ing"
assert("str"+"ing", "string")
assert(str+ing, "string")
str = "walk"
assert(str+ing, "walking")
assert(type(str), "<str>")
declare arr = [1, 2, 3]
assert(arr[0], 1)
assert(arr[1], 2)
assert(arr[2], 3)
assert(tostr(try(arr[10])), "(Error line 26 - array index 10 out of range)")
arr[1] = 0
assert(arr, [1, 0, 3])
assert(tostr(try(assert(arr, [0, 0, 0]))), "(Error line 29 - <list> [1, 0, 3] doesn't equal <list> [0, 0, 0])")
assert(type(arr), "<list>")
assert([1, 2, 3][1], 2)
assert(function() "test" end(), "test")
declare obj = <:
    val = 10
    func = function() this.val end
:>
assert(obj.val, 10)
assert(obj.func(), 10)
obj.val = 0
assert(obj.val, 0)
assert(obj.func(), 0)
assert(<:func=function() ["mixed", function() <:nottest="wrong", test=["teststr", 10]:> end] end:>.func()[1]().test[0], "teststr")
assert(type(obj), "<dict>")
declare lazy = {10^2}
assert(tostr(lazy), "(Body <(Prog <(BinOp <(Int 10)>, ^, <(Int 2)>)>)>)")
assert(eval(lazy), 100)
assert(eval(eval({lazy})), 100)
assert(eval(eval(eval({{lazy}}))), 100)
function testfunc(x)
    uneval(x^3)
end
assert(tostr(testfunc(3)), "(Any 27)")
assert(eval(testfunc(3)), 27)
function inline square(x)
    x*x
end
assert(inline square(10), 100)
assert(tostr({inline square(10)}), "(Body <(Prog <(Any 100)>)>)")
declare test = ""
for i=0 i<10 i++
    test += "h"
end
assert(test, "hhhhhhhhhh")
print("Every test passed!")