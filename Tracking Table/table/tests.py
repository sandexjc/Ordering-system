from decimal import Decimal
from types import SimpleNamespace

from django.test import SimpleTestCase

from table.service import OrderWeight


def _plate(material, quantity):
    return SimpleNamespace(material=material, quantity=Decimal(str(quantity)))


def _edge(edge_type, quantity):
    return SimpleNamespace(edge_type=edge_type, quantity=Decimal(str(quantity)))


class OrderWeightMatchingTests(SimpleTestCase):

    def test_plate_gryb_4100_matches_extra_words(self):
        self.assertEqual(OrderWeight.plate_unit_kg("Гръб 4100 Бял"), Decimal("34"))

    def test_plate_gryb_2050(self):
        self.assertEqual(OrderWeight.plate_unit_kg("гръб HDF 2050"), Decimal("17"))

    def test_plate_plot_4100(self):
        self.assertEqual(OrderWeight.plate_unit_kg("Плот 4100 дъб"), Decimal("66"))

    def test_plate_plot_2050(self):
        self.assertEqual(OrderWeight.plate_unit_kg("плот 2050"), Decimal("33"))

    def test_half_sheet_wins_over_agt(self):
        self.assertEqual(OrderWeight.plate_unit_kg("1/2 AGT бял"), Decimal("36"))

    def test_agt_wins_over_mdf(self):
        self.assertEqual(OrderWeight.plate_unit_kg("МДФ AGT 18"), Decimal("40"))

    def test_fazer(self):
        self.assertEqual(OrderWeight.plate_unit_kg("Фазер 3мм"), Decimal("10"))

    def test_mdf_cyrillic_and_latin(self):
        self.assertEqual(OrderWeight.plate_unit_kg("МДФ 18мм"), Decimal("77"))
        self.assertEqual(OrderWeight.plate_unit_kg("MDF 18mm"), Decimal("77"))

    def test_unmatched_plate_uses_default(self):
        self.assertEqual(OrderWeight.plate_unit_kg("W980 ST2"), Decimal("72"))

    def test_edge_22_08_and_22_2(self):
        self.assertEqual(OrderWeight.edge_unit_kg("22/08"), Decimal("0.02"))
        self.assertEqual(OrderWeight.edge_unit_kg("ABS 22/2.0"), Decimal("0.05"))

    def test_unmatched_edge_is_zero(self):
        self.assertEqual(OrderWeight.edge_unit_kg("ABS 23x1"), Decimal("0"))


class OrderWeightCalculateTests(SimpleTestCase):

    def test_rounds_half_up_to_integer(self):
        # 25 lm * 0.02 kg = 0.5 -> 1
        weight = OrderWeight.calculate_weight(
            plates=[],
            edges=[_edge("22/08", "25.0")],
        )
        self.assertEqual(weight, 1)

    def test_combines_plates_and_edges(self):
        weight = OrderWeight.calculate_weight(
            plates=[_plate("Фазер", "2"), _plate("W980 ST2", "1")],
            edges=[_edge("22/2.0", "10")],
        )
        # 2*10 + 1*72 + 10*0.05 = 20 + 72 + 0.5 = 92.5 -> 93
        self.assertEqual(weight, 93)
