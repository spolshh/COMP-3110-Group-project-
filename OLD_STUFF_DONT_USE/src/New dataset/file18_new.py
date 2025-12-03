# function and string demo
def greet(name):
    msg = "Hello, " + name + "!"
    return msg

name = "Alex"
message = greet(name)
print(message)
name2 = "Sam"
print(greet(name2))
# small loop
for ch in name:
    print(ch)
# finished