# Validator Monitor

A python script for monitoring NEAR Protocol validator performance, tracking blocks and chunks production. Runs by default non stop on a timed interval. If you want to get alerts on your validator underperforming, the easiest way to do it is to use with the `--single-run` & `--quiet` mode, while specifying your validator via `--val-id`. Then have ([urlwatch](https://github.com/thp/urlwatch)) call the script and alert you only when the results displayed changed (which will alert when the epoch turns and you've missed any blocks/chunks or every time your miss count changes during an epoch).

## Prerequisites

- Python 3.6 or higher
- Access to a NEAR RPC endpoint (default: `localhost:3030`)

## Usage

```bash
python3 valmon.py [options]
```

### Options

- `--val-id`: Monitor a specific validator by account ID
- `--quiet`: Show only performance data (requires --val-id)
- `--single-run`: Run once and exit
- `--interval`: Set monitoring interval in seconds (default: 60)

### Examples

Monitor all validators:
```bash
python3 valmon.py
```

Monitor specific validator:
```bash
python3 valmon.py --val-id example.near
```

Quick status check:
```bash
python3 valmon.py --val-id example.poolv1.near --quiet --single-run
```

Custom interval:
```bash
python3 valmon.py --interval 300  # Check every 5 minutes
```

## Output

### Full Mode
Shows detailed information about:
- Missing blocks per validator
- Missing chunks per validator
- Timestamp for each check
- Connection status

### Quiet Mode
Displays concise status:
- Number of missed blocks
- Number of missed chunks

## Error Handling

The script handles various error conditions:
- RPC connection failures
- Invalid validator IDs
- Network interruptions

Press Ctrl+C to stop the monitoring process.

## License
CC 4.0
