import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def main():
    st.set_page_config(page_title="Pizza Sales Dashboard", page_icon=":pizza:", layout="wide")

    st.title("🍕 Pizza Sales Performance Dashboard")

    # 1. Load Data
    # For Streamlit deployment, ensure the CSV is accessible. Assuming it's in the same directory.
    try:
        df = pd.read_csv('pizza_sales.csv')
    except FileNotFoundError:
        st.error("Error: 'pizza_sales.csv' not found. Please ensure the file is in the correct directory.")
        return

    # 2. Data Preprocessing
    df['order_datetime'] = pd.to_datetime(df['order_date'] + ' ' + df['order_time'], format='mixed', dayfirst=False)
    df['hour'] = df['order_datetime'].dt.hour
    df['day_of_week'] = df['order_datetime'].dt.day_name()

    # Calculate daily sales metrics
    daily_sales = df.groupby('order_date').agg(
        daily_total_revenue=('total_price', 'sum'),
        daily_unique_orders=('order_id', 'nunique')
    ).reset_index()
    daily_sales['daily_average_order_value'] = daily_sales['daily_total_revenue'] / daily_sales['daily_unique_orders']
    daily_sales['order_date'] = pd.to_datetime(daily_sales['order_date'], format='mixed', dayfirst=False)
    daily_sales = daily_sales.sort_values(by='order_date')

    # 3. Calculate Key Sales Metrics
    pizza_name_sales = df.groupby('pizza_name').agg(
        total_revenue=('total_price', 'sum'),
        total_quantity_sold=('quantity', 'sum')
    ).sort_values(by='total_revenue', ascending=False)

    pizza_category_sales = df.groupby('pizza_category').agg(
        total_revenue=('total_price', 'sum'),
        total_quantity_sold=('quantity', 'sum')
    ).sort_values(by='total_revenue', ascending=False)

    pizza_size_sales = df.groupby('pizza_size').agg(
        total_revenue=('total_price', 'sum'),
        total_quantity_sold=('quantity', 'sum')
    ).sort_values(by='total_revenue', ascending=False)

    overall_average_order_value = df.groupby('order_id')['total_price'].sum().mean()

    st.sidebar.header("Dashboard Filters")

    # Total Revenue Over Time
    st.subheader("📈 Total Revenue Over Time")
    min_date = daily_sales['order_date'].min().date()
    max_date = daily_sales['order_date'].max().date()

    start_date, end_date = st.sidebar.date_input(
        "Select date range",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )

    filtered_daily_sales = daily_sales[(daily_sales['order_date'].dt.date >= start_date) &
                                       (daily_sales['order_date'].dt.date <= end_date)]

    fig1, ax1 = plt.subplots(figsize=(12, 6))
    sns.lineplot(x='order_date', y='daily_total_revenue', data=filtered_daily_sales, ax=ax1)
    ax1.set_title('Total Revenue Over Time')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Total Revenue ($)')
    ax1.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig1)

    # Top N Best-Selling Pizzas by Revenue
    st.subheader("🍕 Top N Best-Selling Pizzas by Revenue")
    num_pizzas = st.slider("Select number of top pizzas to display", min_value=1, max_value=len(pizza_name_sales), value=5)

    top_n_pizzas = pizza_name_sales.head(num_pizzas)
    fig2, ax2 = plt.subplots(figsize=(12, 6))
    sns.barplot(x=top_n_pizzas.index, y=top_n_pizzas['total_revenue'], palette='viridis', hue=top_n_pizzas.index, legend=False, ax=ax2)
    ax2.set_title(f'Top {num_pizzas} Best-Selling Pizzas by Revenue')
    ax2.set_xlabel('Pizza Name')
    ax2.set_ylabel('Total Revenue ($)')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(fig2)

    col1, col2 = st.columns(2)
    with col1:
        # Sales Distribution by Pizza Category
        st.subheader("📊 Sales Distribution by Pizza Category")
        fig3, ax3 = plt.subplots(figsize=(10, 6))
        sns.barplot(x=pizza_category_sales.index, y=pizza_category_sales['total_revenue'], palette='magma', hue=pizza_category_sales.index, legend=False, ax=ax3)
        ax3.set_title('Sales Distribution by Pizza Category')
        ax3.set_xlabel('Pizza Category')
        ax3.set_ylabel('Total Revenue ($)')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig3)

    with col2:
        # Sales Distribution by Pizza Size
        st.subheader("📏 Sales Distribution by Pizza Size")
        fig4, ax4 = plt.subplots(figsize=(10, 6))
        sns.barplot(x=pizza_size_sales.index, y=pizza_size_sales['total_revenue'], palette='cividis', hue=pizza_size_sales.index, legend=False, ax=ax4)
        ax4.set_title('Sales Distribution by Pizza Size')
        ax4.set_xlabel('Pizza Size')
        ax4.set_ylabel('Total Revenue ($)')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig4)

    # Summary Report
    st.subheader("📝 Summary Report")
    if st.button('Generate Summary Report'):
        st.write("### Key Insights")
        st.write(f"- **Overall Average Order Value**: ${overall_average_order_value:.2f}")
        st.write(f"- **Highest Revenue Pizza**: '{pizza_name_sales.index[0]}' generated ${pizza_name_sales['total_revenue'].iloc[0]:.2f}")
        st.write(f"- **Most Popular Pizza (by quantity)**: '{pizza_name_sales['total_quantity_sold'].idxmax()}' with {pizza_name_sales['total_quantity_sold'].max():.0f} units sold")
        st.write(f"- **Dominant Pizza Category**: '{pizza_category_sales.index[0]}' with total revenue of ${pizza_category_sales['total_revenue'].iloc[0]:.2f}")
        st.write(f"- **Preferred Pizza Size**: '{pizza_size_sales.index[0]}' with total revenue of ${pizza_size_sales['total_revenue'].iloc[0]:.2f}")

if __name__ == '__main__':
    main()
