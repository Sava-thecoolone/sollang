function(arr)
    function swap(arr, i, j)
        declare temp = copy(arr[i])
        arr[i] = arr[j]
        arr[j] = temp
    end

    function quickrec(arr, l, r)
        if l < r
            declare pivot = copy(arr[l])
            declare p1 = copy(l)
            declare p2 = copy(r)
            while p1 <= p2
                while arr[p1] < pivot
                    p1++
                end
                while arr[p2] > pivot
                    p2--
                end
                if p1 <= p2
                    swap(arr, p1, p2)
                    p1++
                    p2--
                end
            end
            if l < p2 quickrec(arr, l, p2) end
            if p1 < r quickrec(arr, p1, r) end
        end
    end
    quickrec(arr, 0, len(arr)-1)
    return arr
end