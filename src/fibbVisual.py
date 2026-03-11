n1, n2 = 0, 1

while 1:
    color = n2 % 256
    
    print(f"\033[38;5;{color}m■\033[0m", end="")

    n1, n2 = n2, n1 + n2
