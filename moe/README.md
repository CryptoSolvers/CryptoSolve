# MOE Library

Mode of encryption library to support Cryptography research project. It is based on Catherine Meadow's paper "Symbolic Security Criteria for Blockwise Adaptive Secure Modes of Encrytion".

From Catherine's paper....

The MOE program actions engaged in by the oracle are the following, where the random *c* is a session identifier, identifying blocks that belong to the same message.

1. `rcv_start(c)`. The oracle receives a START message from the adversary, indicating that is going to start sending a sequence of plaintext blocks.

2. `rcv_stop(c)`. The oracle receives a STOP message from the advesary, indicating that it has stopped sending plaintext blocks.

3. `rcv_block(c, x)`. The oracle recieves a block to be encrypted from the advesary.  This is represented by a logical variable *x*, which will be instantiated to the message sent by the advesary as the program executes.

4. `send(c, m)`. The oracle sends a MOE term whose unbound variables are variables x such that `rcv_block(c, x) ` occurs before `send(c, m)`

## Interfaces Included

There is a terminal based tool that can be found as `moe_tool` in the root folder. It provides a help functionality which talks about the different parameters the tool takes.

A web based interface also exists. To start the webserver execute the `moe_website` script located at the root folder. The web based interface features a simulation tool that walks through the interactions between the Advesary and Oracle as well as a tool to find attacks on the cryptosystem.

An attack on the cryptosystem is found if p_unifiers exist between ciphertexts.