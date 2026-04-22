"""
test_queries.py: Structured testing for HealthBridge AI inference engine.
"""

from nlp_predictor import predict_and_extract

def run_tests():
    test_cases = [
        {
            "description": "Clear symptoms",
            "input": "high fever, headache, body pain",
            "expected_method_in": ["bert", "hybrid"]
        },
        {
            "description": "Mixed/vague symptoms",
            "input": "pet dard aur weakness",
            "expected_method_in": ["hybrid"]
        },
        {
            "description": "Regional language",
            "input": "pet mein jalan aur ulti",
            "expected_method_in": ["hybrid"]
        }
    ]

    print("====================================")
    print("  HealthBridge AI Structured Tests")
    print("====================================")
    
    for idx, tc in enumerate(test_cases, 1):
        print(f"\n[Test Case {idx}] {tc['description']}")
        print(f"Input   : \"{tc['input']}\"")
        print(f"Expected: Method should be in {tc['expected_method_in']}")
        print("------------------------------------")
        
        result = predict_and_extract(tc['input'])
        method = result.get('method', 'unknown')
        confidence_level = result.get('confidence_level', 'unknown')
        
        print(f"Method Used      : {method}")
        print(f"Confidence Level : {confidence_level}")
        
        preds = result.get("predictions", [])[:3]
        if preds:
            print("Top Predictions  :")
            for i, p in enumerate(preds, 1):
                print(f"  {i}. {p['disease']:<25} (conf: {p['confidence']:.2f})")
        else:
            print("Top Predictions  : None")
            
        print("------------------------------------")
        match = method in tc['expected_method_in']
        status = "PASSED" if match else "WARNING (Unexpected Method)"
        print(f"Status  : {status}")

if __name__ == "__main__":
    run_tests()
