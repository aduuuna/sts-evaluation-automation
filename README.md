# 📚 STS Course Evaluation & Exam Check-In Bot

## Overview

This project automates the **STS course/lecture evaluation process** and the **mandatory exam check-in** activity for students.
Every semester before exams, students are required to complete these tasks manually — this script streamlines the process to save time and effort.

The automation is **partially supervised**, meaning you still get to review and approve submissions before they are finalized.

---

## 📂 Project Structure

```
.
├── main.py               # Main entry point — runs both evaluation and check-in bots
├── evaluation_bot.py     # Handles the course/lecture evaluation process
├── checkin_bot.py        # Handles the exam check-in process
├── utils.py              # Shared helper functions
├── requirements.txt      # Python dependencies
├── README.md             # This file
└── .env                  # Environment variables (not tracked in Git)
```

---

## 🚀 How It Works

### 1. **Evaluation Phase**

- Logs into the STS portal with your credentials.
- Navigates through courses that require evaluation.
- Automatically fills out the form fields based on predefined logic.
- **Stops before submission** — so you can:

  - Review the evaluation in your browser.
  - Manually click the **Submit** button.

- After submission, return to the terminal and **press ENTER** to continue.
- If a course has **multiple lecturers**, you will be prompted to select the correct lecturer number.

### 2. **Check-In Phase**

- After all evaluations are completed, the bot logs out.
- It then initiates the **exam check-in** process.
- Checks in for all eligible courses automatically.

---

## 📦 Installation

1. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

2. **Create a `.env` file** in your project root:

   ```env
   STS_USERNAME=your_student_id
   STS_PASSWORD=your_student_password
   ```

3. **Run the automation**

   ```bash
   python main.py
   ```

---

## 📝 Notes

- **Human review is still required** — for now, you must manually click "Submit" during evaluation.
- If there’s more than one lecturer for a course, you must select the lecturer number in the terminal prompt.
- The system will automatically proceed to **check-in** after evaluations are completed.

---

## 🔮 Future Plans

- Fully automate the **Submit** button click during evaluation.
- Auto-select lecturer names when there’s only one lecturer assigned.
- Enhanced error handling for network or STS downtime.

---

## ⚠️ Disclaimer

This script is intended for **personal use only**.
Use it responsibly and in compliance with your institution’s policies.

---
