from __future__ import annotations

import json
import re
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
DOWNLOADS = Path("/Users/mariomcmichael/Downloads")
OUT = ROOT / "data" / "dashboard-import-from-pdfs.json"

PDFS = {
    "StaffAssistedSummary-4.pdf": "Staff Assisted Summary Report",
    "CaseLoadSumm-3.pdf": "Case Load Summary",
    "CaseNotes-4.pdf": "Case Management - Individual Case Notes",
    "CaseClosureEmp-3.pdf": "Case Closure Employment - Detail Report",
    "IndividualEmploymentPlan.pdf": "Individual Employment Plan With Objectives",
    "IndividualEmploymentPlan-2.pdf": "Individual Employment Plan",
}


def read_pdf(name: str) -> dict:
    path = DOWNLOADS / name
    reader = PdfReader(str(path))
    pages = []
    for i, page in enumerate(reader.pages, start=1):
        pages.append({"page": i, "text": page.extract_text() or ""})
    return {
        "fileName": name,
        "reportType": PDFS[name],
        "pageCount": len(reader.pages),
        "pages": pages,
        "text": "\n".join(p["text"] for p in pages),
    }


def iso_date(value: str | None) -> str:
    if not value:
        return ""
    value = value.strip()
    for fmt in ("%m/%d/%Y", "%m/%d/%y", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            pass
    return value


def add_days(value: str, days: int) -> str:
    if not value or not re.match(r"\d{4}-\d{2}-\d{2}$", value):
        return ""
    return (datetime.strptime(value, "%Y-%m-%d") + timedelta(days=days)).date().isoformat()


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def title_name(raw: str) -> str:
    raw = clean(raw).replace(" ,", ",")
    if raw.isupper():
        parts = [p.strip().title() for p in raw.split(",")]
        return ", ".join(parts)
    return raw


def split_name_from_lines(lines: list[str], idx: int) -> tuple[str, int]:
    first = clean(lines[idx])
    if idx + 1 < len(lines) and not re.match(r"\d{2}/\d{2}/\d{4}$", clean(lines[idx + 1])):
        nxt = clean(lines[idx + 1])
        if nxt and not re.match(r"^(McMichael|SYSTEM|\d+)$", nxt, re.I):
            return title_name(first + " " + nxt), idx + 1
    return title_name(first), idx


def extract_metadata(text: str) -> dict:
    meta = {}
    patterns = {
        "assignedCaseManager": r"Assigned Case Manager:\s*([^\n]+)",
        "office": r"Office(?: Location)?:\s*([^\n]+)",
        "program": r"Program:\s*([^\n]+)",
        "region": r"(?:LWDB/Region|Region/LWDB):\s*([^\n]+)",
        "reportRunTime": r"Report Run Time:\s*([\s\S]{0,60}?)(?:\n[A-Z][^\n]+:|\nOffice/Staff|\nUsername|\nLWDB|\Z)",
    }
    for key, pattern in patterns.items():
        m = re.search(pattern, text)
        if m:
            meta[key] = clean(m.group(1))
    dates = re.search(r"Date Range:\s*([\s\S]{0,80}?)(?:Assigned|Report|Office|$)", text)
    if not dates:
        dates = re.search(r"Start Date:\s*([0-9/]+)\s*End Date:\s*([0-9/]+)", text)
        if dates:
            meta["reportDateRange"] = {"from": iso_date(dates.group(1)), "to": iso_date(dates.group(2))}
    else:
        found = re.findall(r"\d{1,2}/\d{1,2}/\d{4}", dates.group(1))
        if len(found) >= 2:
            meta["reportDateRange"] = {"from": iso_date(found[0]), "to": iso_date(found[1])}
    return meta


def extract_staff_assisted(pdf: dict) -> list[dict]:
    rows = []
    for page in pdf["pages"]:
        lines = [clean(x) for x in page["text"].splitlines() if clean(x)]
        i = 0
        while i < len(lines) - 6:
            if (
                re.match(r"^[A-Za-z0-9]+$", lines[i])
                and lines[i].lower() not in {"username", "assisting", "staff", "system"}
                and re.match(r"^\d{5,}$", lines[i + 1])
            ):
                if re.match(r"^\d{2}/\d{2}/\d{4}$", lines[i + 3]) or (i + 4 < len(lines) and re.match(r"^\d{2}/\d{2}/\d{4}$", lines[i + 4])):
                    username = lines[i]
                    state_id = lines[i + 1]
                    individual, name_idx = split_name_from_lines(lines, i + 2)
                    date_idx = name_idx + 1
                    if date_idx + 3 < len(lines):
                        rows.append({
                            "activityId": f"staff_{state_id}_{len(rows)+1}",
                            "username": username,
                            "stateId": state_id,
                            "individual": individual,
                            "dateAssisted": iso_date(lines[date_idx]),
                            "staff": lines[date_idx + 1],
                            "entryType": lines[date_idx + 2],
                            "timeSpentAssisting": lines[date_idx + 3],
                            "sourceFile": pdf["fileName"],
                            "sourcePage": page["page"],
                        })
                        i = date_idx + 4
                        continue
            i += 1
    return rows


def extract_caseload(pdf: dict) -> dict:
    text = pdf["text"]
    meta = extract_metadata(text)
    rows = []
    for label in ("American Job Center - Clarksville *", "McMichael, Mario", "Total:"):
        pattern = re.escape(label) + r"\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)"
        m = re.search(pattern, text)
        if m:
            row = {
                "officeOrStaff": label.rstrip(":"),
                "currentActiveCases": int(m.group(1)),
                "closedCasesWithNoExit": int(m.group(2)),
                "inCurrentQuarterFollowUp": int(m.group(3)),
                "firstQuarter": int(m.group(4)),
                "secondQuarter": int(m.group(5)),
                "thirdQuarter": int(m.group(6)),
                "fourthQuarter": int(m.group(7)),
            }
            rows.append(row)
    totals = rows[-1] if rows and rows[-1]["officeOrStaff"] == "Total" else {}
    return {
        "program": meta.get("program", ""),
        "region": meta.get("region", ""),
        "office": meta.get("office", "American Job Center - Clarksville *"),
        "assignedCaseManager": meta.get("assignedCaseManager", ""),
        "reportRunTime": meta.get("reportRunTime", ""),
        "rows": rows,
        "totals": totals,
    }


def extract_case_notes(pdf: dict) -> list[dict]:
    notes = []
    header_by_state = {}
    for page in pdf["pages"]:
        lines = [clean(x) for x in page["text"].splitlines() if clean(x)]
        for i in range(len(lines) - 6):
            if re.match(r"^[A-Za-z0-9]+$", lines[i]) and not lines[i].lower().startswith("userid"):
                if re.match(r"\d{2}/\d{2}/\d{4}$", lines[i + 3] if i + 3 < len(lines) else ""):
                    userid = lines[i]
                    individual, name_idx = split_name_from_lines(lines, i + 1)
                    date_idx = name_idx + 1
                    if date_idx + 4 < len(lines) and re.match(r"\d{2}/\d{2}/\d{4}$", lines[date_idx]):
                        header_by_state[userid] = {
                            "userid": userid,
                            "individual": individual,
                            "createdBy": lines[date_idx + 1],
                            "createDate": iso_date(lines[date_idx]),
                            "contactDate": iso_date(lines[date_idx + 2]) if re.match(r"\d{2}/\d{2}/\d{4}$", lines[date_idx + 2]) else "",
                            "contactType": lines[date_idx + 3],
                            "lastEditedBy": lines[date_idx + 4] if date_idx + 4 < len(lines) else "",
                        }
        text = page["text"]
        for match in re.finditer(r"(?P<edit>\d{2}/\d{2}/\d{4})\s+(?P<state>\d{5,})\s+(?P<body>[\s\S]*?)(?=\nLast Edit\s*\nDate|\Z)", text):
            body = clean(match.group("body"))
            if not body or body.startswith("Case Subject"):
                continue
            parts = re.split(r"\s+Narrative:\s+", body, maxsplit=1)
            subject = clean(parts[0])
            case_body = clean("Narrative: " + parts[1]) if len(parts) > 1 else body
            state_id = match.group("state")
            outcome = infer_outcome(case_body + " " + subject)
            notes.append({
                "caseNoteId": f"note_{state_id}_{len(notes)+1}",
                "userid": "",
                "stateId": state_id,
                "individual": "",
                "createdBy": "",
                "createDate": "",
                "contactDate": iso_date(match.group("edit")),
                "contactType": "",
                "lastEditedBy": "",
                "lastEditDate": iso_date(match.group("edit")),
                "caseSubject": subject,
                "caseNotes": case_body,
                "extractedSections": split_note_sections(case_body),
                "inferredOutcome": outcome,
                "sourceFile": pdf["fileName"],
                "sourcePage": page["page"],
            })
    return notes


def infer_outcome(text: str) -> str:
    low = text.lower()
    if "successful contact" in low or "confirmed" in low or "employment verified" in low:
        return "Successful"
    if "voicemail" in low or "left vm" in low:
        return "Left VM"
    if "no response" in low or "no answer" in low:
        return "No Reply"
    if "email" in low and "sent" in low:
        return "Email Sent"
    if "unable to contact" in low:
        return "Unable to Contact"
    return ""


def split_note_sections(text: str) -> dict:
    labels = ["Narrative", "Assessment", "Plan / Next Steps", "Actions"]
    out = {"narrative": "", "assessment": "", "planNextSteps": "", "actions": []}
    for label, key in [("Narrative:", "narrative"), ("Assessment:", "assessment"), ("Plan / Next Steps:", "planNextSteps")]:
        m = re.search(re.escape(label) + r"\s*(.*?)(?= Assessment:| Plan / Next Steps:| Actions:|$)", text)
        if m:
            out[key] = clean(m.group(1))
    m = re.search(r"Actions:\s*(.*)$", text)
    if m:
        out["actions"] = [clean(x) for x in re.split(r"•|-", m.group(1)) if clean(x)]
    return out


def extract_closures(pdf: dict) -> list[dict]:
    text = pdf["text"]
    chunks = re.split(r"App #:\s*", text)[1:]
    rows = []
    for chunk in chunks:
        app = clean(chunk.splitlines()[0])
        def grab(label: str, next_label: str | None = None) -> str:
            labels = ["App #:", "Close Date:", "State ID:", "Name:", "Case Manager:", "Office:", "Employer:", "Industry", "City:", "Contact:", "Phone:", "Job Title:", "O*Net:", "Salary Unit:", "Wage:", "Hours:", "Start Date:", "End Date:", "Total #"]
            if next_label:
                pattern = re.escape(label) + r"\s*([\s\S]*?)" + re.escape(next_label)
            else:
                alternatives = "|".join(re.escape(x) for x in labels if x != label)
                pattern = re.escape(label) + r"\s*([\s\S]*?)(?=" + alternatives + r"|\Z)"
            m = re.search(pattern, chunk)
            return clean(m.group(1)) if m else ""
        rows.append({
            "closureId": f"closure_{app}",
            "applicationNumber": app,
            "closeDate": iso_date(grab("Close Date:")),
            "stateId": grab("State ID:"),
            "name": title_name(grab("Name:")),
            "caseManager": grab("Case Manager:"),
            "office": grab("Office:"),
            "employer": grab("Employer:"),
            "industry": grab("Industry"),
            "city": grab("City:"),
            "contact": grab("Contact:"),
            "phone": grab("Phone:"),
            "jobTitle": grab("Job Title:"),
            "onet": grab("O*Net:"),
            "salaryUnit": grab("Salary Unit:"),
            "wage": grab("Wage:"),
            "hours": grab("Hours:"),
            "startDate": iso_date(grab("Start Date:")),
            "endDate": iso_date(grab("End Date:")),
            "sourceFile": pdf["fileName"],
            "sourcePage": 1,
        })
    return [r for r in rows if r["stateId"]]


def extract_ieps(pdf: dict) -> list[dict]:
    rows = []
    lines = [clean(x) for x in pdf["text"].splitlines() if clean(x)]
    i = 0
    while i < len(lines) - 8:
        if lines[i] == "Northern Middle Tennessee" and i + 8 < len(lines):
            office = lines[i + 1]
            if re.match(r"^\d{5,}$", lines[i + 2]):
                rows.append({
                    "iepId": f"iep_{lines[i+2]}_{lines[i+4]}",
                    "stateId": lines[i + 2],
                    "individualName": title_name(lines[i + 3]),
                    "lwdb": lines[i],
                    "office": office,
                    "planId": lines[i + 4],
                    "planStatus": lines[i + 5],
                    "planCreatedDate": iso_date(lines[i + 6]),
                    "planStartDate": iso_date(lines[i + 7]),
                    "planEditDate": iso_date(lines[i + 8]),
                    "iepCloseDate": "",
                    "planCreatedBy": "",
                    "planLastEditedBy": "",
                    "goals": [],
                    "sourceFile": pdf["fileName"],
                    "sourcePage": None,
                })
                i += 9
                continue
        i += 1
    # Goal extraction is imperfect in these wrapped PDF reports, but goal descriptions are still useful.
    goal_matches = re.finditer(r"(?P<status>Open|Closed)\s+(?P<desc>(?:Employment|The IEP|Get job|Obtain|The veteran)[\s\S]{20,260}?)(?=(?:\n\d{2}/\d{2}/\d{4})|\nIEP Close|\Z)", pdf["text"])
    goals = [{"goalStatus": m.group("status"), "goalDescription": clean(m.group("desc"))} for m in goal_matches]
    for idx, row in enumerate(rows):
        if idx < len(goals):
            row["goals"].append({
                "goalId": "",
                "programOnGoal": "WP",
                "goalCreateDate": row["planCreatedDate"],
                "goalCreatedBy": row["planCreatedBy"],
                "goalEditedBy": row["planLastEditedBy"],
                "goalStatus": goals[idx]["goalStatus"],
                "goalDescription": goals[idx]["goalDescription"],
                "objectives": [],
            })
    return rows


def main() -> None:
    pdfs = {name: read_pdf(name) for name in PDFS}
    meta = {}
    for pdf in pdfs.values():
        meta.update({k: v for k, v in extract_metadata(pdf["text"]).items() if v})

    staff = extract_staff_assisted(pdfs["StaffAssistedSummary-4.pdf"])
    case_notes = extract_case_notes(pdfs["CaseNotes-4.pdf"])
    closures = extract_closures(pdfs["CaseClosureEmp-3.pdf"])
    ieps = extract_ieps(pdfs["IndividualEmploymentPlan.pdf"]) + extract_ieps(pdfs["IndividualEmploymentPlan-2.pdf"])
    caseload = extract_caseload(pdfs["CaseLoadSumm-3.pdf"])

    clients = build_clients(staff, case_notes, closures, ieps)

    output = {
        "sourceBatch": {
            "createdAt": datetime.now().isoformat(timespec="seconds"),
            "filesProcessed": [
                {"fileName": pdf["fileName"], "reportType": pdf["reportType"], "pageCount": pdf["pageCount"]}
                for pdf in pdfs.values()
            ],
            "reportDateRange": meta.get("reportDateRange", {}),
            "assignedCaseManager": meta.get("assignedCaseManager", "McMichael, Mario"),
            "office": meta.get("office", "American Job Center - Clarksville *"),
            "program": meta.get("program", "Title III - Wagner-Peyser (WP)"),
            "region": meta.get("region", "Northern Middle Tennessee"),
        },
        "caseloadSummary": caseload,
        "clients": clients,
        "contacts": [c for client in clients for c in client["contacts"]],
        "staffAssistedActivities": staff,
        "caseNotes": case_notes,
        "employmentClosures": closures,
        "individualEmploymentPlans": ieps,
        "dashboardImport": {"clients": clients},
        "dataQuality": {
            "warnings": [
                {
                    "message": "PDF text extraction from wrapped reports can split names and long descriptions; review dashboardImport clients before final upload.",
                    "sourceFile": "all",
                    "sourcePage": None,
                }
            ],
            "unmatchedRecords": [],
            "assumptions": [
                {
                    "field": "status",
                    "assumption": "Employment closure records set client status to Employed; open IEP/activity without closure defaults to Active Job Search.",
                    "affectedStateIds": [c["stateId"] for c in clients],
                }
            ],
        },
    }
    OUT.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"wrote {OUT}")
    print(f"clients: {len(clients)} staff rows: {len(staff)} notes: {len(case_notes)} closures: {len(closures)} ieps: {len(ieps)}")


def build_clients(staff: list[dict], notes: list[dict], closures: list[dict], ieps: list[dict]) -> list[dict]:
    data: dict[str, dict] = {}

    def ensure(state_id: str, name: str = "") -> dict:
        if not state_id:
            state_id = "unknown"
        if state_id not in data:
            data[state_id] = {
                "clientId": f"client_{state_id}",
                "name": title_name(name) if name else "",
                "stateId": state_id,
                "enrolledDate": "",
                "lastContactDate": "",
                "nextFollowUpDate": "",
                "status": "Active Job Search",
                "contactOutcome": "",
                "failedContacts": 0,
                "educationCertification": "",
                "assignedStaff": "McMichael, Mario",
                "isVeteran": True,
                "branch": "Other",
                "poc": {"primaryPhone": "", "mobilePhone": "", "email": ""},
                "careerGoal": "",
                "supportNeeds": "",
                "barriers": "",
                "notes": "",
                "goals": [],
                "contacts": [],
                "jobLeads": [],
                "tasks": [],
                "reports": [],
            }
        if name and not data[state_id]["name"]:
            data[state_id]["name"] = title_name(name)
        return data[state_id]

    staff_by_state = defaultdict(list)
    for row in staff:
        client = ensure(row["stateId"], row["individual"])
        staff_by_state[row["stateId"]].append(row)
        if row["staff"]:
            client["assignedStaff"] = row["staff"]

    notes_by_state = defaultdict(list)
    for note in notes:
        client = ensure(note["stateId"], note.get("individual", ""))
        notes_by_state[note["stateId"]].append(note)
        event = {
            "eventId": note["caseNoteId"],
            "date": note["contactDate"] or note["lastEditDate"],
            "scenario": note["caseSubject"] or "Case Note",
            "method": note["contactType"] or "",
            "outcome": note["inferredOutcome"],
            "servicesProvided": note["extractedSections"].get("narrative", ""),
            "clientAction": "",
            "cmAction": note["extractedSections"].get("planNextSteps", ""),
            "nextFollowUpDate": add_days(note["contactDate"] or note["lastEditDate"], 14),
            "generatedNote": note["caseNotes"],
        }
        client["contacts"].append(event)

    for closure in closures:
        client = ensure(closure["stateId"], closure["name"])
        client["status"] = "Employed" if closure.get("employer") or closure.get("jobTitle") else "Closed"
        client["contactOutcome"] = "Successful"
        client["assignedStaff"] = closure["caseManager"] or client["assignedStaff"]
        if not client["poc"]["primaryPhone"]:
            client["poc"]["primaryPhone"] = closure.get("phone", "")
        if not client["careerGoal"]:
            client["careerGoal"] = closure.get("jobTitle", "")
        detail = f"Employment closure {closure['closeDate']}: {closure.get('jobTitle') or 'job'} with {closure.get('employer') or 'employer not listed'}"
        if closure.get("wage"):
            detail += f", wage {closure['wage']}"
        if closure.get("hours"):
            detail += f", hours {closure['hours']}"
        if closure.get("startDate"):
            detail += f", start date {closure['startDate']}"
        client["notes"] = append_note(client["notes"], detail)
        client["reports"].append({
            "reportId": closure["closureId"],
            "date": closure["closeDate"],
            "reportType": "Employment Closure",
            "narrative": detail,
        })

    for iep in ieps:
        client = ensure(iep["stateId"], iep["individualName"])
        if not client["enrolledDate"]:
            client["enrolledDate"] = iep["planStartDate"] or iep["planCreatedDate"]
        if iep["planStatus"] == "Closed" and client["status"] != "Employed":
            client["status"] = "Closed"
        elif iep["planStatus"] == "Open" and client["status"] not in ("Employed", "Closed"):
            client["status"] = "Active Job Search"
        for goal in iep.get("goals", []):
            desc = goal.get("goalDescription", "")
            if desc and not client["careerGoal"]:
                client["careerGoal"] = desc
            client["goals"].append({
                "title": desc or "Individual Employment Plan Goal",
                "targetDate": "",
                "percent": 100 if goal.get("goalStatus") == "Closed" else 0,
                "status": goal.get("goalStatus") or iep["planStatus"],
                "updatedAt": iep["planEditDate"],
                "source": "Individual Employment Plan",
            })

    for state_id, client in data.items():
        dates = []
        if staff_by_state.get(state_id):
            dates.extend([r["dateAssisted"] for r in staff_by_state[state_id] if r["dateAssisted"]])
        if notes_by_state.get(state_id):
            dates.extend([n["contactDate"] or n["lastEditDate"] for n in notes_by_state[state_id] if n["contactDate"] or n["lastEditDate"]])
        if dates:
            client["lastContactDate"] = max(dates)
            client["nextFollowUpDate"] = add_days(client["lastContactDate"], 14)
        if notes_by_state.get(state_id):
            latest = sorted(notes_by_state[state_id], key=lambda n: n["contactDate"] or n["lastEditDate"])[-1]
            client["contactOutcome"] = latest["inferredOutcome"] or client["contactOutcome"]
            client["notes"] = append_note(client["notes"], f"Latest case note {latest['contactDate'] or latest['lastEditDate']}: {latest['caseSubject']}. {latest['caseNotes'][:500]}")
            client["failedContacts"] = sum(1 for n in notes_by_state[state_id] if n["inferredOutcome"] in ("Left VM", "No Reply", "Unable to Contact"))
        if staff_by_state.get(state_id):
            total = len(staff_by_state[state_id])
            client["notes"] = append_note(client["notes"], f"Staff assisted activity records in source batch: {total}.")
        if not client["name"]:
            client["name"] = f"State ID {state_id}"
        if not client["goals"]:
            client["goals"] = default_goals_from_client(client)

    return sorted(data.values(), key=lambda c: c["name"])


def append_note(existing: str, addition: str) -> str:
    addition = clean(addition)
    if not addition:
        return existing
    return f"{existing}\n{addition}".strip() if existing else addition


def default_goals_from_client(client: dict) -> list[dict]:
    return [{
        "title": client.get("careerGoal") or "Obtain employment aligned with career goals",
        "targetDate": "",
        "percent": 100 if client.get("status") in ("Employed", "Closed") else 0,
        "status": "Closed" if client.get("status") in ("Employed", "Closed") else "Open",
        "updatedAt": client.get("lastContactDate", ""),
        "source": "Generated from dashboard import",
    }]


if __name__ == "__main__":
    main()
