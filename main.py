import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(page_title="Cafe BI Dashboard", layout="wide")

st.title("☕ Cafe Sales Analytics Platform")

# =============================
# DB CONNECTION
# =============================
@st.cache_resource
def get_conn():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="12345",
        database="cafe_analytics"
    )

conn = get_conn()

@st.cache_data
def load_data(query):
    return pd.read_sql(query, conn)

customers = load_data("SELECT * FROM clean_customers")
offers = load_data("SELECT * FROM clean_offers")
events = load_data("SELECT * FROM clean_events")

# =============================
# MAIN MENU (YOUR STYLE)
# =============================
menu = st.sidebar.radio(
    "Main Menu",
    ["📊 Project Insights", "👤 Customer View", "🎯 Offer Analytics", "ℹ️ About"]
)

# =============================
# 📊 PROJECT INSIGHTS (OVERVIEW)
# =============================
if menu == "📊 Project Insights":

 
    st.subheader("📊 Executive Business Overview")

    # =============================
    # 1. KPI CARDS (EXECUTIVE LEVEL)
    # =============================
    total_customers = len(customers)
    total_events = len(events)
    total_offers = len(offers)

    offer_completed = events[events["event"] == "offer completed"].shape[0]
    offer_viewed = events[events["event"] == "offer viewed"].shape[0]
    offer_received = events[events["event"] == "offer received"].shape[0]

    col1, col2, col3 = st.columns(3)

    col1.metric("👤 Customers", total_customers)
    col2.metric("📊 Events", total_events)
    col3.metric("🎯 Offers", total_offers)

    st.divider()

    # =============================
    # 2. OFFER FUNNEL (MOST IMPORTANT)
    # =============================
    st.subheader("🔁 Offer Funnel (Customer Journey)")

    funnel_data = pd.DataFrame({
        "stage": ["Received", "Viewed", "Completed"],
        "count": [offer_received, offer_viewed, offer_completed]
    })

    fig1 = px.funnel(funnel_data, x="count", y="stage")
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("""
    **Business Insight:**
    - Shows drop-off between stages
    - Helps identify weak conversion points
    - Key metric for marketing effectiveness
    """)

    st.divider()

    # =============================
    # 3. EVENT DISTRIBUTION
    # =============================
    st.subheader("📊 Customer Event Behavior")

    event_dist = events["event"].value_counts().reset_index()
    event_dist.columns = ["event", "count"]

    fig2 = px.bar(
        event_dist,
        x="event",
        y="count",
        color="event",
        text="count"
    )

    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("""
    **Business Insight:**
    - Shows engagement distribution
    - High “received” but low “completed” = weak offer performance
    - Helps optimize campaign strategy
    """)

    st.divider()

    # =============================
    # 4. CUSTOMER ENGAGEMENT SCORE
    # =============================
    st.subheader("👤 Customer Engagement Distribution")

    engagement = events.groupby("customer_id").size().reset_index(name="activity")

    fig3 = px.histogram(
        engagement,
        x="activity",
        nbins=30,
        color_discrete_sequence=["#00CC96"]
    )

    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("""
    **Business Insight:**
    - Most customers have low engagement
    - Small group drives majority of activity
    - Useful for loyalty targeting strategy
    """)

    st.divider()

    # =============================
    # 5. TOP INSIGHTS SUMMARY
    # =============================
    st.subheader("🧠 Key Business Insights")

    st.markdown("""
    ### 🎯 Core Findings:

    - Large gap exists between **offer received vs completed**
    - Customer engagement is **highly skewed (power users)**
    - Most value comes from **small active customer segment**
    - Offers need optimization to improve conversion rate

    ### 📌 Business Actions:
    - Improve offer design to reduce drop-off
    - Target high-engagement customers for retention
    - Personalize offers based on behavior
    """)

# =============================
# 👤 CUSTOMER VIEW
# =============================
elif menu == "👤 Customer View":

  
    st.subheader("👤 Customer Intelligence Dashboard")

    # =============================
    # 1. AGE DISTRIBUTION
    # =============================
    st.markdown("### 🎂 Age Distribution")

    fig1 = px.histogram(
        customers,
        x="age",
        nbins=30,
        color_discrete_sequence=["#636EFA"]
    )
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("""
    **Insight:**
    - Most customers are concentrated in middle-age group
    - Helps target promotions for dominant age segment
    """)

    st.divider()

    # =============================
    # 2. GENDER vs AGE
    # =============================
    st.markdown("### ⚧ Gender vs Age Analysis")

    fig2 = px.box(
        customers,
        x="gender",
        y="age",
        color="gender"
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("""
    **Insight:**
    - Age distribution is similar across genders
    - Slight variation in median age between groups
    - Useful for gender-specific marketing strategies
    """)

    st.divider()

    # =============================
    # 3. AGE vs INCOME
    # =============================
    st.markdown("### 📈 Age vs Income Relationship")

    fig3 = px.scatter(
        customers,
        x="age",
        y="income",
        color="gender",
        opacity=0.6
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("""
    **Insight:**
    - Income generally increases with age up to a point
    - High-income segment is concentrated in mid-age group
    - Valuable for premium offer targeting
    """)

    st.divider()

    # =============================
    # 4. GENDER vs INCOME
    # =============================
    st.markdown("### 💰 Gender vs Income Analysis")

    gender_income = customers.groupby("gender")["income"].mean().reset_index()

    fig4 = px.bar(
        gender_income,
        x="gender",
        y="income",
        color="gender"
    )
    st.plotly_chart(fig4, use_container_width=True)

    st.markdown("""
    **Insight:**
    - Average income differs across gender segments
    - Helps in personalized pricing or targeting strategies
    - Useful for campaign segmentation
    """)

    st.divider()

    # =============================
    # SUMMARY INSIGHTS
    # =============================
    st.markdown("### 🧠 Customer Summary Insights")

    st.markdown("""
    - Majority of customers fall in a specific age range → ideal target group
    - Gender differences exist in income behavior
    - Age strongly influences purchasing power
    - These patterns help design targeted marketing campaigns
    """)
# =============================
# 🎯 OFFER ANALYTICS
# =============================
elif menu == "🎯 Offer Analytics":

    st.subheader("🎯 Offer Performance Intelligence")

    # =============================
    # 1. OFFER TYPE ANALYSIS
    # =============================
    st.markdown("### 📦 Offer Type Performance")

    offer_type_perf = events.merge(offers, on="offer_id", how="left")

    offer_type_count = offer_type_perf["offer_type"].value_counts().reset_index()
    offer_type_count.columns = ["offer_type", "count"]

    fig1 = px.bar(
        offer_type_count,
        x="offer_type",
        y="count",
        color="offer_type",
        title="Usage by Offer Type"
    )
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("""
    **Insight:**
    - Shows which type of offers (e.g., discount, buy-one-get-one) are most engaging
    """)

    st.divider()

    # =============================
    # 2. REWARD ANALYSIS
    # =============================
    st.markdown("### 💰 Reward Impact Analysis")

    reward_perf = offer_type_perf.groupby("reward").size().reset_index(name="usage")

    fig2 = px.line(
        reward_perf,
        x="reward",
        y="usage",
        markers=True,
        title="Reward vs Engagement"
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("""
    **Insight:**
    - Helps identify whether higher rewards lead to higher engagement
    - Useful for optimizing marketing cost vs conversion
    """)

    st.divider()

    # =============================
    # 3. CHANNEL ANALYSIS
    # =============================
    st.markdown("### 📡 Channel Effectiveness")

    channel_df = offers.copy()

    # explode channels
    channel_df["channels"] = channel_df["channels"].apply(
        lambda x: eval(x) if isinstance(x, str) else x
    )

    channel_exploded = channel_df.explode("channels")

    channel_perf = channel_exploded.merge(events, on="offer_id", how="left")

    channel_count = channel_perf["channels"].value_counts().reset_index()
    channel_count.columns = ["channel", "count"]

    fig3 = px.pie(
        channel_count,
        names="channel",
        values="count",
        title="Engagement by Channel"
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("""
    **Insight:**
    - Shows which marketing channels (email, mobile, social, web) perform best
    - Helps optimize campaign distribution strategy
    """)

    st.divider()

    # =============================
    # SUMMARY INSIGHTS
    # =============================
    st.markdown("### 🧠 Key Business Insights")

    st.markdown("""
    - Certain **offer types dominate user engagement**
    - **Reward levels influence completion behavior**
    - Some **channels outperform others significantly**
    - Optimization can reduce marketing cost while increasing conversions
    """)

# =============================
# ℹ️ ABOUT
# =============================
elif menu == "ℹ️ About":

    st.subheader("ℹ️ About This Project")

    st.markdown("""
    ### ☕ Cafe Sales Analytics Platform

    This dashboard analyzes:
    - Customer demographics
    - Offer performance
    - Customer engagement behavior

    ### 🧠 Architecture
    clean_customers → clean_events → clean_offers → Streamlit BI Layer

    ### ⚙️ Tech Stack
    - Python
    - Streamlit
    - MySQL
    - Plotly
    - Pandas
    """)
    # -----------------------------------------------------------
    # Author Section
    # -----------------------------------------------------------
    st.markdown("## 👨‍💻 About the Author")

    st.markdown("""
    **Name:** *Keerthana🎓*  
    **Profile:** Data Science Enthusiast  
    
    """)

    # Social Links Section
    st.subheader("🔗 Connect with Me")
    st.write("""
    **Keerthana| Data Science Enthusiast 🎓**   
    **GitHub:** [Checkout the link here](https://github.com/Keerthana-Mathaiyan?tab=repositories)  
    **LinkedIn:** [Click here](https://www.linkedin.com/in/keerthana-mathaiyan/)  
    """)

    # -----------------------------------------------------------
    # License Section
    # -----------------------------------------------------------

    st.markdown("## 📄 License")
    st.markdown("""
    This project is developed for **educational and research purposes only**.  
    """)
    
    st.success("Thank you for exploring this project!")
