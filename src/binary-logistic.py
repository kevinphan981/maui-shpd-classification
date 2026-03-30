import pandas as pd
import numpy as np
import statsmodels.api as sm
import seaborn as sns
from statsmodels.formula.api import mnlogit


path = 'clean-data/shpd-labelled.csv'
df = pd.read_csv(path)
print("Unique outcomes for Statute 106:", df['Opinion 106'].unique())
print("Unique outcomes for Statute 6E:", df['Opinion 6E'].unique())


outcome_map_6E_binary = {
    'no effect': 0,
    'effect': 1
}

# too redundant.
df['6E_outcomes_binary'] = df['opinion_6e_binary'].map(outcome_map_6E_binary)

df_3 = df.dropna(subset = [f'6E_outcomes_binary'])
print("Shape of binary dataset: ", df_3.shape)


X = pd.get_dummies(df_3['Label'], drop_first = True).astype(int)
X = sm.add_constant(X) # add intercept
y = df_3[f'6E_outcomes_binary']

binary_model = sm.Logit(y, X).fit()
print(binary_model.summary())

categories = df_3['Label'].unique()
dummy_data = pd.get_dummies(categories, drop_first=True).astype(int)
dummy_data = sm.add_constant(dummy_data, has_constant='add')

dummy_data = dummy_data.reindex(columns=X.columns, fill_value=0)

# 1. Get probabilities for your training data
train_probs = binary_model.predict(X)

# 2. Get probabilities for your categories (using the dummy_data from before)
# ensure dummy_data has the same columns as X
category_probs = binary_model.predict(dummy_data)

# make df
prob_table = pd.DataFrame({
    'Label': categories,
    'Prob_of_Effect': category_probs
})

print(prob_table.sort_values(by='Prob_of_Effect', ascending=False))

'''
    Accuracy tests
'''
# 0.5 is the standard threshold
y_pred = (train_probs >= 0.5).astype(int)

#accuracy scores
from sklearn.metrics import accuracy_score, balanced_accuracy_score
acc = accuracy_score(y, y_pred)
b_acc = balanced_accuracy_score(y, y_pred)
baseline = y.value_counts(normalize=True).max()

print(f"Raw Accuracy: {acc:.2%}")
print(f"Balanced Accuracy: {b_acc:.2%}")
print(f"Zero-Rate Baseline: {baseline:.2%}")

# use a threshold reflecting your actual distribution (~9%)
y_pred_adjusted = (train_probs > 0.09).astype(int)

from sklearn.metrics import confusion_matrix
print(confusion_matrix(y, y_pred_adjusted))