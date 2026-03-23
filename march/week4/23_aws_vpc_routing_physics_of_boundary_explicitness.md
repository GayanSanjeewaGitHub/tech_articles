# The Physics of VPC Routing: Why Traffic Feels Invisible Inside a Cloud Until It Crosses a Boundary

## The Trap

A VPC here. A subnet there. A router in the middle. An internet gateway on the edge. A NAT gateway somewhere nearby. The diagram feels understandable because every arrow looks like a deliberate path someone must manually create.

Inside a VPC, not every path needs to be explicitly drawn. In fact, one of the first architectural confusions in cloud networking comes from assuming that subnets inside the same VPC need to be manually taught how to find each other.

They do not.

The deeper question is this: **when does traffic move “for free” inside a VPC, and when does it suddenly require an explicit route, gateway, peering connection, or translation step?**

If you miss that boundary, VPC design becomes memorization.

## The Stop-Time Moment

It is not just a folder where subnets are stored. It is a private routing domain.

When you create a VPC, the platform gives it a route table with a local route for the VPC CIDR. That one fact explains more than most beginners realize.

If your VPC is `10.0.0.0/16`, then traffic for that CIDR already knows its target is local.

That means two subnets inside the same VPC are neighborhoods inside one governed space.

Ask yourself:

**Why would two buildings inside the same housing complex need a passport to visit each other?**

**Why would a subnet need an internet gateway to talk to another subnet in the same VPC?**

**What changes the moment traffic tries to leave the VPC's private routing boundary?**

This is the invisible mechanic people miss. Local routing is implicit. External routing is explicit.

## The Mental Model Shift

Stop thinking in disconnected subnets. Start thinking in routing boundaries.

Subnets are not isolated little networks by default. They are partitions inside a larger routing domain.

### Thinking Shifts

- Stop thinking every subnet needs its own hand-written path to nearby subnets.
- Start thinking the VPC provides local reachability across its own CIDR automatically.
- Stop thinking “public” and “private” describe where the subnet lives.
- Start thinking they describe what routes the subnet is allowed to use.
- Stop thinking NAT is general connectivity magic.
- Start thinking NAT is an address-translation escape hatch for outbound communication.

## The What-If Scenarios

### 1. Misunderstanding Local Routing

What happens if you think subnet-to-subnet communication inside one VPC requires explicit routes to each subnet?

You overcomplicate the design and miss the purpose of the VPC route table. The local route already covers the VPC CIDR. That is why internal communication feels automatic.

### 2. Confusing Region and Availability Zone Scope

What happens if you think a subnet can simply belong to another region?

You break the mental model of placement. A subnet belongs to an availability zone, and availability zones belong to a region. You can span a system across multiple regions, but not by stretching one subnet across them.

### 3. Treating Internet Access as Default

What happens if a subnet has no route to `0.0.0.0/0` through an internet gateway?

It does not have internet. That is what makes it private. Privacy in this case is a routing fact.

## The Architecture

### Inside the VPC

- The VPC has a CIDR block.
- The VPC route table includes a local route for that CIDR.
- Subnets carved from that CIDR can reach each other through that local routing domain.
- You do not create special internet-style routes just to move between subnets in the same VPC.

### Leaving the VPC Boundary

The moment traffic needs to go somewhere outside that local domain, explicit routing begins.

- To reach the internet, the route table needs a path such as `0.0.0.0/0` to an internet gateway.
- If that path exists, the subnet behaves as public.
- If that path does not exist, the subnet is private from an internet-routing perspective.

### Reaching Other Private Networks

If one VPC needs to speak to another VPC, local routing is no longer enough.

- You need an explicit connectivity construct such as VPC peering or a transit-style hub.
- It moves over the cloud provider's private backbone, which is why it feels closer to internal infrastructure than public exposure.

But this introduces a new dependency: your reachability depends on that path staying healthy.

### Why NAT Exists

A better intuition is your home router.

- Devices inside your home have private addresses.
- The router owns the public-facing identity.
- When internal devices reach outward, the router translates that traffic so the outside world sees a reachable public source.

That is the same class of idea in cloud networking. A private subnet can use NAT to initiate outbound communication without becoming directly reachable from the internet.

## The Question to Sit With

If traffic inside a VPC is effortless because the routing boundary already exists, and traffic outside the VPC becomes difficult because every escape path must be made explicit, then what are you really designing when you design cloud networking: IP ranges, or trust boundaries?

And when a subnet is called private, is that a label on the subnet itself, or simply evidence that you refused to create a route that would let the world in?