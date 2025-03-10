import streamlit as st
import os
import numpy as np
import pandas as pd
import plotly.express as px

# Configure page
st.set_page_config(page_title="Marketing Mix Modelling Dashboard", 
        layout="wide", page_icon = "logo1.svg")

logo_col, title_col = st.columns([1, 3])

with logo_col:
    # Adjust width as needed
    st.write("")
    st.image("P_LOGO.png", width=600) 

with title_col:
    #st.markdown("""<h3 style="font-size: 38px; margin-top: 0px;"> Marketing Mix Modelling Dashboard </h3>""", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: right;'>Marketing Mix Modelling Dashboard</h1>", unsafe_allow_html=True)
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

# Zmienne globalne
result_factors = {}
ROI = 0
total_spend = 0
sales_cont = {}

# definicje funkcji do wykresów
def sales_cont_func(demo_data):
    global result_factors, ROI, total_spend, sales_cont
    selected_columns = demo_data[['Tot_sale', 'Baseline', 'TV', 'Display', 'Social', 'SEA']]
    media_columns = demo_data[['TV', 'Display', 'Social', 'SEA']]
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
    multiplied_columns = media_columns.mul(selected_car_price, axis=0)
    sum_multiplied_columns = multiplied_columns.sum()
    total_sum = sum_multiplied_columns.sum()
    total_spend = demo_data['Spend'].sum()
    ROI = (total_sum / total_spend)
    return result_factors, ROI, total_spend, sales_cont

def leads_sum(demo_data):
    leads_columns = demo_data[['Expected_leads','Actual_leads']]
    leads_factors = {}
    for column in leads_columns:
        leads_factors[column] = demo_data[column].sum()
    
    difference = leads_factors['Expected_leads'] - leads_factors['Actual_leads']
    result = {'Difference': difference}
    
    return {'Actual': leads_factors['Actual_leads'],
            'Expected': leads_factors['Expected_leads'],
            'Difference': result['Difference']}

def format_with_million(value):
    return f"{value / 1_000_000:.1f}M"
    
def expected_leads_chart(demo_data, group_by):
    data_grouped = demo_data.groupby(group_by).agg({'Expected_leads':'sum', 'Actual_leads':'sum'}).reset_index()
    fig_exl = px.line(data_grouped, x=group_by, y=['Expected_leads', 'Actual_leads'], 
        labels={'value': 'Values', 'time': group_by}, title='Expected leads vs. Actual leads',
                      color_discrete_map= {'Expected_leads': '#135DD8', 'Actual_leads': '#D6001C'}, width=700, height=300)
    fig_exl.update_layout(legend_title='Legend', template='plotly_white')
    st.plotly_chart(fig_exl) 

def result_factors_chart(result_factors):
    result_factors_df = pd.DataFrame(list(result_factors.items()), columns=['Factor', 'Percentage'])
    fig_rs = px.bar(result_factors_df, x='Factor', y='Percentage', 
                      title='Sales contribution by baseline and marketing channel', color_discrete_sequence=['#0050B5'], width=700, height=300)   
    st.plotly_chart(fig_rs) 
        
def marketing_funnel_chart(demo_data):
    funnel_columns = demo_data[['Impressions', 'Leads', 'Opportunities', 'Customers']]
    funnel_factors = {}
    for column in funnel_columns:
        funnel_factors[column] = demo_data[column].sum()

    funnel_data = {'number': list(funnel_factors.values()), 'stage': list(funnel_factors.keys())}
    fig_mf = px.funnel(funnel_data, x='number', y='stage', title='Marketing funnel and conversion rates', 
                       color_discrete_sequence=['#3C5291'], width=700, height=300)
    fig_mf.update_layout(yaxis_title=None)
    st.plotly_chart(fig_mf) #, key="unique_key_3"

def base_chart(demo_data):
    data_source = demo_data[[group_by, 'Baseline', 'TV', 'Display', 'Social', 'SEA']]
    data_grouped = data_source.groupby(group_by).agg({el :'sum' for el in data_source.columns if el != group_by}).reset_index()
        
    fig_base = px.area(data_grouped, x=group_by, y=(data_grouped.columns), color_discrete_sequence=px.colors.sequential.Sunset, width=700, height=300) # sorted(data_source.columns[:-1]
    fig_base.update_layout(xaxis_title=group_by, yaxis_title='Values', title='Decomposition over time', showlegend=True)
    fig_base.update_layout(showlegend=True)
    st.plotly_chart(fig_base) #, key="unique_key_4"

# definicja kolumn nagłówka
st.markdown(""" <h4 style="font-size: 20px; margin-bottom: -20px;"> Data Selection </h4> """, unsafe_allow_html=True)

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

# definicja drugiego rzędu parametwów
st.markdown("""<h4 style="font-size: 20px; margin-bottom: -20px;"> Target Parameter - Work in Progress </h4> """, unsafe_allow_html=True)
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

# definicja tabów ze scenariuszami
scenarios = ["Scenario 1", "Scenario 2", "Scenario 3"]
tab1, tab2, tab3 = st.tabs(scenarios)

def Scenario_1(demo_data): 
    st.markdown( """<h4 style="font-size: 20px; margin-bottom: -20px;"> Leads </h4>""", unsafe_allow_html=True)         
    stat_col, summarizer_col, funnel_col = st.columns([1,2,2])
        
    # Parametry ogólne po lewej stronie taba
    with stat_col:
        leads_result = leads_sum(demo_data)
        formatted_actual = format_with_million(leads_result['Actual'])
        formatted_expected = format_with_million(leads_result['Expected'])
        formatted_difference = format_with_million(leads_result['Difference'])

        st.write('Actual:', formatted_actual)
        st.write('Expected:', formatted_expected)
        st.write('Difference:', formatted_difference)
            
        spend_col, roi_col = st.columns([2,2])     
        with spend_col:
            st.markdown("""<h4 style="font-size: 20px; margin-bottom: -20px;"> Spend </h4>""", unsafe_allow_html=True) 
            sales_cont_func(demo_data)
            formatted_total_spend = f"€{total_spend:,.2f}"
            st.write(formatted_total_spend)
        with roi_col:
            st.markdown("""<h4 style="font-size: 20px; margin-bottom: -20px;"> ROI </h4>""", unsafe_allow_html=True)    
            sales_cont_func(demo_data)
            formatted_ROI = round(ROI, 2)
            st.write(formatted_ROI)
                        
        st.markdown("""<h4 style="font-size: 20px; margin-bottom: -20px;"> Sales contribution</h4>""", unsafe_allow_html=True)
        st.write(f"Baseline: {sales_cont['Baseline']} %")
        st.write(f"All channels: {sales_cont['All channels']:.2f}%")

    with summarizer_col:
        expected_leads_chart(demo_data, group_by)
        result_factors_chart(result_factors)   
            
    with funnel_col:
        marketing_funnel_chart(demo_data)
        base_chart(demo_data)
with tab1: 
    Scenario_1(demo_data)
   
def Scenario_2(demo_data): 
    st.markdown("""<h4 style="font-size: 20px; margin-bottom: -20px;"> Leads </h4>""", unsafe_allow_html=True)  
    stat_col, summarizer_col, funnel_col = st.columns([1,2,2])
        
        # Part for overall statistics
    with stat_col:
        leads_result = leads_sum(demo_data)
        formatted_actual = format_with_million(leads_result['Actual'])
        formatted_expected = format_with_million(leads_result['Expected'])
        formatted_difference = format_with_million(leads_result['Difference'])

        st.write('Actual:', formatted_actual)
        st.write('Expected:', formatted_expected)
        st.write('Difference:', formatted_difference) 
            
        spend_col, roi_col = st.columns([2,2])     
        with spend_col:
            st.markdown("""<h4 style="font-size: 20px; margin-bottom: -20px;"> Spend </h4>""", unsafe_allow_html=True) 
            sales_cont_func(demo_data)
            formatted_total_spend = f"€{total_spend:,.2f}"
            st.write(formatted_total_spend)
        with roi_col:
            st.markdown("""<h4 style="font-size: 20px; margin-bottom: -20px;"> ROI </h4>""", unsafe_allow_html=True)    
            sales_cont_func(demo_data)
            formatted_ROI = round(ROI, 2)
            st.write(formatted_ROI)
            
        st.markdown("""<h4 style="font-size: 20px; margin-bottom: -20px;"> Sales contribution</h4>""", unsafe_allow_html=True)
        st.write(f"Baseline: {sales_cont['Baseline']} %")
        st.write(f"All channels: {sales_cont['All channels']:.2f}%")

    with summarizer_col:
        expected_leads_chart(demo_data, group_by)
        result_factors_chart(result_factors)    
    
    with funnel_col:
        marketing_funnel_chart(demo_data)          
        base_chart(demo_data)
with tab2: 
    Scenario_2(demo_data1)

def Scenario_3(demo_data): 
    st.markdown("""<h4 style="font-size: 20px; margin-bottom: -20px;"> Leads </h4>""", unsafe_allow_html=True)
    stat_col, summarizer_col, funnel_col = st.columns([1,2,2])
        
        # Part for overall statistics
    with stat_col:
        leads_result = leads_sum(demo_data)
        formatted_actual = format_with_million(leads_result['Actual'])
        formatted_expected = format_with_million(leads_result['Expected'])
        formatted_difference = format_with_million(leads_result['Difference'])

        st.write('Actual:', formatted_actual)
        st.write('Expected:', formatted_expected)
        st.write('Difference:', formatted_difference)
            
        spend_col, roi_col = st.columns([2,2])     
        with spend_col:
            st.markdown("""<h4 style="font-size: 20px; margin-bottom: -20px;"> Spend </h4>""", unsafe_allow_html=True) 
            sales_cont_func(demo_data)
            formatted_total_spend = f"€{total_spend:,.2f}"
            st.write(formatted_total_spend)
        with roi_col:
            st.markdown("""<h4 style="font-size: 20px; margin-bottom: -20px;"> ROI </h4>""", unsafe_allow_html=True)    
            sales_cont_func(demo_data)
            formatted_ROI = round(ROI, 2)
            st.write(formatted_ROI)
            
        st.markdown("""<h4 style="font-size: 20px; margin-bottom: -20px;"> Sales contribution</h4>""", unsafe_allow_html=True)
        st.write(f"Baseline: {sales_cont['Baseline']} %")
        st.write(f"All channels: {sales_cont['All channels']:.2f}%")

    with summarizer_col:
        expected_leads_chart(demo_data, group_by)
        result_factors_chart(result_factors)    
    
    with funnel_col:
        marketing_funnel_chart(demo_data)
        base_chart(demo_data)
with tab3: 
    Scenario_3(demo_data2)

