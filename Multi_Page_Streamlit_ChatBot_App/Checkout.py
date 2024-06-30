import streamlit as st

st.title("Register")

st.write("New Customers - Please Register Customer Info Here")

# st.text_input("First Name", value="", key="first_name")
# st.write("You have entered: ", st.session_state["first_name"])

# st.text_input(label="First Name", value="", key="first_name")
# st.text_input(label="Last Name", value="", key="last_name")
# st.text_input(label="Customer Email", value="", key="customer_email")
# st.text_input(label="Customer Location", value="", key="customer_location")

placeholder_first_name = st.empty()
placeholder_last_name = st.empty()
placeholder_customer_email = st.empty()
placeholder_customer_location = st.empty()
# input = placeholder.text_input('text')
# click_clear = st.button('clear text input', key=1)
# if click_clear:
#     input = placeholder.text_input('text', value='', key=1)

user_input_first_name = placeholder_first_name.text_input(label="First Name", value="", key="first_name")
user_input_last_name = placeholder_last_name.text_input(label="Last Name", value="", key="last_name")
user_input_customer_email = placeholder_customer_email.text_input(label="Customer Email", value="", key="customer_email")
user_input_customer_location = placeholder_customer_location.text_input(label="Customer Location", value="", key="customer_location")

# st.write("You have entered", st.session_state['first_name'])

if st.button("Register"):
    with st.spinner("Connecting to database..."):
        db_conn_2 = st.session_state.db
        # sql_command = """INSERT INTO customer (first_name,last_name,customer_email,customer_location) VALUES (:first_name, :last_name, :customer_email, :customer_location)
        #                  ON DUPLICATE KEY UPDATE first_name=VALUES(first_name), last_name=VALUES(last_name), customer_email=VALUES(customer_email), customer_location=VALUES(customer_location)
        #               """
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

    # st.session_state['first_name'] = ""
    # st.session_state['last_name'] = ""
    # st.session_state['customer_email'] = ""
    # st.session_state['customer_location'] = ""
    # st.rerun()

    user_input_first_name = placeholder_first_name.text_input(label="First Name")
    user_input_last_name = placeholder_last_name.text_input(label="Last Name")
    user_input_customer_email = placeholder_customer_email.text_input(label="Customer Email")
    user_input_customer_location = placeholder_customer_location.text_input(label="Customer Location")

        

        

