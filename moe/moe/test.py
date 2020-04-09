from new_commands import *
from moe import *
gen = Filtered_MOE_Generator()
for i in range(6):
    gen.get_next_moe()
m = gen.get_next_moe()
print(m)
sess = MOESession(chaining_function = BetterCustomMoe, custom_moe_thing = m)
sess.rcv_start(0)
f = Function("f", 1)
for i in range(5):
    print(sess.rcv_block(0, f))
