print(1)              # number
print("str"+"ing")    # string
print(1, 2, 3)        # multiple arguments
print([1, 2, 3])      # array
print(true)           # bool
print(4 > 5 | 1 == 0) # False
print(2 ^ 3 ^ 2)      # 512


# this is a comment

declare var = 30  # variable
declare var2 = 10
print(var+var2)   # 40
print(var-var2)   # 20
print(var/var2)   # 3.0 (turns into float)
print(var//var2)  # 3   (stays as int)
print(var*var2)   # 300
print(var^var2)   # 59049000000000

var = var2 // 2   # assignment
print(var)        # 5

# constants
print(MAX_FLOAT)  # 1.7976931348623157e+308
print(MAX_INT)    # 9223372036854775807
print(MIN_INT)    # -9223372036854775807
print(INF)        # inf
print(NaN)        # nan

declare arr = [1, 2, 3]
arr[1] = 0
print(arr)     # [1, 0, 3]
print(len(arr))   # 3
declare i = 0
while i < len(arr)
    arr[i] = 5
    i++
end
print(arr)     # [5, 5, 5]


declare x = 6
function square(y)
    y *= y    # affects outer x (passed by reference)
    return y
end

print(x)           # 6
print(square(x))   # 36
print(x)           # now 36
x = 6
print(square(copy(x))) # 36
print(x)           # stays 6

declare arr = [4, 5, 6]  # overwrites previous declaration
function test(somearr)
    somearr[1] = 0    # affects outer arr
end

print(arr)    # [4, 5, 6]
test(arr)
print(arr)    # [4, 0, 6]


# calculate pi because why not
declare pi = 0.0
declare sign = 1.0
declare i = 0
while i < 1000000
    pi += sign / (2 * i + 1)
    sign = -sign
    i += 1
end
print(pi * 4)