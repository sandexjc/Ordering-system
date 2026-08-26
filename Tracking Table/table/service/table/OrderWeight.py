from decimal import Decimal, ROUND_HALF_UP


_PLATE_DEFAULT_KG = Decimal("72")
_EDGE_22_08_KG = Decimal("0.02")
_EDGE_22_2_KG = Decimal("0.05")


def _normalized(value):
    return (value or "").strip().casefold()


def _contains(*needles):
    folded = tuple(needle.casefold() for needle in needles)

    def match(text):
        return all(needle in text for needle in folded)

    return match


def _prefix(prefix):
    folded = prefix.casefold()

    def match(text):
        return text.startswith(folded)

    return match


# First match wins. Keep more specific plate names above generic ones.
_PLATE_RULES = (
    (_contains("гръб", "4100"), Decimal("34")),
    (_contains("гръб", "2050"), Decimal("17")),
    (_contains("плот", "4100"), Decimal("66")),
    (_contains("плот", "2050"), Decimal("33")),
    (_prefix("1/2"), Decimal("36")),
    (_contains("AGT"), Decimal("40")),
    (_contains("фазер"), Decimal("10")),
    (_contains("МДФ"), Decimal("77")),
    (_contains("MDF"), Decimal("77")),
)

_EDGE_RULES = (
    (_contains("22/08"), _EDGE_22_08_KG),
    (_contains("22/2.0"), _EDGE_22_2_KG),
)


class OrderWeight:

    @staticmethod
    def plate_unit_kg(material):
        text = _normalized(material)
        for match, kilograms in _PLATE_RULES:
            if match(text):
                return kilograms
        return _PLATE_DEFAULT_KG

    @staticmethod
    def edge_unit_kg(edge_type):
        text = _normalized(edge_type)
        for match, kilograms in _EDGE_RULES:
            if match(text):
                return kilograms
        return Decimal("0")

    @classmethod
    def calculate_weight(cls, plates, edges):
        total = Decimal("0")
        for plate in plates:
            total += plate.quantity * cls.plate_unit_kg(plate.material)
        for edge in edges:
            total += edge.quantity * cls.edge_unit_kg(edge.edge_type)
        return int(total.quantize(Decimal("1"), rounding=ROUND_HALF_UP))

    @classmethod
    def update_weight(cls, order):
        # Imported lazily: table.models load this package while models are still initializing.
        from table.models import Edge, Plate

        plates = Plate.objects.for_order(order)
        edges = Edge.objects.for_order(order)
        weight = cls.calculate_weight(plates, edges)
        if order.weight == weight:
            return weight
        order.weight = weight
        order.save(update_fields=["weight"])
        return weight
