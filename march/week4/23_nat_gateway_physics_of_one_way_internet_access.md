# The Physics of NAT Gateways: Why Private Subnets Still Need a Way Out

## The Trap

Most people hear “private subnet” and immediately assume one thing: no internet.

A private subnet is not a place where machines should never communicate outward. It is a place where machines should not be directly reachable from the outside world.

If you take the naive view, you end up asking the wrong question: if a workload is private, why give it any path to the internet at all?

The better question is harsher: **how do you let a machine fetch updates and dependencies without turning that same machine into a public destination?**

## The Stop-Time Moment

It may sit behind an API layer. It may never need to accept unsolicited inbound traffic from the internet. But it still often needs to do ordinary operational work:

- download operating system updates
- pull packages or containers
- call external APIs

Now ask yourself:

**If you remove all outbound internet access, how will that machine maintain itself?**

**If you give it a direct route to an internet gateway, have you preserved privacy or quietly destroyed it?**

**What kind of network path allows “go out” without also meaning “others can come in”?**

This is the hidden mechanic many beginners miss. Private means non-publicly addressable, not inert.

## The Mental Model Shift

Stop thinking private means disconnected. Start thinking private means not directly exposed.

A private subnet is valuable because it does not advertise a direct route for the outside world to initiate traffic back to it.

### Thinking Shifts

- Stop thinking internet access is a binary yes-or-no property.
- Start thinking inbound and outbound internet behavior are separate design decisions.
- Stop thinking NAT is a security feature by itself.
- Start thinking NAT is a translation mechanism that supports a specific traffic pattern.
- Stop thinking a private subnet is “safe” because of its label.
- Start thinking it is private only because its routing and exposure model enforce that reality.

## The What-If Scenarios

### 1. Direct Internet Gateway on a Supposedly Private Subnet

What happens if you point `0.0.0.0/0` from a private subnet directly to an internet gateway?

You have changed the character of the subnet. The machine now has a direct internet path instead of mediated outbound access.

### 2. No Outbound Path at All

What happens if a private workload has no route outward?

It may be isolated, but it may also be operationally crippled. Updates fail. External dependencies cannot be fetched. Images cannot be pulled. Suddenly “secure” means “stuck.”

### 3. Misunderstanding Subnet-to-Subnet Communication

What happens if someone assumes NAT is needed for private subnets to talk to public subnets or other subnets inside the same VPC?

They misunderstand the routing boundary. Internal subnet communication rides on local VPC routing. NAT is not there to help siblings inside the same VPC find each other.

## The Architecture

### Public Subnet Behavior

- A public subnet has a route such as `0.0.0.0/0` pointing to an internet gateway.
- This is where you place components whose job is to face outward.

### Private Subnet Behavior

- A private subnet does not send its default route directly to the internet gateway.
- That is why unsolicited inbound internet traffic does not simply arrive there.
- But workloads inside it may still need outbound reachability.

### Where NAT Fits

- The private subnet sends default outbound traffic to a NAT gateway instead of to the internet gateway.
- The NAT gateway lives in a public subnet and has the ability to reach outward.
- Outbound requests from private resources are translated through that gateway.
- Return traffic for those initiated sessions can come back.
- Random new inbound internet requests do not suddenly gain a route into the private subnet.

NAT creates one-way usefulness, not symmetrical exposure.

## The Intuition That Usually Makes It Click

Think of a housing complex.

- One building has a main gate to the outside road.
- Another building is deeper inside and does not open directly to the street.
- A shuttle carries residents from the inner building out to the main road.
- But strangers from the road cannot use that shuttle route to wander back into the inner building.

It is controlled exit, not open arrival.

## Why Routing Tables Matter More Than Labels

People often talk about public and private subnets as if those are built-in identities. They are really consequences of routing choices.

- If default traffic goes to an internet gateway, the subnet behaves publicly.
- If default traffic goes to a NAT gateway, the subnet supports outbound access without direct public exposure.
- If no outbound route exists, the subnet is more tightly isolated.

The subnet name is not the truth. The route table is.

## The Question to Sit With

If a private subnet can still reach outward through NAT, and a public subnet is public only because its route table allows direct internet egress, then are you really designing “private” and “public” infrastructure, or are you designing which side gets to initiate the conversation?

And if privacy in cloud networking is mostly a question of who may start the path, how many teams are calling something secure when they have really only attached the wrong label to the wrong route table?