from render_options.print_render_options import PrintRenderOptions
import unittest


class TestPrintRenderOptions(unittest.TestCase):
    def test_dpi_table(self):
        self.assertEqual(PrintRenderOptions.dpi_table("6000x3000"), 460)
        self.assertEqual(PrintRenderOptions.dpi_table("6000x3000"), 460)
        self.assertEqual(PrintRenderOptions.dpi_table("6000x3000"), 460)
        self.assertEqual(PrintRenderOptions.dpi_table("1200x1800"), 960)
        self.assertEqual(PrintRenderOptions.dpi_table("3700x2700"), 720)
        self.assertEqual(PrintRenderOptions.dpi_table("1400x3000"), 960)
        self.assertEqual(PrintRenderOptions.dpi_table("12000x3000"), 150)


if __name__ == '__main__':
    unittest.main()
