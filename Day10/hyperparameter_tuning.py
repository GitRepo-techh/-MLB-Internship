import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LogisticRegression
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler




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




param_grid = {
    "C": [0.01, 0.1, 1, 10, 100],
    "penalty": ["l1", "l2"],
    "solver": ["liblinear", "saga"]
}

gradient_search = GridSearchCV(
    estimator = model, 
    param_grid = param_grid,
    cv = 5,
    scoring = "recall"
)


gradient_search.fit(for_x_train, y_train)   

print("Best parameters:", gradient_search.best_params_)
print("Best score:", gradient_search.best_score_)




from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix
)
 

best_model = gradient_search.best_estimator_
 
y_pred_tuned = best_model.predict(for_x_test)
 
accuracy_tuned = accuracy_score(y_test, y_pred_tuned)
precision_tuned = precision_score(y_test, y_pred_tuned)
recall_tuned = recall_score(y_test, y_pred_tuned)
f1_tuned = f1_score(y_test, y_pred_tuned)
cm_tuned = confusion_matrix(y_test, y_pred_tuned)



print(f"Accuracy : {accuracy_tuned:.4f}")
print(f"Precision: {precision_tuned:.4f}")
print(f"Recall   : {recall_tuned:.4f}")
print(f"F1-Score : {f1_tuned:.4f}")
print("Confusion Matrix:")
print(cm_tuned)


plt.figure(figsize=(6, 5))
sns.heatmap(
    cm_tuned, annot=True, fmt='d', cmap='Greens',
    xticklabels=data.target_names, yticklabels=data.target_names
)
plt.xlabel('Predicted Label')
plt.ylabel('Actual Label')
plt.title('Tuned Logistic Regression - Confusion Matrix')
plt.tight_layout()
plt.savefig('tuned_confusion_matrix.png', dpi=150)
plt.show()
 
print("\nSaved: tuned_confusion_matrix.png")
 

print(f"{'Metric':<12}{'Baseline':<12}{'Tuned':<12}")
print(f"{'Accuracy':<12}{'<fill in>':<12}{accuracy_tuned:<12.4f}")
print(f"{'Precision':<12}{'<fill in>':<12}{precision_tuned:<12.4f}")
print(f"{'Recall':<12}{'<fill in>':<12}{recall_tuned:<12.4f}")
print(f"{'F1-Score':<12}{'<fill in>':<12}{f1_tuned:<12.4f}")