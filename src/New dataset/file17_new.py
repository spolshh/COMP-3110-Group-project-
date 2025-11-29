# list processing
numbers = [1, 2, 3, 4, 5, 6]
squared = []
for n in numbers:
    squared.append(n * n)
print("Squared:", squared)
evens = [x for x in numbers if x % 2 == 0]
print("Evens:", evens)
total = sum(numbers)
print("Total:", total)
avg = total / len(numbers)
print("Avg:", avg)
# end