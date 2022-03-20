import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_folium import folium_static
import folium
from folium.plugins import HeatMap
month_days = {'January': 31,


              'February': 28, 'March': 31,


              'April': 30, 'May': 31,


              'June': 30, 'July': 31,


              'August': 31, 'September': 30,


              'October': 31, 'November': 30, 'December': 30}

month_to_num = {key: i+1 for i, key in enumerate(month_days)}
num_to_month = {(i+1): key for i, key in enumerate(month_days)}
st.title('Atlanta Crime Statistics')
@st.cache(allow_output_mutation=True)
def loader():
    df09to19 = pd.read_csv('./Dataset/2009-2019.csv',  low_memory=False)
    df20p1 = pd.read_csv('./Dataset/2020p1.csv',  low_memory=False)
    df20p2 = pd.read_csv('./Dataset/2020p2.csv',  low_memory=False)
    df21 = pd.read_csv('./Dataset/2021.csv',  low_memory=False)
    df22 = pd.read_csv('./Dataset/2022.csv',  low_memory=False)
    df = pd.concat([df09to19, df20p1, df20p2, df21, df22])
    return df

df = loader()
df['occur_datet_new'] = df['occur_date'] + ' ' + df['occur_time']
df['occur_datet_new'] = pd.to_datetime(df['occur_datet_new'])

data = df.copy()
data = data.dropna(subset=['lat', 'long'])
# here
choice = st.sidebar.multiselect('Select type of Crimes', (sorted(list(data.ucr_literal.unique()))))
st.sidebar.markdown(" #### Select the hour range (in Military Time)")

if not st.sidebar.checkbox("All day", True, key='2'):
    hour = st.sidebar.multiselect('Hours:', list(range(24)), default=list(range(24)))
else:
    hour = list(range(24))

months = st.sidebar.multiselect('Months', ('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'), default=('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'))

list(data.occur_datet_new.dt.year.unique())

years = st.sidebar.multiselect('Years', (list(range(2009, 2022))), default=list(range(2009, 2022)))

def cpy(data):
    subdata = data
    if len(choice) > 0:
        subdata = subdata[subdata.ucr_literal.isin(choice)]
    subdata = subdata[subdata['occur_datet_new'].dt.hour.isin(hour)]
    nums = []
    for mes in months:
        nums.append(month_to_num[mes])
    subdata = subdata[subdata['occur_datet_new'].dt.month.isin(nums)]
    subdata = subdata[subdata['occur_datet_new'].dt.year.isin(years)]
    crime_per_type = subdata['ucr_literal'].value_counts()
    crime_per_type = pd.DataFrame({'Type': crime_per_type.index, 'Crimes': crime_per_type.values})
    st.markdown(' #### Crimes per type in the selected years')
    fig = px.bar(crime_per_type, x='Type', y='Crimes', height=500)
    st.plotly_chart(fig)
    return subdata
# cpy(data)
data = cpy(data)
def heatmap(data):

    st.markdown(' #### Heatmap of the selected years with crimes and years')
    subdata = data
    heat = subdata[['lat', 'long']]
    m6 = folium.Map(location=[33.767693, -84.4908154], tiles='Stamen Toner', zoom_start=10)
    HeatMap(data=heat, radius=9.5).add_to(m6)
    folium_static(m6)
heatmap(data)
st.markdown(' #### Monthly Crime Count')

def monthly_crime(data):
    intmeses = [month_to_num[i] for i in months]
    for m in range(1, 13):
        if m not in intmeses:
            break
    gra = pd.DataFrame()
    gra['months'] = [num_to_month[i][:3] for i in range(1, 13)]
    gra.set_index('months', inplace=True)
    for year in years:
        time_series = subdata[['occur_datet_new']]
        time_series = time_series[time_series.occur_datet_new.dt.year == int(year)]
        time_series['months'] = time_series.occur_datet_new.dt.month
        cri_mes = []
        mes_es = []
        for i in range(1, 13):
            cri_mes.append(len(time_series[time_series.months == i]))
            mes_es.append(num_to_month[i][:3])
        gra[year] = cri_mes
    fig = px.line(gra, labels={"value": "amount", "variable": "year", "months": "months"})
    st.plotly_chart(fig)
subdata = data
monthly_crime(subdata)
st.markdown("### Crime Distribution by Hour ")

def hourly_crime(data):
    hours = [i for i in range(0, 24)]
    distribution = []
    for i, h in enumerate(hours):
        subd = subdata[subdata['occur_datet_new'].dt.hour == h]
        distribution.append(subd.shape[0])
    df = pd.DataFrame({'hour': hours, 'amount': distribution})
    fig = px.bar(df, x='hour', y='amount', height=500)
    fig.update_layout(
        xaxis=dict(
            tickmode='array',
            tickvals=list(range(24)),
            ticktext=list(range(24))))
    st.plotly_chart(fig)
hourly_crime(data)
st.markdown("### Crime Distribution by Day")

def daily_crime(data):
    dia_semana = [i for i in range(0, 7)]

    dia_str = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    distribution = []

    for i, d in enumerate(dia_semana):

        subd = subdata[subdata['occur_datet_new'].dt.dayofweek == d]

        distribution.append(subd.shape[0])

    df = pd.DataFrame({'day': dia_str, 'amount': distribution})

    fig = px.bar(df, x='day', y='amount', height=500)

    st.plotly_chart(fig)

daily_crime(data)
