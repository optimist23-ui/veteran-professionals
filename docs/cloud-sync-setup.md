# Cloud Sync Setup

This app is now cloud-ready with Supabase. It still works locally if cloud settings are blank.

## 1. Create Supabase Project

1. Go to Supabase.
2. Create a new project.
3. Copy the project URL.
4. Copy the anon/public key.

Only use the anon/public key in the browser. Do not paste the service-role key into this project.

## 2. Run Database Schema

Open Supabase SQL Editor and run:

```text
docs/supabase-cloud-schema.sql
```

This creates:

- `dvop_dashboard_states`
- Row Level Security
- Policies so each signed-in user only sees their own dashboard state
- An update timestamp trigger

## 3. Create Your Login

In Supabase Auth, create a user with your email and password, or use Supabase's normal sign-up flow.

## 4. Add Project Credentials

Edit:

```text
cloud-config.js
```

Fill in:

```js
window.DVOP_CLOUD_CONFIG = {
  supabaseUrl: "https://YOUR-PROJECT.supabase.co",
  supabaseAnonKey: "YOUR-PUBLIC-ANON-KEY",
  appKey: "dvop-command-center-main"
};
```

## 5. Use In The App

1. Open the app.
2. Enter email and password in the top bar.
3. Click `Sign In`.
4. Click `Sync`.

After that, changes save to local storage and cloud storage. Open the same hosted app on another device, sign in, and the dashboard state will load.

## Notes

- This first cloud version syncs the whole dashboard state as one JSON document.
- That is the fastest reliable way to get all devices synced.
- Later, the app can split this into separate cloud tables for clients, notes, reports, tasks, and resources.
