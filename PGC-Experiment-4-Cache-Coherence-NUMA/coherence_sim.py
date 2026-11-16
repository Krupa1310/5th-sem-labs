
import sys

PROTOCOLS = ["MSI", "MESI", "MOESI"]


def simulate(protocol, layout, iterations):
    stats = {
        "bus": 0,
        "BusRd": 0,
        "BusRdX": 0,
        "BusUpgr": 0,
        "invalidations": 0,
        "writeback": 0,
        "c2c": 0,
        "silent": 0
    }

    caches = {
        0: {"A": "I", "B": "I"},
        1: {"A": "I", "B": "I"}
    }

    trace = []

    def read(core, line):
        other = 1 - core
        state = caches[core][line]
        other_state = caches[other][line]

        if state != "I":
            return

        stats["bus"] += 1
        stats["BusRd"] += 1

        if other_state == "I":
            caches[core][line] = (
                "E" if protocol in ("MESI", "MOESI") else "S"
            )

        elif other_state == "M":
            if protocol == "MOESI":
                caches[other][line] = "O"
                caches[core][line] = "S"
                stats["c2c"] += 1
            else:
                caches[other][line] = "S"
                caches[core][line] = "S"
                stats["writeback"] += 1

        elif other_state == "O":
            caches[core][line] = "S"
            stats["c2c"] += 1

        elif other_state in ("S", "E"):
            if other_state == "E":
                caches[other][line] = "S"
            caches[core][line] = "S"

    def write(core, line):
        other = 1 - core
        state = caches[core][line]
        other_state = caches[other][line]

        if state == "M":
            return

        if state == "E":
            caches[core][line] = "M"
            stats["silent"] += 1
            return

        if state == "S":
            stats["bus"] += 1
            stats["BusUpgr"] += 1

        elif state == "I":
            stats["bus"] += 1
            stats["BusRdX"] += 1

        if other_state != "I":
            stats["invalidations"] += 1

            if other_state in ("M", "O"):
                if protocol == "MOESI":
                    if other_state == "M":
                        stats["c2c"] += 1
                else:
                    stats["writeback"] += 1

        caches[other][line] = "I"
        caches[core][line] = "M"

    operations = (
        [("A", 0), ("A", 1)]
        if layout == "adjacent"
        else [("A", 0), ("B", 1)]
    )

    for iteration in range(iterations):
        for line, core in operations:
            read(core, line)

            if iteration < 2 and layout == "adjacent":
                trace.append(
                    (core, "R", line, caches[0][line], caches[1][line])
                )

            write(core, line)

            if iteration < 2 and layout == "adjacent":
                trace.append(
                    (core, "W", line, caches[0][line], caches[1][line])
                )

    return stats, trace


def main():
    iterations = int(sys.argv[1]) if len(sys.argv) > 1 else 1000

    print("State trace, first 2 iterations, adjacent layout")
    print("Line A: Core 0 / Core 1")

    for protocol in PROTOCOLS:
        _, trace = simulate(protocol, "adjacent", 2)

        print(f"\n{protocol}:")

        for core, operation, line, c0, c1 in trace:
            print(
                f"Core {core} {operation} line {line} "
                f"-> C0={c0}, C1={c1}"
            )

    print(f"\nTotals for {iterations} iterations")
    print(
        f"{'Layout':<10} {'Protocol':<10} {'bus':>8} "
        f"{'BusRd':>8} {'BusRdX':>8} {'BusUpgr':>10} "
        f"{'invalidations':>14} {'writeback':>10} "
        f"{'c2c':>8} {'silent E->M':>12}"
    )

    for layout in ("adjacent", "padded"):
        for protocol in PROTOCOLS:
            stats, _ = simulate(protocol, layout, iterations)

            print(
                f"{layout:<10} {protocol:<10} "
                f"{stats['bus']:>8} "
                f"{stats['BusRd']:>8} "
                f"{stats['BusRdX']:>8} "
                f"{stats['BusUpgr']:>10} "
                f"{stats['invalidations']:>14} "
                f"{stats['writeback']:>10} "
                f"{stats['c2c']:>8} "
                f"{stats['silent']:>12}"
            )


if __name__ == "__main__":
    main()


