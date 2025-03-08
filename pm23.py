import streamlit as st
import os
import numpy as np
import pandas as pd
import plotly.express as px

# Configure page
st.set_page_config(page_title="Marketing Mix Modelling Dashboard", 
        layout="wide", page_icon = "assets/logo1.svg")

# Create two columns: one for the logo, one for the title
logo_col, title_col = st.columns([1.5, 6])

with logo_col:
    # Adjust width as needed
    st.write("")
    st.image("logo2.png") 

with title_col:
    #st.write("### Marketing Mix Modelling Dashboard")
    st.markdown("""<h3 style="font-size: 38px; margin-top: 0px;"> Marketing Mix Modelling Dashboard </h3>""", unsafe_allow_html=True)
    
# Inject custom CSS for frontend formatting
st.markdown(f"""
        <style>
        /* Remove all margins and padding from the main container */
        .block-container {{
            padding-top: 0px !important;
            margin-top: 0px !important;
            padding-left: 50px !important;
            padding-right: 50px !important;
        }}
        /* Hide Streamlit header */
        header {{visibility: hidden;}}
        /* Hide Streamlit footer */
        footer {{visibility: hidden;}}
        /* Hide Streamlit hamburger menu */
        .stDeployButton, .st-emotion-cache-1avcm0n, .st-emotion-cache-16idsys {{
            display: none !important;
        }}
        </style>
    """
, unsafe_allow_html=True)

st.markdown("<hr style='border:1px solid red'>", unsafe_allow_html=True)

# Tutaj dodajemy źródła
demo_data = pd.read_excel('demo_data.xlsx')
demo_data1 = pd.read_excel('demo_data1.xlsx')
demo_data2 = pd.read_excel('demo_data2.xlsx')

# tutaj wykonujemy obliczenia do wykresów


st.markdown(
    """
    <h4 style="font-size: 20px; margin-bottom: -20px;"> Data Selection </h4>
    """, unsafe_allow_html=True
)

data_sel_col1, data_sel_col2, data_sel_col3, data_sel_col4 = st.columns([2,2,2,2])

with data_sel_col1:
    start_date = st.selectbox("Start Date", demo_data['days_period'].unique(), format_func=lambda x: x.strftime('%Y-%m-%d'), key="start_date")
    end_date = st.selectbox("End Date", demo_data['days_period'].unique(), format_func=lambda x: x.strftime('%Y-%m-%d'), key="end_date")
with data_sel_col2:
    market_selection = st.selectbox("Market_selection", demo_data['market_selection'].unique(), key="market_selection")
with data_sel_col3:
    car_serie = st.selectbox("Car series", demo_data['car_serie'].unique(), key="car_serie")
with data_sel_col4:
    group_by = st.selectbox("Group by", ["Quarter", "Month", "Week"])
       
st.markdown(
    """
    <h4 style="font-size: 20px; margin-bottom: -20px;"> Target Parameter - Work in Progress </h4>
    """, unsafe_allow_html=True
)
st.markdown("<hr style='border:1px solid grey'>", unsafe_allow_html=True)
target_col1, target_col2, target_col3, target_col4 = st.columns([2,2,2,2])

with target_col1:
    st.text_input("Marketing budget", "80,000,000 €")
with target_col2:
    weight_col1, weight_col2 = st.columns([2,2])
    with weight_col1:
        st.selectbox("Weighting", ["Display", "Display x2"], index=1)
    with weight_col2:    
        st.selectbox(" ", ["Social", "Social x2"])                 
with target_col3:
    st.selectbox("Target", ["Customers", "Opportunities", "Leads"])                
with target_col4:   
    pass

scenarios = ["Scenario 1", "Scenario 2", "Scenario 3"]
tab1, tab2, tab3 = st.tabs(scenarios)

with tab1: # Scenario 1 layout
    st.markdown( """<h4 style="font-size: 20px; margin-bottom: -20px;"> Leads </h4>""", unsafe_allow_html=True)      
    selected_columns = demo_data[['Tot_sale', 'Baseline', 'TV', 'Display', 'Social', 'SEA']]
    cont_factors = {}
    for column in selected_columns:
        cont_factors[column] = demo_data[column].sum()
        
    result_factors = {}
    for column in ['Baseline', 'TV', 'Display', 'Social', 'SEA']:
        result_factors[column] = round((cont_factors[column] / cont_factors['Tot_sale']) * 100, 2)

    sales_cont = {}
    sales_cont['Baseline'] = result_factors['Baseline']
    sales_cont['All channels'] = sum(result_factors[key] for key in result_factors if key != 'Baseline')
    selected_car_price = demo_data['Car_Price']
    multiplied_columns = selected_columns.mul(selected_car_price, axis=0)
    sum_multiplied_columns = multiplied_columns.sum()
    total_sum = sum_multiplied_columns.sum()
    total_spend = demo_data['Spend'].sum()
    ROI = (total_sum / total_spend)/100
    
    stat_col, summarizer_col, funnel_col = st.columns([1,2,2])
        
        # Part for overall statistics
    with stat_col:
        st.write("**Actual:** 69.0 M")  
        st.write("**Expected:** 74.0 M")  
        st.write("Difference: +5 M") 
            
        spend_col, roi_col = st.columns([2,2])     
        with spend_col:
            st.markdown(
                """<h4 style="font-size: 20px; margin-bottom: -20px;"> Spend </h4>""", unsafe_allow_html=True
            ) 
            formatted_total_spend = f"€{total_spend:,.2f}"
            st.write(formatted_total_spend)
        with roi_col:
            st.markdown(
                """<h4 style="font-size: 20px; margin-bottom: -20px;"> ROI </h4>""", unsafe_allow_html=True
            )    
            formatted_ROI = round(ROI, 2)
            st.write(formatted_ROI)
                        
        st.markdown(
            """<h4 style="font-size: 20px; margin-bottom: -20px;"> Sales contribution</h4>""", unsafe_allow_html=True
        )
        st.write(f"Baseline: {sales_cont['Baseline']} %")
        st.write(f"All channels: {sales_cont['All channels']} %")

    with summarizer_col:
        fig_sc1 = px.line(demo_data, x= group_by , y=['Expected_leads', 'Actual_leads'], labels={'value':'Values', 'time': group_by }, title='Expected leads vs. Actual leads')
        fig_sc1.update_layout(legend_title='Legend',template='plotly_white')
        st.plotly_chart(fig_sc1, key="unique_key_1")
       
        result_factors_df = pd.DataFrame(list(result_factors.items()), columns=['Factor', 'Percentage'])
        fig_sc11 = px.bar(result_factors_df, x='Factor', y='Percentage', title='Sales contribution by baseline and marketing channel',color_discrete_sequence=['#0050B5'])
        st.plotly_chart(fig_sc11, key="unique_key_11")
    
    with funnel_col:
        funnel_columns = demo_data[['Impressions', 'Leads', 'Opportunities', 'Customers']]
        funnel_factors = {}
        for column in funnel_columns:
            funnel_factors[column] = demo_data[column].sum()

        data = {'number': list(funnel_factors.values()),'stage': list(funnel_factors.keys())}
        fig_sc12 = px.funnel(data, x='number', y='stage', title='Marketing funnel and converstion rates',color_discrete_sequence=['#3C5291'])
        fig_sc12.update_layout(yaxis_title=None)
        st.plotly_chart(fig_sc12, key="unique_key_12")
    # ------------------------------
with tab2: # Scenario 2 layout
    st.markdown("""<h4 style="font-size: 20px; margin-bottom: -20px;"> Leads </h4>""", unsafe_allow_html=True)
    selected_columns2 = demo_data1[['Tot_sale', 'Baseline', 'TV', 'Display', 'Social', 'SEA']]
    cont_factors2 = {}
    for column in selected_columns2:
        cont_factors2[column] = demo_data1[column].sum()
        
    result_factors2 = {}
    for column in ['Baseline', 'TV', 'Display', 'Social', 'SEA']:
        result_factors2[column] = round((cont_factors2[column] / cont_factors2['Tot_sale']) * 100, 2)    

    sales_cont2 = {}
    sales_cont2['Baseline'] = result_factors2['Baseline']
    sales_cont2['All channels'] = sum(result_factors2[key] for key in result_factors2 if key != 'Baseline')
    selected_car_price2 = demo_data1['Car_Price']
    multiplied_columns2 = selected_columns2.mul(selected_car_price2, axis=0)
    sum_multiplied_columns2 = multiplied_columns2.sum()
    total_sum2 = sum_multiplied_columns2.sum()
    total_spend2 = demo_data1['Spend'].sum()
    ROI2 = (total_sum2 / total_spend2)/100
    
    stat_col, summarizer_col, funnel_col = st.columns([1,2,2])
        
        # Part for overall statistics
    with stat_col:
        st.write("**Actual:** 69.0 M")  
        st.write("**Expected:** 74.0 M")  
        st.write("Difference: +5 M") 
            
        spend_col, roi_col = st.columns([2,2])     
        with spend_col:
            st.markdown(
                """<h4 style="font-size: 20px; margin-bottom: -20px;"> Spend </h4>""", unsafe_allow_html=True
            ) 
            formatted_total_spend2 = f"€{total_spend2:,.2f}"
            st.write(formatted_total_spend2)
        with roi_col:
            st.markdown(
                """<h4 style="font-size: 20px; margin-bottom: -20px;"> ROI </h4>""", unsafe_allow_html=True
            )    
            formatted_ROI2 = round(ROI2, 2)
            st.write(formatted_ROI2)
            
        st.markdown(
            """<h4 style="font-size: 20px; margin-bottom: -20px;"> Sales contribution</h4>""", unsafe_allow_html=True
        )
        st.write(f"Baseline: {sales_cont2['Baseline']} %")
        st.write(f"All channels: {sales_cont2['All channels']} %")

    with summarizer_col:
        fig_sc2 = px.line(demo_data, x= group_by , y=['Expected_leads', 'Actual_leads'], labels={'value':'Values', 'time': group_by }, title='Expected leads vs. Actual leads')
        fig_sc2.update_layout(legend_title='Legend',template='plotly_white')
        st.plotly_chart(fig_sc2, key="unique_key_2")
       
        result_factors_df = pd.DataFrame(list(result_factors.items()), columns=['Factor', 'Percentage'])
        fig_sc21 = px.bar(result_factors_df, x='Factor', y='Percentage', title='Sales contribution by baseline and marketing channel',color_discrete_sequence=['#0050B5'])
        st.plotly_chart(fig_sc21, key="unique_key_21")
    
    with funnel_col:
        funnel_columns = demo_data1[['Impressions', 'Leads', 'Opportunities', 'Customers']]
        funnel_factors = {}
        for column in funnel_columns:
            funnel_factors[column] = demo_data1[column].sum()

        data = {'number': list(funnel_factors.values()),'stage': list(funnel_factors.keys())}
        fig_sc22 = px.funnel(data, x='number', y='stage', title='Marketing funnel and converstion rates',color_discrete_sequence=['#3C5291'])
        fig_sc22.update_layout(yaxis_title=None)
        st.plotly_chart(fig_sc22, key="unique_key_22")        
    # ------------------------------
with tab3: # Scenario 3 layout
    st.markdown("""<h4 style="font-size: 20px; margin-bottom: -20px;"> Leads </h4>""", unsafe_allow_html=True)
    selected_columns3 = demo_data2[['Tot_sale', 'Baseline', 'TV', 'Display', 'Social', 'SEA']]
    cont_factors3 = {}
    for column in selected_columns3:
        cont_factors3[column] = demo_data2[column].sum()
        
    result_factors3 = {}
    for column in ['Baseline', 'TV', 'Display', 'Social', 'SEA']:
        result_factors3[column] = round((cont_factors3[column] / cont_factors3['Tot_sale']) * 100, 2)    

    sales_cont3 = {}
    sales_cont3['Baseline'] = result_factors3['Baseline']
    sales_cont3['All channels'] = sum(result_factors3[key] for key in result_factors3 if key != 'Baseline')
    selected_car_price3 = demo_data2['Car_Price']
    multiplied_columns3 = selected_columns3.mul(selected_car_price3, axis=0)
    sum_multiplied_columns3 = multiplied_columns3.sum()
    total_sum3 = sum_multiplied_columns3.sum()
    total_spend3 = demo_data2['Spend'].sum()
    ROI3 = (total_sum3 / total_spend3)/100
    
    stat_col, summarizer_col, funnel_col = st.columns([1,2,2])
        
        # Part for overall statistics
    with stat_col:
        st.write("**Actual:** 69.0 M")  
        st.write("**Expected:** 74.0 M")  
        st.write("Difference: +5 M") 
            
        spend_col, roi_col = st.columns([2,2])     
        with spend_col:
            st.markdown(
                """<h4 style="font-size: 20px; margin-bottom: -20px;"> Spend </h4>""", unsafe_allow_html=True
            ) 
            formatted_total_spend3 = f"€{total_spend3:,.2f}"
            st.write(formatted_total_spend3)
        with roi_col:
            st.markdown(
                """<h4 style="font-size: 20px; margin-bottom: -20px;"> ROI </h4>""", unsafe_allow_html=True
            )    
            formatted_ROI3 = round(ROI3, 2)
            st.write(formatted_ROI3)
            
        st.markdown(
            """<h4 style="font-size: 20px; margin-bottom: -20px;"> Sales contribution</h4>""", unsafe_allow_html=True
        )
        st.write(f"Baseline: {sales_cont3['Baseline']} %")
        st.write(f"All channels: {sales_cont3['All channels']} %")

    with summarizer_col:
        fig_sc3 = px.line(demo_data, x= group_by , y=['Expected_leads', 'Actual_leads'], labels={'value':'Values', 'time': group_by }, title='Expected leads vs. Actual leads')
        fig_sc3.update_layout(legend_title='Legend',template='plotly_white')
        st.plotly_chart(fig_sc3, key="unique_key_3")

        result_factors_df = pd.DataFrame(list(result_factors.items()), columns=['Factor', 'Percentage'])
        fig_sc31 = px.bar(result_factors_df, x='Factor', y='Percentage', title='Sales contribution by baseline and marketing channel',color_discrete_sequence=['#0050B5'])
        st.plotly_chart(fig_sc31, key="unique_key_31")
    
    with funnel_col:
        funnel_columns = demo_data2[['Impressions', 'Leads', 'Opportunities', 'Customers']]
        funnel_factors = {}
        for column in funnel_columns:
            funnel_factors[column] = demo_data2[column].sum()

        data = {'number': list(funnel_factors.values()),'stage': list(funnel_factors.keys())}
        fig_sc32 = px.funnel(data, x='number', y='stage', title='Marketing funnel and converstion rates',color_discrete_sequence=['#3C5291'])
        fig_sc32.update_layout(yaxis_title=None)
        st.plotly_chart(fig_sc32, key="unique_key_32")


