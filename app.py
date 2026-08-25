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

# Replace your current st.markdown styling block with this:
st.markdown("""
<style>
/* Adjust container padding so content isn't cut off by top bar */
.block-container {
    padding-top: 3.5rem !important;
    padding-bottom: 2rem !important;
}

/* Add spacing above top elements */
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
    st.markdown("### 📚 Athenaeum")
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

# ---------------- Helper: KPIs ----------------
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

# ---------------- Catalog page ----------------
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

    # Add / edit form
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

def coming_soon(label):
    st.subheader(label)
    st.info("This section isn't wired up in the prototype yet.")

# ---------------- Router ----------------
page = st.session_state.page
role = st.session_state.role

if page == "Dashboard":
    if role == "Admin":
        dashboard_admin()
    elif role == "Librarian":
        dashboard_librarian()
    else:
        dashboard_student()
elif page in ("Catalog", "Browse Catalog"):
    catalog_page(can_manage=(role != "Student"))
else:
    coming_soon(page)
