-- program "Sandbox"
print("hewwo")

function fact(n)
    if n == 0 then
        return 1
    else
        return n * fact(n - 1)
    end
end

print("number for factorial:")
input = io.read("*n")
print(fact(input))
