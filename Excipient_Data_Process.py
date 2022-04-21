#!/usr/bin/env python
# coding: utf-8

# import reqs
import pandas as pd
import re 
import os
import glob
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from sklearn import preprocessing
from matplotlib import rcParams

# set pathway
plate_path = r'path\Plate.xls'
# set plate number
plate_num = "PLATE_004"

# import data sheet and clean data
raw = pd.read_excel (plate_path)
df = pd.DataFrame(raw)
df = df[df['Cells/Singlets - FSC/Singlets - SSC/GFP+ | Freq. of Parent'] != '0 %']
df = df[df['Cells/Singlets - FSC/Singlets - SSC/GFP+ | Freq. of Parent'] != '100 %']
df = df[df["Unnamed: 0"].str.contains("Mean|SD") == False]

# import control data and clean
raw_controls = pd.read_excel (r'path\Controls.xls')
df_con = pd.DataFrame(raw_controls)
df_con = df_con[df_con["Unnamed: 0"].str.contains("Mean|SD") == False]

# each plate gets its own data frame, clean each df, and get rid of columns that are unneeded
df_plate1_01 = df[df["Unnamed: 0"].str.contains('plate01')].replace('[\%,]', '', regex=True).drop(["Unnamed: 0", 'Cells | Freq. of Parent', 'Cells/Singlets - FSC | Freq. of Parent',       'Cells/Singlets - FSC/Singlets - SSC | Freq. of Parent'],axis=1)

# controls plate
controls = df_con[df_con["Unnamed: 0"].str.contains('plate01')].replace('[\%,]', '', regex=True).drop(["Unnamed: 0", 'Cells | Freq. of Parent', 'Cells/Singlets - FSC | Freq. of Parent',       'Cells/Singlets - FSC/Singlets - SSC | Freq. of Parent'],axis=1)

# normalize values from 0 to 1
df1 = pd.concat([df_plate1_01, controls], axis = 0)
df_list =[df1]
df_normalized = []
cols = ['GFP Expression', 'Count', 'Mean', 'Median']

# using min max normalization to normalize data from 0 to 1
for df in df_list:
    cols = cols
    df = df
    min_max_scaler = preprocessing.MinMaxScaler()
    np_scaled = min_max_scaler.fit_transform(df)
    df_normalized = pd.DataFrame(np_scaled, columns = cols)

# break the list back into individual data frames
df1_1 = df_normalized[1:]

# get the highs and lows
df_high_median = df1_1[df1_1.Median >= .80].reset_index()
df_low_median = df1_1[df1_1.Median <= .20].reset_index()

# bar plot gfp expression
sns.set_theme(style="whitegrid")
plt.figure(figsize=(35,15))
ax_gfp = sns.barplot(x=df1_1.index, y="GFP Expression", color = 'black', data=df1_1, alpha=0.8)    .set(title= 'LNP Excipient GFP Expression')
plt.savefig('GFP.jpg', dpi = 150, transparent=True)

# bar plot mean
sns.set_theme(style="whitegrid")
plt.figure(figsize=(35,15))
ax_mean = sns.barplot(x=df1_1.index, y="Mean", color = 'maroon', data=df1_1, alpha=0.8)    .set(title= 'LNP Excipient Mean Fluorescent Intensity')
plt.savefig('Mean.jpg', dpi = 150, transparent=True)

# bar plot median
sns.set_theme(style="whitegrid")
plt.figure(figsize=(35,15))
ax_med = sns.barplot(x=df1_1.index, y="Median", color = 'navy', data=df1_1, alpha=0.8)    .set(title= 'LNP Excipient Median Fluorescent Intensity')
plt.savefig('Median.jpg', dpi = 150, transparent=True)

# correlating plate number back to master spreadsheet to check for compound identification
# load raw spreadsheet
raw_master = pd.read_excel(r'path\Excipient_Library_Master.xlsx')
df_master = pd.DataFrame(raw_master)

# change format for plate and only select plate that is the plate_num, make into new df
df_master = df_master.loc[df_master['PLATE'] == plate_num].sort_values(by=['WELL']).reset_index().reset_index()
df_master.level_0 = df_master.level_0 + 1
df_master = df_master.rename(columns={"level_0": "index", "index": "index_old"})

# inner join  on the master to get rest of data
df_highmed_match = df_master.merge(df_high_median, on='index', how='inner').drop(["Count"],axis=1)
df_lowmed_match = df_master.merge(df_low_median, on='index', how='inner').drop(["Count"],axis=1)

# save as two separate excel files
df_highmed_match.to_excel("df_highmed_match.xlsx")
df_lowmed_match.to_excel("df_lowmed_match.xlsx")
