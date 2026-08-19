declare sys = importffi("sys")
declare math = importffi("math")
declare decimal = importffi("decimal")
sys.set_int_max_str_digits(10000000)

function round(n)
    if n%1 > 0.5 n//1+1 else n//1 end
end

function fib(n)
    declare phi = (decimal.Decimal(1) + decimal.Decimal(5).sqrt()) / decimal.Decimal(2)
    return round(phi^n / decimal.Decimal(5).sqrt())
end

declare start = time()
declare v = fib(500000)
declare t = time()-start

print("fib("+tostr(500000)+") in "+tostr(t)+" seconds, "+tostr(math.floor(math.log10(v))+1)+" digits long")