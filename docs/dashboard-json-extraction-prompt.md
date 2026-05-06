# Dashboard JSON Extraction Prompt

Use this prompt when uploading Jobs4TN/VOS PDF reports and asking an AI tool to create a JSON file for the DVOP Productivity Command Center.

## Prompt

You are converting uploaded Jobs4TN/VOS PDF reports into one clean JSON object for a DVOP case management dashboard.

Extract all available data from the uploaded PDFs. The uploaded files may include:

- Staff Assisted Summary Report
- Case Load Summary
- Case Management - Individual Case Notes
- Case Closure Employment - Detail Report
- Individual Employment Plan with objective columns
- Individual Employment Plan without objective columns

Return only valid JSON. Do not include markdown, commentary, citations, or explanations outside the JSON.

Use `null` when a field is not present. Use empty arrays when a section has no records. Preserve original names and IDs exactly as shown, but also normalize dates to `YYYY-MM-DD` where possible. If a date cannot be normalized, keep the original date string in `rawDate`.

Create one JSON object with this top-level shape:

```json
{
  "sourceBatch": {
    "createdAt": "",
    "filesProcessed": [],
    "reportDateRange": {
      "from": "",
      "to": ""
    },
    "assignedCaseManager": "",
    "office": "",
    "program": "",
    "region": ""
  },
  "caseloadSummary": {},
  "clients": [],
  "contacts": [],
  "staffAssistedActivities": [],
  "caseNotes": [],
  "employmentClosures": [],
  "individualEmploymentPlans": [],
  "dashboardImport": {
    "clients": []
  },
  "dataQuality": {
    "warnings": [],
    "unmatchedRecords": [],
    "assumptions": []
  }
}
```

## Extraction Rules

1. Match people primarily by `stateId`.
2. If `stateId` is missing, match by normalized name.
3. Preserve duplicate report rows in the detailed arrays.
4. Deduplicate only inside `dashboardImport.clients`, keeping the most recent information.
5. The most recent report information overrides older information when populating dashboard fields.
6. Do not invent values.
7. Do not include personally sensitive numbers unless they appear as State ID, application number, phone, or staff/user ID in the report.
8. Keep generated summaries factual and short.

## Source Batch Fields

Populate:

```json
{
  "sourceBatch": {
    "createdAt": "current extraction date/time if known",
    "filesProcessed": [
      {
        "fileName": "",
        "reportType": "",
        "pageCount": null
      }
    ],
    "reportDateRange": {
      "from": "",
      "to": ""
    },
    "assignedCaseManager": "",
    "office": "",
    "program": "",
    "region": ""
  }
}
```

## Caseload Summary

From Case Load Summary, extract:

```json
{
  "caseloadSummary": {
    "program": "",
    "region": "",
    "office": "",
    "assignedCaseManager": "",
    "reportRunTime": "",
    "rows": [
      {
        "officeOrStaff": "",
        "currentActiveCases": null,
        "closedCasesWithNoExit": null,
        "inCurrentQuarterFollowUp": null,
        "firstQuarter": null,
        "secondQuarter": null,
        "thirdQuarter": null,
        "fourthQuarter": null
      }
    ],
    "totals": {
      "currentActiveCases": null,
      "closedCasesWithNoExit": null,
      "inCurrentQuarterFollowUp": null,
      "firstQuarter": null,
      "secondQuarter": null,
      "thirdQuarter": null,
      "fourthQuarter": null
    }
  }
}
```

## Clients

Create one client record per unique `stateId`.

```json
{
  "clientId": "",
  "stateId": "",
  "name": "",
  "aliases": [],
  "assignedStaff": "",
  "office": "",
  "program": "",
  "status": "",
  "enrolledDate": "",
  "lastContactDate": "",
  "nextFollowUpDate": "",
  "contactOutcome": "",
  "failedContacts": null,
  "educationCertification": "",
  "isVeteran": true,
  "branch": "",
  "careerGoal": "",
  "supportNeeds": "",
  "barriers": "",
  "notes": "",
  "poc": {
    "primaryPhone": "",
    "mobilePhone": "",
    "email": ""
  },
  "goals": [],
  "contacts": [],
  "jobLeads": [],
  "tasks": [],
  "reports": [],
  "sourceRefs": []
}
```

Client field mapping:

- `stateId`: State ID from any report.
- `name`: Individual Name, Individual, or Name.
- `assignedStaff`: Assigned Case Manager, Staff, Case Manager, Created By, or Plan Created By.
- `status`: Prefer IEP `Plan Status`; use closure report to infer `Closed` if a closure exists; otherwise use `"Active Job Search"` when active case/case note activity exists.
- `enrolledDate`: Use IEP `Plan Start Date` or Plan Created Date when no enrollment field exists.
- `lastContactDate`: Most recent Case Notes `Contact Date` or Staff Assisted `Date Assisted`.
- `nextFollowUpDate`: If last contact exists, calculate 14 days after last contact.
- `contactOutcome`: Infer from case note subject/body when possible: `Successful`, `Left VM`, `No Reply`, `Email Sent`, `Unable to Contact`, or `Not recorded`.
- `failedContacts`: Count recent unsuccessful/no-reply/left-VM contact attempts if available; otherwise null.
- `careerGoal`: Use IEP Goal Description or objective text.
- `notes`: Summarize latest case note, closure, IEP, and activity into a short operational note.
- `goals`: Include IEP plan/goal records.

## Staff Assisted Activities

From Staff Assisted Summary, extract every row:

```json
{
  "activityId": "",
  "username": "",
  "stateId": "",
  "individual": "",
  "dateAssisted": "",
  "staff": "",
  "entryType": "",
  "timeSpentAssisting": "",
  "sourceFile": "",
  "sourcePage": null
}
```

Also aggregate per client for dashboard/client notes:

```json
{
  "stateId": "",
  "totalAssistedRecords": null,
  "lastDateAssisted": "",
  "totalTimeSpentAssisting": ""
}
```

## Case Notes

From Case Management - Individual Case Notes, extract both header rows and note body rows.

```json
{
  "caseNoteId": "",
  "userid": "",
  "stateId": "",
  "individual": "",
  "createdBy": "",
  "createDate": "",
  "contactDate": "",
  "contactType": "",
  "lastEditedBy": "",
  "lastEditDate": "",
  "caseSubject": "",
  "caseNotes": "",
  "extractedSections": {
    "narrative": "",
    "assessment": "",
    "planNextSteps": "",
    "actions": []
  },
  "inferredOutcome": "",
  "sourceFile": "",
  "sourcePage": null
}
```

When case notes contain labels such as `Narrative`, `Assessment`, `Plan / Next Steps`, or `Actions`, split those into `extractedSections`.

Map case notes into client `contacts`:

```json
{
  "eventId": "",
  "date": "",
  "scenario": "",
  "method": "",
  "outcome": "",
  "servicesProvided": "",
  "clientAction": "",
  "cmAction": "",
  "nextFollowUpDate": "",
  "generatedNote": ""
}
```

## Employment Closures

From Case Closure Employment Detail Report, extract:

```json
{
  "closureId": "",
  "applicationNumber": "",
  "closeDate": "",
  "stateId": "",
  "name": "",
  "caseManager": "",
  "office": "",
  "employer": "",
  "industry": "",
  "city": "",
  "contact": "",
  "phone": "",
  "jobTitle": "",
  "onet": "",
  "salaryUnit": "",
  "wage": "",
  "hours": "",
  "startDate": "",
  "endDate": "",
  "sourceFile": "",
  "sourcePage": null
}
```

If a client has an employment closure, set dashboard client:

- `status`: `"Employed"` or `"Closed"` depending on the report status context.
- `contactOutcome`: `"Successful"` if employment details are present.
- `notes`: Include employer, job title, wage, hours, start date, and closure date.

## Individual Employment Plans

From Individual Employment Plan reports, extract:

```json
{
  "iepId": "",
  "stateId": "",
  "individualName": "",
  "lwdb": "",
  "office": "",
  "planId": "",
  "planStatus": "",
  "planCreatedDate": "",
  "planStartDate": "",
  "planEditDate": "",
  "iepCloseDate": "",
  "planCreatedBy": "",
  "planLastEditedBy": "",
  "goals": [
    {
      "goalId": "",
      "programOnGoal": "",
      "goalCreateDate": "",
      "goalCreatedBy": "",
      "goalEditedBy": "",
      "goalStatus": "",
      "goalDescription": "",
      "objectives": []
    }
  ],
  "sourceFile": "",
  "sourcePage": null
}
```

If objective columns are present, extract each objective:

```json
{
  "objectiveId": "",
  "objectiveDescription": "",
  "objectiveStatus": "",
  "objectiveCreatedDate": "",
  "objectiveDueDate": "",
  "objectiveCompletionDate": "",
  "serviceCode": "",
  "serviceDescription": ""
}
```

Map IEP goals into dashboard client `goals`:

```json
{
  "title": "",
  "targetDate": "",
  "percent": 0,
  "status": "",
  "updatedAt": "",
  "source": "Individual Employment Plan"
}
```

## Dashboard Import

Populate `dashboardImport.clients` with deduplicated records that can be imported into the app.

Each client in `dashboardImport.clients` must follow this simplified app-compatible shape:

```json
{
  "clientId": "client_stateId_or_slug",
  "name": "",
  "stateId": "",
  "enrolledDate": "",
  "lastContactDate": "",
  "nextFollowUpDate": "",
  "status": "",
  "contactOutcome": "",
  "failedContacts": 0,
  "educationCertification": "",
  "assignedStaff": "",
  "isVeteran": true,
  "branch": "",
  "poc": {
    "primaryPhone": "",
    "mobilePhone": "",
    "email": ""
  },
  "careerGoal": "",
  "supportNeeds": "",
  "barriers": "",
  "notes": "",
  "goals": [],
  "contacts": [],
  "jobLeads": [],
  "tasks": [],
  "reports": []
}
```

Dashboard status values must be one of:

```json
["Active Job Search", "Employed", "Closed", "On Hold", "Pending Intake"]
```

Dashboard contact outcome values must be one of:

```json
["", "Successful", "Left VM", "No Reply", "Email Sent", "Text Sent", "Unable to Contact", "Initial Intake"]
```

If the source value does not exactly match one of those values, map it to the closest value and explain the mapping in `dataQuality.assumptions`.

## Data Quality

Populate:

```json
{
  "dataQuality": {
    "warnings": [
      {
        "message": "",
        "sourceFile": "",
        "sourcePage": null
      }
    ],
    "unmatchedRecords": [
      {
        "reason": "",
        "recordType": "",
        "rawText": "",
        "sourceFile": "",
        "sourcePage": null
      }
    ],
    "assumptions": [
      {
        "field": "",
        "assumption": "",
        "affectedStateIds": []
      }
    ]
  }
}
```

## Final Output Requirement

Return only one valid JSON object. The JSON must be parseable. Do not include markdown fences.
