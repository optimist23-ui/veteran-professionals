# Productivity Website Foundation

## Purpose

This website should work as a veteran services command center: a place to capture intake, connect clients to job leads and resources, track follow-up dates, and generate progress narratives from structured data.

The intake sheet is the best foundation for the system because it already defines the real conversation flow:

1. Introduction and trust-building
2. Veteran eligibility
3. Career direction
4. Education and skills
5. Job search activity
6. Support needs
7. Stability and barriers
8. Commitment
9. Service delivery
10. Follow-up and accountability

## Core Modules

### Dashboard

The first screen should be similar to the uploaded `DVOP_Client_Dashboard.xlsx` workbook. It should show the work that needs attention today while preserving the workbook's caseload-tracking structure.

- Follow-ups due
- Clients needing contact
- Upcoming key dates
- Open tasks
- Recent job leads
- New resources or flyers
- Clients with stalled progress

Dashboard table columns should include:

- Name
- State ID
- Enrolled
- Last Contact
- Status
- Next Follow-Up
- Days Without Contact
- Contact Outcome
- Failed Contacts
- Education / Certification
- Assigned POC
- Veteran
- Branch
- Contact info
- Notes

The system should automatically calculate:

- `Next Follow-Up = Last Contact + 14 days`
- `Days Without Contact = Today - Last Contact`

Urgency rules:

- `0-14 days`: current
- `15-30 days`: follow-up needed
- `31+ days`: urgent
- `Failed Contacts >= 3`: escalation flag

### Clients

Each client should have a record that combines intake, progress, tasks, resources, and narrative history.

Suggested client fields:

- Client ID
- Name
- Phone
- Email
- Preferred contact method
- Veteran branch
- Service dates
- Transition or separation status
- Service-connected disability rating
- Current employment status
- Unemployment duration
- Career goal
- Target job type
- Long-term goal
- Open to short-term work
- Education level
- Certifications or licenses
- Resume status
- Job search activity
- Applying consistently
- Housing stability
- Transportation status
- Financial concerns
- Childcare or family responsibilities
- Work-impacting conditions
- Biggest job search challenge
- Support needs
- Progress stage
- Progress percent
- Next action date
- Last contact date
- Assigned staff
- Notes

### Tasks

Tasks should represent concrete actions attached to a client, resource, job lead, or event.

Suggested task fields:

- Task ID
- Title
- Client ID
- Related resource ID
- Related job lead ID
- Status
- Priority
- Due date
- Completed date
- Assigned staff
- Notes

### Resources

Resources should hold the materials that support the service plan.

Resource types:

- Job leads
- Job fairs
- Flyers
- Training programs
- Workshops
- Resume help
- Certification or licensing support
- Community support
- Employer contacts
- Documents
- HTML pages

Suggested resource fields:

- Resource ID
- Title
- Type
- File path or URL
- Date added
- Event date
- Location
- Tags
- Related client IDs
- Notes

### Key Dates

Dates should be tracked separately so the dashboard can surface what matters.

Date types:

- Intake date
- Follow-up date
- Resume review date
- Job fair date
- Application deadline
- Interview date
- Training start date
- Certification date
- Case review date
- Closure date

### Case Narratives

Narratives should be generated from the structured client record and activity history.

Useful narrative types:

- Intake summary
- Career direction summary
- Barrier and support summary
- Service plan
- Two-week follow-up summary
- Progress update
- Case timeline
- Closure summary

## Intake Workflow

The intake should function as a guided conversation, not just a form.

Recommended stages:

1. Start with the intro script and role explanation.
2. Capture veteran eligibility details.
3. Identify current work status and career direction.
4. Capture education, resume status, certifications, and licenses.
5. Record current job search activity.
6. Identify support needs such as resume help, interviews, job leads, training, or direction.
7. Capture barriers and stability factors.
8. Confirm readiness and commitment.
9. Generate an initial service plan.
10. Schedule the follow-up, usually about two weeks out.

## Progress Stages

Suggested client progress stages:

- New Intake
- Eligibility Review
- Career Direction
- Resume / Skills Prep
- Active Job Search
- Job Leads Sent
- Event / Training Referral
- Follow-Up Scheduled
- Progress Review
- Employed / Stabilized
- Closed

## JSON Functions

The product should support three JSON actions.

### Import Clients And Tasks

Use this when adding new clients, bulk tasks, key dates, resources, or job leads.

```json
{
  "action": "import",
  "clients": [
    {
      "clientId": "client_001",
      "name": "Example Client",
      "branch": "Army",
      "employmentStatus": "Unemployed",
      "careerGoal": "Logistics",
      "progressStage": "New Intake",
      "keyDates": [
        {
          "type": "intake",
          "date": "2026-05-05"
        }
      ]
    }
  ],
  "tasks": [
    {
      "taskId": "task_001",
      "clientId": "client_001",
      "title": "Send updated job leads",
      "status": "Open",
      "priority": "High",
      "dueDate": "2026-05-06"
    }
  ]
}
```

### Update Client Progress

Use this after check-ins, completed tasks, new barriers, job applications, interviews, or resource referrals.

```json
{
  "action": "updateClientProgress",
  "clientId": "client_001",
  "progressStage": "Job Leads Sent",
  "progressPercent": 45,
  "lastContactDate": "2026-05-05",
  "nextActionDate": "2026-05-19",
  "notes": "Sent job leads and job fair flyer. Client agreed to continue applying and review leads before follow-up."
}
```

### Generate Reports

Use this to generate case narratives, timelines, progress summaries, and follow-up notes.

```json
{
  "action": "generateReport",
  "clientId": "client_001",
  "reportType": "progressSummary",
  "dateRange": {
    "from": "2026-05-05",
    "to": "2026-05-19"
  },
  "include": [
    "intake",
    "tasks",
    "keyDates",
    "resources",
    "progressNotes"
  ]
}
```

## Best Fit In The Ecosystem

This should serve as the operating layer between intake conversations and the documents/resources already in the workspace.

Recommended ecosystem role:

- Intake sheet becomes the client entry point.
- Job leads become searchable resources that can be attached to a client.
- Flyers and workshop files become resource cards with dates and tags.
- Tasks become the accountability layer after each client conversation.
- Key dates become the daily dashboard and follow-up engine.
- JSON becomes the import/update/report bridge.
- Narratives become the output layer for documentation, progress reviews, and follow-up summaries.

## Daily Workflow

Recommended daily use:

1. Open the dashboard.
2. Review follow-ups due today.
3. Open each client record.
4. Update progress using quick fields or JSON.
5. Attach relevant job leads, flyers, workshops, or documents.
6. Create next tasks.
7. Generate a short progress narrative.
8. Set the next follow-up date.

## Next Build Priorities

1. Add a client intake form based on the uploaded intake sheet.
2. Add a client detail view with progress, tasks, resources, key dates, and narrative history.
3. Add JSON import, JSON progress update, and JSON report generation panels.
4. Connect existing job lead data and resource documents to client records.
5. Add dashboard cards for follow-ups, stalled clients, key dates, and open tasks.

## Uploaded Tool References

The uploaded HTML tools should be treated as working prototypes for the full ecosystem.

- `DVOP_Client_Dashboard.html`: daily command center and caseload tracker.
- `DVOP_CaseNote_Generator.html`: contact documentation and case note generator.
- `VA_Form_28-10289_Generator.html`: formal VA progress report generator.
- `AJC_Dashboard_Reports.html`: searchable report pathway and reference library.

More detailed guidance is captured in `docs/uploaded-html-ecosystem-guidance.md`.

The uploaded Excel workbook dashboard pattern is captured in `docs/dashboard-workbook-reference.md`.
