# n = int(input())
# product = 1
# sum = 0

# def product_of_factorial(n):
#     global product
#     if n == 0:
#         product *= 1
#     else:
#         product *= n
#         return product_of_factorial(n-1)

# def sum_of_factorial(n):
#     global sum
#     if n == 0:
#         sum += 0
#     else:
#         sum += n
#         return sum_of_factorial(n-1)

# sum_of_factorial(n)
# product_of_factorial(n)   
# print(product + sum)
# n= int(input('factorial this: '))

# def factorial():
#     if n == 1:
#         return 1
#     else:
#         return n*factorial(n-1)
t = input()
dict = {"uppers":[],"lowers":[]}
for n in t:
    if n.isupper():
        dict["uppers"].append(n)
    else:
        dict["lowers"].append(n)
print(''.join(dict["uppers"]))
print(''.join(dict["lowers"]))