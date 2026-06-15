import streamlit as st

# Set up the browser tab title and layout
st.set_page_config(page_title="Monster Game", page_icon="👹", layout="centered")

# Initialize session state variables so the app remembers what page you are on
if "page" not in st.session_state:
    st.session_state.page = "landing"
if "chosen_monster" not in st.session_state:
    st.session_state.chosen_monster = None

# ----------------------------------------------------
# 1. THE LANDING PAGE
# ----------------------------------------------------
if st.session_state.page == "landing":
    st.title("👹 Monster Rebel Chronicles")
    st.write("Welcome to the neon-lit streets where fashion meets claws.")
    st.write("---")
    
    # Big primary action button
    if st.button("PLAY", type="primary", use_container_width=True):
        st.session_state.page = "selection"
        st.rerun()

# ----------------------------------------------------
# 2. CHARACTER SELECTION SCREEN
# ----------------------------------------------------
elif st.session_state.page == "selection":
    st.title("Choose Your Monster")
    st.write("Pick your character to begin the adventure:")
    st.write("---")
    
    # Create two columns side-by-side for the choices
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎸 The Guy Monster")
        st.markdown("**Style:** Sleek black leather motorcycle jacket.")
        st.caption("A mysterious vibe with zero patience for rules.")
        
        if st.button("Select Guy Monster", use_container_width=True):
            st.session_state.chosen_monster = "Guy Monster (Black Leather Jacket)"
            st.session_state.page = "gameplay"
            st.rerun()
            
    with col2:
        st.subheader("🧷 The Girl Monster")
        st.markdown("**Style:** Vibrant pink leather jacket.")
        st.caption("Fierce, custom-patched, and ready to break things.")
        
        if st.button("Select Girl Monster", use_container_width=True):
            st.session_state.chosen_monster = "Girl Monster (Pink Leather Jacket)"
            st.session_state.page = "gameplay"
            st.rerun()

# ----------------------------------------------------
# 3. THE GAMEPLAY SCREEN
# ----------------------------------------------------
elif st.session_state.page == "gameplay":
    st.title("🎮 Game Active")
    st.success(f"You are currently playing as: **{st.session_state.chosen_monster}**")
    st.write("---")
    
    # Placeholder for future game mechanics
    st.info("Next up: Add your maps, canvas layouts, or battle systems here!")
    
    # Button to reset state and head back to start
    if st.button("Quit to Main Menu"):
        st.session_state.page = "landing"
        st.session_state.chosen_monster = None
        st.rerun()