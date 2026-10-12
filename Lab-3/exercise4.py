ch = input("Enter a single character: ").lower()

if len(ch) == 1 and ch.isalpha():
    if ch in ['a', 'e', 'i', 'o', 'u']:
        print("Vowel")
    else:
        print("Not vowel")
else:
    print("Invalid input. Please enter a single alphabetical character.")