import time
from math import sqrt

def compute_primes(limit):
    """Compute all prime numbers up to the given limit using the Sieve of Eratosthenes."""
    sieve = [True] * (limit + 1)
    sieve[0] = sieve[1] = False  # 0 and 1 are not prime numbers
    for num in range(2, int(sqrt(limit)) + 1):
        if sieve[num]:
            for multiple in range(num * num, limit + 1, num):
                sieve[multiple] = False
    primes = [i for i, is_prime in enumerate(sieve) if is_prime]
    return primes

def intensive_computation():
    """Run the prime number computation repeatedly to consume CPU power."""
    limit = 10**6  # Adjust this for more/less intensive work
    iteration = 1

    while True:
        start_time = time.time()
        primes = compute_primes(limit)
        end_time = time.time()

        print(f"Iteration {iteration}: Computed {len(primes)} primes up to {limit} in {end_time - start_time:.2f} seconds.")
        iteration += 1
        # Increase the limit for subsequent iterations to make the computation more demanding
        limit += 10**6

while 1==1:
    intensive_computation()
