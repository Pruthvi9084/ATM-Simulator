import streamlit as st
import pymongo
from pymongo import MongoClient
import datetime
import pandas as pd

def loan():
    
    def connect_to_mongodb():
        client = MongoClient("mongodb://localhost:27017/") 
        return client

    client = connect_to_mongodb()    
    db1 = client["Atm"]  
    collection2 = db1['Loan']
    
    def validate_loan_account(text):
        return text.isdigit() and len(text) == 6

    def validate_loan_pin(text):
        return text.isdigit() and len(text) == 4

    def authenticate_loan(loan_account_number, loan_pin, collection2):
        user = collection2.find_one(
            {"account_number": "{loan_account_number}", "pin": "{loan_pin}", "active": True}
        )
        return user is not None

    account_number = st.text_input('Enter Your 6 Digit Loan Account Number', value='', key='lac')
    pin = st.text_input('Enter Your 4 Digit Loan Pin', type='password')

    option = st.selectbox('Select Login To Login',['Stay Logged Out','Login'])
    
    if(option == 'Stay Logged Out'):
        pass

    if(option == 'Login'):
        if validate_loan_account(account_number) and validate_loan_pin(pin):
            loan_account_number = int(account_number)
            loan_pin = int(pin)
            user = collection2.find_one({"account_number": loan_account_number , "pin": loan_pin})
            if user:
                st.write("Logged In successfully")
                loan = st.selectbox('',['Select','Display Loans','Pay Loan Amount','Display Transactions'])
                
                if loan == 'Select':
                    pass
                
                if loan == 'Display Loans':
                    loan_details = []
                    for loan in user["loans"]:
                        loan_info = {
                            "Loan Type": loan["loan_type"],
                            "Interest Rate": loan["interest_rate"],
                            "Loan Issue Date": loan["loan_date"],
                            "Loan Allocation": loan["loan_allocation"],
                            "Amount Paid": loan["amount_paid"],
                            "Remaining Payment": loan["remaining_payment"]}
                        loan_details.append(loan_info)                        
                    df = pd.DataFrame(loan_details)
                    st.write(df)
                
                if loan == 'Pay Loan Amount':
                    pay_loan = ['Select']
                    for loan in user['loans']:
                        pay_loan.append(loan['loan_type'])
                    loan_pay = st.selectbox('',pay_loan)

                    if(loan_pay != 'Select'):
                        st.write(f'You have selected {loan_pay}')
                        amount = st.text_input('Enter the amount you want to pay')
                        amt = int(amount) if amount.isdigit() else 0
                        
                        if(amt<0):
                            st.write('Invalid amount')
                        
                        for loan in user['loans']:
                            if loan['loan_type'] == loan_pay:
                                if(amt>loan['remaining_payment']):
                                    st.write('Amount is more then remaining amount')
                                else:
                                    if(st.button('Pay')):
                                            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                            transaction = {
                                                "date": current_time[:10], 
                                                "amount_paid": amt,         
                                                "time": current_time[11:]    
                                            }
                                            new_amt = loan['remaining_payment']-amt
                                            new_paid = loan['amount_paid']+amt
                                            
                                            collection2.update_one(
                                                {"account_number": loan_account_number, "loans.loan_type": loan_pay},
                                                {
                                                    "$set": {
                                                    "loans.$.remaining_payment": new_amt,
                                                    "loans.$.amount_paid": new_paid
                                                },
                                                    "$push": {
                                                    "loans.$.transactions": transaction
                                                }
                                                }
                                            )

                                            st.write(f'Payment of {amt} successfully processed for {loan_pay}.')
                                            break
                                        
                if(loan == 'Display Transactions'):
                    pay_loan = ['Select']
                    for loan in user['loans']:
                        pay_loan.append(loan['loan_type'])
                    loan_pay = st.selectbox('',pay_loan)

                    if(loan_pay != 'Select'):
                        st.write(f'You have selected {loan_pay}')
                        for loan in user['loans']:
                            if(loan['loan_type']==loan_pay):
                                trans = []
                                for t in loan['transactions']:
                                    tran = {
                                        "Date":t['date'],
                                        "Amount Paid":t["amount_paid"],
                                        "Time":t["time"]
                                    }
                                    trans.append(tran)
                                df = pd.DataFrame(trans)
                                st.write(df)
                    
            else:
                st.write('User Not Found Please Contact The Respective Bank')
            
    
