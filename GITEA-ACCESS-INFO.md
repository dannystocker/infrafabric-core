# InfraFabric Gitea Repository - Access Information

## Repository Details

**Repository URL**: http://localhost:4000/ds-infrafabric2/infrafabric
**Repository Type**: Private
**Status**: Active (all files successfully pushed)

## User Account

**Username**: `ds-infrafabric2`
**Password**: `InfraFabric_DS2025!`
**Email**: `ds-infrafabric2@local.gitea`
**Account Type**: Admin
**Created**: October 30, 2025

## API Access

**API Token**: `0b1956c7043933190790a3847640c7b2126e2eec`
**Token Name**: `full-access`
**Scopes**: All (full repository access)

### Using the API Token

For git operations:
```bash
git clone http://ds-infrafabric2:0b1956c7043933190790a3847640c7b2126e2eec@localhost:4000/ds-infrafabric2/infrafabric.git
```

For API calls:
```bash
curl -H "Authorization: token 0b1956c7043933190790a3847640c7b2126e2eec" \
  "http://localhost:4000/api/v1/repos/ds-infrafabric2/infrafabric"
```

## Repository Contents

```
infrafabric/
├── README.md                                     # Campaign overview
├── marketing/
│   └── page-zero/
│       ├── outreach-targets-master.csv          # 84 contacts (base data)
│       ├── outreach-targets-hyper-targeted.csv  # With research & persona bridges
│       ├── outreach-targets-FINAL-RANKED.csv    # Sorted by priority score
│       └── PRIORITIZATION-REPORT.md             # Strategic analysis
└── GITEA-ACCESS-INFO.md                         # This file
```

## Repository Statistics

- **Total Contacts**: 84 decision-makers
- **Personas**: 7 categories
- **Priority Tiers**: 41 Tier A (buyers), 43 Tier B (amplifiers)
- **Top Priority Contacts**: 13 scored 90+
- **Campaign Duration**: 14 weeks (5 phases)

## Git Remote Configuration

Current remote in local repository:
```
origin  http://ds-infrafabric2:0b1956c7043933190790a3847640c7b2126e2eec@localhost:4000/ds-infrafabric2/infrafabric.git
```

## Web Access

1. Navigate to: http://localhost:4000/
2. Sign in with:
   - Username: `ds-infrafabric2`
   - Password: `InfraFabric_DS2025!`
3. View repository at: http://localhost:4000/ds-infrafabric2/infrafabric

## Quick Commands

### Pull latest changes
```bash
cd /home/setup/infrafabric
git pull origin master
```

### Push new changes
```bash
cd /home/setup/infrafabric
git add .
git commit -m "Your commit message"
git push origin master
```

### Clone to new location
```bash
git clone http://ds-infrafabric2:0b1956c7043933190790a3847640c7b2126e2eec@localhost:4000/ds-infrafabric2/infrafabric.git
```

## Security Notes

- This is a **private repository** - not visible to other gitea users
- API token has **full access** - keep secure
- Password contains special characters - use token for git operations
- All credentials are stored locally only

## Backup Location

ZIP archive also available at:
- **Windows**: `C:\users\setup\downloads\infrafabric-outreach-campaign.zip`
- **WSL**: `/mnt/c/users/setup/downloads/infrafabric-outreach-campaign.zip`

---

**Created**: October 30, 2025
**Gitea Version**: Running on http://localhost:4000
**Local Path**: /home/setup/infrafabric
