import streamlit as st
import time

st.title("Login")

placeholder_login_info = st.empty()

user_input_login_info = placeholder_login_info.text_input(label="Login", value="", key="login_info")
print(user_input_login_info)
print(st.session_state['login_info'])
# if st.session_state['login_info'] == "":
#     time.sleep(1)

if st.button('Login'):
    with st.spinner("Connecting to database..."):
        db_conn_2 = st.session_state.db

        sql_command = """SELECT * FROM customer WHERE customer_email = :customer_email
                    """
        sql_parameters = {'customer_email': st.session_state['login_info']}
                        
        retreived_result_obj = db_conn_2.run(command=sql_command,
                                             fetch='cursor',
                                             parameters=sql_parameters 
                                            )
        logged_in_customer_info = retreived_result_obj.mappings().all()
        # print(logged_in_customer_info)
        # print(logged_in_customer_info[0]['customer_id'])
        if logged_in_customer_info:
            st.session_state['customer_id'] = logged_in_customer_info[0]['customer_id']
            st.success("User Logged in Successfully")

    user_input_login_info = placeholder_login_info.text_input(label="Login")

if st.session_state['customer_id']:
        st.sidebar.button("Logout", on_click=lambda: st.session_state.update(customer_id=None, cart=[]))
        st.sidebar.write(f"Customer ID: {st.session_state['customer_id']}")
else:
    st.sidebar.write("Not logged in")

# def login():
#     customer_email = st.text_input('Email')
#     if st.button('Login'):
#         cursor = db.cursor(dictionary=True)
#         cursor.execute("SELECT * FROM Customer WHERE customer_email=%s", (customer_email,))
#         customer = cursor.fetchone()
#         if customer:
#             st.session_state['customer_id'] = customer['customer_id']
#             st.success("Logged in successfully")
#             st.experimental_rerun()