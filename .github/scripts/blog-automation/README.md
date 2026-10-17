# AI Blog Automation

This workflow creates two bilingual (Persian/English) design-blog articles per week, with two AI-generated images per article. It uses the existing article page as a visual template and adds a card to both the homepage and `/blog/`, then updates `sitemap.xml`.

## Install

1. Copy these files into the repository without removing existing site assets.
2. In GitHub, open **Settings → Secrets and variables → Actions → New repository secret**.
3. Create a secret named `OPENAI_API_KEY` containing an API key with access to the configured text and image models.
4. Open **Actions → AI Blog Publisher → Run workflow** for a first manual test.
5. Inspect the resulting commit and deployed site. Scheduled runs are Monday/Thursday at 06:30 UTC; GitHub scheduled jobs can start late.

## Important

- The workflow only commits when generation and validation finish successfully.
- API usage is billable. Each run requests one text completion and two image generations.
- Change `OPENAI_TEXT_MODEL` / `OPENAI_IMAGE_MODEL` in the workflow if your account uses different model access.
- Slugs are English and stable. Existing article folders and images are left untouched.
- The first manual run is recommended before relying on the schedule.
