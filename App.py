import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px

# ---------------- Database Connection ----------------
def init_connection():
    return psycopg2.connect(
        host="localhost",
        dbname="food_wastage_db",
        user="postgres",
        password="swara",
        port="5432"
    )

conn = init_connection()
cur = conn.cursor()

# ---------------- Load Data ----------------
def load_data(query):
    cur.execute(query)
    rows = cur.fetchall()
    colnames = [desc[0] for desc in cur.description]
    return pd.DataFrame(rows, columns=colnames)

# ---------------- CRUD Functions ----------------
def run_query(query, params=None):
    if params is None:
        cur.execute(query)
    else:
        cur.execute(query, params)
    conn.commit()

def add_provider(name, type_, address, city, contact):
    cur.execute("INSERT INTO providers (name, type, address, city, contact) VALUES (%s,%s,%s,%s,%s)",
                (name, type_, address, city, contact))
    conn.commit()

def update_provider(provider_id, name, type_, address, city, contact):
    cur.execute("""UPDATE providers 
                   SET name=%s, type=%s, address=%s, city=%s, contact=%s 
                   WHERE provider_id=%s""",
                (name, type_, address, city, contact, provider_id))
    conn.commit()

def delete_provider(provider_id):
    cur.execute("DELETE FROM providers WHERE provider_id=%s", (provider_id,))
    conn.commit()

def add_receiver(name, type_, city, contact):
    cur.execute("INSERT INTO receivers (name, type, city, contact) VALUES (%s,%s,%s,%s)",
                (name, type_, city, contact))
    conn.commit()

def update_receiver(receiver_id, name, type_, city, contact):
    cur.execute("""UPDATE receivers 
                   SET name=%s, type=%s, city=%s, contact=%s 
                   WHERE receiver_id=%s""",
                (name, type_, city, contact, receiver_id))
    conn.commit()

def delete_receiver(receiver_id):
    cur.execute("DELETE FROM receivers WHERE receiver_id=%s", (receiver_id,))
    conn.commit()

def add_food_listing(provider_id, food_name, quantity, expiry_date, food_type, meal_type, location):
    cur.execute("""INSERT INTO food_listings 
                   (provider_id, food_name, quantity, expiry_date, food_type, meal_type, location) 
                   VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                (provider_id, food_name, quantity, expiry_date, food_type, meal_type, location))
    conn.commit()

def update_food_listing(food_id, provider_id, food_name, quantity, expiry_date, food_type, meal_type, location):
    cur.execute("""UPDATE food_listings 
                   SET provider_id=%s, food_name=%s, quantity=%s, expiry_date=%s, food_type=%s, meal_type=%s, location=%s
                   WHERE food_id=%s""",
                (provider_id, food_name, quantity, expiry_date, food_type, meal_type, location, food_id))
    conn.commit()

def delete_food_listing(food_id):
    cur.execute("DELETE FROM food_listings WHERE food_id=%s", (food_id,))
    conn.commit()

def add_claim(food_id, receiver_id, claim_date, quantity, status):
    cur.execute("INSERT INTO claims (food_id, receiver_id, claim_date, quantity, status) VALUES (%s,%s,%s,%s,%s)",
                (food_id, receiver_id, claim_date, quantity, status))
    conn.commit()

def update_claim(claim_id, food_id, receiver_id, claim_date, quantity, status):
    cur.execute("""UPDATE claims 
                   SET food_id=%s, receiver_id=%s, claim_date=%s, quantity=%s, status=%s
                   WHERE claim_id=%s""",
                (food_id, receiver_id, claim_date, quantity, status, claim_id))
    conn.commit()

def delete_claim(claim_id):
    cur.execute("DELETE FROM claims WHERE claim_id=%s", (claim_id,))
    conn.commit()
#-----------------------------------------------------------
# ---------------- Predefined Queries ----------------
queries = {
    "1. Providers & Receivers per city": """
        SELECT city, 
               COUNT(DISTINCT provider_id) AS total_providers, 
               COUNT(DISTINCT receiver_id) AS total_receivers
        FROM providers FULL JOIN receivers USING(city)
        GROUP BY city;
    """,
    "2. Top provider types contributing food": """
        SELECT type, COUNT(*) AS total_contributions
        FROM providers
        GROUP BY type
        ORDER BY total_contributions DESC;
    """,
    "3. Contact info of providers by city": """
        SELECT name, city, contact FROM providers ORDER BY city;
    """,
    "4. Receivers with most food claims": """
        SELECT r.name, COUNT(c.claim_id) AS total_claims
        FROM claims c
        JOIN receivers r ON c.receiver_id = r.receiver_id
        GROUP BY r.name
        ORDER BY total_claims DESC;
    """,
    "5. Total food available": """
        SELECT SUM(quantity) AS total_food_quantity FROM food_listings;
    """,
    "6. City with most food listings": """
        SELECT location, COUNT(food_id) AS listings
        FROM food_listings
        GROUP BY location
        ORDER BY listings DESC;
    """,
    "7. Most common food types": """
        SELECT food_type, COUNT(*) AS frequency
        FROM food_listings
        GROUP BY food_type
        ORDER BY frequency DESC;
    """,
    "8. Claims per food item": """
        SELECT f.food_name, COUNT(c.claim_id) AS claim_count
        FROM claims c
        JOIN food_listings f ON c.food_id = f.food_id
        GROUP BY f.food_name;
    """,
    "9. Provider with most successful claims": """
        SELECT p.name, COUNT(c.claim_id) AS successful_claims
        FROM claims c
        JOIN food_listings f ON c.food_id = f.food_id
        JOIN providers p ON f.provider_id = p.provider_id
        WHERE c.status='Completed'
        GROUP BY p.name
        ORDER BY successful_claims DESC;
    """,
    "10. Claim status distribution": """
        SELECT status, COUNT(*) FROM claims GROUP BY status;
    """,
    "11. Avg food claimed per receiver": """
        SELECT r.name, ROUND(AVG(f.quantity),2) AS avg_quantity
        FROM claims c
        JOIN food_listings f ON c.food_id = f.food_id
        JOIN receivers r ON c.receiver_id = r.receiver_id
        GROUP BY r.name;
    """,
    "12. Most claimed meal type": """
        SELECT meal_type, COUNT(*) AS claim_count
        FROM claims c
        JOIN food_listings f ON c.food_id=f.food_id
        GROUP BY meal_type
        ORDER BY claim_count DESC;
    """,
    "13. Total food donated per provider": """
        SELECT p.name, SUM(f.quantity) AS total_donated
        FROM food_listings f
        JOIN providers p ON f.provider_id=p.provider_id
        GROUP BY p.name
        ORDER BY total_donated DESC;
    """,
     "14. Claimed vs Unclaimed Donations": """
        SELECT CASE WHEN c.food_id IS NULL THEN 'Unclaimed' ELSE 'Claimed' END AS claim_status,
               COUNT(*) AS count
        FROM food_listings f
        LEFT JOIN claims c ON f.food_id = c.food_id
        GROUP BY claim_status;
    """,
    "15. Most Common Meal Type by City": """
        SELECT city, meal_type, COUNT(*) AS count
        FROM providers p
        JOIN food_listings f ON p.provider_id = f.provider_id
        GROUP BY city, meal_type
        ORDER BY city, count DESC;
    """,
    "16. Monthly Donation Trends": """
        SELECT TO_CHAR(expiry_date, 'YYYY-MM') AS month, COUNT(*) AS donation_count
        FROM food_listings
        GROUP BY month
        ORDER BY month;
    """,
    "17. Providers Without Donations": """
        SELECT p.name
        FROM providers p
        LEFT JOIN food_listings f ON p.provider_id = f.provider_id
        WHERE f.food_id IS NULL;
    """,
    "18. Location-wise Most Common Food Type": """
        SELECT location, food_type, COUNT(*) AS food_count
        FROM food_listings
        GROUP BY location, food_type
        ORDER BY location, food_count DESC;
    """,
    "19. Top Providers by Unique Food Items Donated": """
        SELECT p.name AS provider_name, COUNT(DISTINCT f.food_name) AS unique_food_items
        FROM providers p
        JOIN food_listings f ON p.provider_id = f.provider_id
        GROUP BY p.name
        ORDER BY unique_food_items DESC;
    """,
    "20. Receiver Cities by Claim Count": """
        SELECT r.city, COUNT(c.claim_id) AS claim_count
        FROM receivers r
        JOIN claims c ON r.receiver_id = c.receiver_id
        GROUP BY r.city
        ORDER BY claim_count DESC;
    """
}


# ---------------- Streamlit UI ----------------
st.set_page_config(page_title="Food Wastage Management", layout="wide")
st.title("🍽️ Local Food Wastage Management System")

menu = ["Dashboard","Main Dashboard", "View Tables", "Add/Update/Delete Data", "Run Queries","EDA & Predictions" ]
choice = st.sidebar.radio("Menu", menu)


# ---------------- Dashboard ----------------
if choice == "Dashboard":
    st.subheader("📊 Food Wastage Insights")
    df_listings = load_data("SELECT * FROM food_listings")
    df_claims = load_data("SELECT * FROM claims")

    # Claimed Quantity = claims join food_listings
    df_claims_qty = load_data("""
        SELECT SUM(f.quantity) AS claimed_qty
        FROM claims c
        JOIN food_listings f ON c.food_id = f.food_id
    """)
    claimed_qty = int(df_claims_qty["claimed_qty"].iloc[0]) if not df_claims_qty.empty else 0

    # --- KPI Metrics ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🍲 Total Listings", len(df_listings))
    with col2:
        st.metric("✅ Total Claims", len(df_claims))
    with col3:
        total_qty = int(df_listings["quantity"].sum()) if not df_listings.empty else 0
        st.metric("📦 Total Food Quantity", total_qty)
    with col4:
        st.metric("🎯 Claimed Quantity", claimed_qty)

    # --- Charts ---
    col1, col2 = st.columns(2)
    with col1:
        if not df_listings.empty and "food_name" in df_listings.columns:
            fig1 = px.bar(df_listings, x="food_name", y="quantity", 
                          title="Available Food Listings")
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("No Food Listings data available.")

    with col2:
        df_claims_chart = load_data("""
            SELECT r.name AS receiver_name, SUM(f.quantity) AS total_claimed
            FROM claims c
            JOIN receivers r ON c.receiver_id = r.receiver_id
            JOIN food_listings f ON c.food_id = f.food_id
            GROUP BY r.name
        """)
        if not df_claims_chart.empty:
            fig2 = px.pie(df_claims_chart, names="receiver_name", values="total_claimed", 
                          title="Food Claimed by Receivers")
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No Claims data available for chart.")


# ----------------Main  Dashboard ----------------
if choice == "Main Dashboard":
    st.subheader("📊 Food Wastage Insights")

    # Sidebar Filters
    locations = load_data("SELECT DISTINCT location FROM food_listings")["location"].dropna().tolist()
    providers = load_data("SELECT DISTINCT provider_id FROM food_listings")["provider_id"].dropna().tolist()
    food_types = load_data("SELECT DISTINCT food_type FROM food_listings")["food_type"].dropna().tolist()
    meal_types = load_data("SELECT DISTINCT meal_type FROM food_listings")["meal_type"].dropna().tolist()

    location_filter = st.sidebar.multiselect("Filter by Location", locations)
    provider_filter = st.sidebar.multiselect("Filter by Provider", providers)
    food_filter = st.sidebar.multiselect("Filter by Food Type", food_types)
    meal_filter = st.sidebar.multiselect("Filter by Meal Type", meal_types)

    query = "SELECT * FROM food_listings WHERE 1=1"
    if location_filter:
        query += f" AND location IN ({','.join(['%s']*len(location_filter))})"
    if provider_filter:
        query += f" AND provider_id IN ({','.join(['%s']*len(provider_filter))})"
    if food_filter:
        query += f" AND food_type IN ({','.join(['%s']*len(food_filter))})"
    if meal_filter:
        query += f" AND meal_type IN ({','.join(['%s']*len(meal_filter))})"

    cur.execute(query, tuple(location_filter + provider_filter + food_filter + meal_filter))
    rows = cur.fetchall()
    df_listings = pd.DataFrame(rows, columns=[desc[0] for desc in cur.description])

    st.dataframe(df_listings)

    if not df_listings.empty:
        fig = px.bar(df_listings, x="food_name", y="quantity", color="food_type", title="Food Listings Overview")
        st.plotly_chart(fig, use_container_width=True)

# # ---------------- Add / Update / Delete Data ----------------
# elif choice == "Add/Update/Delete Data":
#     st.subheader("➕ Manage Records")

#     tab1, tab2, tab3, tab4 = st.tabs(["Providers", "Receivers", "Food Listings", "Claims"])

#     with tab1:
#         st.write("Add / Update / Delete Providers")
#         # Add Provider
#         with st.expander("➕ Add Provider"):
#             name = st.text_input("Name")
#             type_ = st.text_input("Type")
#             address = st.text_input("Address")
#             city = st.text_input("City")
#             contact = st.text_input("Contact")
#             if st.button("Add Provider"):
#                 add_provider(name, type_, address, city, contact)
#                 st.success("Provider Added ✅")
#         # Update/Delete
#         df = load_data("SELECT * FROM providers")
#         st.dataframe(df)

#     # (Similarly add Update/Delete forms for Receivers, Food Listings, Claims ...)

# ---------------- Add / Update / Delete Data ----------------
elif choice == "Add/Update/Delete Data":
    st.subheader("➕ Manage Records")

    tab1, tab2, tab3, tab4 = st.tabs(["Providers", "Receivers", "Food Listings", "Claims"])

    # ---------------- Providers ----------------
    with tab1:
        st.write("Add / Update / Delete Providers")

        # Add Provider
        with st.expander("➕ Add Provider"):
            name = st.text_input("Provider Name")
            type_ = st.text_input("Provider Type")
            address = st.text_input("Provider Address")
            city = st.text_input("Provider City")
            contact = st.text_input("Provider Contact")
            if st.button("Add Provider"):
                add_provider(name, type_, address, city, contact)
                st.success("✅ Provider Added")

        # Update Provider
        with st.expander("✏️ Update Provider"):
            pid = st.number_input("Provider ID", min_value=1, step=1)
            new_city = st.text_input("New City")
            if st.button("Update Provider"):
                run_query("UPDATE providers SET city=%s WHERE provider_id=%s", (new_city, pid))
                st.success("✅ Provider Updated")

        # Delete Provider
        with st.expander("🗑️ Delete Provider"):
            pid_del = st.number_input("Delete Provider ID", min_value=1, step=1)
            if st.button("Delete Provider"):
                run_query("DELETE FROM providers WHERE provider_id=%s", (pid_del,))
                st.success("✅ Provider Deleted")

        df = load_data("SELECT * FROM providers")
        st.dataframe(df)

    # ---------------- Receivers ----------------
    with tab2:
        st.write("Add / Update / Delete Receivers")

        # Add Receiver
        with st.expander("➕ Add Receiver"):
            rname = st.text_input("Receiver Name")
            rtype = st.text_input("Receiver Type")
            rcity = st.text_input("Receiver City")
            rcontact = st.text_input("Receiver Contact")
            if st.button("Add Receiver"):
                run_query("INSERT INTO receivers (name, type, city, contact) VALUES (%s,%s,%s,%s)",
                          (rname, rtype, rcity, rcontact))
                st.success("✅ Receiver Added")

        # Update Receiver
        with st.expander("✏️ Update Receiver"):
            rid = st.number_input("Receiver ID", min_value=1, step=1)
            new_city = st.text_input("New City (Receiver)")
            if st.button("Update Receiver"):
                run_query("UPDATE receivers SET city=%s WHERE receiver_id=%s", (new_city, rid))
                st.success("✅ Receiver Updated")

        # Delete Receiver
        with st.expander("🗑️ Delete Receiver"):
            rid_del = st.number_input("Delete Receiver ID", min_value=1, step=1)
            if st.button("Delete Receiver"):
                run_query("DELETE FROM receivers WHERE receiver_id=%s", (rid_del,))
                st.success("✅ Receiver Deleted")

        df = load_data("SELECT * FROM receivers")
        st.dataframe(df)

    # ---------------- Food Listings ----------------
    with tab3:
        st.write("Add / Update / Delete Food Listings")

        # Add Food Listing
        with st.expander("➕ Add Food Listing"):
            pid = st.number_input("Provider ID (FK)", min_value=1, step=1)
            food_name = st.text_input("Food Name")
            qty = st.number_input("Quantity", min_value=1, step=1)
            expiry = st.date_input("Expiry Date")
            if st.button("Add Food Listing"):
                run_query("INSERT INTO food_listings (provider_id, food_name, quantity, expiry_date) VALUES (%s,%s,%s,%s)",
                          (pid, food_name, qty, expiry))
                st.success("✅ Food Listing Added")

        # Update Food Listing
        with st.expander("✏️ Update Food Listing"):
            fid = st.number_input("Food ID", min_value=1, step=1)
            new_qty = st.number_input("New Quantity", min_value=1, step=1)
            if st.button("Update Food Listing"):
                run_query("UPDATE food_listings SET quantity=%s WHERE food_id=%s", (new_qty, fid))
                st.success("✅ Food Listing Updated")

        # Delete Food Listing
        with st.expander("🗑️ Delete Food Listing"):
            fid_del = st.number_input("Delete Food ID", min_value=1, step=1)
            if st.button("Delete Food Listing"):
                run_query("DELETE FROM food_listings WHERE food_id=%s", (fid_del,))
                st.success("✅ Food Listing Deleted")

        df = load_data("SELECT * FROM food_listings")
        st.dataframe(df)

    # ---------------- Claims ----------------
    with tab4:
        st.write("Add / Update / Delete Claims")

        # Add Claim
        with st.expander("➕ Add Claim"):
            fid = st.number_input("Food ID (FK)", min_value=1, step=1)
            rid = st.number_input("Receiver ID (FK)", min_value=1, step=1)
            status = st.selectbox("Status", ["Pending", "Completed", "Cancelled"])
            if st.button("Add Claim"):
                run_query("INSERT INTO claims (food_id, receiver_id, status, timestamp) VALUES (%s,%s,%s,NOW())",
                          (fid, rid, status))
                st.success("✅ Claim Added")

        # Update Claim
        with st.expander("✏️ Update Claim"):
            cid = st.number_input("Claim ID", min_value=1, step=1)
            new_status = st.selectbox("New Status", ["Pending", "Completed", "Cancelled"])
            if st.button("Update Claim"):
                run_query("UPDATE claims SET status=%s WHERE claim_id=%s", (new_status, cid))
                st.success("✅ Claim Updated")

        # Delete Claim
        with st.expander("🗑️ Delete Claim"):
            cid_del = st.number_input("Delete Claim ID", min_value=1, step=1)
            if st.button("Delete Claim"):
                run_query("DELETE FROM claims WHERE claim_id=%s", (cid_del,))
                st.success("✅ Claim Deleted")

        df = load_data("SELECT * FROM claims")
        st.dataframe(df)



# ---------------- View Tables ----------------
elif choice == "View Tables":
    st.subheader("📋 Database Tables")
    table = st.selectbox("Select Table", ["providers", "receivers", "food_listings", "claims"], key="view_table")
    df = load_data(f"SELECT * FROM {table}")
    st.dataframe(df)

# ---------------- Add Data ----------------
elif choice == "Add Data":
    st.subheader("➕ Insert Records")

    tab1, tab2, tab3, tab4 = st.tabs(["Provider", "Receiver", "Food Listing", "Claim"])

    with tab1:
        name = st.text_input("Provider Name", key="prov_name")
        type_ = st.text_input("Provider Type", key="prov_type")
        address = st.text_input("Provider Address", key="prov_address")
        city = st.text_input("Provider City", key="prov_city")
        contact = st.text_input("Provider Contact", key="prov_contact")
        if st.button("Add Provider", key="add_prov"):
            add_provider(name, type_, address, city, contact)
            st.success("✅ Provider Added")

    with tab2:
        name = st.text_input("Receiver Name", key="recv_name")
        type_ = st.text_input("Receiver Type", key="recv_type")
        city = st.text_input("Receiver City", key="recv_city")
        contact = st.text_input("Receiver Contact", key="recv_contact")
        if st.button("Add Receiver", key="add_recv"):
            add_receiver(name, type_, city, contact)
            st.success("✅ Receiver Added")

    with tab3:
        provider_id = st.number_input("Provider ID", key="food_provider", step=1)
        food_name = st.text_input("Food Name", key="food_name")
        quantity = st.number_input("Quantity", key="food_qty", step=1)
        expiry_date = st.date_input("Expiry Date", key="food_exp")
        if st.button("Add Food Listing", key="add_food"):
            add_food_listing(provider_id, food_name, quantity, expiry_date)
            st.success("✅ Food Listing Added")

    with tab4:
        food_id = st.number_input("Food ID", key="claim_food", step=1)
        receiver_id = st.number_input("Receiver ID", key="claim_recv", step=1)
        claim_date = st.date_input("Claim Date", key="claim_date")
        quantity = st.number_input("Quantity", key="claim_qty", step=1)
        if st.button("Add Claim", key="add_claim"):
            add_claim(food_id, receiver_id, claim_date, quantity)
            st.success("✅ Claim Added")

# ---------------- Run Queries ----------------
elif choice == "Run Queries":
    st.subheader("📝 Predefined & Custom Queries")

    # Predefined queries dropdown
    query_name = st.selectbox("Choose a predefined query", list(queries.keys()))
    if st.button("Run Selected Query", key="run_predefined"):
        try:
            df = load_data(queries[query_name])
            st.dataframe(df)
            if not df.empty:
                st.bar_chart(df.select_dtypes(include=['int64', 'float64']))
        except Exception as e:
            st.error(f"❌ Error: {e}")

    st.markdown("---")
    st.subheader("🔎 Custom SQL Query")
    query = st.text_area("Enter SQL Query", key="custom_sql")
    if st.button("Run Custom", key="run_sql"):
        try:
            df = load_data(query)
            st.dataframe(df)
        except Exception as e:
            st.error(f"❌ Error: {e}")



# ---------------- EDA & Predictions ----------------
elif choice == "EDA & Predictions":
    st.subheader("🔎 EDA (Exploratory Data Analysis) & 🔮 Predictions")

    # --- Filters (sidebar) ---
    st.sidebar.markdown("### Filters (EDA)")
    # City list (from providers)
    try:
        df_cities = load_data("SELECT DISTINCT city FROM providers WHERE city IS NOT NULL ORDER BY city")
        cities = ["All"] + df_cities["city"].dropna().astype(str).tolist()
    except Exception:
        cities = ["All"]

    city_filter = st.sidebar.selectbox("City", options=cities, index=0)

    # Food listings with join (to get city)
    df_listings = load_data("""
        SELECT f.food_id, f.provider_id, f.food_name, f.quantity, f.expiry_date,
               COALESCE(p.city, 'Unknown') AS city
        FROM food_listings f
        LEFT JOIN providers p ON f.provider_id = p.provider_id
        ORDER BY f.food_id DESC
    """)

    # Claims with join (for status analysis)
    try:
        df_claims = load_data("""
            SELECT c.claim_id, c.food_id, c.receiver_id, c.status, c.timestamp,
                   f.food_name, f.quantity, f.expiry_date,
                   COALESCE(p.city, 'Unknown') AS city
            FROM claims c
            LEFT JOIN food_listings f ON c.food_id = f.food_id
            LEFT JOIN providers p ON f.provider_id = p.provider_id
            ORDER BY c.claim_id DESC
        """)
    except Exception:
        df_claims = pd.DataFrame()

    # Apply city filter
    if city_filter != "All" and not df_listings.empty:
        df_listings = df_listings[df_listings["city"] == city_filter]
    if city_filter != "All" and not df_claims.empty:
        df_claims = df_claims[df_claims["city"] == city_filter]

    # --- KPIs ---
    c1, c2, c3, c4 = st.columns(4)
    total_items = int(df_listings["quantity"].sum()) if not df_listings.empty else 0
    total_listings = len(df_listings)
    total_claims = len(df_claims)
    completed_claims = int((df_claims["status"].str.lower() == "completed").sum()) if "status" in df_claims else 0

    c1.metric("📦 Total Quantity", total_items)
    c2.metric("🧾 Listings", total_listings)
    c3.metric("✅ Claims", total_claims)
    c4.metric("🏁 Completed", completed_claims)

    st.markdown("---")

    # --- EDA Charts ---
    colA, colB = st.columns(2)

    # 1) Top Foods by Quantity
    with colA:
        if not df_listings.empty:
            top_foods = (df_listings.groupby("food_name", dropna=False)["quantity"]
                         .sum().reset_index().sort_values("quantity", ascending=False).head(10))
            fig = px.bar(top_foods, x="food_name", y="quantity",
                         title="🍽️ Top Foods by Quantity", text="quantity")
            fig.update_layout(xaxis_title="", yaxis_title="Qty")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No listings available for this filter.")

    # 2) Listings by City
    with colB:
        if not df_listings.empty:
            by_city = (df_listings.groupby("city")["food_id"].count()
                       .reset_index().rename(columns={"food_id": "listings"})
                       .sort_values("listings", ascending=False))
            fig = px.bar(by_city, x="city", y="listings", title="🏙️ Listings by City", text="listings")
            fig.update_layout(xaxis_title="", yaxis_title="Listings")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No city data found.")

    # 3) Expiry Calendar (near-expiry focus)
    st.markdown("#### ⏳ Near-Expiry Items (next 7 days)")
    if not df_listings.empty and "expiry_date" in df_listings:
        df_listings["expiry_date"] = pd.to_datetime(df_listings["expiry_date"], errors="coerce")
        today = pd.Timestamp.today().normalize()
        soon = df_listings[(df_listings["expiry_date"] >= today) & (df_listings["expiry_date"] <= today + pd.Timedelta(days=7))]
        if not soon.empty:
            soon = soon.assign(days_left=(soon["expiry_date"] - today).dt.days)
            fig = px.scatter(soon, x="expiry_date", y="quantity", size="quantity",
                             hover_data=["food_name", "city", "provider_id", "days_left"],
                             title="Next 7 Days Expiries (bubble ~ quantity)")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(soon.sort_values(["days_left", "quantity"], ascending=[True, False]))
        else:
            st.info("No items expiring in next 7 days.")
    else:
        st.info("Expiry data not available.")

    # 4) Claims Status Pie
    st.markdown("#### 🥧 Claims Status Distribution")
    if not df_claims.empty and "status" in df_claims:
        pie = df_claims["status"].value_counts().reset_index()
        pie.columns = ["status", "count"]
        fig = px.pie(pie, names="status", values="count", title="Claims Status")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No claims data available.")

    st.markdown("---")

    # --- Simple Predictions / Risk Scoring ---
    st.subheader("🔮 Predictions & Smart Alerts")

    # A) High Waste Risk (heuristic): High qty & fewer days to expiry
    risk_df = df_listings.copy()
    if not risk_df.empty and "expiry_date" in risk_df:
        risk_df["expiry_date"] = pd.to_datetime(risk_df["expiry_date"], errors="coerce")
        today = pd.Timestamp.today().normalize()
        risk_df["days_to_expiry"] = (risk_df["expiry_date"] - today).dt.days
        # normalize quantity (avoid division by zero)
        qmax = max(1, risk_df["quantity"].max())
        risk_df["q_norm"] = risk_df["quantity"] / qmax
        # Risk score: higher if quantity large & expiry near
        risk_df["risk_score"] = (risk_df["q_norm"] * (1 / (risk_df["days_to_expiry"].clip(lower=1)))).round(3)
        alerts = risk_df.sort_values("risk_score", ascending=False).head(10)

        st.markdown("**🚨 High Waste Risk Items (Top 10)**")
        st.dataframe(alerts[["food_id", "food_name", "city", "quantity", "expiry_date", "days_to_expiry", "risk_score"]])

        fig = px.bar(alerts, x="food_name", y="risk_score", hover_data=["quantity", "expiry_date", "city"],
                     title="High Waste Risk Score")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Risk scoring requires valid expiry dates.")

    # B) Monthly Donations Trend + naive forecast (last 3-month avg)
    st.markdown("#### 📈 Monthly Donation Trend & Naive Forecast")
    if not df_listings.empty and "expiry_date" in df_listings:
        temp = df_listings.dropna(subset=["expiry_date"]).copy()
        temp["expiry_date"] = pd.to_datetime(temp["expiry_date"], errors="coerce")
        temp["month"] = temp["expiry_date"].dt.to_period("M").astype(str)
        trend = temp.groupby("month")["food_id"].count().reset_index().rename(columns={"food_id": "donations"})
        trend = trend.sort_values("month")

        if not trend.empty:
            fig = px.line(trend, x="month", y="donations", markers=True, title="Monthly Donations")
            st.plotly_chart(fig, use_container_width=True)

            # naive 1-step forecast = last 3 months mean
            last3 = trend["donations"].tail(3)
            if len(last3) > 0:
                forecast_val = int(round(last3.mean()))
                st.success(f"🔮 Next-month naive forecast (avg last 3 months): **{forecast_val} donations**")
        else:
            st.info("Not enough data for monthly trend.")
    else:
        st.info("Cannot compute monthly trend without expiry dates.")

    st.markdown("---")

    # --- Contact Helpers (quick actions) ---
    st.subheader("📞 Quick Contacts")
    st.caption("Providers & Receivers contact details for coordination")

    try:
        df_prov_contact = load_data("SELECT provider_id, name, city, contact FROM providers ORDER BY city, name")
        st.write("**Providers**")
        st.dataframe(df_prov_contact)
    except Exception:
        st.info("Providers table not accessible.")

    try:
        df_recv_contact = load_data("SELECT receiver_id, name, city, contact FROM receivers ORDER BY city, name")
        st.write("**Receivers**")
        st.dataframe(df_recv_contact)
    except Exception:
        st.info("Receivers table not accessible.")
