import streamlit as st
import pandas as pd
from pathlib import Path
from xml.etree import ElementTree as ET
import json
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import re


def detect_file_format(file_path):
    extension = Path(file_path).suffix.lower()
    if extension == '.csv':
        return 'csv'
    elif extension == '.json':
        return 'json'
    elif extension == '.xml':
        return 'xml'
    else:
        return 'unsupported'

def read_csv(file_path):
    return pd.read_csv(file_path)

def read_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def read_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    data = []
    for item in root:
        item_data = {}
        for child in item:
            item_data[child.tag] = child.text
        data.append(item_data)
    return pd.DataFrame(data)

def data_analysis_page(file_path):
    st.title("Data Analysis")

    file_format = detect_file_format(file_path)
    st.write(f"Retrieved file is in {file_format.upper()} format")

    if file_format == 'csv':
        data = read_csv(file_path)
    elif file_format == 'json':
        data = read_json(file_path)
    elif file_format == 'xml':
        data = read_xml(file_path)
    else:
        st.warning("Unsupported file format")

    # Display the retrieved data
    st.write(f"<h2 style='font-size: 35px;'>Retrieved Data : </h2>", unsafe_allow_html=True)
    st.write(data)

    # Display summary statistics
    st.write(f"<h2 style='font-size: 35px;'>Data Summary :</h2>", unsafe_allow_html=True)
    data_summary = data.describe(include='all')
    st.write(data_summary)

    # Display data types
    st.write(f"<h2 style='font-size: 35px;'>Data Types : </h2>", unsafe_allow_html=True)
    data_types = data.dtypes
    st.write(data_types)

    # Initialize session state
    if 'converted_data' not in st.session_state:
        st.session_state.converted_data = data.copy()

    # Select column for analysis
    selected_column = st.selectbox("Select a column for analysis:", data.columns)
    if selected_column:
        try:
            numeric_data = data[selected_column].apply(pd.to_numeric, errors='coerce')
            numeric_data = numeric_data.dropna()  # Remove NaN values
            average = numeric_data.mean()
            total_rows = len(data)
            user_engagement = numeric_data.sum()

            # Create columns for layout
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown('<div class="white-box">', unsafe_allow_html=True)
                st.write(f"<h2 style='font-size: 35px;'>Average {selected_column}</h2>", unsafe_allow_html=True)
                st.write(f"<p style='font-size: 24px;'>{average:.2f}</p>", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with col2:
                st.markdown('<div class="white-box">', unsafe_allow_html=True)
                st.write(f"<h2 style='font-size: 35px;'>Total Number of Rows</h2>", unsafe_allow_html=True)
                st.write(f"<p style='font-size: 24px;'>{total_rows}</p>", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with col3:
                st.markdown('<div class="white-box">', unsafe_allow_html=True)
                st.write(f"<h2 style='font-size: 35px;'>User Engagement</h2>", unsafe_allow_html=True)
                st.write(f"<p style='font-size: 24px;'>Sum of {selected_column}: {user_engagement}</p>", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

        except ValueError:
            st.warning(f"Selected column '{selected_column}' contains non-numeric values.")

    # Convert column data type if you wish to
    # Allow user to select a column for data conversion
    column_to_convert = st.selectbox("Select a column for data conversion:", st.session_state.converted_data.columns)

    # Check if the selected column is already numeric
    if pd.api.types.is_numeric_dtype(st.session_state.converted_data[column_to_convert]):
        st.warning(f"Column '{column_to_convert}' is already numeric. Please select a different column.")
    else:
        # Provide a button to initiate data conversion
        if st.button("Convert to Numeric"):
            # Remove commas from values if the column is not numeric
            st.session_state.converted_data[column_to_convert] = st.session_state.converted_data[
                column_to_convert].str.replace(',', '')

            try:
                # Convert to numeric
                st.session_state.converted_data[column_to_convert] = pd.to_numeric(
                    st.session_state.converted_data[column_to_convert])
                st.success(f"Converted '{column_to_convert}' to numeric.")
            except ValueError:
                st.warning(f"Column '{column_to_convert}' contains non-numeric values.")

    # Display updated data types
    updated_data_types = st.session_state.converted_data.dtypes
    st.write(updated_data_types)
    st.write(st.session_state.converted_data)

    # Histogram of selected column with tooltips using Altair
    # Histogram of selected column with tooltips using Altair
    st.markdown('<div class="white-box">', unsafe_allow_html=True)
    st.write('## Histogram')

    # Select Numeric Column for Histogram
    selected_column_hist = st.selectbox("Select Numeric Column for Histogram", st.session_state.converted_data.columns)

    # Generate histogram
    hist = alt.Chart(st.session_state.converted_data).mark_bar().encode(
        x=alt.X(f'{selected_column_hist}:Q', bin=alt.Bin(maxbins=20), title=f'{selected_column_hist}'),
        y=alt.Y('count():Q', title='Frequency'),
        tooltip=[f'{selected_column_hist}:Q', 'count():Q']
    ).properties(
        width=600,
        height=400,
        title=f'Distribution of {selected_column_hist}'
    )
    st.altair_chart(hist, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Density plot using Altair
    # Density plot using Altair
    st.markdown('<div class="white-box">', unsafe_allow_html=True)
    st.write('## Density Plot')

    # Get a list of available columns for X-axis selection
    available_columns1 = st.session_state.converted_data.columns.tolist()

    # Provide a unique key for the radio button
    selected_column1 = st.radio("Select X-axis Column:", available_columns1, key='density_radio')

    # Create the density plot based on the selected column
    density_chart = alt.Chart(st.session_state.converted_data).mark_area().encode(
        alt.X(f'{selected_column1}:Q', title=selected_column1),  # Use the selected column here
        alt.Y('density:Q', title='Density'),
        alt.Tooltip([f'{selected_column1}:Q', 'density:Q'])
    ).transform_density(
        selected_column1,  # Use the selected column here
        as_=[selected_column1, 'density']
    ).properties(
        width=600,
        height=400,
        title=f'Density Plot of {selected_column1}'
    )
    st.altair_chart(density_chart, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Double bar chart test
    # Create a double bar chart comparing procedure_price and cred_procedure_price for available data
    st.write('## Double Bar Chart: Comparison of Procedure Prices')

    # Get a list of available columns for X and Y axis selection
    available_columns = st.session_state.converted_data.columns.tolist()

    # Create dropdowns for selecting X and Y axes
    selected_x_column = st.selectbox("Select X-axis Column:", available_columns)
    selected_y_column = st.selectbox("Select Y-axis Column:", available_columns)

    if not st.session_state.converted_data.empty:
        chart = alt.Chart(st.session_state.converted_data).mark_bar().encode(
            x=alt.X(f'{selected_x_column}:N', title='Disease'),
            y=alt.Y(f'{selected_y_column}:Q', title='Price (INR)', scale=alt.Scale(domain=(0, 7000000))),
            color=alt.Color('type_of_procedure:N', title='Type of Procedure',
                            scale=alt.Scale(range=['blue', 'orange'])),
            tooltip=[f'{selected_x_column}:N', f'{selected_y_column}:Q', 'type_of_procedure:N']
        ).transform_fold(
            [selected_x_column, selected_y_column],
            as_=['type_of_procedure', 'price']
        ).properties(
            width=600,
            height=400,
            title='Comparison of Procedure Prices by Disease'
        )
        st.markdown('<div class="white-box">', unsafe_allow_html=True)
        st.altair_chart(chart, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.write('No valid data available for comparison.')

    # Separate available and unavailable data
    available_data = data[data['price'].notnull()]
    unavailable_data = data[data['price'].isnull()]

    # Calculate the count of available and unavailable data
    available_count = available_data.shape[0]
    unavailable_count = unavailable_data.shape[0]

    # Create columns for layout
    col1, col2 = st.columns(2)

    # Display the available vs unavailable data using a bar chart
    with col1:
        st.write('## Available vs Unavailable Data')
        # Display count of available and unavailable data
        st.write(f"Available Data Count: {available_count}")
        st.write(f"Unavailable Data Count: {unavailable_count}")
        chart = alt.Chart(pd.DataFrame({'Status': ['Available', 'Unavailable'],
                                        'Count': [len(available_data), len(unavailable_data)]})).mark_bar().encode(
            x='Status:N',
            y='Count:Q',
            color=alt.Color('Status:N', scale=alt.Scale(range=['green', 'red'])),
            tooltip=['Status:N', 'Count:Q']
        )
        st.altair_chart(chart, use_container_width=True)

    # Create a doughnut chart using Plotly
    with col2:
        labels = ['Available', 'Unavailable']
        values = [available_count, unavailable_count]
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.4)])
        st.plotly_chart(fig, use_container_width=True)


# Example usage
file_path = "data_ret.csv"
data_analysis_page(file_path)





