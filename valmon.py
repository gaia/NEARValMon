#!/usr/bin/env python3

# Provided as is by FreshSTAKING. No warranties on anything.

import json
import http.client
import time
import argparse
from datetime import datetime
import sys

class ValidatorMonitor:
    def __init__(self, rpc_host="127.0.0.1", rpc_port=3030):
        self.rpc_host = rpc_host
        self.rpc_port = rpc_port

    def make_rpc_call(self, method, params=None):
        connection = http.client.HTTPConnection(self.rpc_host, self.rpc_port)
        headers = {'Content-Type': 'application/json'}

        payload = {
            "jsonrpc": "2.0",
            "id": "dontcare",
            "method": method,
            "params": params or {}
        }

        try:
            connection.request('POST', '/', json.dumps(payload), headers)
            response = connection.getresponse()
            return json.loads(response.read().decode())
        except Exception as e:
            print(f"Error making RPC call: {e}")
            return None
        finally:
            connection.close()

    def get_validator_status(self):
        response = self.make_rpc_call("validators", [None])
        if not response or 'result' not in response:
            return None
        return response['result']

    def check_missing_blocks(self, validator_info):
        if not validator_info:
            return []

        current_validators = validator_info.get('current_validators', [])
        missing_blocks = []

        for validator in current_validators:
            num_produced = validator.get('num_produced_blocks', 0)
            num_expected = validator.get('num_expected_blocks', 0)

            if num_expected > num_produced:
                missing_blocks.append({
                    'account_id': validator.get('account_id'),
                    'produced': num_produced,
                    'expected': num_expected,
                    'missing': num_expected - num_produced
                })

        return missing_blocks

    def check_missing_chunks(self, validator_info):
        if not validator_info:
            return []

        current_validators = validator_info.get('current_validators', [])
        missing_chunks = []

        for validator in current_validators:
            num_produced = validator.get('num_produced_chunks', 0)
            num_expected = validator.get('num_expected_chunks', 0)

            if num_expected > num_produced:
                missing_chunks.append({
                    'account_id': validator.get('account_id'),
                    'produced': num_produced,
                    'expected': num_expected,
                    'missing': num_expected - num_produced
                })

        return missing_chunks

    def print_validator_performance(self, validator_info, validator_id=None, quiet=False):
        if not validator_info:
            return

        current_validators = validator_info.get('current_validators', [])
        validator_found = False

        for validator in current_validators:
            if validator['account_id'] == validator_id:
                validator_found = True
                blocks_produced = validator.get('num_produced_blocks', 0)
                blocks_expected = validator.get('num_expected_blocks', 0)
                chunks_produced = validator.get('num_produced_chunks', 0)
                chunks_expected = validator.get('num_expected_chunks', 0)

                blocks_missed = blocks_expected - blocks_produced
                chunks_missed = chunks_expected - chunks_produced

                if quiet:
                    if blocks_missed == 0 and chunks_missed == 0:
                        print("no blocks missed, no chunks missed")
                    elif blocks_missed > 0 and chunks_missed == 0:
                        print(f"{blocks_missed} blocks missed, no chunks missed")
                    elif blocks_missed == 0 and chunks_missed > 0:
                        print(f"no blocks missed, {chunks_missed} chunks missed")
                    else:
                        print(f"{blocks_missed} blocks missed, {chunks_missed} chunks missed")
                else:
                    print(f"\nValidator: {validator_id}")
                    print(f"Blocks: {blocks_produced}/{blocks_expected}")
                    print(f"Chunks: {chunks_produced}/{chunks_expected}")
                break

        if not validator_found:
            print(f"Validator {validator_id} not found")

    def monitor(self, interval=60, validator_id=None, quiet=False, single_run=False):
        if quiet and not validator_id:
            print("Error: Quiet mode can only be used when a validator ID is specified")
            sys.exit(1)

        if not quiet:
            print(f"Starting validator monitoring (checking every {interval} seconds)...")
            print(f"Connecting to RPC at {self.rpc_host}:{self.rpc_port}")

        while True:
            try:
                validator_info = self.get_validator_status()
                if not validator_info:
                    if not quiet:
                        print("Failed to get validator information")
                    continue

                if validator_id:
                    self.print_validator_performance(validator_info, validator_id, quiet)
                else:
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    print(f"\n=== Validator Status Check at {timestamp} ===")

                    missing_blocks = self.check_missing_blocks(validator_info)
                    missing_chunks = self.check_missing_chunks(validator_info)

                    if missing_blocks:
                        print("\nValidators missing blocks:")
                        for item in missing_blocks:
                            print(f"- {item['account_id']}: missing {item['missing']} blocks "
                                  f"(produced {item['produced']}/{item['expected']})")

                    if missing_chunks:
                        print("\nValidators missing chunks:")
                        for item in missing_chunks:
                            print(f"- {item['account_id']}: missing {item['missing']} chunks "
                                  f"(produced {item['produced']}/{item['expected']})")

                    if not missing_blocks and not missing_chunks:
                        print("All validators are performing as expected")

                if single_run:
                    break

            except KeyboardInterrupt:
                if not quiet:
                    print("\nMonitoring stopped by user")
                break
            except Exception as e:
                if not quiet:
                    print(f"Error during monitoring: {e}")

            time.sleep(interval)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Monitor NEAR validators performance')
    parser.add_argument('--val-id', type=str, help='Output only the performance info for the given validator')
    parser.add_argument('--quiet', action='store_true', help='Output only the validator specific performance data')
    parser.add_argument('--single-run', action='store_true', help='Run once then exit')
    parser.add_argument('--interval', type=int, default=60, help='Monitoring interval in seconds')
    args = parser.parse_args()

    monitor = ValidatorMonitor()
    monitor.monitor(
        interval=args.interval,
        validator_id=args.val_id,
        quiet=args.quiet,
        single_run=args.single_run
    )
