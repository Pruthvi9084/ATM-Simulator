import streamlit as st
import pymongo
from pymongo import MongoClient
import datetime
import pandas as pd


def Atm_functions():
    
    def connect_to_mongodb():
        client = MongoClient("mongodb://localhost:27017/") 
        return client

    client = connect_to_mongodb()    
    db1 = client["Atm"]  
    collection1 = db1["Accounts"]
    
    def validate_account(text):
        return text.isdigit() and len(text) == 4

    def validate_pin(text):
        return text.isdigit() and len(text) == 4

    def authenticate(account_number, pin, collection1):
        user = collection1.find_one(
            {"account_number": "{account_number}", "pin": "{pin}", "active": True}
        )
        return user is not None
    
    account_number = st.text_input('Enter Your 4 Digit Account Number', value='', key='ac')
    pin = st.text_input('Enter Your 4 Digit Pin', type='password')

    option = st.selectbox('',['Stay Logged Out','Login'])
    
    if(option == 'Stay Logged Out'):
        pass

    if(option == 'Login'):
        
        if validate_account(account_number) and validate_pin(pin):
            account_number = int(account_number)
            pin = int(pin)
            user = collection1.find_one({"account_number": account_number , "pin": pin})
            
            if user:
                st.write("logged in successfully")
                
                choice= st.selectbox('Select One Option',['Options','View Balance','Deposit','withdrawal','Transactions'])

                if(choice == 'Options'):
                    st.write('The options are 1) View Balance 2) withdrawal 3) Deposit 4) Transactions')
                
                if(choice == 'View Balance'):
                   st.write(f"Current balance is {user['balance']}")
                   
                if(choice == 'withdrawal'):
                    amount = st.text_input('Enter the amount you want to with draw')
                    if amount:
                        amt = int(amount)
                        if(st.button('Withdraw')):
                            if(amt > user['balance']):
                                st.write('Insufficient balance')
                            else:
                                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                new_balance = user['balance'] - amt
                                collection1.update_one(
                                    {"account_number": account_number},
                                    {
                                        "$set": {"balance": new_balance},
                                        "$push": {
                                        "transactions": {
                                        "type": "withdrawal",
                                        "amount": amount,
                                        "timestamp": current_time}}})
                                st.write(f"{amt} withdrawal successfull")

                            
                if(choice == 'Deposit'):
                    amount = st.text_input('Enter the amount ')
                    if amount:
                        amt = int(amount)
                        if(st.button('Deposit')):
                            if(amt > 40000):
                                st.write('Amount is too large')
                            else:
                                new_balance = user['balance'] + amt
                                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                collection1.update_one(
                                {"account_number": account_number},
                                {
                                    "$set": {"balance": new_balance},
                                    "$push": {
                                    "transactions": {
                                    "type": "Deposit",
                                    "amount": amt,
                                    "timestamp": current_time}}})
                                st.write(f"{amt} deposition successfull")

                if(choice == 'Transactions'):
                    n_transactions = st.number_input('Enter the number of transactions', min_value=1, max_value=10, value=5)
    
                    if st.button('Show Transactions'):
                        user = collection1.find_one({"account_number": int(account_number)})
                        if user:
                            transactions = user.get('transactions', [])
                            last_n_transactions = transactions[-n_transactions:]
            
                            transactions_data = []
                            for i, transaction in enumerate(last_n_transactions, start=1):
                                transaction_info = {
                                "Transaction": i,
                                "Type": transaction['type'],
                                "Amount": transaction['amount'],
                                "Timestamp": transaction['timestamp']
                                }
                                transactions_data.append(transaction_info)

                            st.write(f"Last {n_transactions} Transactions for Account Number {account_number}:")
                            st.dataframe(pd.DataFrame(transactions_data))
           
            else:
                st.write("Account does not exist")
                
        else:
            st.error('Invalid Account Number or PIN')
    
    