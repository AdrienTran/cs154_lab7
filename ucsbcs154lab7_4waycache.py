# ucsbcs154lab7_4waycache.py
# All Rights Reserved
# Copyright (c) 2022 Jonathan Balkind
# Distribution Prohibited

import pyrtl

pyrtl.core.set_debug_mode()

# Cache parameters:
# 32 bit addresses
# 4 ways
# 16 rows
# 16 bytes (4 words) per block

# Inputs
req_new = pyrtl.Input(bitwidth=1, name='req_new')       # High on cycles when a request is occurring
req_addr = pyrtl.Input(bitwidth=32, name='req_addr')    # Requested address
req_type = pyrtl.Input(bitwidth=1, name='req_type')     # 0 read, 1 write
req_data = pyrtl.Input(bitwidth=32, name='req_data')    # Only for writes

# Outputs
resp_hit = pyrtl.Output(bitwidth=1, name='resp_hit')    # Indicates whether there was a cache hit
resp_data = pyrtl.Output(bitwidth=32, name='resp_data') # If read request, return data at req_addr

# Memories
valid_0 = pyrtl.MemBlock(bitwidth=1, addrwidth=4, max_read_ports=2, max_write_ports=1, asynchronous=True, name='valid_0')
valid_1 = pyrtl.MemBlock(bitwidth=1, addrwidth=4, max_read_ports=2, max_write_ports=1, asynchronous=True, name='valid_1')
valid_2 = pyrtl.MemBlock(bitwidth=1, addrwidth=4, max_read_ports=2, max_write_ports=1, asynchronous=True, name='valid_2')
valid_3 = pyrtl.MemBlock(bitwidth=1, addrwidth=4, max_read_ports=2, max_write_ports=1, asynchronous=True, name='valid_3')

tag_0 = pyrtl.MemBlock(bitwidth=24, addrwidth=4, max_read_ports=2, max_write_ports=1, asynchronous=True, name='tag_0')
tag_1 = pyrtl.MemBlock(bitwidth=24, addrwidth=4, max_read_ports=2, max_write_ports=1, asynchronous=True, name='tag_1')
tag_2 = pyrtl.MemBlock(bitwidth=24, addrwidth=4, max_read_ports=2, max_write_ports=1, asynchronous=True, name='tag_2')
tag_3 = pyrtl.MemBlock(bitwidth=24, addrwidth=4, max_read_ports=2, max_write_ports=1, asynchronous=True, name='tag_3')

data_0 = pyrtl.MemBlock(bitwidth=128, addrwidth=4, max_read_ports=2, max_write_ports=1, asynchronous=True, name='data_0')
data_1 = pyrtl.MemBlock(bitwidth=128, addrwidth=4, max_read_ports=2, max_write_ports=1, asynchronous=True, name='data_1')
data_2 = pyrtl.MemBlock(bitwidth=128, addrwidth=4, max_read_ports=2, max_write_ports=1, asynchronous=True, name='data_2')
data_3 = pyrtl.MemBlock(bitwidth=128, addrwidth=4, max_read_ports=2, max_write_ports=1, asynchronous=True, name='data_3')

# To track which Way entry to replace next.
repl_way = pyrtl.MemBlock(bitwidth=2, addrwidth=4, max_read_ports=2, max_write_ports=1, asynchronous=True, name='repl_way')

# TODO: Declare your own WireVectors, MemBlocks, etc.
# tag, index, offset, temp = pyrtl.chop(req_addr, 24, 4, 2, 2)
# tag = req_addr[slice(31, 8, -1)]
# index = req_addr[slice(7, 4, -1)]
# offset = req_addr[slice(3, 0, -1)]
tag = pyrtl.WireVector(bitwidth=24, name='tag')
index = pyrtl.WireVector(bitwidth=4, name='index')
offset = pyrtl.WireVector(bitwidth=2, name='offset')
tag <<= req_addr[8:32]  
index <<= req_addr[4:8]
offset <<= req_addr[2:4]

write_mask = pyrtl.WireVector(bitwidth=128)
write_data = pyrtl.WireVector(bitwidth=128)

data_0_payload = pyrtl.WireVector(bitwidth=128, name='data_0_payload')
data_1_payload = pyrtl.WireVector(bitwidth=128, name='data_1_payload')
data_2_payload = pyrtl.WireVector(bitwidth=128, name='data_2_payload')
data_3_payload = pyrtl.WireVector(bitwidth=128, name='data_3_payload')

data_0_payload <<= data_0[index]
data_1_payload <<= data_1[index]
data_2_payload <<= data_2[index]
data_3_payload <<= data_3[index]

hit_0 = pyrtl.WireVector(bitwidth=1, name='hit_0')
hit_1 = pyrtl.WireVector(bitwidth=1, name='hit_1')
hit_2 = pyrtl.WireVector(bitwidth=1, name='hit_2')
hit_3 = pyrtl.WireVector(bitwidth=1, name='hit_3')
hit_result = pyrtl.WireVector(bitwidth=1, name='hit_result')

enable_0 = pyrtl.WireVector(bitwidth=1, name='enable_0')
enable_1 = pyrtl.WireVector(bitwidth=1, name='enable_1')
enable_2 = pyrtl.WireVector(bitwidth=1, name='enable_2')
enable_3 = pyrtl.WireVector(bitwidth=1, name='enable_3')

replace_way = repl_way[index]

####################################################################################

# TODO: Check four entries in a row in parallel.

with pyrtl.conditional_assignment:
    with req_new == 1:
        with ((valid_0[index] == 1) & (tag == tag_0[index])):
            hit_0 |= 1
        with ((valid_1[index] == 1) & (tag == tag_1[index])):
            hit_1 |= 1
        with ((valid_2[index] == 1) & (tag == tag_2[index])):
            hit_2 |= 1
        with ((valid_3[index] == 1) & (tag == tag_3[index])):
            hit_3 |= 1

# TODO: Determine if hit or miss.
hit_result <<= (hit_0 | hit_1 | hit_2 | hit_3)

# TODO: If request type is write, write req_data to appropriate block address
with pyrtl.conditional_assignment:
    with req_new == 1:
        with req_type == 1:
            with hit_result == 0: # Handling write misses
                with replace_way == 0:
                    enable_0 |= pyrtl.Const(1)
                with replace_way == 1:
                    enable_1 |= pyrtl.Const(1)
                with replace_way == 2:
                    enable_2 |= pyrtl.Const(1)
                with replace_way == 3:
                    enable_3 |= pyrtl.Const(1)
            with hit_result == 1: # Handling write hits
                with hit_0:
                    enable_0 |= pyrtl.Const(1)
                with hit_1:
                    enable_1 |= pyrtl.Const(1)
                with hit_2:
                    enable_2 |= pyrtl.Const(1)
                with hit_3:
                    enable_3 |= pyrtl.Const(1)
        with req_type == 0:
            with hit_result == 0: # Handling read misses
                with replace_way == 0:
                    enable_0 |= pyrtl.Const(1)
                with replace_way == 1:
                    enable_1 |= pyrtl.Const(1)
                with replace_way == 2:
                    enable_2 |= pyrtl.Const(1)
                with replace_way == 3:
                    enable_3 |= pyrtl.Const(1)

# offset by 0, 32, 64, 96 bits
data_shift_amount = pyrtl.WireVector(bitwidth=8, name='data_shift_amount')            
data_shift_amount <<= offset*32

write_mask <<= pyrtl.select(hit_result, ~pyrtl.shift_left_logical(pyrtl.Const(0x0ffffffff, bitwidth=128), data_shift_amount), 0)
write_data <<= pyrtl.shift_left_logical(req_data.zero_extended(bitwidth=128), data_shift_amount)

data_0[index] <<= pyrtl.MemBlock.EnabledWrite((data_0_payload & write_mask) | write_data, enable_0) 
data_1[index] <<= pyrtl.MemBlock.EnabledWrite((data_1_payload & write_mask) | write_data, enable_1)
data_2[index] <<= pyrtl.MemBlock.EnabledWrite((data_2_payload & write_mask) | write_data, enable_2)
data_3[index] <<= pyrtl.MemBlock.EnabledWrite((data_3_payload & write_mask) | write_data, enable_3)

# TODO: Handle replacement. Be careful handling replacement when you
# also have to do a write
with pyrtl.conditional_assignment:
    with req_new == 1:
        with hit_result == 0:
            # repl_way[index] |= pyrtl.select(replace_way == 3, 0, repl_way[index] + 1)
            # repl_way[index] |= repl_way[index] + 1
            
            with replace_way == 0:
                tag_0[index] |= tag
                valid_0[index] |= pyrtl.Const(1)
                repl_way[index] |= pyrtl.Const(1)
            with replace_way == 1:
                tag_1[index] |= tag
                valid_1[index] |= pyrtl.Const(1)
                repl_way[index] |= pyrtl.Const(2)
            with replace_way == 2:
                tag_2[index] |= tag
                valid_2[index] |= pyrtl.Const(1)
                repl_way[index] |= pyrtl.Const(3)
            with replace_way == 3:
                tag_3[index] |= tag
                valid_3[index] |= pyrtl.Const(1)
                repl_way[index] |= pyrtl.Const(0)
            
# TODO: Determine output
with pyrtl.conditional_assignment:
    selected_data = pyrtl.WireVector(bitwidth=128, name='selected_data')
    with hit_0:
        selected_data |= data_0[index]
    with hit_1:
        selected_data |= data_1[index]
    with hit_2:
        selected_data |= data_2[index]
    with hit_3:
        selected_data |= data_3[index]
    
with pyrtl.conditional_assignment:
    with req_new == 0:
        resp_hit |= 0
        resp_data |= 0
    with req_new == 1:
        with req_type == 0: 
            with hit_result == 1: # Handling read hits
                resp_hit |= 1
                
                # selected_data = pyrtl.WireVector(bitwidth=128, name='selected_data')
                # with hit_0:
                #     selected_data |= data_0[index]
                # with hit_1:
                #     selected_data |= data_1[index]
                # with hit_2:
                #     selected_data |= data_2[index]
                # with hit_3:
                #     selected_data |= data_3[index]
                    
                # with hit_0:
                #     resp_data |= data_0[index]
                # with hit_1:
                #     resp_data |= data_1[index]
                # with hit_2:
                #     resp_data |= data_2[index]
                # with hit_3:
                #     resp_data |= data_3[index]

                resp_data |= pyrtl.corecircuits.mux(offset, selected_data[0:32], selected_data[32:64], selected_data[64:96], selected_data[96:128])
                
            with hit_result == 0: # Handling read misses
                resp_hit |= 0
                resp_data |= 0
        with req_type == 1:
            with hit_result == 1: # Handling write hits
                resp_hit |= 1
                resp_data |= 0
            with hit_result == 0: # Handling write misses
                resp_hit |= 0
                resp_data |= 0
            

############################## SIMULATION ######################################

def TestNoRequest(simulation, trace, addr=1024):
    simulation.step({
        'req_new':0,
        'req_addr':addr,
        'req_type':0,
        'req_data':0,
    })

    assert(trace.trace["resp_hit"][-1] == 0)
    assert(trace.trace["resp_data"][-1] == 0)
    print("Passed No Request Case!")

# Precondition: addr is not already in the cache.
# Postcondition: There is a cache miss. 
def TestMiss(simulation, trace, addr = 0):
    simulation.step({
        'req_new':1,
        'req_addr':addr,
        'req_type':0,
        'req_data':0,
    })

    assert(trace.trace["resp_hit"][-1] == 0)
    assert(trace.trace["resp_data"][-1] == 0)

    print("Passed Miss Case!")

# Precondition: addr is already in the cache.
# Postcondition: There is a cache hit and the cache returns
# the expected word. 
def TestHit(simulation, trace, addr = 0, expected_data = 0):
    simulation.step({
        'req_new':1,
        'req_addr':addr,
        'req_type':0,
        'req_data':0,
    })

    assert(trace.trace["resp_hit"][-1] == 1)
    assert(trace.trace["resp_data"][-1] == expected_data) 

    print("Passed Hit Case!")

# Precondition: addr is already in the cache.
# Postcondition: The word located at memory address 'addr'
# has been replaced with 'new_data'.
def TestWrite(simulation, trace, addr=0, new_data=156):
    simulation.step({
        'req_new': 1,
        'req_addr': addr,
        'req_type': 1,
        'req_data': new_data,
    })

    assert(trace.trace["resp_hit"][-1] == 1)
    assert(trace.trace["resp_data"][-1] == 0) 

    # Read back the correct value
    simulation.step({
        'req_new': 1,
        'req_addr': addr,
        'req_type': 0,
        'req_data': 0,
    })

    assert(trace.trace["resp_hit"][-1] == 1)
    assert(trace.trace["resp_data"][-1] == new_data) 
    print("Passed Write Test!")

# Precondition: addr does not already hit in the cache.
# Postcondition: addr exists in the cache at the correct
# cache index
def TestCorrectIndex(simulation, trace, addr = 32):
    simulation.step({
        'req_new': 1,
        'req_addr': addr,
        'req_type': 0,
        'req_data': 0,
    })

    assert(trace.trace["resp_hit"][-1] == 0)
    assert(trace.trace["resp_data"][-1] == 0) 

    bin_addr = bin(addr)[2:]
    missing_bits = 32 - len(bin_addr)
    if missing_bits > 0:
        bin_addr = ("0" * missing_bits) + bin_addr

    cache_index = int("0b" + bin_addr[-8:-4], 2)
    addr_tag = int("0b" + bin_addr[:24], 2)

    tag_0_val = 0 if len(simulation.inspect_mem(tag_0)) < cache_index else simulation.inspect_mem(tag_0)[cache_index]
    tag_1_val = 0 if len(simulation.inspect_mem(tag_1)) < cache_index else simulation.inspect_mem(tag_1)[cache_index]
    tag_2_val = 0 if len(simulation.inspect_mem(tag_2)) < cache_index else simulation.inspect_mem(tag_2)[cache_index]
    tag_3_val = 0 if len(simulation.inspect_mem(tag_3)) < cache_index else simulation.inspect_mem(tag_3)[cache_index]

    assert((tag_0_val == addr_tag) | (tag_1_val == addr_tag) | (tag_2_val == addr_tag) | (tag_3_val == addr_tag))

    # Ensure that we hit in the next cycle.
    simulation.step({
        'req_new': 1,
        'req_addr': addr,
        'req_type': 0,
        'req_data': 0,
    })

    assert(trace.trace["resp_hit"][-1] == 1)
    assert(trace.trace["resp_data"][-1] == 0) 

    print("Passed Correct Index Test!")

sim_trace = pyrtl.SimulationTrace()
sim = pyrtl.Simulation(tracer=sim_trace)

TestNoRequest(sim, sim_trace)
TestMiss(sim, sim_trace)
TestHit(sim, sim_trace)
TestWrite(sim, sim_trace)
TestCorrectIndex(sim, sim_trace)


# Print trace
# sim_trace.render_trace(symbol_len=8)