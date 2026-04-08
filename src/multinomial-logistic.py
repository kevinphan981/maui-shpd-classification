import pandas as pd
import numpy as np
import statsmodels.api as sm
import seaborn as sns
from statsmodels.formula.api import mnlogit


path = 'clean-data/shpd-labelled.csv'
df = pd.read_csv(path)
print("Unique outcomes for Statute 106:", df['Opinion 106'].unique())
print("Unique outcomes for Statute 6E:", df['Opinion 6E'].unique())


outcome_map_106 = {
    'No Historic Properies Affected': 0,
    'No Adverse Effect': 0,
    'Adverse Effect': 1,
    'Foreclosure': 2
}

outcome_map_6E = {
    'no effect': 0,
    'effect with agreed commitments': 1,
    'effect with proposed commitments': 2
}

outcome_map_6E_binary = {
    'no effect': 0,
    'effect': 1
}

# too redundant.
df['106_outcomes'] = df['Opinion 106'].map(outcome_map_106)
df['6E_outcomes'] = df['Opinion 6E'].map(outcome_map_6E)
df['6E_outcomes_binary'] = df['opinion_6e_binary'].map(outcome_map_6E_binary)

def setup(code, df):
    # will need to find a way to add the other stuff later...
    name = f"outcomes_{code}"
    df = df.dropna(subset=[f'{code}_outcomes'])
    print(f"Shape of {code}: ", df.shape)
    return df

df_1 = setup(106, df) # very small, 111...
print(df_1.head())
df_2 = setup('6E', df) # much bigger, 2781...
df_3 = df.dropna(subset = [f'6E_outcomes_binary'])



# getting dummy variables for regressions
# def regress(df, label, code):
#     X = pd.get_dummies(df[label], drop_first = True).astype(int)
#     X = sm.add_constant(X) # add intercept
#     y = df[f'{code}_outcomes']

#     model_mn = sm.MNLogit(y,X)
#     result_mn = model_mn.fit()

#     print(result_mn.summary())

# model1 = regress(df, label = 'Label', code = 106)


X = pd.get_dummies(df_2['Label'], drop_first = True).astype(int)
X = sm.add_constant(X) # add intercept
y = df_2[f'6E_outcomes'] # change or adapt to 106, 6E_outcomes

model_mn = sm.MNLogit(y,X)
result_mn = model_mn.fit()
print(result_mn.summary())

categories = df_2['Label'].unique()
dummy_data = pd.get_dummies(categories, drop_first=True).astype(int)
dummy_data = sm.add_constant(dummy_data, has_constant='add')

dummy_data = dummy_data.reindex(columns=X.columns, fill_value=0)
# Predict the probabilities
probabilities = result_mn.predict(dummy_data)
print(probabilities)

# Wrap the names in a list if they aren't already
# column_names = result_mn.model.endog_names
# if isinstance(column_names, str):
#     print(column_names)
#     column_names = [column_names]

# # Combine into a clean table
# prob_table = pd.DataFrame(probabilities, index=categories, 
#                           columns=column_names)

inv_map_6E = {v: k for k, v in outcome_map_6E.items()}
clean_column_names = [inv_map_6E[i] for i in range(len(inv_map_6E))]

# 2. Re-create the table with explicit labels
prob_table = pd.DataFrame(
    probabilities.values, 
    index=categories, 
    columns=clean_column_names
)

prob_table_reset = prob_table.reset_index().rename(columns={'index': 'category'})
# print(prob_table.head(n = 100))

from great_tables import GT
table = GT(prob_table_reset, rowname_col="category")

table = (
    table.tab_header(title = "Probability Table of Different Categories")
    .fmt_number(columns = ['no effect', 'effect with agreed commitments', 'effect with proposed commitments'], n_sigfig = 4)
    .fmt_percent(columns = ['no effect', 'effect with agreed commitments', 'effect with proposed commitments'])
)

table.show()


# gemini slop

from sklearn.metrics import confusion_matrix, classification_report
import matplotlib.pyplot as plt

# 1. Get predicted probabilities for your original training data X
pred_probs = result_mn.predict(X)

# 2. Get the index of the highest probability for each row
# This converts the probabilities into a single predicted class (0, 1, or 2)
y_pred = np.argmax(pred_probs.values, axis=1)

# 3. Ensure your actual y is in the same integer format
# We map the original labels to the codes statsmodels used
y_actual = y.astype('category').cat.codes

# 4. Create the Confusion Matrix
cm = confusion_matrix(y_actual, y_pred)
labels = y.astype('category').cat.categories
print(labels)

# 5. Plot it for easy reading
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=labels, yticklabels=labels)
plt.xlabel('Predicted Label')
plt.ylabel('Actual Label')
plt.title('Permit Outcome Confusion Matrix')
# plt.show()

# 6. Print the detailed stats
# Calculate what percentage the model got right
accuracy = (y_pred == y_actual).mean()
print(f"Overall Accuracy: {accuracy:.2%}")

''' 
    Zero rate baseline test
    basically, what if we just kept saying no effect the entire time
'''

# Calculate the baseline
baseline_accuracy = y.value_counts(normalize=True).max()

print(f"Zero-Rate Baseline: {baseline_accuracy:.2%}")
print(f"Your Model Accuracy: {accuracy:.2%}")

# The 'Improvement' over guessing
lift = accuracy - baseline_accuracy
print(f"Model Lift: {lift:.2%}")

# balanced accuracy
from sklearn.metrics import balanced_accuracy_score
b_acc = balanced_accuracy_score(y_actual, y_pred)
print(f"Balanced Accuracy: {b_acc:.2%}")

# Convert coefficients to Relative Risk Ratios, am I tripping balls and do these labels actually mean something
rrr = np.exp(result_mn.params)
print(rrr)

## ehhh kind of