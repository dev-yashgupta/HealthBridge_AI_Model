
from main import diagnose
import json

def test():
    query = "Mujhe do din se pet mein bohot dard hai aur dast ho rahe hain."
    print(f"Testing Query: {query}")
    
    result = diagnose("TEST_USER", query)
    
    if result["status"] == "success":
        print("\n--- Diagnosis Result ---")
        print(f"Detected Symptoms: {', '.join(result['detected_symptoms'].keys())}")
        print(f"Duration: {result['duration_days']} days")
        print(f"Top Disease: {result['top_disease']}")
        print(f"Confidence: {result['top_score']}%")
        print(f"Urgency: {result['urgency']}")
        print(f"Method Used: {result['method_used']}")
        print("\n--- Report Summary ---")
        # Print first few lines of report
        lines = result['report'].split('\n')
        for line in lines[:10]:
            print(line)
        print("...")
    else:
        print(f"Error: {result.get('message', 'Unknown error')}")

if __name__ == "__main__":
    test()
