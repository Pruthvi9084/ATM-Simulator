import streamlit as st
import Atm_Basic
import Loan

st.header('ATM SIMULATOR')

selection = st.selectbox('Select Your Option',['Select','Login ATM','Login Loan'])

if selection == 'Select':
    pass

if selection == 'Login ATM':
    Atm_Basic.Atm_functions()
    
if selection == 'Login Loan':
    Loan.loan()
    
    