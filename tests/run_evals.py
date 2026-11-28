import csv
import sys
from pathlib import Path

# Add src to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from novatech_agent.agent import agent

def run_evaluations():
    csv_path = Path(__file__).resolve().parent.parent / "data" / "tests.csv"
    if not csv_path.exists():
        print(f"Error: tests file not found at {csv_path}")
        return

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        tests = list(reader)

    print("=" * 80)
    print(f"Running NovaTech Agent Benchmark Evaluation ({len(tests)} test cases)")
    print("=" * 80)
    
    passed_count = 0
    
    for row in tests:
        test_id = row["id"]
        msg = row["user_message"]
        exp_intent = row["expected_intent"]
        exp_keyword = row["expected_keyword"]
        
        # 1. Check classification
        intent_obj = agent.classify_intent(msg)
        intent_match = (intent_obj.intent == exp_intent)
        
        # 2. Check agent response (normalizing formatted currency numbers)
        response = agent.respond(msg, thread_id=f"eval_thread_{test_id}")
        clean_resp = response.lower().replace(",", "")
        clean_keyword = exp_keyword.lower().replace(",", "")
        keyword_match = (clean_keyword in clean_resp)
        
        passed = intent_match and keyword_match
        if passed:
            passed_count += 1
            status = "PASS"
        else:
            status = "FAIL"
            
        print(f"[{status}] Test #{test_id:2s} | Msg: '{msg[:45]}...'")
        if not passed:
            print(f"       Expected Intent: {exp_intent} (Got: {intent_obj.intent})")
            print(f"       Expected Keyword: '{exp_keyword}'")
            print(f"       Response Snippet: '{response[:90]}...'")

    accuracy = (passed_count / len(tests)) * 100
    print("=" * 80)
    print(f"Evaluation Summary: {passed_count}/{len(tests)} Tests Passed ({accuracy:.1f}% Accuracy)")
    print("=" * 80)
    return passed_count == len(tests)

if __name__ == "__main__":
    success = run_evaluations()
    sys.exit(0 if success else 1)
