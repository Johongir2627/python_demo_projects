def reverse_string(n):
    b = []
    for i in n:
        b.append(i)
    d = ''.join(b[::-1])
    return d


def count_vowels(n):
    vowels = 'aeiou'
    summ = 0
    for i in n:
        for j in vowels:
            if i == j:
                summ += 1
    return summ