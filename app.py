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
</style>
""", unsafe_allow_html=True)

# ---------------- Top bar ----------------
top_l, top_m, top_r = st.columns([2, 3, 2])
with top_l:
    st.markdown("### 📚 BorrowHub")
with top_m:
    role = st.radio("Role", list(NAV.keys()), horizontal=True, label_visibility="collapsed",
                    index=list(NAV.keys()).index(st.session_state.role))
    if role != st.session_state.role:
        st.session_state.role = role
        st.session_state.page = "Dashboard"
        st.rerun()
with top_r:
    st.markdown(f"<div style='text-align:right; color:gray;'>Signed in as <b>{st.session_state.role}</b></div>", unsafe_allow_html=True)

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

    st.markdown("#### Overdue books")
    st.dataframe(OVERDUE, use_container_width=True, hide_index=True)

def dashboard_student():
    st.subheader("Your library")
    c1, c2 = st.columns(2)
    c1.metric("Books borrowed", len(MY_LOANS))
    c2.metric("Fines due", "₹0")

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
    if st.session_state.editing_id is not None:
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
    if st.session_state.confirm_delete_id is not None:
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
    
    users_df = pd.DataFrame([
        {"ID": "USR-101", "Name": "Aravind K.", "Role": "Student", "Status": "Active", "Joined": "Jan 2025"},
        {"ID": "USR-102", "Name": "Priya S.", "Role": "Librarian", "Status": "Active", "Joined": "Mar 2024"},
        {"ID": "USR-103", "Name": "Rahul M.", "Role": "Student", "Status": "Suspended", "Joined": "Feb 2025"},
        {"ID": "USR-104", "Name": "Elena R.", "Role": "Admin", "Status": "Active", "Joined": "Jan 2023"},
    ])
    
    c1, c2 = st.columns([3, 1])
    c1.text_input("Search user...", label_visibility="collapsed", placeholder="Search user...")
    if c2.button("➕ Add User", use_container_width=True):
        st.toast("Add User action initialized.")
        
    st.dataframe(users_df, use_container_width=True, hide_index=True)

def page_reports():
    st.subheader("Analytics & Reports")
    st.caption("System usage metrics and circulation analytics.")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Monthly Circulations")
        chart_data = pd.DataFrame({"Month": ["May", "Jun", "Jul", "Aug"], "Checkouts": [120, 185, 240, 310]})
        fig = px.bar(chart_data, x="Month", y="Checkouts")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.markdown("#### Most Active Categories")
        cat_data = pd.DataFrame({"Category": ["Software Eng", "History", "Fiction", "CS"], "Borrows": [45, 30, 25, 20]})
        fig2 = px.pie(cat_data, names="Category", values="Borrows")
        st.plotly_chart(fig2, use_container_width=True)

def page_settings():
    st.subheader("System Settings")
    st.caption("Configure portal global parameters.")
    st.text_input("Library Name", value="BorrowHub")
    st.number_input("Default Loan Period (Days)", min_value=1, value=14)
    st.number_input("Late Fine Rate (₹ per day)", min_value=0, value=5)
    st.toggle("Enable Automated Email Reminders", value=True)
    if st.button("Save Settings", type="primary"):
        st.toast("Settings updated successfully!")

# ---------------- Librarian Pages ----------------
def page_issue_return():
    st.subheader("Issue / Return Desk")
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
    st.dataframe(members_df, use_container_width=True, hide_index=True)

def page_overdue_fines():
    st.subheader("Overdue & Fines Tracking")
    st.dataframe(OVERDUE, use_container_width=True, hide_index=True)
    if st.button("Send Reminders to Overdue Members"):
        st.toast("Notification emails dispatched!")

# ---------------- Student Pages ----------------
def page_my_books():
    st.subheader("My Borrowed Books")
    st.dataframe(MY_LOANS, use_container_width=True, hide_index=True)
    if st.button("Request Loan Extension"):
        st.toast("Renewal request sent to Librarian.")

def page_profile():
    st.subheader("Student Profile")
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
