base = float(input("Enter base: "))
exp = int(input("Enter exponent (power): "))

result = 1.0
for _ in range(abs(exp)):
    result *= base

if exp < 0:
    result = 1.0 / result

print(f"{base} ^ {exp} = {result}")