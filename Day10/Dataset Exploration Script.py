import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix





data = load_breast_cancer()
x, y = data.data, data.target


x_train, x_test,  y_train, y_test = train_test_split(x, y, test_size = 0.2, random_state = 69, stratify = y )

standardrize = StandardScaler()

for_x_train = standardrize.fit_transform(x_train)
for_x_test = standardrize.transform(x_test)


model = LogisticRegression(random_state = 12, max_iter = 5000)

model.fit(for_x_train, y_train)



print("Model trained successfully.")


y_pred = model.predict(for_x_test)


print(f"Predicted labels: {y_pred}")
print(f"Actual labels   : {y_test}")



print(accuracy_score(y_test, y_pred))
print(precision_score(y_test, y_pred))
print(recall_score(y_test, y_pred))
print(f1_score(y_test, y_pred))
print(confusion_matrix(y_test, y_pred))





cm = confusion_matrix(y_test, y_pred)

plt.figure(figsize=(6, 5))
sns.heatmap(
    cm,
    annot=True,           # write the numbers inside each cell
    fmt='d',               # format numbers as integers, not decimals
    cmap='Blues',           # color scheme
    xticklabels=data.target_names,
    yticklabels=data.target_names
)
plt.xlabel('Predicted Label')
plt.ylabel('Actual Label')
plt.title('Baseline Logistic Regression - Confusion Matrix')
plt.tight_layout()
plt.savefig('baseline_confusion_matrix.png', dpi=150)
plt.show()