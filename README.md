# AutoClinic-Reminder

## Project Overview
The **AutoClinic-Reminder** RPA solution automates two critical clinic workflows: sending timely appointment reminders to patients to reduce no‑shows, and delivering lab reports to patients once they become available. By integrating email notifications with simple file‑system monitoring, the project streamlines communication without manual effort.

---

## Architecture
### ReminderBot.xaml (Sequence)
1. **Read CSV** – Loads `Data/appointments.csv` into a DataTable.
2. **Iterate Rows** – Loops through each appointment row.
3. **Trigger Condition** – Checks if the appointment is 24‑48 hours away (`TotalHours >= 24 && TotalHours <= 48`).
4. **Transform** – Builds a personalized email body. If the test type is *Blood Test* a fasting note is added; otherwise a generic note is used.
5. **Action** – Sends an SMTP email (`Send Mail` activity) with the subject `Appointment Reminder – <Doctor Name>`.
6. **Log** – Appends a line to `Data/reminder_log.txt` recording the patient name and reminder timestamp.

### LabReportBot.xaml (Flowchart)
1. **Trigger** – Retrieves all `*.pdf` files from the `Lab_Outputs` folder.
2. **Extract Registry** – Reads `Data/patients_registry.csv` into a DataTable.
3. **For Each File** – Iterates over each PDF file:
   - **Extract** – Uses a regular expression to pull the numeric patient ID from the file name.
   - **Lookup** – Finds the matching patient row in the registry DataTable.
   - **Transform** – Determines if a match exists (`foundMatch`).
   - **Action (Match)** – Sends the PDF as an email attachment, moves the file to `Archived_Reports`, and logs the dispatch in `lab_status_log.txt`.
   - **Action (No Match)** – Logs a “NOT FOUND” entry in `lab_status_log.txt`.

### Main.xaml (Orchestration)
- **Try Catch 1** – Invokes **ReminderBot.xaml**; on failure writes an error message to the output console.
- **Try Catch 2** – Invokes **LabReportBot.xaml**; on failure writes an error message.
- Each `Try Catch` includes an empty `Finally` block for future clean‑up logic.

---

## RPA Workflow Pattern
| Bot | Trigger | Extract | Transform | Action | Log |
|-----|---------|---------|-----------|--------|-----|
| **ReminderBot** | Appointment row meets 24‑48 h window (if condition) | Read appointment CSV row data | Build personalized email body (conditional fasting note) | Send SMTP email to patient | Append reminder entry to `reminder_log.txt` |
| **LabReportBot** | New PDF files discovered via `Directory.GetFiles` | Read patient registry CSV; extract patient ID from file name using regex | Determine if patient exists; compose email body | Send email with PDF attachment; move file to archive | Append status line to `lab_status_log.txt` |

---

## Key Technical Decisions
- **CSV over Excel** – The environment lacks Excel activity licensing and CSV files are lightweight, portable, and easier to process with `ReadCsvFile`.
- **Regex for Patient ID** – File names follow a pattern like `PAT_12345_Report.pdf`. A regular expression (`\d+`) reliably extracts the numeric ID even if the prefix changes, whereas string splitting would be fragile.
- **Sequence vs Flowchart** –
  - *ReminderBot* is a straightforward linear process, best expressed as a **Sequence** for readability.
  - *LabReportBot* contains branching (`If foundMatch`) and iterative file handling, making a **Flowchart** a clearer visual representation of the decision flow.
- **Log File for Dispatch Status** – Updating a CSV column would require read‑modify‑write cycles for each email, risking concurrency issues. A simple append‑only `lab_status_log.txt` provides an immutable audit trail with minimal overhead.

---

## Error Handling
- **Main.xaml** wraps each bot invocation in its own `Try Catch`. On exception, a `Write Line` activity prints `Error running <Bot>: <exception.Message>`.
- **LabReportBot** includes an `If/Else` that logs a “NOT FOUND in registry” entry when the patient ID cannot be matched, ensuring the workflow continues without crashing.

---

## Limitations & Production Considerations
- The project uses **dummy patient data** and a plain SMTP server; a real deployment would require:
  - **HIPAA‑compliant encryption** for email content and attachments.
  - Secure storage and access control for patient CSV files.
  - **UiPath Orchestrator Queues** to scale processing, handle retries, and monitor job status.
  - Robust error logging and alerting (e.g., to a monitoring dashboard).
- File paths are hard‑coded (e.g., `Lab_Outputs`). In production these should be configurable via arguments or assets.

---

*This README was generated automatically to aid in project submission and live demo presentation.*
