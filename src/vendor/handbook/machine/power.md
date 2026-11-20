# Power

How the machine spends power: one power profile that the kernel and every Nerv service follow, cores that sleep as deeply as the next wake-up allows, and a desktop that keeps the fast cores quick to wake only while something moves on screen. On an N1X laptop at an idle desktop on battery, Nerv draws the same power as the kernel's default settings and hands work between programs eight to eleven times faster.

## The power profile

The machine has one power profile, and everything that changes how much power it uses follows it. On battery the profile is `saver`, on mains `balanced`, and it changes the moment the power source does. A machine without a battery stays `balanced`.

```
$ power
saver; on battery, 82%
```

To set it by hand until the power source next changes, and to hand the choice back:

```
$ doas power performance
$ doas power auto
```

| Profile | What it does |
| --- | --- |
| `performance` | The cores prefer speed over saving, and no core sleeps in a state that takes longer than 100 µs to leave. |
| `balanced` | The machine as it booted. On a laptop, the firmware's own balanced mode. |
| `saver` | The cores prefer saving, each one is capped at the clock where work costs it the least energy, and the firmware is asked for its quietest mode, where it has one. |

## Where `saver` caps the clock

Each kind of core has a point past which a little more speed costs a lot more power. `saver` holds each core at that point. On an N1X laptop, measured on battery:

| Core | Top clock | `saver` cap | Power per core at the top | At the cap |
| --- | --- | --- | --- | --- |
| Cortex-X925 (fast) | 3.9 GHz | 3.4 GHz | 5.70 W | 2.55 W |
| Cortex-A725 (efficient) | 2.8 GHz | 2.5 GHz | 1.10 W | 0.36 W |

A fast core gives up 13% of its clock and draws 55% less power. An efficient core gives up 11% and draws 67% less. Work a person waits for, a build or a page load, keeps most of its speed for less than half the power.

## Idle cores

Most of the time most cores have nothing to do, and how they sleep decides the battery. Two things set it.

**The kernel is tickless.** A core with nothing to run stops its timer tick and sleeps until something actually needs it. It is not woken a thousand times a second to find nothing to do.

**Each sleep is as deep as the next wake-up allows.** A core can doze, waking in microseconds, or power down further, saving more but taking longer to come back. Choosing between them is a guess about how long the core will stay idle. Nerv makes that guess from how this core was actually woken recently, by timers and by other work alike. The kernel's default guesses mainly from the next timer, and on a tickless machine much of what wakes a core is not a timer: a program handing work to another, such as a frame passing from the compositor to the GPU. Guessing from timers alone puts cores too deep for those hand-offs, and every one of them then waits for the core to power back up.

On an N1X laptop at an idle desktop on battery, 2026-11-19, one hand-off from one process to another:

| | The kernel's default | Nerv |
| --- | --- | --- |
| Idle power | 9.58–9.67 W | 9.66 W |
| Time for a hand-off, median | 266–387 µs | 34 µs |
| Hand-offs over 1 ms, per 5,000 | 359–414 | 3 |

The same power, eight to eleven times faster at the median, and almost none of the millisecond stalls a person sees as a stutter.

```
$ cat /sys/devices/system/cpu/cpuidle/current_governor
teo
```

## While something moves on screen

A frame is several programs waking each other in turn, and the slowest of those wake-ups decides whether the frame is on time. While something moves, the compositor holds the fast cores to their shallowest sleep, which they leave at once, and lets go when the screen is still. It also tells the kernel that its own drawing thread runs on a fast core at full clock, with a short turn so it is not kept waiting behind other work. What it starts does not inherit either.

The hold is a connection to the power service and lasts only as long as it: a compositor that exits or crashes cannot leave the cores held. Any program can take it the same way:

```
$ power hold -- my-benchmark
```

On the same laptop and conditions, one round of a frame's hand-offs:

| | Cores free | Fast cores held |
| --- | --- | --- |
| Idle power | 9.66 W | 10.26 W |
| Round trip, median | 21 µs | 21 µs |
| Round trip, 99th percentile | 695 µs | 46 µs |
| Rounds over 1 ms, per 5,000 | 2 | 0 |

0.6 W, paid only while something moves, buys a worst case fifteen times shorter.
