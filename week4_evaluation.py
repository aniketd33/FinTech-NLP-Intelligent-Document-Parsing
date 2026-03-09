"""
NER Model Evaluation Script
Week 2 Deliverable: F1-Score Calculation
"""

from sklearn.metrics import f1_score, precision_score, recall_score
import json

# Ground Truth Data (Manually Annotated)
# Inhe tumhe manually annotate karna padega
GROUND_TRUTH = {
    "AgapeAtpCorp_20191202_10-KA_EX-10.1_11911128_EX-10.1_Supply Agreement.pdf": {
        "DATE": ["December 2, 2019", "January 1, 2020"],
        "MONEY": ["$1.00", "$500,000"],
        "PARTY": ["Agape ATP Corp", "Customer"],
        "LAW": ["Delaware"]
    },
    "VnueInc_20150914_8-K_EX-10.1_9259571_EX-10.1_Promotion Agreement.pdf": {
        "DATE": ["September 10, 2015", "January 16, 2016"],
        "MONEY": ["$5,000", "$2,500.00", "600,000 shares"],
        "PARTY": ["VNUE", "Promoter"],
        "LAW": ["Nevada"]
    },
    "SalesforcecomInc_20171122_10-Q_EX-10.1_10961535_EX-10.1_Reseller Agreement.pdf": {
        "DATE": ["November 22, 2017"],
        "MONEY": [],
        "PARTY": ["Salesforce.com, Inc."],
        "LAW": ["Delaware"]
    }
}

def calculate_f1_for_entity(pred_values, true_values):
    """Calculate F1 for a single entity type"""
    pred_set = set(pred_values)
    true_set = set(true_values)
    
    all_values = pred_set.union(true_set)
    
    y_pred = [1 if v in pred_set else 0 for v in all_values]
    y_true = [1 if v in true_set else 0 for v in all_values]
    
    if len(y_true) == 0 and len(y_pred) == 0:
        return {"precision": 1.0, "recall": 1.0, "f1": 1.0, "note": "No data"}
    
    if len(y_true) == 0:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0, "note": "No ground truth"}
    
    if len(y_pred) == 0:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0, "note": "No predictions"}
    
    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    
    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4)
    }

def evaluate_model(predictions_dict):
    """Evaluate full model performance"""
    results = {}
    
    entity_types = ["DATE", "MONEY", "PARTY", "LAW"]
    
    for entity_type in entity_types:
        all_preds = []
        all_true = []
        
        for filename, pred in predictions_dict.items():
            true = GROUND_TRUTH.get(filename, {})
            
            all_preds.extend(pred.get(entity_type, []))
            all_true.extend(true.get(entity_type, []))
        
        results[entity_type] = calculate_f1_for_entity(all_preds, all_true)
        results[entity_type]["predicted"] = len(all_preds)
        results[entity_type]["actual"] = len(all_true)
    
    return results

def print_evaluation_report(results):
    """Print formatted evaluation report"""
    print("\n" + "="*70)
    print("📊 NER MODEL EVALUATION REPORT - LexiScan Auto")
    print("="*70)
    
    print(f"\n{'Entity':<10} {'Precision':<12} {'Recall':<12} {'F1-Score':<12} {'Predicted':<12} {'Actual':<10}")
    print("-"*70)
    
    for entity, metrics in results.items():
        print(f"{entity:<10} {metrics['precision']:<12.4f} {metrics['recall']:<12.4f} {metrics['f1']:<12.4f} {metrics['predicted']:<12} {metrics['actual']:<10}")
    
    print("-"*70)
    
    # Calculate average F1 (excluding 'note' keys)
    f1_values = [r['f1'] for k, r in results.items() if 'f1' in r]
    avg_f1 = sum(f1_values) / len(f1_values) if f1_values else 0
    
    print(f"\n🎯 Overall Average F1-Score: {avg_f1:.4f}")
    
    if avg_f1 >= 0.8:
        print("✅ Excellent Performance!")
    elif avg_f1 >= 0.6:
        print("🟡 Good Performance - Room for improvement")
    else:
        print("🔴 Needs Improvement")
    
    print("="*70 + "\n")

# Sample Predictions from API (Replace with actual API results)
SAMPLE_PREDICTIONS = {
    "AgapeAtpCorp_20191202_10-KA_EX-10.1_11911128_EX-10.1_Supply Agreement.pdf": {
        "DATE": [],
        "MONEY": ["$1.00"],
        "PARTY": ["The Customer covenants...", "Subject to the foregoing..."],
        "LAW": []
    },
    "VnueInc_20150914_8-K_EX-10.1_9259571_EX-10.1_Promotion Agreement.pdf": {
        "DATE": ["September 10, 2015", "2015-09-10", "January 16, 2016"],
        "MONEY": ["$5,000", "$2,500.00"],
        "PARTY": ["VNUE"],
        "LAW": ["Nevada"]
    },
    "SalesforcecomInc_20171122_10-Q_EX-10.1_10961535_EX-10.1_Reseller Agreement.pdf": {
        "DATE": [],
        "MONEY": [],
        "PARTY": [],
        "LAW": []
    }
}

if __name__ == "__main__":
    print("🔄 Running NER Model Evaluation...\n")
    
    results = evaluate_model(SAMPLE_PREDICTIONS)
    print_evaluation_report(results)
    
    # Print detailed comparison
    print("\n📋 Detailed Comparison:")
    print("-"*50)
    
    for filename, pred in SAMPLE_PREDICTIONS.items():
        true = GROUND_TRUTH.get(filename, {})
        print(f"\n📄 {filename}")
        print(f"   DATE - Pred: {pred.get('DATE', [])}, True: {true.get('DATE', [])}")
        print(f"   MONEY - Pred: {pred.get('MONEY', [])}, True: {true.get('MONEY', [])}")
        print(f"   PARTY - Pred: {pred.get('PARTY', [])}, True: {true.get('PARTY', [])}")