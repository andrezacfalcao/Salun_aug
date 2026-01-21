"""
Clinical Risk and Fairness Metrics for DermaMNIST

Metrics for binary classification analysis (malignant vs benign)
for machine unlearning evaluation.

Classes:
- Malignant (positivo=1): akiec (0), bcc (1), mel (4)
- Benign (negativo=0): bkl (2), df (3), nv (5), vasc (6)
"""

import numpy as np
import torch
import torch.nn.functional as F

MALIGNANT_CLASSES = [0, 1, 4]  # akiec, bcc, mel
BENIGN_CLASSES = [2, 3, 5, 6]  # bkl, df, nv, vasc

__all__ = [
    'MALIGNANT_CLASSES',
    'BENIGN_CLASSES',
    'binarize_labels',
    'compute_clinical_risk',
    'compute_risk_scenarios',
    'compute_fairness_metrics',
    'compute_all_metrics',
    'collect_predictions',
]


def binarize_labels(y, malignant_classes=MALIGNANT_CLASSES):
    """
    Converte labels multiclasse para binário (maligno=1, benigno=0)
    
    Args:
        y: array de labels (0-6)
        malignant_classes: lista de índices das classes malignas
        
    Returns:
        array binário (1=maligno, 0=benigno)
    """
    if isinstance(y, torch.Tensor):
        y = y.cpu().numpy()
    return np.isin(y, malignant_classes).astype(int)


def compute_clinical_risk(y_true, y_pred, cost_fn, cost_fp):
    """
    Calcula o risco clínico para classificação binarizada (maligno vs benigno)
    
    Fórmulas:
        R_global = (C_FN × FN + C_FP × FP) / N
        R_maligno = (C_FN × FN_maligno) / N_maligno
        R_benigno = (C_FP × FP_benigno) / N_benigno
    
    Args:
        y_true: labels verdadeiros (originais 0-6)
        y_pred: labels preditos (originais 0-6)
        cost_fn: custo do falso negativo (não detectar maligno)
        cost_fp: custo do falso positivo (classificar benigno como maligno)
        
    Returns:
        dict com métricas de risco
    """
    y_true_bin = binarize_labels(y_true)
    y_pred_bin = binarize_labels(y_pred)
    
    fn = ((y_true_bin == 1) & (y_pred_bin == 0)).sum()
    fp = ((y_true_bin == 0) & (y_pred_bin == 1)).sum()
    
    n_total = len(y_true_bin)
    n_malignant = (y_true_bin == 1).sum()
    n_benign = (y_true_bin == 0).sum()
    
    risk_global = (cost_fn * fn + cost_fp * fp) / n_total if n_total > 0 else 0
    
    risk_malignant = (cost_fn * fn) / n_malignant if n_malignant > 0 else 0
    risk_benign = (cost_fp * fp) / n_benign if n_benign > 0 else 0
    
    risk_gap = abs(risk_malignant - risk_benign)
    
    return {
        'risk_global': float(risk_global),
        'risk_malignant': float(risk_malignant),
        'risk_benign': float(risk_benign),
        'risk_gap': float(risk_gap),
        'fn': int(fn),
        'fp': int(fp),
        'n_malignant': int(n_malignant),
        'n_benign': int(n_benign)
    }


def compute_risk_scenarios(y_true, y_pred):
    """
    Calcula o risco para os cenários de custo definidos
    
    Cenários:
        - scenario_I: C_FN=1, C_FP=1 (custos iguais)
        - scenario_II: C_FN=20, C_FP=1 (FN 20x mais caro)
    
    Args:
        y_true: labels verdadeiros
        y_pred: labels preditos
        
    Returns:
        dict com riscos para cada cenário
    """
    cost_scenarios = {
        'scenario_I': {'cost_fn': 1, 'cost_fp': 1},
        'scenario_II': {'cost_fn': 20, 'cost_fp': 1},
    }
    
    results = {}
    for scenario_name, costs in cost_scenarios.items():
        results[scenario_name] = compute_clinical_risk(
            y_true, y_pred,
            costs['cost_fn'],
            costs['cost_fp']
        )
    
    return results


def compute_fairness_metrics(y_true, y_pred):
    """
    Calcula métricas de fairness para classificação binarizada (maligno vs benigno)
    
    Fórmulas:
        EOD = |TPR_maligno - TNR_benigno|
        Δ_EO = |TPR_maligno - TNR_benigno|
        Δ_DP = |P(Ŷ=1|Y=1) - P(Ŷ=1|Y=0)|
        Acc_worst = min(Acc_maligno, Acc_benigno)
    
    Args:
        y_true: labels verdadeiros (originais 0-6)
        y_pred: labels preditos (originais 0-6)
        
    Returns:
        dict com métricas de fairness
    """
    y_true_bin = binarize_labels(y_true)
    y_pred_bin = binarize_labels(y_pred)
    
    mask_malignant = y_true_bin == 1
    mask_benign = y_true_bin == 0
    
    y_true_mal = y_true_bin[mask_malignant]
    y_pred_mal = y_pred_bin[mask_malignant]
    
    tp_mal = ((y_true_mal == 1) & (y_pred_mal == 1)).sum()
    fn_mal = ((y_true_mal == 1) & (y_pred_mal == 0)).sum()
    
    tpr_malignant = tp_mal / (tp_mal + fn_mal) if (tp_mal + fn_mal) > 0 else 0
    acc_malignant = tp_mal / len(y_true_mal) if len(y_true_mal) > 0 else 0
    
    y_true_ben = y_true_bin[mask_benign]
    y_pred_ben = y_pred_bin[mask_benign]
    
    fp_ben = ((y_true_ben == 0) & (y_pred_ben == 1)).sum()
    tn_ben = ((y_true_ben == 0) & (y_pred_ben == 0)).sum()
    
    tnr_benign = tn_ben / (fp_ben + tn_ben) if (fp_ben + tn_ben) > 0 else 0
    acc_benign = tn_ben / len(y_true_ben) if len(y_true_ben) > 0 else 0
    
    eod = abs(tpr_malignant - tnr_benign)
    
    eo_diff = abs(tpr_malignant - tnr_benign)
    
    pred_positive_rate_mal = y_pred_mal.mean() if len(y_pred_mal) > 0 else 0
    pred_positive_rate_ben = y_pred_ben.mean() if len(y_pred_ben) > 0 else 0
    dp_diff = abs(pred_positive_rate_mal - pred_positive_rate_ben)
    
    worst_group_acc = min(acc_malignant, acc_benign)
    
    acc_gap = abs(acc_malignant - acc_benign)
    
    tn_global = ((y_true_bin == 0) & (y_pred_bin == 0)).sum()
    fp_global = ((y_true_bin == 0) & (y_pred_bin == 1)).sum()
    fn_global = ((y_true_bin == 1) & (y_pred_bin == 0)).sum()
    tp_global = ((y_true_bin == 1) & (y_pred_bin == 1)).sum()
    
    tpr_global = tp_global / (tp_global + fn_global) if (tp_global + fn_global) > 0 else 0
    tnr_global = tn_global / (fp_global + tn_global) if (fp_global + tn_global) > 0 else 0
    
    return {
        'tpr_malignant': float(tpr_malignant),
        'tnr_benign': float(tnr_benign),
        'acc_malignant': float(acc_malignant),
        'acc_benign': float(acc_benign),
        
        'equalized_odds_diff': float(eod),
        'equal_opportunity_diff': float(eo_diff),
        'demographic_parity_diff': float(dp_diff),
        'worst_group_accuracy': float(worst_group_acc),
        'accuracy_gap': float(acc_gap),
        
        'tpr_global': float(tpr_global),
        'tnr_global': float(tnr_global),
        
        'tp': int(tp_global),
        'tn': int(tn_global),
        'fp': int(fp_global),
        'fn': int(fn_global),
        'n_malignant': int(mask_malignant.sum()),
        'n_benign': int(mask_benign.sum())
    }


def compute_all_metrics(y_true, y_pred):
    """
    Calcula todas as métricas (risco + fairness)
    
    Args:
        y_true: labels verdadeiros (originais 0-6)
        y_pred: labels preditos (originais 0-6)
        
    Returns:
        dict com todas as métricas
    """
    fairness = compute_fairness_metrics(y_true, y_pred)
    risk = compute_risk_scenarios(y_true, y_pred)
    
    return {
        'fairness': fairness,
        'risk': risk
    }


def collect_predictions(data_loader, model, device):
    """
    Coleta labels verdadeiros e predições de um data loader
    
    Args:
        data_loader: PyTorch DataLoader
        model: modelo treinado
        device: dispositivo (cuda/cpu)
        
    Returns:
        tuple (y_true, y_pred) como numpy arrays
    """
    model.eval()
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for data, target in data_loader:
            data = data.to(device)
            target = target.to(device)
            
            output = model(data)
            pred = output.argmax(dim=1)
            
            all_preds.append(pred.cpu().numpy())
            all_labels.append(target.cpu().numpy())
    
    y_true = np.concatenate(all_labels)
    y_pred = np.concatenate(all_preds)
    
    if y_true.ndim > 1:
        y_true = y_true.squeeze()
    if y_pred.ndim > 1:
        y_pred = y_pred.squeeze()
    
    return y_true, y_pred
