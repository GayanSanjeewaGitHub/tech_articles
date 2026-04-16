# Stateless vs. Stateful Firewalls: Why AWS Has Both NACLs and Security Groups

## 5 Intuitive Takeaways

1. **NACLs are stateless (blind security guard), Security Groups are stateful (guard with a memory)** — a NACL inspects every packet independently against its rules — it doesn't remember that a packet came in, so you must explicitly write outbound rules to let the response back out. A Security Group remembers the connection: if inbound traffic is allowed in, the return traffic is automatically allowed out without any outbound rule. Think of it as: NACLs check your ID both ways; Security Groups stamp your hand at the door.

2. **The source port is almost never the same as the destination port — and this is where most confusion starts** — when your laptop connects to a database on port 3306, your laptop doesn't send FROM port 3306. It picks a random ephemeral port (1024–65535). So the return traffic goes back to that random port, not 3306. This is why stateless NACLs need an explicit outbound rule allowing the full ephemeral port range — you literally don't know which port the response needs to reach.

3. **NACLs attach to subnets, Security Groups attach to instances — they operate at different blast radii** — a NACL is the perimeter fence around an entire subnet (all resources inside). A Security Group is the lock on a specific door (one EC2 instance, one RDS database). You use NACLs for broad subnet-level isolation and Security Groups for fine-grained per-service port restrictions (MySQL on 3306, MongoDB on 27017, MSSQL on 1433).

4. **Both are just firewall rules operating at different OSI layers with different memory models** — the confusion isn't really about AWS-specific concepts. It's about understanding how any firewall works: match source IP, destination IP, source port, destination port against a rule table. The only architectural question is whether the firewall tracks connection state (stateful = Security Group) or treats every packet as a stranger (stateless = NACL). Once you internalize this, every cloud provider's networking model becomes obvious.

5. **You need both because defense-in-depth requires different granularities of control** — NACLs give you a coarse subnet-level kill switch (block an entire IP range from reaching anything in the subnet). Security Groups give you surgical per-instance rules (only this app server can talk to this database on this port). Layering stateless broad filtering with stateful per-resource filtering is how you build a network that fails closed at multiple boundaries, not just one.
