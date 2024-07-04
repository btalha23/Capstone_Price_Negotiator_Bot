import streamlit as st

if st.session_state['customer_id']:
        st.sidebar.button("Logout", on_click=lambda: st.session_state.update(customer_id=None, cart=[]))
        st.sidebar.write(f"Customer ID: {st.session_state['customer_id']}")
else:
    st.sidebar.write("Not logged in")

st.title("Register")

st.write("New Customers - Please Register Customer Info Here")

placeholder_first_name = st.empty()
placeholder_last_name = st.empty()
placeholder_customer_email = st.empty()
placeholder_customer_location = st.empty()

user_input_first_name = placeholder_first_name.text_input(label="First Name", value="", key="first_name")
user_input_last_name = placeholder_last_name.text_input(label="Last Name", value="", key="last_name")
user_input_customer_email = placeholder_customer_email.text_input(label="Customer Email", value="", key="customer_email")
user_input_customer_location = placeholder_customer_location.text_input(label="Customer Location", value="", key="customer_location")

if st.button("Register"):
    with st.spinner("Connecting to database..."):
        db_conn_2 = st.session_state.db

        sql_command = """INSERT INTO customer (first_name,last_name,customer_email,customer_location) VALUES (:first_name, :last_name, :customer_email, :customer_location)
                      """
        sql_parameters = {'first_name': st.session_state['first_name'],
                        'last_name': st.session_state['last_name'],
                        'customer_email': st.session_state['customer_email'],
                        'customer_location': st.session_state['customer_location']}
                        
        db_conn_2.run(command=sql_command,
                    parameters=sql_parameters 
                    )
        
        st.success("User Registered Successfully")

    user_input_first_name = placeholder_first_name.text_input(label="First Name")
    user_input_last_name = placeholder_last_name.text_input(label="Last Name")
    user_input_customer_email = placeholder_customer_email.text_input(label="Customer Email")
    user_input_customer_location = placeholder_customer_location.text_input(label="Customer Location")

    st.switch_page(st.session_state['login_page'])

        

        

