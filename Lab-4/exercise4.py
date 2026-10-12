def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

total_sum = 0
for num in range(2, 1000):
    if is_prime(num):
        total_sum += num

print("Sum of all primes below 1000:", total_sum)