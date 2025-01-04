import yaml

import streamlit as st
import streamlit_authenticator as stauth



AUTH_YAML_PATH = "/app/auth.yaml"


# if st.session_state["authentication_status"]:
#     authenticator.logout()
#     st.write(f'Welcome *{st.session_state["name"]}*')
#     st.title('Some content')
# elif st.session_state["authentication_status"] is False:
#     st.error('Username/password is incorrect')
# elif st.session_state["authentication_status"] is None:
#     st.warning('Please enter your username and password')
def login() -> bool:
    """ Return True if logged in, False otherwise """


    # first time run - load authenticator
    if st.session_state.get("authenticator", None) is None:
        try:
            with open(AUTH_YAML_PATH) as file:
                config = yaml.safe_load(file)
        except FileNotFoundError:
            st.error("This instance has not been configured.  Missing `auth.yaml` file.")
            # TODO - just create an empty file and then re-run?  Put default root password in there and have user change it?
            st.stop()

        st.session_state.authenticator = stauth.Authenticate(
            config["credentials"],
            config["cookie"]["name"],
            config["cookie"]["key"],
            config["cookie"]["expiry_days"],
            # config["pre-authorized"],
        )


    # authenticate
    # https://blog.streamlit.io/streamlit-authenticator-part-1-adding-an-authentication-component-to-your-app/
    # https://github.com/mkhorasani/Streamlit-Authenticator?ref=blog.streamlit.io
    st.session_state.authenticator.login(location="main", max_concurrent_users=1, fields={
        "Form name": "PlebChat!",
        "Username": "Username",
        "Password": "Password",
        "Login": "Welcome!",
    })


    if st.session_state["authentication_status"]:
        return True

    elif st.session_state["authentication_status"] is False:
        st.error("Username/password is incorrect")
        return False

    elif st.session_state["authentication_status"] is None:
        st.info('Please enter your username and password')
        return False


    # 🤷 should never get here - just in case
    return False