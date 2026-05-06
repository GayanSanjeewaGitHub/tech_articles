# VPC Networking: Why Two Layers of Access Control Exist and When Each Fails

## The Problem: Traffic Reaches Your Database and You Don't Know How

You deployed an MSSQL and MySQL instance in the same subnet. You configured a security group to allow port 1433. Somehow, traffic on port 3306 still reaches the MySQL box. **You assumed subnet-level rules were filtering it.** They weren't configured. You had one layer of defense and thought you had two.

- Security groups allow traffic, but the NACL (Network Access Control List) was left wide open
- A compromised EC2 in the same subnet can reach every other instance — no network-level isolation
- Return traffic gets blocked unexpectedly because NACLs are **stateless** — you allowed inbound but forgot outbound

## Why This Happens

- **NACLs are stateless:** Allowing inbound traffic does **not** automatically allow the response out. Both directions must be explicitly configured
- **Security groups are stateful:** Allowing inbound port 22 automatically permits the return traffic. No outbound rule needed
- Most teams skip NACL configuration and rely entirely on security groups — **one layer instead of two**

**Why does this distinction exist?** NACLs operate at the **subnet boundary** — they filter everything entering or leaving the subnet. Security groups attach to the **ENI (Elastic Network Interface)** of individual instances. Different granularity, different purpose.

## The Mental Model Shift

> **NACLs are the perimeter gate that checks badges in both directions. Security groups are the door locks on individual rooms inside.**

| Aspect | NACL | Security Group |
|---|---|---|
| Attaches to | Subnet | ENI (instance-level) |
| Statefulness | **Stateless** — must allow both inbound AND outbound | **Stateful** — return traffic automatic |
| Granularity | All traffic entering/leaving the subnet | Per-instance filtering |
| Common practice | Often left permissive | Primary enforcement layer |

## The Architecture: VPC Building Blocks

1. **VPC** — a CIDR block defining your private IP space (e.g., `10.0.0.0/16`)
2. **Subnets** — carved from the VPC CIDR, placed in specific **Availability Zones** for physical redundancy
3. **NACLs** — stateless firewall at the subnet boundary (inbound + outbound rules required)
4. **Security Groups** — stateful firewall at the instance ENI (inbound rule auto-permits return)
5. **Internet Gateway** — attached to the VPC, enables outbound internet access
6. **Route Tables** — navigation rules: `10.0.0.0/8 → local`, `0.0.0.0/0 → IGW`

Traffic flow: **Internet → Route Table → NACL (subnet) → Security Group (ENI) → Instance**

## Real Consequences

- **DB subnet with no NACL rules:** Every port is open at the subnet level. Only security groups stand between the internet and your database
- **NACL allows inbound 443 but no outbound rule:** HTTPS requests arrive, responses get dropped. Users see timeouts with no server-side errors
- **Single AZ deployment:** One data center outage takes down your entire service. Subnets across AZs exist for exactly this reason

## The Question to Sit With

Your security group allows port 1433 inbound. Your NACL allows all traffic. **If you're relying on one layer of access control and calling it "defense in depth," what exactly is the second layer defending?**
