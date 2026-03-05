import shap

def compute_shap_values(model, X):
    explainer = shap.TreeExplainer(model)
    shap_values = explainer(X)
    return shap_values