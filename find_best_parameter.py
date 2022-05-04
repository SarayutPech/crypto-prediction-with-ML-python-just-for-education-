# -*- coding: utf-8 -*-
"""PJ_ML.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/18DbPS0JeWr6zk9jEmWknButJwQKClKg8

## import lib
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import StandardScaler
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
from matplotlib.pyplot import figure
from sklearn.svm import SVR
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.tree import DecisionTreeClassifier

import copy

"""## read CSV"""

csv = pd.read_csv('https://www.cryptodatadownload.com/cdd/Binance_BNBUSDT_1h.csv',skiprows=1)

csv

"""## Data Cleaning

### Drop cols ที่คิดว่าไม่ใช้
"""

csv.drop(columns='unix',inplace = True)

csv.info()

csv['tradecount'].fillna( csv['tradecount'].mean() )
csv.info()

"""### แบ่ง X,Y"""

X = csv[['open','high','low','Volume BNB','Volume USDT']]
# X.drop( columns='close' ,inplace = True)
Y = csv[[ 'close' ]]
all_X = csv.iloc[:, 2:]
all_Y = csv[[ 'close' ]]

X.columns.to_list()

X.describe()

X.boxplot(column=['open', 'high', 'low'])

X.boxplot(column=['Volume USDT'])

X.boxplot(column=['Volume BNB'])

"""## Standardize"""

standard_scaler = StandardScaler()
X = pd.DataFrame(standard_scaler.fit_transform(X.values), index = X.index, columns=X.columns )

X.describe()

corr_df = X.corr()
corr_df

X.boxplot(column=['open', 'high', 'low'])

X.boxplot(column=['Volume BNB', 'Volume USDT'])

"""#Linear Model

## เนื่องจาก plot ภาพมาดูแล้ว 'Volume BNB', 'Volume USDT', 'tradecount' มีค่า outliner มากพอควรแถมค่า correration ยังต่ำมากๆ
การทำนายจึงใช้เพียง 'open', 'high', 'low'

##train test split
"""

X = X[['open', 'high', 'low']]

X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size = 0.2, random_state = 6301)

lr = LinearRegression()
lr.fit(X_train, Y_train)
y_pred = lr.predict(X_test)

r2 = r2_score(Y_test, y_pred)
mse = mean_squared_error(Y_test, y_pred)

rmse = np.sqrt(mse)
mae = mean_absolute_error(Y_test, y_pred)
print('r2 : ',r2)
print('mse : ', mse)
print('rmse : ', rmse)
print('mae : ', mae)

y_pred = lr.predict(X)

ans = copy.copy(X)
ans['date'] = csv['date']
ans['close_pred'] = y_pred
ans['close'] = y_pred
# ans = ans[['date', 'symbol', 'high', 'low', 'Volume BNB',
#        'Volume USDT', 'tradecount', 'open', 'close', 'close_pred']]

ans

figure(figsize=(30, 15))

ax = plt.gca()

ans.plot(kind='line',x='date',y='close', color='red', linewidth=3,ax=ax)
ans.plot(kind='line',x='date',y='close_pred', color='blue', linewidth=1,ax=ax)
plt.xticks(rotation=90)

plt.show()

"""## กำหนด Parameter"""

# Create Model List
regression = { 'LR': LinearRegression(), 'SVR': SVR(), }
# Create Parameter Dictionary for Linear Regression
fit_intercept = [True, False]
normalize = [True, False]
params_LR = dict( fit_intercept = fit_intercept, normalize = normalize)
# Create Parameter Dictionary for SVR
kernel = ['linear', 'rbf', 'poly']
C_list = [10, 100]
ep_list = [0.1, 1, 5]
gamma = [0.01, 0.1]
degree = [2, 3]
params_SVR = dict( kernel = kernel, C = C_list, epsilon = ep_list, gamma = gamma, degree = degree )

"""## Grid Search"""

grid_result = []

for EST in regression:
  model = regression[EST]
  if (EST == 'LR'):
    params = params_LR
  else:
    params = params_SVR

  grid = GridSearchCV( estimator=model, n_jobs = 1,

  verbose = 1,
  cv = 2,
  scoring = 'neg_mean_squared_error',
  param_grid = params )

  grid_result.append(grid.fit(X_train, Y_train))
  print('===========================================================================================')

# Show Best Parameters for both models
print('Linear')
print('Best params: ',grid_result[0].best_params_)
print('Best score: ', grid_result[0].best_score_)

# Show Best Parameters for both models
print('SVR')
print('Best params: ',grid_result[1].best_params_)
print('Best score: ', grid_result[1].best_score_)

"""## SVR Model ด้วย Best params"""

svm = SVR(kernel='rbf')
best_param = {'C': 100, 'degree': 2, 'epsilon': 0.1, 'gamma': 0.01, 'kernel': 'linear'}
svm.set_params( **best_param )
svm.fit( X_train, Y_train )

Y_pred = svm.predict(X_test)
r2 = r2_score(Y_test, Y_pred)
mse = mean_squared_error(Y_test, Y_pred)

rmse = np.sqrt(mse)
mae = mean_absolute_error(Y_test, Y_pred)
print('r2 : ',r2)
print('mse : ', mse)
print('rmse : ', rmse)
print('mae : ', mae)

Y_pred = svm.predict(X)

ans = pd.DataFrame()
ans = copy.copy(csv)
# ans['close'] = all_Y
ans['close_pred'] = Y_pred
ans = ans[['date', 'symbol', 'high', 'low', 'Volume BNB',
       'Volume USDT', 'tradecount', 'open', 'close', 'close_pred']]

ans

temp_ans = copy.copy(ans)

figure(figsize=(30, 15))

ax = plt.gca()

ans.plot(kind='line',x='date',y='close', color='red', linewidth=3,ax=ax)
ans.plot(kind='line',x='date',y='close_pred', color='blue', linewidth=1,ax=ax)
plt.xticks(rotation=90)

plt.show()

for index, row in ans.iterrows():
  #row["shoud_pay_ot"] = "Something" << is not worked
  if row["close_pred"] >= row["open"]:
    ans.loc[index,"Should_do_SVM"] = "Buy"
  elif row["close_pred"] < row["open"]:
    ans.loc[index,"Should_do_SVM"] = "Sell"

SVM_ans = copy.copy(ans)

"""## LR Model ด้วย Best params"""

lr = LinearRegression()
best_param = {'fit_intercept': True, 'normalize': False}
lr.set_params( **best_param )
lr.fit( X_train, Y_train )

Y_pred = lr.predict(X_test)
r2 = r2_score(Y_test, Y_pred)
mse = mean_squared_error(Y_test, Y_pred)

rmse = np.sqrt(mse)
mae = mean_absolute_error(Y_test, Y_pred)
print('r2 : ',r2)
print('mse : ', mse)
print('rmse : ', rmse)
print('mae : ', mae)

Y_pred = lr.predict(X)

ans_lr = pd.DataFrame()
ans_lr = copy.copy(csv)
# ans['close'] = all_Y
ans_lr['close_pred'] = Y_pred
ans_lr = ans_lr[['date', 'symbol', 'high', 'low', 'Volume BNB',
       'Volume USDT', 'tradecount', 'open', 'close', 'close_pred']]

ans_lr

figure(figsize=(30, 15))

ax = plt.gca()

ans_lr.plot(kind='line',x='date',y='close', color='red', linewidth=3,ax=ax)
ans_lr.plot(kind='line',x='date',y='close_pred', color='blue', linewidth=1,ax=ax)
plt.xticks(rotation=90)

plt.show()

for index, row in ans_lr.iterrows():
  #row["shoud_pay_ot"] = "Something" << is not worked
  if row["close_pred"] >= row["open"]:
    ans_lr.loc[index,"Should_do_LR"] = "Buy"
  elif row["close_pred"] < row["open"]:
    ans_lr.loc[index,"Should_do_LR"] = "Sell"

LR_ans = copy.copy(ans_lr)

LR_ans

"""# การทำนายด้วย classification

## input
"""

csv = pd.read_csv('https://www.cryptodatadownload.com/cdd/Binance_BNBUSDT_1h.csv',skiprows=1)

csv.drop(columns='unix',inplace=True)
csv.drop(columns='symbol',inplace=True)
csv

"""## แปลงราคาปิดของชั่วโมงนั้นๆให้เป็นกลุ่มของข้อมูล
โดยการแปลงง่ายๆโดยถ้าราคาปิดสูงกว่าราคาเปิดก็จะเป็น action Buy
"""

for index, row in csv.iterrows():
  #row["shoud_pay_ot"] = "Something" << is not worked
  if row["open"] < row["close"]:
    csv.loc[index,"Should_do"] = "Buy"
  else:
    csv.loc[index,"Should_do"] = "Sell"

csv.drop(columns='close',inplace=True)

csv

"""## standardized"""

X = csv[['open','high','low']]
Y = csv[['Should_do']]

standard_scaler = StandardScaler()
X = pd.DataFrame(standard_scaler.fit_transform(X.values), index = X.index, columns=X.columns )

X

NSample = Y["Should_do"].value_counts()
NSample.to_list()

"""## แบ่ง Train Test"""

X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size = 0.2, random_state = 6301)

ASM_function = ['entropy', 'gini'] 
maxD = [4, 6, 8, 10] # try at least 2 values

ASM_y_pred = []
ASM_DTScore = []
model = []

for i in range(0,4):
  ModelDT = DecisionTreeClassifier(criterion=ASM_function[i%2], splitter='best',max_depth =maxD[i] )
  model.append (ModelDT.fit(X_train,Y_train))
  ASM_y_pred.append( ModelDT.predict(X_test) )
  ASM_DTScore.append( accuracy_score(Y_test, ASM_y_pred[i]) )
ASM_DTScore

ASM_DTScore.index( max(ASM_DTScore) )

print('Confusion Matrix: ')
print(confusion_matrix(Y_test, ASM_y_pred[ASM_DTScore.index( max(ASM_DTScore) )]))
print('Classification Report: ')
print(classification_report(Y_test, ASM_y_pred[ASM_DTScore.index( max(ASM_DTScore) )]))

ans = Y_test[['Should_do']]
ans['Should_do_pred'] = ASM_y_pred[1]

ans

NSample = ans["Should_do"].value_counts()
NSample.to_list()

y_pred = model[ASM_DTScore.index( max(ASM_DTScore) )].predict(X)

model[ASM_DTScore.index( max(ASM_DTScore) )].get_params()

"""## เพื่อให้ง่ายต่อการเปรียบเทียบเราจึงนำทั้ง 2 model ที่คิดว่าดีที่สุดมาวิเคราะห์กัน"""

SVM_ans

SVM_ans['Should_do_Classi'] = y_pred
SVM_ans

SVM_ans['Should_do_Classi'] = y_pred

SVM_ans['Should_do_LR'] = LR_ans['Should_do_LR']
SVM_ans

for index, row in SVM_ans.iterrows():
  if row["open"] < row["close"]:
    SVM_ans.loc[index,"Should_do_real"] = "Buy"
  else:
    SVM_ans.loc[index,"Should_do_real"] = "Sell"

SVM_ans

"""### เทียบระหว่าง Action ที่เราคาดหวังและ Action ที่เราทำนายจาก Regression และ Classification"""

SVM_score = [0,0]
Classi_score = [0,0]
LR_score = [0,0]

for index, row in SVM_ans.iterrows():
  if row["Should_do_real"] == row["Should_do_SVM"]:
    SVM_score[0] += 1
  elif row["Should_do_real"] != row["Should_do_SVM"]:
    SVM_score[1] += 1

  if row["Should_do_real"] == row["Should_do_Classi"]:
    Classi_score[0] += 1
  elif row["Should_do_real"] != row["Should_do_Classi"]:
    Classi_score[1] += 1

  if row["Should_do_real"] == row["Should_do_LR"]:
    LR_score[0] += 1
  elif row["Should_do_real"] != row["Should_do_LR"]:
    LR_score[1] += 1

Classi_score

SVM_score

LR_score

"""# เทียบกันกับทั้ง 3 โมเดล"""

print('LR score')
print('True  : ',LR_score[0])
print('False : ',LR_score[1])
print('True percent  : ', LR_score[0] / (LR_score[0] + LR_score[1]))
print('False percent : ', LR_score[1] / (LR_score[0] + LR_score[1]))
print('==========================================')
print('SVM score')
print('True  : ',SVM_score[0])
print('False : ',SVM_score[1])
print('True percent  : ', SVM_score[0] / (SVM_score[0] + SVM_score[1]))
print('False percent : ', SVM_score[1] / (SVM_score[0] + SVM_score[1]))
print('==========================================')
print('Classification score')
print('True  : ',Classi_score[0])
print('False : ',Classi_score[1])
print('True percent  : ', Classi_score[0] / (Classi_score[0] + Classi_score[1]))
print('False percent : ', Classi_score[1] / (Classi_score[0] + Classi_score[1]))
print('==========================================')

"""Classification Report ของ model ต่างๆ"""

print('Confusion Matrix: ')
print(confusion_matrix(SVM_ans['Should_do_real'], SVM_ans["Should_do_SVM"]))
print('Classification Report: ')
print(classification_report(SVM_ans['Should_do_real'], SVM_ans["Should_do_SVM"]))

print('Confusion Matrix: ')
print(confusion_matrix(SVM_ans['Should_do_real'], SVM_ans["Should_do_LR"]))
print('Classification Report: ')
print(classification_report(SVM_ans['Should_do_real'], SVM_ans["Should_do_LR"]))

print('Confusion Matrix: ')
print(confusion_matrix(SVM_ans['Should_do_real'], SVM_ans["Should_do_Classi"]))
print('Classification Report: ')
print(classification_report(SVM_ans['Should_do_real'], SVM_ans["Should_do_Classi"]))
