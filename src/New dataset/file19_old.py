# factorial and accumulation
def factorial(n):
    res = 1
    for i in range(1, n + 1):
        res *= i
    return res

print("5! =", factorial(5))
nums = [2, 3, 4]
acc = 1
for x in nums:
    acc *= x
print("Product:", acc)
# goodbye