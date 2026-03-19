from evaluation_bot import run_evaluation
from checkin_bot import run_checkin

if __name__ == "__main__":
    print("Starting automation: evaluations first.")
    eval_ok = run_evaluation(keep_browser_open=False)
    if eval_ok:
        print("\nEvaluations done — starting check-in process now.")
        check_ok = run_checkin()
        if check_ok:
            print("\n All tasks completed: evaluations and check-ins finished.")
        else:
            print("\nCheck-in script failed or had issues. Check logs.")
    else:
        print("\nEvaluation script failed or was interrupted. Aborting check-in.")
