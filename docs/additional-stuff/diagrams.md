# 🗂️ Project Watchdog Workflow Diagram

This diagram shows the flow of the **AWS Recon Scanner v5** workflow from start to finish. Think of it as your “map” of the pipeline.

            ┌───────────────┐
            │   Webhook     │
            │ /scan?target= │
            │  <IP/Host>    │
            └──────┬────────┘
                   │
                   ▼
            ┌───────────────┐
            │    Regex      │
            │ Extract target│
            └──────┬────────┘
                   │
                   ▼
            ┌───────────────┐
            │ Execute Scan  │
            │ aws-scan      │
            └──────┬────────┘
                   │
                   ▼
            ┌───────────────┐
            │  Wait / If    │
            │  Retry logic  │
            └──────┬────────┘
      ┌────────────┴─────────────┐
      │                          │
      ▼                          ▼
┌───────────────┐           ┌───────────────┐
│ Get Scan      │           │ Merge Results │
│ Results       │           └──────┬────────┘
└──────┬────────┘                  │
▼                           ▼
┌───────────────┐           ┌───────────────┐
│ AI Report     │──────────>│ Convert to File│
│ Generation    │           └──────┬────────┘
└──────┬────────┘                  │
▼                           ▼
┌───────────────┐           ┌───────────────┐
│ Upload Report │<──────────│ Markdown .md  │
│ to NAS /      │           │ File Saved    │
│ Local Storage │           └───────────────┘
└───────────────┘
