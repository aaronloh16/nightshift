# Nightshift

Automated overnight content pipeline: monitors trending AI/dev topics, drafts tweets, delivers a morning digest.

## Stack
- **Runtime**: Python 3.12+
- **Integrations**: Composio SDK (GitHub, Reddit, Telegram)
- **LLM**: Claude API for tweet drafting
- **Scheduler**: cron or similar for overnight runs

## Architecture
1. **Collectors** — pull trending content from GitHub (trending repos), Reddit (r/LocalLLaMA, r/MachineLearning, r/programming), Hacker News (public API, no Composio needed)
2. **Drafter** — Claude API call: feed trending topics + writing style examples → draft tweets
3. **Delivery** — Telegram bot sends morning digest with drafted tweets
4. **v2: Repo Gen** — GitHub API via Composio to create repos + READMEs from ideas

## Composio Integrations
- GitHub API — trending repos + repo creation (v2)
- Reddit API — subreddit hot posts
- Telegram Bot — digest delivery
- OAuth handled by Composio (main value prop)

## Dev Workflow
```bash
pip install -e ".[dev]"        # install with dev deps
python -m nightshift.main      # run the pipeline
pytest                         # run tests
```

## Key Decisions
- Keep each collector as its own module for easy add/remove
- HN uses public API directly (no Composio needed)
- Store style examples in `config/style.yaml`
- `.env` for API keys (COMPOSIO_API_KEY, ANTHROPIC_API_KEY)
