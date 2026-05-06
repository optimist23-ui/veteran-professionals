# Uploaded HTML Ecosystem Guidance

## Reviewed References

- `/Users/mariomcmichael/Documents/Claude/Projects/Progress Report/VA_Form_28-10289_Generator.html`
- `/Users/mariomcmichael/Documents/Claude/Projects/HTML Tracker/DVOP_Client_Dashboard.html`
- `/Users/mariomcmichael/Desktop/HTMLs/AJC_Dashboard_Reports.html`
- `/Users/mariomcmichael/Documents/Claude/Projects/HTML Tracker/DVOP_CaseNote_Generator.html`

## Best Role For Each Tool

### DVOP Client Dashboard

Best role: daily command center.

This is the strongest starting point for the productivity website because it already tracks:

- Active caseload
- Enrollment date
- Last contact date
- Next follow-up date
- Days without contact
- Client status
- Notes
- Last case note
- Daily checklist
- Resource links
- JSON update/export

This should become the home screen of the full system.

### DVOP Case Note Generator

Best role: contact documentation engine.

This tool should sit inside or beside the client record. It supports several scenarios:

- Outbound call
- Check-in
- Successful contact
- Unsuccessful contact
- Case closure

The case note generator should save each generated note back to the selected client record instead of living as a separate one-off page.

### VA Form 28-10289 Generator

Best role: formal progress report generator.

This tool is more specialized than the dashboard. It should be used when a client needs a formal VA progress report with:

- Client identity
- Referral date
- Employment goal
- Last contact
- Employment outcome
- Job referrals
- Services provided
- Remarks
- Case manager signature
- JSON backup/import

This should become a report-generation module that pulls data from the main client record.

### AJC Dashboard Reports

Best role: reporting pathway library.

This is not a client tracker. It is a reference guide for where to find reports and what each report supports.

It should become a searchable resource/report directory with:

- Report name
- System pathway
- Purpose
- Program area
- Frequency
- Notes
- Related workflow

## Recommended Ecosystem Structure

The full productivity website should combine the uploaded tools into one flow:

1. Intake captures the veteran/client situation.
2. Client dashboard tracks caseload, follow-ups, and status.
3. Client record holds all notes, tasks, resources, reports, key dates, and progress.
4. Case note generator creates contact documentation from structured events.
5. VA report generator creates formal monthly or progress reports from the same client data.
6. Resource library stores job leads, flyers, workshops, reports, links, and files.
7. JSON tools import, update, export, and generate reports across the ecosystem.

## Main Data Objects

### Client

The client record should be the central object.

Core fields:

- `clientId`
- `name`
- `stateId`
- `phone`
- `email`
- `enrolledDate`
- `intakeDate`
- `lastContactDate`
- `nextFollowUpDate`
- `status`
- `progressStage`
- `progressPercent`
- `employmentGoal`
- `assignedStaff`
- `notes`
- `barriers`
- `supportNeeds`
- `keyDates`

### Contact Event

Every call, check-in, missed contact, or closure should become a contact event.

Core fields:

- `eventId`
- `clientId`
- `date`
- `time`
- `scenario`
- `method`
- `result`
- `servicesProvided`
- `veteranAction`
- `caseManagerAction`
- `nextFollowUpDate`
- `generatedNote`

### Task

Tasks should represent the next action after intake, contact, or report generation.

Core fields:

- `taskId`
- `clientId`
- `title`
- `status`
- `priority`
- `dueDate`
- `completedDate`
- `source`
- `notes`

### Resource

Resources should include links, files, flyers, workshops, job leads, and report pathways.

Core fields:

- `resourceId`
- `title`
- `type`
- `url`
- `filePath`
- `eventDate`
- `tags`
- `relatedClientIds`
- `notes`

### Report

Reports should be generated outputs saved against the client or office workflow.

Core fields:

- `reportId`
- `clientId`
- `reportType`
- `dateRange`
- `generatedAt`
- `sourceData`
- `narrative`
- `formData`

## JSON Strategy

The uploaded files already point toward the right system design: JSON should be a first-class update layer, not an afterthought.

Recommended JSON actions:

- `importClients`
- `updateClientProgress`
- `addContactEvent`
- `generateCaseNote`
- `generateVAReport`
- `importResources`
- `exportBackup`
- `generateReport`

Example client update:

```json
{
  "action": "updateClientProgress",
  "clientId": "client_001",
  "status": "Active Job Search",
  "progressStage": "Job Leads Sent",
  "lastContactDate": "2026-05-05",
  "nextFollowUpDate": "2026-05-19",
  "notes": "Sent job leads and job fair flyer. Veteran will review leads and continue applications before next follow-up."
}
```

Example contact event:

```json
{
  "action": "addContactEvent",
  "clientId": "client_001",
  "scenario": "successfulContact",
  "date": "2026-05-05",
  "method": "Phone",
  "servicesProvided": [
    "Job leads",
    "Job fair flyer",
    "Job search guidance"
  ],
  "veteranAction": "Review job leads and continue applying.",
  "caseManagerAction": "Follow up in two weeks.",
  "nextFollowUpDate": "2026-05-19"
}
```

## Best Productivity Fit

For your work style, this ecosystem should serve as a working desk, not a passive archive.

Recommended placement:

- Dashboard: start here every morning.
- Intake: use when a new client enters the system.
- Client record: use during every client interaction.
- Case note generator: use immediately after contact.
- Tasks: use to capture the next action before leaving a client record.
- Resources: use when sending job leads, flyers, workshops, or report pathways.
- VA report generator: use for formal reporting periods.
- JSON: use for fast bulk updates, backups, and moving data between tools.

## Build Priorities

1. Merge dashboard, intake, case note, and report concepts into one shared data model.
2. Build a client detail screen with tabs for overview, intake, contacts, tasks, resources, dates, and reports.
3. Convert the case note generator into a client-attached contact event tool.
4. Convert the VA form generator into a report module fed by client data.
5. Convert AJC report pathways into searchable resources.
6. Add import/export JSON for the entire workspace.
7. Add action-specific JSON tools for client updates, contact events, and report generation.
