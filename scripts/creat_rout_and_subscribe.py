import sys
import os

if len(sys.argv) != 4:
    print("Usage: python creat_rout_and_subscribe.py <num_houses> <prefix> <output_dir>")
    sys.exit(1)

num_houses = int(sys.argv[1])
prefix = sys.argv[2]
output_dir = sys.argv[3]

if not os.path.isdir(output_dir):
    print(f"Error: Output directory '{output_dir}' does not exist.")
    sys.exit(1)

out_path = os.path.join(output_dir, "fncs_msg.txt")
outF = open(out_path, "w")

line = ""
for index in range(1, num_houses + 1):
    line += f'route "commit:Market_1.current_market.clearing_price -> HOUSE_{index}/clearPrice; 0";\n'
    line += f'route "commit:Market_1.market_id -> HOUSE_{index}/mktID; 0";\n'
    line += f'route "commit:Market_1.current_price_mean_24h -> HOUSE_{index}/avgPrice; 0";\n'
    # This line is duplicated in the original, keeping it for consistency
    line += f'route "commit:Market_1.current_price_mean_24h -> HOUSE_{index}/avgPrice; 0";\n'
    line += f'route "commit:Market_1.current_price_stdev_24h -> HOUSE_{index}/stdevPrice; 0";\n'

    line += f'subscribe "function:auction/submit_bid_state <- {prefix}/HOUSE_{index}@Market_1/submit_bid_state";\n'
    line += f'subscribe "precommit:HOUSE_{index}.proxy_clear_price <- {prefix}/Market_1@HOUSE_{index}/clearPrice";\n'
    line += f'subscribe "precommit:HOUSE_{index}.proxy_market_id <- {prefix}/Market_1@HOUSE_{index}/mktID";\n'
    line += f'subscribe "precommit:HOUSE_{index}.proxy_average <- {prefix}/Market_1@HOUSE_{index}/avgPrice";\n'
    line += f'subscribe "precommit:HOUSE_{index}.proxy_standard_deviation <- {prefix}/Market_1@HOUSE_{index}/stdevPrice";\n'

outF.write(line)
outF.close()

print(f"Successfully generated {out_path}")
