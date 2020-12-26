import random
import sqlite3


conn = sqlite3.connect('./card.s3db')
cur = conn.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS card('
            'id INTEGER PRIMARY KEY AUTOINCREMENT,'
            'number TEXT,'
            'pin TEXT,'
            'balance INTEGER DEFAULT 0);')
conn.commit()


def check_luhn(card_number):
    card_number_list = list(card_number)
    partial_sum = 0
    for i in range(0, len(card_number), 2):
        if int(card_number_list[i]) * 2 > 9:
            partial_sum += int(card_number_list[i]) * 2 - 9
        else:
            partial_sum += int(card_number_list[i]) * 2
    for i in range(1, len(card_number_list), 2):
        partial_sum += int(card_number_list[i])
    if partial_sum % 10 == 0:
        return True
    else:
        return False


def create_card():
    card_number_start = "4000000" + f'{random.randrange(1, 10 ** 8):08}'
    card_number_list = list(card_number_start)
    partial_sum = 0
    for i in range(0, len(card_number_list), 2):
        if int(card_number_list[i]) * 2 > 9:
            partial_sum += int(card_number_list[i]) * 2 - 9
        else:
            partial_sum += int(card_number_list[i]) * 2
    for i in range(1, len(card_number_list), 2):
        partial_sum += int(card_number_list[i])
    check_sum = 10 - (partial_sum % 10)
    if check_sum == 10:
        check_sum = 0
    card_number = card_number_start + str(check_sum)
    pin = f'{random.randrange(1, 9999):04}'
    cur.execute('INSERT INTO card (number, pin) VALUES ({}, {});'.format(card_number, pin))
    conn.commit()
    print("Your card has been created")
    print("Your card number:")
    print(card_number)
    print("Your card PIN:")
    print(pin)
    main()


def login():
    user_card_nb = input("Enter your card number:\n")
    user_pin = input("Enter your PIN:\n")
    cur.execute('SELECT * FROM card WHERE number={};'.format(user_card_nb))
    db_card_data = cur.fetchall()
    if len(db_card_data) == 0:
        print("Wrong card number or PIN")
        return main()
    else:
        pin = db_card_data[0][2]
        if pin == user_pin:
            print("Your have successfully logged in")
            return db_card_data
        else:
            print("Wrong card number or PIN!")
            return main()


def account_manage(db_card_data):
    manage = input("1. Balance \n"
                   "2. Add income \n"
                   "3. Do transfer \n"
                   "4. Close account \n"
                   "5. Log out \n"
                   "0. Exit \n")
    if manage == "1":
        print("Balance: " + str(db_card_data[0][3]))
        account_manage(db_card_data)
    if manage == "2":
        income = input("How much do you want to add? \n")
        cur.execute('UPDATE card SET balance = {} WHERE number={};'.format(db_card_data[0][3] + int(income), db_card_data[0][1]))
        conn.commit()
        cur.execute('SELECT * FROM card WHERE number={};'.format(db_card_data[0][1]))
        db_card_data = cur.fetchall()
        account_manage(db_card_data)
    if manage == "3":
        transfer_account = input("Enter card number:\n")
        if transfer_account == db_card_data[0][1]:
            print("You can't transfer money to the same account!")
            return account_manage(db_card_data)
        if not check_luhn(transfer_account):
            print("Probably you made a mistake in the card number. Please try again!")
            return account_manage(db_card_data)
        cur.execute('SELECT * FROM card WHERE number={};'.format(transfer_account))
        transfer_card_data = cur.fetchall()
        if len(transfer_card_data) == 0:
            print("Such a card does not exist.")
            return account_manage(db_card_data)
        else:
            transfer_amount = input("Enter how much money do you want to transfer:\n")
            if int(transfer_amount) <= db_card_data[0][3]:
                cur.execute('UPDATE card SET balance = {} WHERE number={}'.format(transfer_card_data[0][3] + int(transfer_amount), transfer_card_data[0][1]))
                conn.commit()
                cur.execute('UPDATE card SET balance = {} WHERE number={}'.format(db_card_data[0][3] - int(transfer_amount), db_card_data[0][1]))
                conn.commit()
                print("Success!")
                cur.execute('SELECT * FROM card WHERE number={};'.format(db_card_data[0][1]))
                db_card_data = cur.fetchall()
                return account_manage(db_card_data)
            else:
                print("Not enough money!")
                return account_manage(db_card_data)
    if manage == "4":
        cur.execute('DELETE FROM card WHERE number={};'.format(db_card_data[0][1]))
        conn.commit()
        print("The account has been closed!")
        main()
    if manage == "5":
        print("Your have successfully logged out!")
        main()
    if manage == "0":
        print("Bye!")
        exit()


def main():
    promp = "1. Create an account \n" \
            "2. Log into account \n" \
            "0. Exit \n"
    action = input(promp)

    if action == "0":
        print("Bye!")
        exit()
    if action == "1":
        create_card()
    if action == "2":
        db_card_data = login()
        account_manage(db_card_data)


main()
