import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
import seaborn as sns

data=pd.read_excel('Online Retail.xlsx')

country_cus= data[['Country','CustomerID']].drop_duplicates()
print(country_cus.groupby('Country')['CustomerID'].aggregate('count').sort_values(ascending=False))
data=data[data['Country']=='United Kingdom']
print(data.isna().sum())
data.dropna(axis=0, subset=['CustomerID'], inplace=True)
print(data.Quantity.min())
print(data.UnitPrice.min())
data=data[data['Quantity']>0]
data['InvoiceDate']=pd.to_datetime(data['InvoiceDate'])
data['TotalAmount']=data['Quantity']*data['UnitPrice']

print(data.InvoiceDate.max())
latest_date=dt.datetime(2011,12,10)
RFMscores= data.groupby('CustomerID').agg({'InvoiceDate': lambda x: (latest_date-x.max()).days, 'InvoiceNo': lambda x: len(x), 'TotalAmount': lambda x: sum(x)})
RFMscores['InvoiceDate']=RFMscores.InvoiceDate.astype('int')
RFMscores.rename(columns={'InvoiceDate':'Recency', 'InvoiceNo':'Frequency', 'TotalAmount':'Monetary'},inplace=True)

print(RFMscores.Recency.describe())
ax=sns.distplot(RFMscores.Recency)

print(RFMscores.Frequency.describe())
x1= RFMscores[RFMscores['Frequency']<1000]
ax1=sns.distplot(x1.Frequency)

print(RFMscores.Monetary.describe())
x2= RFMscores[RFMscores['Monetary']<10000]
ax2=sns.distplot(x2.Monetary)

quantiles=RFMscores.quantile(q=[0.25,0.5,0.75])

def R_scoring(x,p):
    if x<= quantiles[p][0.25]:
        return 1
    if x<= quantiles[p][0.5]:
        return 2
    if x<= quantiles[p][0.75]:
        return 3
    else:
        return 4
def FM_scoring(x,p):
    if x<= quantiles[p][0.25]:
        return 4
    if x<= quantiles[p][0.5]:
        return 3
    if x<= quantiles[p][0.75]:
        return 2
    else:
        return 1
RFMscores['R']=RFMscores.agg({'Recency': lambda x: R_scoring(x,'Recency')})
RFMscores['F']=RFMscores.agg({'Frequency': lambda x: FM_scoring(x,'Frequency')})
RFMscores['M']=RFMscores.agg({'Monetary': lambda x: FM_scoring(x,'Monetary')})

RFMscores['RFMGroups']=RFMscores.R.map(str)+RFMscores.F.map(str)+RFMscores.M.map(str)
RFMscores['RFMScores']=RFMscores[['R','F','M']].sum(axis=1)
loyalty_levels=['Platinum','Gold','Silver','Bronze']
level_cuts=pd.qcut(RFMscores.RFMScores, q=4, labels=loyalty_levels)
RFMscores['RFM_Loyalty_Level']=level_cuts.values
scatter=RFMscores[RFMscores['Frequency']<1500]
scatter=scatter[scatter['Monetary']<10000]

sns.scatterplot(data=scatter, x="Frequency", y="Monetary", hue="RFM_Loyalty_Level", alpha=0.5)






