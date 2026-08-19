# SOL
*Stands for SecondOrderLang, pronounced like 'soul'*


This is a simple language interpretter i made as a programming exercise

It is not meant to be used in any serious projects, however it is still quite powerful on it's own

## Run
To enter REPL run main.py in src with no arguments, to run a file pass it as an argument

You can also use the -ast flag to get the generated AST of a file

## Syntax
SOL has simplistic syntax which is a combionation of lua and c

### Examples
hello world
```python
print("Hello, World!") # this is a comment
```

variables
```python
declare x = 20
declare y = 10
print(x+y) # 30
print(x-y) # 10
print(x/y) # 2.0
print(x//y) # integer division - 2
print(x*y) # 200
```

strings
```python
declare x = "str"
declare y = "int"
print(x+y) # string
print(x[0]) # s
print(x[1]) # t
```

arrays
```python
declare x = [6, 5, 4]
print(x) # [6, 5, 4]
print(x[0]) # 6
print([4, 5, 6][1]) # 5
```

functions
```python
function square(x) x*x end # last statement returns
print(square(5)) # 25
declare squaretoo = function(x) x*x end # exactly the same thing
print(squaretoo(5)) # 25

function triangle(x)
    if x < 1 return 0 end
    return triangle(x-1)+x
end
print(triangle(3)) # 6

# similarly, anonymous syntax:
declare triangle = function(x)
    if x < 1 return 0 end
    return triangle(x-1)+x
end
print(triangle(3)) # 6

# no declare:
print(function() 10 end()) # 10

# no declare recursion:
print(function(x)
    if x < 1 return 0 end
    return thisfunc(x-1)+x # thisfunc return the current function, even undeclared
end(3)) # 6
```

objects
```python
declare obj = <:
    val = 10
    func = function() this.val end
    change = function() this.val = 5 end
    getthis = function() this end
:>

print(obj.val) # 10
print(obj.func()) # 10
print(obj.getthis().val) # 10
print(obj.getthis().getthis().getthis().val) # 10
obj.change()
print(obj.val) # 5
print(obj.func()) # 5
```

ast
```python
declare x = {print(10)} # everything in {} is not executed
print(x) # (Body <(Prog <(Call <(Var print)> {<(Int 10)>})>)>)
print({x}) # (Body <(Prog <(Var x)>)>)
eval(x) # 10

declare a = 10
declare b = 20
print({a+b}) # (Body <(Prog <(BinOp <(Var a)>, +, <(Var b)>)>)>)
print(uneval(a+b)) # (Any 30), everything in uneval() is turned into an AST

print(inline 5+5) # 10
print({inline 5+5}) # (Body <(Prog <(Any 10)>)>)
function inline square(x) x*x end
print(try(square(5))) # (Error line 14 - undeclared variable 'square')
print(inline square(5)) # 25
print({inline square(5)}) # (Body <(Prog <(Any 25)>)>)
```

You can look at .sol files in this directory for more examples
