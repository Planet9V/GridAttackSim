import sys
import os

if len(sys.argv) != 3:
    print("Usage: python creat_zpl_file.py <num_houses> <output_dir>")
    sys.exit(1)

num_houses = int(sys.argv[1])
output_dir = sys.argv[2]

if not os.path.isdir(output_dir):
    print(f"Error: Output directory '{output_dir}' does not exist.")
    sys.exit(1)

out_path = os.path.join(output_dir, "fncs.zpl")
outF = open(out_path, "w")

index = 1
space = " "
line = "name = ns3_1 \n"
line += "time_delta = 1ns \n"
line += "broker = tcp://localhost:5570 \n"
line += "values \n"

while (index < num_houses + 1):
    line += f"{space*4}fncs_msg/HOUSE_{index}@Market_1/submit_bid_state\n"
    line += f"{space*8}topic = fncs_msg/HOUSE_{index}@Market_1/submit_bid_state\n"
    line += f"{space*8}default = \"\"\n"
    line += f"{space*8}type = string\n"
    line += f"{space*8}list = false\n"

    line += f"{space*4}fncs_msg/Market_1@HOUSE_{index}/clearPrice \n"
    line += f"{space*8}topic = fncs_msg/Market_1@HOUSE_{index}/clearPrice \n"
    line += f"{space*8}default = \"\" \n"
    line += f"{space*8}ttype = string \n"
    line += f"{space*8}list = false \n"

    line += f"{space*4}fncs_msg/Market_1@HOUSE_{index}/mktID \n"
    line += f"{space*8}topic = fncs_msg/Market_1@HOUSE_{index}/mktID \n"
    line += f"{space*8}default = \"\" \n"
    line += f"{space*8}type = string \n"
    line += f"{space*8}list = false \n"

    line += f"{space*4}fncs_msg/Market_1@HOUSE_{index}/avgPrice \n"
    line += f"{space*8}topic = fncs_msg/Market_1@HOUSE_{index}/avgPrice \n"
    line += f"{space*8}default = \"\" \n"
    line += f"{space*8}type = string \n"
    line += f"{space*8}list = false \n"

    line += f"{space*4}fncs_msg/Market_1@HOUSE_{index}/stdevPrice \n"
    line += f"{space*8}topic = fncs_msg/Market_1@HOUSE_{index}/stdevPrice \n"
    line += f"{space*8}default = \"\" \n"
    line += f"{space*8}type = string \n"
    line += f"{space*8}list = false \n"

    # This seems redundant, but keeping it to match original logic
    line += f"{space*4}fncs_msg/Market_1@HOUSE_{index}/clearPrice \n"
    line += f"{space*8}topic = fncs_msg/Market_1@HOUSE_{index}/clearPrice \n"
    line += f"{space*8}default = \"\" \n"
    line += f"{space*8}type = string \n"
    line += f"{space*8}list = false \n"

    index += 1

outF.write(line)
outF.close()

print(f"Successfully generated {out_path}")
