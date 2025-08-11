# main.py
from evaluation_bot import run_evaluation
from checkin_bot import run_checkin

if __name__ == "__main__":
    print("🚀 Starting automation: evaluations first.")
    eval_ok = run_evaluation(keep_browser_open=False)
    if eval_ok:
        print("\n✅ Evaluations done — starting check-in process now.")
        check_ok = run_checkin()
        if check_ok:
            print("\n🎯 All tasks completed: evaluations and check-ins finished.")
        else:
            print("\n⚠️ Check-in script failed or had issues. Check logs.")
    else:
        print("\n⚠️ Evaluation script failed or was interrupted. Aborting check-in.")
