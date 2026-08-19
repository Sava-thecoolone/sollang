print({2 ^ 3 ^ 2}) # (Body (Prog (BinOp (Int 2), ^, (BinOp (Int 3), ^, (Int 2)))))
print({(inline 2 ^ 3 ^ 2) * 8}) # (Body (Prog (BinOp (Any 512), *, (Int 8))))

function inline sq(x)
    return x*x
end

print({inline sq(5)})  # (Body (Prog (Any 25)))
try(print(sq(5)))      # (Error line 8 - undeclared variable 'sq')

function inline lcomp(arr, cond)
    declare newarr = []
    for i=0 i<len(arr) i++ if eval(cond) append(newarr, arr[i]) end end
    return newarr
end

print(inline lcomp(0..10, {arr[i]%2 == 0})) # [0, 2, 4, 6, 8]