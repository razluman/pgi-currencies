from django.contrib.auth.models import User
from .models import Rate, Currency


def import_rate():
    user_id = input("Enter user id : ")
    user = User.objects.get(pk=user_id)
    res = input(f"Import with {user} ? ")
    if res.upper() != "O":
        print("Operation cancelled")
        return
    # filename = "Rate-2023-05-07.csv"
    filename = "Rate.csv"
    i = 1
    sep = "\t"
    with open(filename, "r") as file:
        for line in file:
            line = line.replace("\n", "")
            data = line.split(sep)
            date = data[1]
            rate = data[2]
            currency = Currency.objects.get(pk=data[3])
            Rate.objects.create(
                date=date,
                rate=rate,
                currency=currency,
                created_by=user,
                updated_by=user,
            )
            print(i)
            i = i + 1
    print("Finished")


import_rate()
