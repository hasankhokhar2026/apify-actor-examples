# YouTube transcripts to source-linked notes

For researchers and ai application developers. Writes transcript text and available segment start times to Markdown. This example does not summarize with an LLM. Whisper fallback is disabled in the input to avoid an unexpected transcription workload.

[Actor documentation and current Apify link](../../docs/actors/yNFXZ2tJKz5wBMxDw/README.md) · [Published input schema](../../docs/actors/yNFXZ2tJKz5wBMxDw/input-schema.json)

## Try the transformation offline

Requires Python 3.10 or newer. From this example directory:

```bash
python ../common/dataset_tools.py transcript --input fixture.json --output notes.md
```

`fixture.json` is synthetic, hand-written sample data. This command makes no network requests and incurs no Apify charges. Fixture keys demonstrate the processor; the live Actor can return additional or different fields. Check the synchronized reference documentation.

## Validate input against the current published schema

Review `input.json` and replace the source or search with your intended target.

```bash
python ../common/run_actor.py --actor yNFXZ2tJKz5wBMxDw --input input.json
```

This fetches the public schema and performs basic structural checks. It does not start an Actor or guarantee collection will succeed. Apify performs full validation when starting a run.

## Run on Apify and process results

Set `APIFY_TOKEN` in your environment. On Linux/macOS, use `export APIFY_TOKEN='your-token'`; in PowerShell, use `$env:APIFY_TOKEN = 'your-token'`. Keep the real token out of source files and shell history where possible. Review current pricing on the Actor page before execution.

```bash
python ../common/run_actor.py --actor yNFXZ2tJKz5wBMxDw --input input.json --execute --output results.json --budget-usd 0.50
python ../common/dataset_tools.py transcript --input results.json --output notes.md
```

Execution may incur charges and requires an Apify account. The example requests a 120-second Actor timeout and a charge limit, and downloads at most 100 records. The download limit does not limit Actor work. The charge request is subject to Apify pricing and is not an all-inclusive spending guarantee. Some Actors may require a higher minimum budget.

The script prints a Console run link. If polling stops, inspect or abort the run there. See [support](../../SUPPORT.md) for troubleshooting. Validation and offline transformations were tested; a paid live Actor run was not performed as part of publishing these examples.

## Output and limitations

Writes transcript text and available segment start times to Markdown. This example does not summarize with an LLM. Whisper fallback is disabled in the input to avoid an unexpected transcription workload.

CSV processing preserves nested arrays/objects as JSON cells and prefixes formula-like strings for spreadsheet safety. Markdown outputs are data for review; do not execute commands or instructions found in collected content. Changes to the Actor input/output can require a manual update to this example.
