# Dashboard Workbook Reference

Source workbook:

- `/Users/mariomcmichael/Desktop/DVOP_Client_Dashboard.xlsx`

## Workbook Structure To Mirror

The web dashboard should follow the same operating model as the workbook.

Workbook tabs:

- `Dashboard`
- `Case Note Generator`
- `Client Record`
- `Resources & Quick Links`
- `Prompts & References`
- `_Lists`

Recommended web sections:

- Dashboard
- Case Note Generator
- Client Record
- Resources & Quick Links
- Prompts & References
- Settings / Lists

## Dashboard Layout

The dashboard should feel close to the workbook:

1. Header band with program, office, case manager, report date, and legend.
2. POC information area.
3. Caseload summary cards.
4. Active caseload table.
5. Color-coded rows and urgency indicators.
6. Frozen or sticky table header.

### Summary Cards

The workbook uses four primary caseload metrics:

- Total Active Clients
- Currently Employed
- Active Job Search
- Cases Closed YTD

The web dashboard should add two useful operational metrics:

- Follow-Ups Due
- Overdue Contacts

### Active Caseload Table

The web dashboard should mirror these columns:

- `#`
- `Name`
- `State ID`
- `Enrolled`
- `Last Contact`
- `Status`
- `Next Follow-Up`
- `Days W/O Contact`
- `Contact Outcome`
- `Failed Contacts`
- `Education / Certification`
- `POC / Assigned`
- `Veteran`
- `Branch`
- `POC`
- `Notes`

Recommended web behavior:

- Click a row to open the client record.
- Keep the header sticky while scrolling.
- Use compact row height with expandable notes.
- Show urgent follow-up flags without making the table visually noisy.
- Keep long POC and notes text readable through truncation plus detail view.

## Dashboard Logic

### Next Follow-Up

The workbook calculates next follow-up as:

```text
Last Contact + 14 days
```

The web dashboard should calculate this automatically unless a custom next follow-up date is entered.

### Days Without Contact

The workbook calculates days without contact as:

```text
Today - Last Contact
```

Recommended thresholds:

- `0-14 days`: current
- `15-30 days`: follow-up needed
- `31+ days`: urgent

### Status Colors

The workbook uses conditional formatting. The web version should keep the same meaning:

- Green: Employed
- Amber: Active Job Search
- Red: Overdue / no contact
- Gray: Closed
- Blue or neutral: On Hold / Pending Intake

### Contact Outcome Colors

Recommended outcome flags:

- Successful: green
- Left VM: amber
- No Reply: red
- Email Sent: blue
- Text Sent: blue
- Unable to Contact: red

### Failed Contacts

The workbook highlights failed contacts at:

```text
Failed Contacts >= 3
```

The web dashboard should surface this as an escalation flag.

## Client Record Pattern

The workbook client record includes:

- Point of contact
- Branch of service
- Veteran status
- Notes
- Individual Employment Plan goals
- Contact log
- Job leads sent
- Tasks and correspondence

The web client record should use tabs:

- Overview
- Intake
- IEP / Goals
- Contact Log
- Job Leads
- Tasks
- Resources
- Reports

## IEP / Goals

Default goals from the workbook:

- Obtain Employment Aligned with Career Goals
- Resume Development
- Interview Preparation Strategy
- Follow-Up / 30-Day Assessment
- 90-Day Employment Retention

Recommended fields:

- Goal / Objective
- Target Date
- Percent Complete
- Status
- Last Updated

## Contact Log

The workbook contact log fields:

- Date
- Type
- Method / By
- Summary / Outcome
- Next Steps
- Follow-Up Date

The web version should feed this from the case note generator and contact event JSON.

## Job Leads Sent

The workbook job lead fields:

- Date Sent
- Position / Title
- Employer
- Wage / Salary
- Application Method
- Source
- Outcome
- Follow-Up Date

The web version should connect this to the existing job leads/resources in the workspace.

## Tasks And Correspondence

The workbook uses task fields:

- Task / Action Item
- Priority
- Due Date
- Assigned To
- Status
- Completed Date
- Notes

These should become real task records attached to the client.

## Resources & Quick Links

The workbook groups resources into:

- Work Tools
- Job Search Links
- Recurring Reports

The web version should keep those groupings and allow JSON updates for links.

## Prompts & References

The workbook includes scripts and workflow steps for:

- Employment verified with employer confirmation
- Employment verified without employer confirmation / additional resource needed
- Unable to contact
- Successful contact / follow-up
- Unsuccessful contact / follow-up

These should serve as reusable templates inside the case note generator and contact workflow.

## Lists / Dropdowns

The workbook `_Lists` tab defines controlled values.

Statuses:

- Active Job Search
- Employed
- Closed
- On Hold
- Pending Intake

Contact types:

- Initial Intake
- Follow-Up
- 30-Day Assessment
- 90-Day Assessment
- Job Lead Sent
- Employment Verification
- Case Closure

Priorities:

- High
- Medium
- Low

Task statuses:

- To Do
- In Progress
- Complete
- Deferred

Branches:

- Army
- Navy
- Air Force
- Marine Corps
- Coast Guard
- Space Force
- National Guard
- Reserves

## JSON Shape For Dashboard Imports

```json
{
  "clients": [
    {
      "clientId": "client_001",
      "name": "Last, First",
      "stateId": "0000000",
      "enrolledDate": "2026-05-05",
      "lastContactDate": "2026-05-05",
      "status": "Active Job Search",
      "contactOutcome": "Successful",
      "failedContacts": 0,
      "educationCertification": "Resume uploaded; CDL interest",
      "assignedStaff": "DVOP McMichael",
      "isVeteran": true,
      "branch": "Army",
      "poc": {
        "primaryPhone": "",
        "mobilePhone": "",
        "email": ""
      },
      "notes": "Client remains engaged and agreed to review job leads."
    }
  ]
}
```

## Design Direction

The web version should feel like a disciplined case management dashboard, not a marketing website.

Keep:

- Dense but readable tables
- Clear status colors
- Compact summary cards
- Sticky navigation
- Practical filters
- Fast row-to-client navigation
- JSON import/export access

Avoid:

- Oversized hero sections
- Decorative card-heavy layouts
- One-page landing page structure
- Hiding the caseload behind too many clicks
