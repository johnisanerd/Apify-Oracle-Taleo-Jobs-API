# Oracle Taleo Jobs API: Oracle Job Postings as JSON, from Python or MCP

This repo shows two ways to use the [Oracle Fusion Recruiting and Taleo Jobs API](https://apify.com/johnvc/oracle-taleo-jobs-api?fpr=9n7kx3) on Apify: a Python quick start managed with `uv`, and MCP install guides for five AI clients ([Claude Cowork Desktop](https://claude.ai/referral/uIlpa7nPLg), [Claude Code](https://claude.ai/referral/uIlpa7nPLg), Claude on the web, Cursor, and ChatGPT). Cowork and Claude Code both start with a free trial.

Give the API a company name, like `Oracle` or `Chase`, or an Oracle careers URL, and it returns every live job posting as structured JSON: titles, every location, exact ISO posted dates, requisition IDs, category and organization, employer-published skills, latitude and longitude, extracted pay ranges, and direct apply URLs. It reads both Oracle recruiting products, current Oracle Fusion Recruiting (Cloud CX) boards and legacy Oracle Taleo boards. You do not need board credentials or a proxy.

Input schema: [full parameter reference](https://apify.com/johnvc/oracle-taleo-jobs-api/input-schema?fpr=9n7kx3)

## Video walkthrough

[![Apify MCP setup walkthrough](https://img.youtube.com/vi/jREWahDGhJM/0.jpg)](https://www.youtube.com/watch?v=jREWahDGhJM)

### Text walkthrough

Looking for a Taleo API usually leads to Oracle's authenticated Taleo Business Edition web services, which need customer credentials and exist to create and update requisitions rather than to read public listings. This Actor takes the other path: it reads the same public candidate feed the careers page itself uses. The two main inputs are `companies` (plain names or website domains) and `startUrls` (an Oracle Fusion Recruiting or Oracle Taleo careers URL when you already know it); the main outputs are `title`, `primaryLocation`, `postedDate`, `requisitionId`, `skills`, `salaryMin` and `salaryMax`, `descriptionMarkdown`, and `applyUrl`, one row per job. The `companies` input matters more than it sounds, because Oracle careers boards live on hosts like `eeho.fa.us2.oraclecloud.com`, where `eeho` is an opaque tenant code rather than a company name, so a URL-only tool is useless until you already know the answer. Turn on `discoverOnly` and the same lookup returns a directory instead: one row per career site with tenant, site number, careers URL, direct jobs API URL, and a live open-job count. A concrete example: run it against Oracle's own board and you get thousands of live openings with the employer's own skill tags and coordinates attached, ready to feed a job board or a scheduled hiring monitor.

## Python quick start

1. Get your free Apify API key: https://apify.com?fpr=9n7kx3
2. Clone this repo, then:

```bash
cp .env.example .env   # paste your APIFY_API_TOKEN inside
uv sync
uv run python oracle-taleo-jobs-api-example.py
```

The default run pulls 5 jobs from a single Oracle Fusion Recruiting board, so your first call costs a fraction of a cent. The other recipes:

```bash
uv run python oracle-taleo-jobs-api-example.py --example discover_sites
uv run python oracle-taleo-jobs-api-example.py --example taleo_jobs
uv run python oracle-taleo-jobs-api-example.py --example new_postings
uv run python oracle-taleo-jobs-api-example.py --example markdown_for_agents
```

If you do not have `uv` yet: `curl -LsSf https://astral.sh/uv/install.sh | sh`

## Oracle Fusion Recruiting and Oracle Taleo jobs in one API

Oracle runs two recruiting products at once. Fusion Recruiting, also sold as Oracle Recruiting Cloud, is the current one and lives on `oraclecloud.com` hosts. Taleo is the older product Oracle acquired in 2012, it lives on `taleo.net` hosts, and it is still in service at plenty of organizations, especially in government, healthcare, and higher education. This API reads both, and the `product` input lets you target `fusion`, `taleo`, or `both`.

Every Oracle Fusion host shape is handled: the regional form (`eeho.fa.us2.oraclecloud.com`), the regionless form (`jpmc.fa.oraclecloud.com`), and the named form (`somecollege-abc123.fa.ocs.oraclecloud.com`).

## Find any company's Oracle careers site without a tenant code

Oracle tenant codes are opaque, so the practical entry point is a company name. Put `Oracle` or `alleghenycollege.edu` into `companies` and the API resolves it to the Oracle careers boards that company actually runs, then reads the employer's own site directory to label each one.

It also filters the decoys. Oracle tenants publish backup and reference-only sites right beside the real ones: Oracle's own tenant publishes six career sites, five of which are inactive placeholders with names like "FOR REFERENCE ONLY" and "Baseline DO NOT UPDATE". `verifyLive` checks each site's published status and its live job count before returning it, and `includeInactive` brings the placeholders back when you are auditing a tenant's full directory.

## Track Oracle job postings on a schedule

Set `postedAfter` to an ISO date and you get only the roles published on or after it. Save the input as an Apify task, put it on a daily or weekly schedule, and diff on `requisitionId` to catch new roles the day they go live. The `new_postings` recipe in this repo does exactly that with a rolling 14 day window.

## Job descriptions in Markdown for AI agents

`descriptionFormat` returns the description as original HTML, clean plain text, or Markdown. Markdown is the one to pick when the output feeds an AI agent or a retrieval index, because headings and lists survive instead of arriving as raw markup or a flattened wall of text. The `skills` array and the primary location's `latitude` and `longitude` come from the employer's own requisition record, so those are published values rather than model guesses.

## Map the Oracle ATS market: which companies run Taleo and which run Oracle Recruiting Cloud

Turn on `discoverOnly` and the API skips job collection entirely, returning one row per career site: `company`, `tenant`, `host`, `siteNumber`, `siteName`, `statusCode`, `careersUrl`, `apiUrl`, and a live `totalJobs` count. That is an install-base map with working URLs and current volumes attached, which is a different thing from a static list of customer names. Use it to size the Oracle ATS market, then run the boards you care about in a second pass.

## Recipes

Each recipe ships as a `--example` in `oracle-taleo-jobs-api-example.py`, and each one has a published task page on Apify. Run the command locally, or open the task page and run it in the browser.

| Recipe | What it answers | Command | Task page |
|---|---|---|---|
| Jobs from one board | Every open role on a single Oracle Fusion Recruiting site | `--example default` | [Export Oracle Recruiting Cloud Jobs to CSV or JSON](https://apify.com/johnvc/oracle-taleo-jobs-api/examples/oracle-recruiting-cloud-jobs-export?fpr=9n7kx3) |
| Career-site discovery | Which Oracle boards does this company run, and how many roles are on each | `--example discover_sites` | [Find Any Company's Oracle Careers Site by Name](https://apify.com/johnvc/oracle-taleo-jobs-api/examples/find-oracle-careers-site-by-company-name?fpr=9n7kx3) |
| Taleo jobs, no login | Read a public Oracle Taleo board without credentials | `--example taleo_jobs` | [Pull Taleo Job Postings via API, No Login Needed](https://apify.com/johnvc/oracle-taleo-jobs-api/examples/taleo-job-postings-api-no-login?fpr=9n7kx3) |
| New postings only | What went live in the last 14 days | `--example new_postings` | [Monitor New Oracle and Taleo Job Postings Daily](https://apify.com/johnvc/oracle-taleo-jobs-api/examples/monitor-oracle-taleo-job-postings-daily?fpr=9n7kx3) |
| Markdown for agents | Descriptions an LLM can actually read, plus employer skill tags | `--example markdown_for_agents` | [Oracle HCM Job Data for Claude and ChatGPT via MCP](https://apify.com/johnvc/oracle-taleo-jobs-api/examples/oracle-hcm-job-data-mcp-server?fpr=9n7kx3) |

Two more task pages have no local helper yet: [Backfill a Job Board with Oracle and Taleo Listings](https://apify.com/johnvc/oracle-taleo-jobs-api/examples/oracle-taleo-job-board-feed-api?fpr=9n7kx3), which reads several boards in one run, and [Map Which Companies Run Oracle Recruiting or Taleo](https://apify.com/johnvc/oracle-taleo-jobs-api/examples/companies-using-oracle-recruiting-and-taleo?fpr=9n7kx3), which returns the directory instead of the jobs. Another ten each cover a single employer's Taleo board, and two cover the API in Chinese. All of them are on the [Examples tab](https://apify.com/johnvc/oracle-taleo-jobs-api/examples?fpr=9n7kx3).

Tip: save any of these inputs as a task in the Apify Console and put it on a Schedule, daily or weekly, so the feed stays fresh without a manual run. Pair the schedule with a diff on `requisitionId` and you have a hiring monitor for any Oracle employer.

## Usage examples

Basic, one Oracle Fusion Recruiting board, kept cheap:

```json
{
  "startUrls": [
    { "url": "https://eeho.fa.us2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_45001" }
  ],
  "maxJobsPerSite": 5,
  "includeDetails": true,
  "descriptionFormat": "text"
}
```

Advanced, resolve a company by name and pull recent engineering roles as Markdown:

```json
{
  "companies": ["Oracle"],
  "product": "fusion",
  "searchText": "engineer",
  "locationFilter": "United States",
  "postedAfter": "2026-08-01",
  "descriptionFormat": "markdown",
  "maxJobsPerSite": 25,
  "maxSites": 3,
  "includeDetails": true,
  "detailConcurrency": 5,
  "verifyLive": true
}
```

Directory only, no jobs:

```json
{
  "companies": ["Oracle", "Chase"],
  "discoverOnly": true,
  "includeInactive": false,
  "maxSites": 10
}
```

## Input parameters

Every field is optional. An empty run returns one explanatory row and exits cleanly rather than failing.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `companies` | array | empty | Company names or website domains, resolved to the Oracle careers boards that company runs. |
| `startUrls` | array | empty | Oracle Fusion Recruiting or Oracle Taleo careers URLs to read directly, skipping resolution. |
| `discoverAll` | boolean | `false` | Enumerate Oracle careers boards in bulk instead of resolving a named list. |
| `discoverOnly` | boolean | `false` | Return one row per career site and skip job collection entirely. |
| `product` | enum | `both` | Limit the run to `fusion`, `taleo`, or `both`. |
| `searchText` | string | empty | Keyword filter, run through the board's own search. |
| `locationFilter` | string | empty | Location filter, run through the board's own location search. |
| `postedAfter` | string | empty | ISO date. Return only jobs posted on or after it. Most accurate with `includeDetails` on. |
| `maxJobsPerSite` | integer | `0` | Cap on jobs per career site. `0` means every job. |
| `maxSites` | integer | `25` | Cap on career sites processed in one run, 1 to 2000. |
| `includeDetails` | boolean | `true` | Fetch each job's full detail record. Turn off for a fast, cheap, list-only pass. |
| `descriptionFormat` | enum | `both` | `html`, `text`, `markdown`, or `both` for all three. |
| `detailConcurrency` | integer | `5` | Parallel detail requests, 1 to 10. |
| `verifyLive` | boolean | `true` | Check each site's live job count before returning it. |
| `includeInactive` | boolean | `false` | Also return backup and reference-only sites. |
| `crawlDepth` | integer | `1` | How many index snapshots to combine when discovering boards, 1 to 4. |

## Output fields

One row per job (`resultType` is `job`): `product`, `title`, `company`, `tenant`, `host`, `siteNumber`, `siteName`, `siteCode`, `siteUrlName`, `careerSection`, `portalId`, `sourceUrl`, `url`, `applyUrl`, `jobId`, `requisitionId`, `category`, `organization`, `department`, `businessUnit`, `legalEmployer`, `jobFamily`, `jobFunction`, `workerType`, `contractType`, `managerLevel`, `jobSchedule`, `jobShift`, `jobType`, `studyLevel`, `workplaceType`, `hotJob`, `locationsText`, `primaryLocation`, `secondaryLocations`, `country`, `countryCode`, `latitude`, `longitude`, `postedDate`, `postedDateTime`, `postingEndDate`, `shortDescription`, `descriptionHtml`, `descriptionText`, `descriptionMarkdown`, `qualifications`, `responsibilities`, `skills`, `salaryText`, `salaryMin`, `salaryMax`, `salaryCurrency`, `totalJobsOnSite`, `scrapedAt`.

In `discoverOnly` mode the row is a career site (`resultType` is `site`) with `company`, `tenant`, `host`, `siteNumber`, `siteName`, `statusCode`, `careersUrl`, `apiUrl`, `totalJobs`, `status`, `siteSource`, and `discoveredAt`.

A retired Taleo board, or a company that turns out not to run Oracle at all, produces a labelled row carrying `errorType` and `errorMessage`. The run keeps going and those rows are never charged.

```json
{
  "resultType": "job",
  "product": "fusion",
  "title": "Lead Principal Platform Software Engineer",
  "company": "Oracle",
  "tenant": "eeho",
  "siteNumber": "CX_45001",
  "applyUrl": "https://eeho.fa.us2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/jobsearch/job/342237/apply",
  "requisitionId": "260005TT",
  "category": "Product and Research",
  "organization": "Oracle Cloud Infrastructure",
  "workplaceType": "Hybrid",
  "primaryLocation": "Bengaluru, India",
  "secondaryLocations": ["Hyderabad, India"],
  "countryCode": "IN",
  "latitude": 12.99838,
  "longitude": 77.73981,
  "postedDate": "2026-08-10",
  "skills": ["C Programming Language", "C++ (Programming Language)", "Cloud Architecture"],
  "descriptionMarkdown": "## About the role\n\n- Design and operate distributed services at scale\n",
  "totalJobsOnSite": 2288
}
```

## People also search for

**What is Taleo?**
Taleo is Oracle's older recruiting product, acquired in 2012 and still running at many organizations. Customer boards live on `taleo.net` hosts, which is why `taleo.net` shows up in so many application URLs. This API reads those public boards directly.

**Is Taleo an ATS?**
Yes. Taleo is an applicant tracking system, and so is its successor, Oracle Fusion Recruiting. Both publish a public candidate-facing job board, and both are covered here through the `product` input.

**What is Oracle Recruiting Cloud?**
It is Oracle's current name for Fusion Recruiting, the recruiting module of Oracle Cloud HCM. If a careers page lives on an `oraclecloud.com` host, that employer is on Oracle Recruiting Cloud, and the `fusion` product setting targets it.

**Does Oracle have a REST API for job postings?**
Oracle's official HCM REST API is built for authenticated enterprise HR integrations and needs tenant credentials. The public candidate feed that backs every Oracle careers page is a separate thing, and that is what this API reads. No tenant credentials are involved.

**Which companies use Oracle Taleo, and can I get a list?**
Run `discoverOnly` mode. Instead of a static list of names, you get one row per live career site with the tenant, the public careers URL, the direct jobs API URL, and a current open-job count.

**How do I connect Oracle HCM job data to Claude or ChatGPT?**
Through MCP. The five install sections below wire the hosted Apify MCP server, with just this Actor preloaded, into [Claude Cowork Desktop or Claude Code](https://claude.ai/referral/uIlpa7nPLg) (both free to try), Claude on the web, Cursor, or ChatGPT. Ask the assistant for a company's Oracle openings and it runs the API for you.

**I only know the company name, not its Oracle URL. Can I still use this?**
Yes, and that is the point. Oracle tenant codes are opaque strings, so a name-based lookup is the only practical way in for most employers.

---

The Actor's MCP server URL, used in all five install sections below:

```
https://mcp.apify.com/?tools=actors,docs,johnvc/oracle-taleo-jobs-api
```

The `actors` and `docs` tools let the assistant discover and read Apify docs, while preloading just this one Actor keeps the tool list small. Auth is either OAuth in the browser when offered, or your Apify API token (the same `APIFY_API_TOKEN` secret used by the Python example). Get a token at https://console.apify.com/settings/integrations and a free Apify account at https://apify.com?fpr=9n7kx3 .

## Install in Claude Cowork Desktop

![Install in Claude Cowork Desktop](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_claude_desktop.png)

Cowork is the desktop app's automation mode. To give it the Oracle Fusion Recruiting and Taleo Jobs API as a tool, add the Apify MCP server as a connector.

1. Open the Claude desktop app and go to **Settings → Connectors** (or **Settings → Developer → Edit Config** to edit `claude_desktop_config.json` directly).
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
2. Add the Apify MCP server, preloaded with only this Actor:

```json
{
  "mcpServers": {
    "apify": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://mcp.apify.com/?tools=actors,docs,johnvc/oracle-taleo-jobs-api"
      ]
    }
  }
}
```

3. Restart the app. When Cowork first calls the tool, complete the OAuth prompt in your browser, or add your Apify API token in the connector settings to skip OAuth.
4. In a Cowork chat, confirm the tool is available and ask it to run the Oracle Taleo Jobs API.

Download the desktop app and start a free trial: https://claude.ai/referral/uIlpa7nPLg
More help: https://docs.apify.com/platform/integrations/claude-desktop

## Install in Claude Code

![Install in Claude Code](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_claude_code.png)

Claude Code is the command-line tool. Add the Actor's MCP server with one command:

```bash
claude mcp add --transport http apify \
  "https://mcp.apify.com/?tools=actors,docs,johnvc/oracle-taleo-jobs-api"
```

To use a token instead of browser OAuth:

```bash
claude mcp add --transport http apify \
  "https://mcp.apify.com/?tools=actors,docs,johnvc/oracle-taleo-jobs-api" \
  --header "Authorization: Bearer YOUR_APIFY_TOKEN"
```

Then verify with `claude mcp list`, or run `/mcp` inside a session. Ask Claude Code to call the Oracle Taleo Jobs API.

Try Claude Code free: https://claude.ai/referral/uIlpa7nPLg
Claude Code MCP docs: https://code.claude.com/docs/en/mcp

## Install in Claude (website)

![Install in Claude (website)](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_claude_ai.png)

On claude.ai you add Apify as a connector, then enable just this Actor's tool.

1. Go to **Settings → Connectors → Browse connectors** and search for **Apify MCP server**. Install it (enable or update if prompted).
2. When connecting, authenticate with your Apify API token, and enable the tool `johnvc/oracle-taleo-jobs-api`.
3. In any chat, open **+ → Connectors** and turn on **Apify**.
4. Alternatively, choose **Add custom connector** and paste the full MCP URL `https://mcp.apify.com/?tools=actors,docs,johnvc/oracle-taleo-jobs-api`, using OAuth when prompted.
5. Ask Claude to run the Oracle Taleo Jobs API.

Open Claude on the web: https://claude.ai

## Install in Cursor

![Install in Cursor](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_cursor.png)

Cursor reads MCP servers from a project file at `.cursor/mcp.json`.

1. In your project, create `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "apify": {
      "url": "https://mcp.apify.com/?tools=actors,docs,johnvc/oracle-taleo-jobs-api"
    }
  }
}
```

2. If you prefer token auth over browser OAuth, add a header:

```json
{
  "mcpServers": {
    "apify": {
      "url": "https://mcp.apify.com/?tools=actors,docs,johnvc/oracle-taleo-jobs-api",
      "headers": { "Authorization": "Bearer YOUR_APIFY_TOKEN" }
    }
  }
}
```

3. Open **Cursor → Settings → MCP** and confirm the **apify** server is connected (green dot).
4. In Composer or Chat, ask Cursor to call the Oracle Taleo Jobs API.

New to Cursor? Get it here: https://cursor.com/referral?code=XQP4VBLI3NNX

## Install in ChatGPT

![Install in ChatGPT](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_ChatGPT.png)

ChatGPT connects to the Apify MCP server through Developer mode (available on ChatGPT Pro, Plus, Business, Enterprise, and Education plans).

1. Click your profile icon, then go to **Settings > Apps**. If you do not see a **Create app** button, open **Advanced settings** and enable **Developer mode**.
2. Click **Create app** and fill out the form:
   - **Name:** Apify
   - **MCP Server URL:** `https://mcp.apify.com/?tools=actors,docs,johnvc/oracle-taleo-jobs-api`
   - **Authentication:** OAuth
3. Click **Create** and authorize the connection with Apify.
4. To use the app in a conversation, click **+** in the chat, choose **Developer mode**, and select **Apify**.

More help: https://docs.apify.com/platform/integrations/mcp

---

[View the Oracle Fusion Recruiting and Taleo Jobs API on Apify Store](https://apify.com/johnvc/oracle-taleo-jobs-api?fpr=9n7kx3)

Made with care by [johnvc on Apify](https://apify.com/johnvc?fpr=9n7kx3).

Last Updated: 2026.09.04
