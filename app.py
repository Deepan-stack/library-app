import re
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="BorrowHub — Library Management", layout="wide")

# ---------------- Data ----------------
def seed_books():
    return pd.DataFrame([
        {"id": 1, "title": "Clean Code", "author": "Robert C. Martin", "isbn": "9780132350884", "category": "Software Engineering", "copies": 4, "available": 2},
        {"id": 2, "title": "The Pragmatic Programmer", "author": "David Thomas", "isbn": "9780135957059", "category": "Software Engineering", "copies": 3, "available": 0},
        {"id": 3, "title": "Sapiens", "author": "Yuval Noah Harari", "isbn": "9780062316097", "category": "History", "copies": 5, "available": 5},
        {"id": 4, "title": "Atomic Habits", "author": "James Clear", "isbn": "9780735211292", "category": "Self-Help", "copies": 6, "available": 1},
        {"id": 5, "title": "Design Patterns", "author": "Erich Gamma", "isbn": "9780201633610", "category": "Software Engineering", "copies": 2, "available": 2},
        {"id": 6, "title": "Educated", "author": "Tara Westover", "isbn": "9780399590504", "category": "Memoir", "copies": 3, "available": 0},
        {"id": 7, "title": "Introduction to Algorithms", "author": "Thomas Cormen", "isbn": "9780262033848", "category": "Computer Science", "copies": 4, "available": 3},
        {"id": 8, "title": "Dune", "author": "Frank Herbert", "isbn": "9780441172719", "category": "Fiction", "copies": 5, "available": 2},
    ])

def seed_users():
    return pd.DataFrame([
        {"ID": "USR-101", "Name": "Aravind K.", "Role": "Student", "Status": "Active", "Joined": "Jan 2025"},
        {"ID": "USR-102", "Name": "Priya S.", "Role": "Librarian", "Status": "Active", "Joined": "Mar 2024"},
        {"ID": "USR-103", "Name": "Rahul M.", "Role": "Student", "Status": "Suspended", "Joined": "Feb 2025"},
        {"ID": "USR-104", "Name": "Elena R.", "Role": "Admin", "Status": "Active", "Joined": "Jan 2023"},
    ])

TREND = pd.DataFrame({
    "day": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    "issued": [12, 18, 9, 22, 15, 6, 4],
})

OVERDUE = pd.DataFrame([
    {"member": "Aravind K.", "book": "The Pragmatic Programmer", "due": "Aug 18", "days": 7},
    {"member": "Priya S.", "book": "Educated", "due": "Aug 20", "days": 5},
    {"member": "Rahul M.", "book": "Atomic Habits", "due": "Aug 22", "days": 3},
])

MY_LOANS = pd.DataFrame([
    {"title": "Clean Code", "due": "Sep 02", "status": "On time"},
    {"title": "Design Patterns", "due": "Aug 24", "status": "Overdue"},
])

# ---------------- Session state ----------------
if "books" not in st.session_state:
    st.session_state.books = seed_books()
if "role" not in st.session_state:
    st.session_state.role = "Admin"
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"
if "editing_id" not in st.session_state:
    st.session_state.editing_id = None
if "confirm_delete_id" not in st.session_state:
    st.session_state.confirm_delete_id = None
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "email" not in st.session_state:
    st.session_state.email = ""
if "users" not in st.session_state:
    st.session_state.users = seed_users()
if "adding_user" not in st.session_state:
    st.session_state.adding_user = False
if "show_signup" not in st.session_state:
    st.session_state.show_signup = False

NAV = {
    "Admin": ["Dashboard", "Catalog", "Users", "Reports", "Settings"],
    "Librarian": ["Dashboard", "Catalog", "Issue / Return", "Members", "Overdue & Fines"],
    "Student": ["Dashboard", "Browse Catalog", "My Books", "Profile"],
}

st.markdown("""
<style>
.block-container {
    padding-top: 3.5rem !important;
    padding-bottom: 2rem !important;
}

div[data-testid="stHorizontalBlock"] {
    align-items: center;
}

div[data-testid="stMetric"] {
    background: var(--secondary-background-color);
    border-radius: 12px;
    padding: 14px 16px;
    border: 1px solid rgba(128,128,128,0.15);
}

/* ---------------- Overall design ---------------- */
h1, h2, h3, h4 { font-family: Georgia, 'Times New Roman', serif !important; }
div[data-testid="stSidebarContent"] { background: #FAFBF7; }
div.stButton > button, div.stFormSubmitButton > button, div.stDownloadButton > button {
    border-radius: 9px !important;
}
div[data-testid="stVerticalBlockBorderWrapper"] { border-radius: 14px !important; }

/* Log out button — red, pinned to the right */
div[data-testid="stVerticalBlock"]:has(> div.logout-marker) { display: flex; justify-content: flex-end; }
div[data-testid="stVerticalBlock"]:has(> div.logout-marker) button {
    background: #B23B3B !important; border-color: #B23B3B !important; color: #fff !important;
}
div[data-testid="stVerticalBlock"]:has(> div.logout-marker) button:hover {
    background: #9a3232 !important; border-color: #9a3232 !important;
}

/* ---------------- Login page ---------------- */
div[data-testid="stVerticalBlockBorderWrapper"]:has(div.login-marker) {
    max-width: 400px;
    margin: 50px auto;
    padding: 6px 8px;
    border-radius: 16px !important;
}
.login-brand-row { display: flex; align-items: center; margin-bottom: 20px; }
.login-logo-box {
    width: 36px; height: 36px; background: #0F6E56; border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 17px; margin-right: 10px;
}
.login-brand-name { font-family: Georgia, 'Times New Roman', serif; font-size: 19px; font-weight: 700; }
.login-title { font-family: Georgia, 'Times New Roman', serif; font-size: 23px; font-weight: 700;
    margin: 2px 0 6px; }
.login-subtitle { color: #5B6158; font-size: 13.5px; margin-bottom: 6px; }
.login-field-label { font-size: 12px; color: #5B6158; margin: 14px 0 4px; font-weight: 500; }

div[data-testid="stRadio"] input[type="radio"] { display: none; }
div[data-testid="stRadio"] > div[role="radiogroup"] { flex-direction: row; gap: 8px; }
div[data-testid="stRadio"] label {
    border: 1px solid rgba(128,128,128,0.3);
    border-radius: 10px;
    padding: 12px 6px;
    flex: 1;
    justify-content: center;
    margin: 0 !important;
}
div[data-testid="stRadio"] label:has(input:checked) {
    border-color: #0F6E56;
    background: #E1F0EA;
}
div[data-testid="stRadio"] label p {
    font-size: 12.5px !important; font-weight: 600 !important; color: #5B6158 !important;
}
div[data-testid="stRadio"] label:has(input:checked) p { color: #0F6E56 !important; }

div.stFormSubmitButton > button[kind="primary"],
div.stButton > button[kind="primary"] {
    background: #0F6E56; border-color: #0F6E56; border-radius: 9px;
    font-weight: 600; padding: 10px 16px;
}
div.stFormSubmitButton > button[kind="primary"]:hover,
div.stButton > button[kind="primary"]:hover {
    background: #0c5a46; border-color: #0c5a46;
}
</style>
""", unsafe_allow_html=True)

# ---------------- Login gate ----------------
ROLE_ICONS = {"Admin": "🛡️", "Librarian": "📖", "Student": "🎓"}

def login_page():
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        with st.container(border=True):
            st.markdown('<div class="login-marker"></div>', unsafe_allow_html=True)
            st.markdown(
                '<div class="login-brand-row">'
                '<div class="login-logo-box">📚</div>'
                '<div class="login-brand-name">BorrowHub</div>'
                '</div>', unsafe_allow_html=True)

            if not st.session_state.show_signup:
                st.markdown('<div class="login-title">Sign in</div>', unsafe_allow_html=True)
                st.markdown('<div class="login-subtitle">Use your Gmail address and pick your role to continue.</div>',
                            unsafe_allow_html=True)

                with st.form("login_form"):
                    st.markdown('<div class="login-field-label">Gmail Address</div>', unsafe_allow_html=True)
                    email = st.text_input("Gmail address", placeholder="yourname@gmail.com",
                                           label_visibility="collapsed")

                    st.markdown('<div class="login-field-label">Role</div>', unsafe_allow_html=True)
                    role = st.radio(
                        "Role", list(NAV.keys()),
                        format_func=lambda r: f"{ROLE_ICONS[r]}  {r}",
                        horizontal=True, label_visibility="collapsed",
                    )

                    submitted = st.form_submit_button("Login", type="primary", use_container_width=True)

                    if submitted:
                        if not re.match(r"^[a-zA-Z0-9._%+-]+@gmail\.com$", email.strip()):
                            st.error("Please enter a valid @gmail.com address.")
                        else:
                            st.session_state.logged_in = True
                            st.session_state.email = email.strip().lower()
                            st.session_state.role = role
                            st.session_state.page = "Dashboard"
                            st.rerun()

                if st.button("➕ Add User", use_container_width=True):
                    st.session_state.show_signup = True
                    st.rerun()

            else:
                st.markdown('<div class="login-title">Add User</div>', unsafe_allow_html=True)
                st.markdown('<div class="login-subtitle">Register a new account, then continue straight to your dashboard.</div>',
                            unsafe_allow_html=True)

                with st.form("signup_form"):
                    st.markdown('<div class="login-field-label">Full Name</div>', unsafe_allow_html=True)
                    name = st.text_input("Full name", placeholder="Your name", label_visibility="collapsed")

                    st.markdown('<div class="login-field-label">Gmail Address</div>', unsafe_allow_html=True)
                    new_email = st.text_input("Gmail address", placeholder="yourname@gmail.com",
                                               label_visibility="collapsed", key="signup_email")

                    st.markdown('<div class="login-field-label">Role</div>', unsafe_allow_html=True)
                    new_role = st.radio(
                        "Role", list(NAV.keys()),
                        format_func=lambda r: f"{ROLE_ICONS[r]}  {r}",
                        horizontal=True, label_visibility="collapsed", key="signup_role",
                    )

                    s1, s2 = st.columns(2)
                    add = s1.form_submit_button("Add User", type="primary", use_container_width=True)
                    back = s2.form_submit_button("Back to sign in", use_container_width=True)

                    if add:
                        if not name.strip():
                            st.error("Full name is required.")
                        elif not re.match(r"^[a-zA-Z0-9._%+-]+@gmail\.com$", new_email.strip()):
                            st.error("Please enter a valid @gmail.com address.")
                        else:
                            new_id = f"USR-{100 + len(st.session_state.users) + 1}"
                            new_row = {"ID": new_id, "Name": name.strip(), "Role": new_role,
                                       "Status": "Active", "Joined": pd.Timestamp.today().strftime("%b %Y")}
                            st.session_state.users = pd.concat(
                                [st.session_state.users, pd.DataFrame([new_row])], ignore_index=True)
                            st.session_state.logged_in = True
                            st.session_state.email = new_email.strip().lower()
                            st.session_state.role = new_role
                            st.session_state.page = "Dashboard"
                            st.session_state.show_signup = False
                            st.toast("User added")
                            st.rerun()
                    if back:
                        st.session_state.show_signup = False
                        st.rerun()

if not st.session_state.logged_in:
    login_page()
    st.stop()

def logout():
    st.session_state.logged_in = False
    st.session_state.email = ""
    st.session_state.page = "Dashboard"
    st.session_state.editing_id = None
    st.session_state.confirm_delete_id = None
    st.session_state.adding_user = False
    st.session_state.show_signup = False
    st.rerun()

# ---------------- Top bar ----------------
top_l, top_m, top_r = st.columns([3, 4, 1.2])
with top_l:
    st.markdown("### 📚 BorrowHub")
with top_m:
    st.markdown(f"<div style='color:gray;'>Signed in as <b>{st.session_state.email}</b> · {st.session_state.role}</div>", unsafe_allow_html=True)
with top_r:
    st.markdown('<div class="logout-marker"></div>', unsafe_allow_html=True)
    if st.button("Log out", use_container_width=True):
        logout()

st.divider()

# ---------------- Sidebar ----------------
with st.sidebar:
    st.markdown(f"**{st.session_state.role} menu**")
    for item in NAV[st.session_state.role]:
        if st.button(item, use_container_width=True,
                     type="primary" if st.session_state.page == item else "secondary"):
            st.session_state.page = item
            st.rerun()

books = st.session_state.books

# ---------------- Dashboard Components ----------------
def dashboard_admin():
    st.subheader("Overview")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Titles in catalog", len(books))
    c2.metric("Total copies", int(books["copies"].sum()))
    c3.metric("Currently issued", int((books["copies"] - books["available"]).sum()))
    c4.metric("Registered members", 214)

    with st.container(border=True):
        st.markdown("#### Books issued this week")
        fig = px.bar(TREND, x="day", y="issued")
        fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=280,
                          plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

def dashboard_librarian():
    st.subheader("Overview")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Due today", 6)
    c2.metric("Pending returns", 9)
    c3.metric("Overdue books", len(OVERDUE))
    c4.metric("Zero-stock titles", int((books["available"] == 0).sum()))

    with st.container(border=True):
        st.markdown("#### Overdue books")
        st.dataframe(OVERDUE, use_container_width=True, hide_index=True)

def dashboard_student():
    st.subheader("Your library")
    c1, c2 = st.columns(2)
    c1.metric("Books borrowed", len(MY_LOANS))
    c2.metric("Fines due", "₹0")

    with st.container(border=True):
        st.markdown("#### Currently borrowed")
        st.dataframe(MY_LOANS, use_container_width=True, hide_index=True)

# ---------------- Catalog Page ----------------
def catalog_page(can_manage: bool):
    st.subheader("Catalog")

    fc1, fc2, fc3 = st.columns([3, 2, 1])
    query = fc1.text_input("Search by title, author, or ISBN", label_visibility="collapsed",
                            placeholder="Search by title, author, or ISBN")
    categories = ["All"] + sorted(books["category"].unique().tolist())
    category = fc2.selectbox("Category", categories, label_visibility="collapsed")
    if can_manage and fc3.button("➕ Add book", use_container_width=True):
        st.session_state.editing_id = "new"

    filtered = books.copy()
    if query:
        q = query.lower()
        mask = (filtered["title"].str.lower().str.contains(q)
                | filtered["author"].str.lower().str.contains(q)
                | filtered["isbn"].str.contains(q))
        filtered = filtered[mask]
    if category != "All":
        filtered = filtered[filtered["category"] == category]

    st.caption(f"{len(filtered)} of {len(books)} titles")

    # Add / Edit form
    if can_manage and st.session_state.editing_id is not None:
        editing_new = st.session_state.editing_id == "new"
        row = None if editing_new else books[books["id"] == st.session_state.editing_id].iloc[0]
        with st.form("book_form", clear_on_submit=False):
            st.markdown(f"**{'Add new book' if editing_new else 'Edit book'}**")
            t = st.text_input("Title", value="" if editing_new else row["title"])
            a = st.text_input("Author", value="" if editing_new else row["author"])
            isbn = st.text_input("ISBN", value="" if editing_new else row["isbn"])
            cat = st.text_input("Category", value="" if editing_new else row["category"])
            cc1, cc2 = st.columns(2)
            copies = cc1.number_input("Total copies", min_value=0, value=1 if editing_new else int(row["copies"]))
            avail = cc2.number_input("Available now", min_value=0, value=1 if editing_new else int(row["available"]))
            s1, s2 = st.columns(2)
            submitted = s1.form_submit_button("Save", type="primary", use_container_width=True)
            cancelled = s2.form_submit_button("Cancel", use_container_width=True)

            if submitted:
                if not t.strip() or not a.strip() or not isbn.strip():
                    st.error("Title, author, and ISBN are required.")
                else:
                    if editing_new:
                        new_id = int(books["id"].max()) + 1 if len(books) else 1
                        new_row = {"id": new_id, "title": t, "author": a, "isbn": isbn,
                                   "category": cat, "copies": int(copies), "available": int(avail)}
                        st.session_state.books = pd.concat([pd.DataFrame([new_row]), books], ignore_index=True)
                        st.toast("Book added to catalog")
                    else:
                        idx = books.index[books["id"] == row["id"]][0]
                        st.session_state.books.loc[idx, ["title", "author", "isbn", "category", "copies", "available"]] = \
                            [t, a, isbn, cat, int(copies), int(avail)]
                        st.toast("Book updated")
                    st.session_state.editing_id = None
                    st.rerun()
            if cancelled:
                st.session_state.editing_id = None
                st.rerun()

    # Delete confirmation
    if can_manage and st.session_state.confirm_delete_id is not None:
        del_row = books[books["id"] == st.session_state.confirm_delete_id].iloc[0]
        st.warning(f"Remove **{del_row['title']}** from the catalog? This can't be undone.")
        d1, d2 = st.columns(2)
        if d1.button("Delete", type="primary", use_container_width=True):
            st.session_state.books = books[books["id"] != del_row["id"]].reset_index(drop=True)
            st.session_state.confirm_delete_id = None
            st.toast("Book removed")
            st.rerun()
        if d2.button("Cancel", use_container_width=True):
            st.session_state.confirm_delete_id = None
            st.rerun()

    # Table
    st.divider()
    with st.container(border=True):
        header = st.columns([3, 2, 2, 2, 2] + ([1.4] if can_manage else [1.2]))
        for col, label in zip(header, ["Title", "Category", "ISBN", "Availability", "", ""][:len(header)]):
            col.markdown(f"**{label}**")

        for _, b in filtered.iterrows():
            cols = st.columns([3, 2, 2, 2, 2] + ([1.4] if can_manage else [1.2]))
            cols[0].markdown(f"**{b['title']}**  \n:gray[{b['author']}]")
            cols[1].write(b["category"])
            cols[2].code(b["isbn"], language=None)
            if b["available"] > 0:
                cols[3].success(f"{b['available']} of {b['copies']} available")
            else:
                cols[3].error("Fully issued")

            if can_manage:
                if cols[4].button("Edit", key=f"edit_{b['id']}", use_container_width=True):
                    st.session_state.editing_id = b["id"]
                    st.rerun()
                if cols[5].button("Delete", key=f"del_{b['id']}", use_container_width=True):
                    st.session_state.confirm_delete_id = b["id"]
                    st.rerun()
            else:
                disabled = b["available"] <= 0
                label = "Notify me" if disabled else "Reserve"
                if cols[4].button(label, key=f"res_{b['id']}", disabled=disabled, use_container_width=True):
                    idx = books.index[books["id"] == b["id"]][0]
                    st.session_state.books.loc[idx, "available"] -= 1
                    st.toast(f'Reserved "{b["title"]}"')
                    st.rerun()

        if filtered.empty:
            st.info("No books match your search.")

# ---------------- Admin Pages ----------------
def page_users():
    st.subheader("User Management")
    st.caption("Manage library system accounts and permissions.")

    users_df = st.session_state.users

    c1, c2, c3 = st.columns([3, 1, 1.3])
    query = c1.text_input("Search user...", label_visibility="collapsed", placeholder="Search user...")
    if c2.button("➕ Add User", use_container_width=True):
        st.session_state.adding_user = True
    csv_bytes = users_df.to_csv(index=False).encode("utf-8")
    c3.download_button("⬇ Download report", data=csv_bytes, file_name="users_report.csv",
                        mime="text/csv", use_container_width=True)

    if st.session_state.adding_user:
        with st.container(border=True):
            with st.form("add_user_form"):
                st.markdown("**Add new user**")
                name = st.text_input("Full name")
                role = st.selectbox("Role", ["Admin", "Librarian", "Student"])
                status = st.selectbox("Status", ["Active", "Suspended"])
                s1, s2 = st.columns(2)
                add = s1.form_submit_button("Save", type="primary", use_container_width=True)
                cancel = s2.form_submit_button("Cancel", use_container_width=True)

                if add:
                    if not name.strip():
                        st.error("Name is required.")
                    else:
                        new_id = f"USR-{100 + len(st.session_state.users) + 1}"
                        new_row = {"ID": new_id, "Name": name.strip(), "Role": role,
                                   "Status": status, "Joined": pd.Timestamp.today().strftime("%b %Y")}
                        st.session_state.users = pd.concat(
                            [st.session_state.users, pd.DataFrame([new_row])], ignore_index=True)
                        st.session_state.adding_user = False
                        st.toast("User added")
                        st.rerun()
                if cancel:
                    st.session_state.adding_user = False
                    st.rerun()

    filtered = users_df
    if query:
        q = query.lower()
        filtered = users_df[users_df["Name"].str.lower().str.contains(q)]

    with st.container(border=True):
        st.dataframe(filtered, use_container_width=True, hide_index=True)

def page_reports():
    st.subheader("Analytics & Reports")
    st.caption("System usage metrics and circulation analytics.")

    chart_data = pd.DataFrame({"Month": ["May", "Jun", "Jul", "Aug"], "Checkouts": [120, 185, 240, 310]})
    cat_data = pd.DataFrame({"Category": ["Software Eng", "History", "Fiction", "CS"], "Borrows": [45, 30, 25, 20]})

    dl_col, _ = st.columns([1, 3])
    dl_col.download_button("⬇ Download report", data=chart_data.to_csv(index=False).encode("utf-8"),
                            file_name="monthly_circulation_report.csv", mime="text/csv",
                            use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.markdown("#### Monthly Circulations")
            fig = px.bar(chart_data, x="Month", y="Checkouts")
            st.plotly_chart(fig, use_container_width=True)
    with c2:
        with st.container(border=True):
            st.markdown("#### Most Active Categories")
            fig2 = px.pie(cat_data, names="Category", values="Borrows")
            st.plotly_chart(fig2, use_container_width=True)

def page_settings():
    st.subheader("System Settings")
    st.caption("Configure portal global parameters.")
    with st.container(border=True):
        st.text_input("Library Name", value="BorrowHub")
        st.number_input("Default Loan Period (Days)", min_value=1, value=14)
        st.number_input("Late Fine Rate (₹ per day)", min_value=0, value=5)
        st.toggle("Enable Automated Email Reminders", value=True)
        if st.button("Save Settings", type="primary"):
            st.toast("Settings updated successfully!")

# ---------------- Librarian Pages ----------------
def page_issue_return():
    st.subheader("Issue / Return Desk")
    with st.container(border=True):
        tab1, tab2 = st.tabs(["📤 Issue Book", "📥 Return Book"])

        with tab1:
            st.selectbox("Select Member", ["USR-101 (Aravind K.)", "USR-103 (Rahul M.)"])
            st.selectbox("Select Book", books[books["available"] > 0]["title"].tolist() if len(books[books["available"] > 0]) > 0 else ["No Available Books"])
            st.date_input("Due Date")
            if st.button("Confirm Issue", type="primary"):
                st.toast("Book issued successfully!")

        with tab2:
            st.text_input("Enter Book ISBN or Member ID")
            if st.button("Process Return"):
                st.toast("Book marked as returned.")

def page_members():
    st.subheader("Member Directory")
    st.caption("Browse registered library members and loan status.")
    members_df = pd.DataFrame([
        {"Member ID": "MEM-01", "Name": "Aravind K.", "Active Loans": 1, "Fines": "₹0"},
        {"Member ID": "MEM-02", "Name": "Priya S.", "Active Loans": 0, "Fines": "₹0"},
        {"Member ID": "MEM-03", "Name": "Rahul M.", "Active Loans": 2, "Fines": "₹15"},
    ])
    with st.container(border=True):
        st.dataframe(members_df, use_container_width=True, hide_index=True)

def page_overdue_fines():
    st.subheader("Overdue & Fines Tracking")
    with st.container(border=True):
        st.dataframe(OVERDUE, use_container_width=True, hide_index=True)
        if st.button("Send Reminders to Overdue Members"):
            st.toast("Notification emails dispatched!")

# ---------------- Student Pages ----------------
def page_my_books():
    st.subheader("My Borrowed Books")
    with st.container(border=True):
        st.dataframe(MY_LOANS, use_container_width=True, hide_index=True)
        if st.button("Request Loan Extension"):
            st.toast("Renewal request sent to Librarian.")

def page_profile():
    st.subheader("Student Profile")
    with st.container(border=True):
        c1, c2 = st.columns(2)
        with c1:
            st.text_input("Full Name", value="Student User", disabled=True)
            st.text_input("Member ID", value="STU-88219", disabled=True)
        with c2:
            st.text_input("Email", value="student@university.edu")
            st.text_input("Department", value="Computer Science & Engineering")
        if st.button("Update Profile", type="primary"):
            st.toast("Profile updated successfully!")

# ---------------- Router ----------------
page = st.session_state.page
role = st.session_state.role

# Core routes
if page == "Dashboard":
    if role == "Admin": dashboard_admin()
    elif role == "Librarian": dashboard_librarian()
    else: dashboard_student()
elif page in ("Catalog", "Browse Catalog"):
    catalog_page(can_manage=(role != "Student"))

# Admin routes
elif page == "Users": page_users()
elif page == "Reports": page_reports()
elif page == "Settings": page_settings()

# Librarian routes
elif page == "Issue / Return": page_issue_return()
elif page == "Members": page_members()
elif page == "Overdue & Fines": page_overdue_fines()

# Student routes
elif page == "My Books": page_my_books()
elif page == "Profile": page_profile()
