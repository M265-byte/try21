import streamlit as st
from PIL import Image
import time
import os

st.set_page_config(page_title="Ancient Tale", layout="wide")

# -----------------------
# Helpers & defaults
# -----------------------
def img_exists(name):
    return os.path.exists(name)

def load_img(name):
    try:
        return Image.open(name)
    except Exception:
        st.warning(f"Missing or unreadable image: {name}")
        return None

def composite_on_bg(bg_path, overlay_path, pos=(100, 50), overlay_size=(300, 300)):
    bg = load_img(bg_path)
    overlay = load_img(overlay_path)
    if bg is None:
        return None
    out = bg.copy()
    if overlay is not None:
        try:
            o = overlay.resize(overlay_size).convert("RGBA")
            out.paste(o, pos, o)
        except Exception:
            # fallback: paste without alpha
            o = overlay.resize(overlay_size)
            out.paste(o, pos)
    return out

def next_page(name):
    st.session_state.page = name

# session defaults
if "page" not in st.session_state:
    st.session_state.page = "menu"
if "character" not in st.session_state:
    st.session_state.character = None   # "girl" or "boy"
if "kids_q_index" not in st.session_state:
    st.session_state.kids_q_index = 0   # for kids questions across kids2 & kids3
if "pearls_answered" not in st.session_state:
    st.session_state.pearls_answered = 0
if "pearl_start_time" not in st.session_state:
    st.session_state.pearl_start_time = None
if "hearts" not in st.session_state:
    st.session_state.hearts = 4
if "ship_q_index" not in st.session_state:
    st.session_state.ship_q_index = 0
if "congrats2_at" not in st.session_state:
    st.session_state.congrats2_at = None

# -----------------------
# Right-side controls helper
# -----------------------
def right_side_columns():
    # returns (content_col, side_col) where side_col is a narrow right column for controls
    content_col, side_col = st.columns([4, 1])
    return content_col, side_col

# -----------------------
# MENU
# -----------------------
if st.session_state.page == "menu":
    content_col, side_col = right_side_columns()
    with content_col:
        bg = load_img("menu.png")
        if bg: st.image(bg, use_container_width=True)
        st.markdown("<h1 style='text-align:center; color: white; font-size:48px;'>Ancient Tales</h1>", unsafe_allow_html=True)
    with side_col:
        # side controls (unique keys)
        if st.button("Sign In", key="menu_signin_btn"):
            next_page("signin")
        if st.button("Enter as Guest", key="menu_guest_btn"):
            next_page("choose_character")

# -----------------------
# SIGN IN (no verification)
# -----------------------
elif st.session_state.page == "signin":
    content_col, side_col = right_side_columns()
    with content_col:
        bg = load_img("menu.png")
        if bg: st.image(bg, use_container_width=True)
        st.markdown("<h2 style='text-align:center; color: white;'>Sign In</h2>", unsafe_allow_html=True)
        st.session_state._email = st.text_input("Email", key="signin_email")
        st.session_state._pwd = st.text_input("Password", type="password", key="signin_pwd")
    with side_col:
        if st.button("Submit", key="signin_submit_btn"):
            if st.session_state._email and st.session_state._pwd:
                next_page("choose_character")
            else:
                st.warning("Please enter email and password")

# -----------------------
# CHARACTER SELECTION (overlay character on character.png)
# -----------------------
elif st.session_state.page == "choose_character":
    content_col, side_col = right_side_columns()
    with content_col:
        # composite character.png + overlayed characters
        # left: Dhabia, right: Nahyan
        bg = load_img("character.png")
        if bg is None:
            # fallback show both as separate
            col_a, col_b = st.columns(2)
            with col_a:
                if img_exists("dhabia.png"): st.image("dhabia.png", width=300)
            with col_b:
                if img_exists("nahyan.png"): st.image("nahyan.png", width=300)
        else:
            # show two composites side-by-side
            # left composite with dhabia
            left_comp = composite_on_bg("character.png", "dhabia.png", pos=(60, 120), overlay_size=(300,300))
            right_comp = composite_on_bg("character.png", "nahyan.png", pos=(60, 120), overlay_size=(300,300))
            col_a, col_b = st.columns(2)
            with col_a:
                if left_comp: st.image(left_comp, use_container_width=True)
                else:
                    if img_exists("dhabia.png"): st.image("dhabia.png", width=300)
            with col_b:
                if right_comp: st.image(right_comp, use_container_width=True)
                else:
                    if img_exists("nahyan.png"): st.image("nahyan.png", width=300)
        st.markdown("<h2 style='text-align:center; color:white;'>Choose Your Character</h2>", unsafe_allow_html=True)
    with side_col:
        # clickable areas implemented as buttons in the side column (unique keys)
        if st.button("Play as Dhabia", key="choose_dhabia_btn"):
            st.session_state.character = "girl"
            # reset scene-specific state
            st.session_state.kids_q_index = 0
            st.session_state.pearls_answered = 0
            st.session_state.pearl_start_time = None
            st.session_state.hearts = 4
            st.session_state.ship_q_index = 0
            next_page("dubainew1")
        if st.button("Play as Nahyan", key="choose_nahyan_btn"):
            st.session_state.character = "boy"
            st.session_state.kids_q_index = 0
            st.session_state.pearls_answered = 0
            st.session_state.pearl_start_time = None
            st.session_state.hearts = 4
            st.session_state.ship_q_index = 0
            next_page("dubainew1")

# Utility to show a single scene (one image) and right-side Next button
def show_scene_with_next(image_name, next_page_name, next_key_suffix):
    content_col, side_col = right_side_columns()
    with content_col:
        img = load_img(image_name)
        if img: st.image(img, use_container_width=True)
    with side_col:
        if st.button("Next ▶", key=f"next_{next_key_suffix}"):
            next_page(next_page_name)

# -----------------------
# STORY SEQUENCE (single scene visible at a time)
# Filenames follow the pattern you provided:
# dubainewgirl1.png / dubainewboy1.png etc.
# -----------------------
# DUBAI 1
if st.session_state.page == "dubainew1":
    suffix = st.session_state.character or "girl"
    show_scene_with_next(f"dubainew1{suffix}.png", "dubainew2", "dubainew1")

# DUBAI 2
elif st.session_state.page == "dubainew2":
    suffix = st.session_state.character or "girl"
    show_scene_with_next(f"dubainew2{suffix}.png", "welcomegirl1" if suffix=="girl" else "welcomeboy1", "dubainew2")

# WELCOME 1
elif st.session_state.page in ("welcomegirl1", "welcomeboy1"):
    suffix = "girl" if st.session_state.page=="welcomegirl1" else "boy"
    show_scene_with_next(f"welcome1{suffix}.png", "welcomegirl2" if suffix=="girl" else "welcomeboy2", f"welcome1_{suffix}")

# WELCOME 2
elif st.session_state.page in ("welcomegirl2", "welcomeboy2"):
    suffix = "girl" if st.session_state.page=="welcomegirl2" else "boy"
    show_scene_with_next(f"welcome2{suffix}.png", "kidsgirl1" if suffix=="girl" else "kidsboy1", f"welcome2_{suffix}")

# KIDS SEQUENCE 1 -> 4 (kids2 & kids3 have questions)
kids_questions = [
    ("Which game are they playing?", ["Tila", "Qubba", "Salam bil Aqaal", "Khosah Biboosah"], "Tila"),
    ("And the second game?", ["Khosah Biboosah", "Tila", "Mawiyah", "Alghimayah"], "Khosah Biboosah"),
]

# kids1
if st.session_state.page in ("kidsgirl1", "kidsboy1"):
    suffix = "girl" if st.session_state.page=="kidsgirl1" else "boy"
    show_scene_with_next(f"kid1{suffix}.png", f"kidsgirl2" if suffix=="girl" else "kidsboy2", f"kid1_{suffix}")

# kids2 (has question)
elif st.session_state.page in ("kidsgirl2", "kidsboy2"):
    suffix = "girl" if st.session_state.page=="kidsgirl2" else "boy"
    content_col, side_col = right_side_columns()
    with content_col:
        img = load_img(f"kid2{suffix}.png")
        if img: st.image(img, use_container_width=True)
    with side_col:
        # show kids question according to kids_q_index
        k_idx = st.session_state.kids_q_index
        if k_idx < len(kids_questions):
            q, opts, ans = kids_questions[k_idx]
            choice = st.radio(q, opts, key=f"kids_q_{k_idx}")
            if st.button("Submit Answer", key=f"kids2_submit_{k_idx}"):
                if choice == ans:
                    st.success("Correct!")
                else:
                    st.error(f"Wrong! Correct answer: {ans}")
                st.session_state.kids_q_index += 1
                # after submitting move to next kids scene or next section when both questions done
                # we want kids2 and kids3 to host the two kids questions in order
                if st.session_state.kids_q_index == 1:
                    # go to kids3 next
                    next_page("kidsgirl3" if suffix=="girl" else "kidsboy3")
                else:
                    # questions done; proceed to kids4
                    next_page("kidsgirl4" if suffix=="girl" else "kidsboy4")
        else:
            # safety fallback
            if st.button("Next ▶", key=f"kids2_next_{suffix}"):
                next_page("kidsgirl3" if suffix=="girl" else "kidsboy3")

# kids3 (has second question)
elif st.session_state.page in ("kidsgirl3", "kidsboy3"):
    suffix = "girl" if st.session_state.page=="kidsgirl3" else "boy"
    content_col, side_col = right_side_columns()
    with content_col:
        img = load_img(f"kid3{suffix}.png")
        if img: st.image(img, use_container_width=True)
    with side_col:
        k_idx = st.session_state.kids_q_index
        # if second question not yet answered, show it
        if k_idx < len(kids_questions):
            q, opts, ans = kids_questions[k_idx]
            choice = st.radio(q, opts, key=f"kids3_q_{k_idx}")
            if st.button("Submit Answer", key=f"kids3_submit_{k_idx}"):
                if choice == ans:
                    st.success("Correct!")
                else:
                    st.error(f"Wrong! Correct answer: {ans}")
                st.session_state.kids_q_index += 1
                # after, go to kids4
                next_page("kidsgirl4" if suffix=="girl" else "kidsboy4")
        else:
            if st.button("Next ▶", key=f"kids3_next_{suffix}"):
                next_page("kidsgirl4" if suffix=="girl" else "kidsboy4")

# kids4
elif st.session_state.page in ("kidsgirl4", "kidsboy4"):
    suffix = "girl" if st.session_state.page=="kidsgirl4" else "boy"
    show_scene_with_next(f"kid4{suffix}.png", "crewgirl1" if suffix=="girl" else "crewboy1", f"kid4_{suffix}")

# CREW 1..9 (one scene at a time)
for i in range(1, 10):
    if st.session_state.page == (f"crewgirl{i}" if st.session_state.character=="girl" else f"crewboy{i}"):
        suffix = st.session_state.character
        # compute next scene
        if i < 9:
            next_sc = f"crewgirl{i+1}" if suffix=="girl" else f"crewboy{i+1}"
        else:
            next_sc = "pearlgame"
        show_scene_with_next(f"crew{i}{suffix}.png", next_sc, f"crew_{i}_{suffix}")

# -----------------------
# PEARL GAME (single background: pearlgamegirl1.png or pearlgameboy1.png)
# -----------------------
if st.session_state.page == "pearlgame":
    suffix = st.session_state.character or "girl"
    content_col, side_col = right_side_columns()
    with content_col:
        bg_name = f"pearlgame{suffix}1.png"
        img = load_img(bg_name)
        if img: st.image(img, use_container_width=True)
    with side_col:
        # start timer
        if st.session_state.pearl_start_time is None:
            st.session_state.pearl_start_time = time.time()
        elapsed = int(time.time() - st.session_state.pearl_start_time)
        hearts_lost = elapsed // 30
        st.session_state.hearts = max(4 - int(hearts_lost), 0)
        st.markdown(f"<div style='text-align:center; font-size:20px; color:red;'>{'❤️ '*st.session_state.hearts}</div>", unsafe_allow_html=True)
        st.markdown("<hr/>", unsafe_allow_html=True)

        # pearl interaction: rather than separate images, we show buttons for each pearl
        pearls_q = [
            ("Pearl 1", "What is the knife used to open oysters called?", ["Sakaria", "Mafak", "Tasa"], "Sakaria"),
            ("Pearl 2", "Large white/pinkish pearl?", ["Danah", "Yaqooti", "Jiwan"], "Danah"),
            ("Pearl 3", "Smaller white shiny pearl?", ["Yaqooti", "Yika", "Mauz"], "Yaqooti"),
            ("Pearl 4", "Yellowish/blueish pearl?", ["Batniyah", "Qimashi", "Rasiyah"], "Qimashi"),
        ]

        # show pearl buttons and question area
        for idx, (label, q, opts, ans) in enumerate(pearls_q):
            if st.button(label, key=f"pearl_btn_{idx}"):
                # place question for this pearl
                st.session_state._current_pearl = idx

        # show current pearl question if any
        if " _current_pearl" in st.session_state:
            pass
        if "_current_pearl" in st.session_state:
            p_idx = st.session_state._current_pearl
            label, q, opts, ans = pearls_q[p_idx]
            st.markdown(f"### {label} question")
            choice = st.radio(q, opts, key=f"pearl_q_{p_idx}")
            if st.button("Submit Pearl Answer", key=f"pearl_submit_{p_idx}"):
                if choice == ans:
                    st.success("Correct! (+1)")
                else:
                    st.error(f"Wrong! Correct: {ans}")
                st.session_state.pearls_answered += 1
                # remove current pearl question
                del st.session_state["_current_pearl"]

        # check end condition
        if st.session_state.pearls_answered >= 4:
            if st.button("Proceed to Ship", key="pearls_done_btn"):
                next_page("ship")
        if st.session_state.hearts <= 0:
            st.error("All hearts lost — returning to ship.")
            if st.button("Proceed to Ship (Retry)"):
                next_page("ship")

# -----------------------
# SHIP scene with 3 questions (in side column)
# -----------------------
if st.session_state.page == "ship":
    suffix = st.session_state.character or "girl"
    content_col, side_col = right_side_columns()
    with content_col:
        img = load_img(f"ship{suffix}1.png")
        if img: st.image(img, use_container_width=True)
    with side_col:
        ship_qs = [
            ("What is the Naukhada's role?", ["Captain / Chief", "Main diver", "Assistant diver"], "Captain / Chief"),
            ("What is Naham's role?", ["Motivator and singer", "Main diver", "Pearl inspector"], "Motivator and singer"),
            ("Who steers the ship?", ["Skuni", "Seeb", "Naham"], "Skuni")
        ]
        idx = st.session_state.ship_q_index
        if idx < len(ship_qs):
            q, opts, ans = ship_qs[idx]
            choice = st.radio(q, opts, key=f"ship_q_radio_{idx}")
            if st.button("Submit Ship Answer", key=f"ship_submit_{idx}"):
                if choice == ans:
                    st.success("Correct!")
                else:
                    st.error(f"Wrong! Correct: {ans}")
                st.session_state.ship_q_index += 1
        else:
            if st.button("Finish and Continue", key="ship_finish_btn"):
                # schedule congrats2 show after 5 seconds
                st.session_state.congrats2_at = time.time() + 5
                next_page("congrats1")

# -----------------------
# CONGRATS sequence
# -----------------------
if st.session_state.page == "congrats1":
    suffix = st.session_state.character or "girl"
    content_col, side_col = right_side_columns()
    with content_col:
        img = load_img(f"congrats{suffix}1.png")
        if img: st.image(img, use_container_width=True)
    # move to congrats2 after 5 seconds
    if st.session_state.congrats2_at is None:
        st.session_state.congrats2_at = time.time() + 5
    if time.time() >= st.session_state.congrats2_at:
        next_page("congrats2")

elif st.session_state.page == "congrats2":
    suffix = st.session_state.character or "girl"
    content_col, side_col = right_side_columns()
    with content_col:
        img = load_img(f"congrats{suffix}2.png")
        if img: st.image(img, use_container_width=True)
        st.markdown("<h2 style='text-align:center; color: white;'>Adventure Complete — Well done!</h2>", unsafe_allow_html=True)
    with side_col:
        if st.button("Play Again", key="playagain_btn"):
            # reset state
            st.session_state.character = None
            st.session_state.kids_q_index = 0
            st.session_state.pearls_answered = 0
            st.session_state.pearl_start_time = None
            st.session_state.hearts = 4
            st.session_state.ship_q_index = 0
            st.session_state.congrats2_at = None
            next_page("menu")

