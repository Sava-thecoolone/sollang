declare sys = importffi("sys")
declare math = importffi("math")
sys.set_int_max_str_digits(10000000)

function round(n)
    if n%1 > 0.5 n//1+1 else n//1 end
end

function fib(n)
    declare a = 0
    declare b = 1
    for i=0 i<n i++
        declare temp = copy(b)
        b += a
        a = temp
    end
    return a
end

declare start = time()
declare v = fib(500000)
declare t = time()-start

print("fib("+tostr(500000)+") in "+tostr(t)+" seconds, "+tostr(math.floor(math.log10(v))+1)+" digits long")
