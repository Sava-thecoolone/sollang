<:
    lcomp = function(arr, cond)
        declare newarr = []
        for i=0 i<len(arr) i++ if eval(cond) append(newarr, arr[i]) end end
        return newarr
    end

    join = function(arr, str)
        declare newstr = ""
        for i=0 i<len(arr) i++ newstr += tostr(arr[i]) if i < len(arr)-1 newstr += str end end
        return newstr
    end

    reverse = function(arr)
        declare newarr = []
        for i=len(arr)-1 i>=0 i-- append(newarr, arr[i]) end
        return newarr
    end
:>