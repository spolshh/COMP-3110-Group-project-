# file I/O simulation (no real files)
lines = ["first", "second", "third", "fourth", "fifth"]
for idx, val in enumerate(lines, start=1):
    print(idx, val)
# modify list
lines.append("sixth")
lines.insert(2, "inserted")
for l in lines:
    print("Line:", l)
# finish