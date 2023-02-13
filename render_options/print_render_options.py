class PrintRenderOptions:
    @staticmethod
    def dpi_table(size: str) -> int:
        size = size.replace("х", "x")
        if "—" in size:
            size = size.split("—")[0]
        if "-" in size:
            size = size.split("-")[0]
        length = int(size.split("x")[0])
        width = int(size.split("x")[1])

        if 2.5 < length / width:
            return 150
        if 1.75 < length / width < 2.5:
            return 460
        if 1.5 < length / width <= 1.75:
            return 460
        if 0.7 < length / width <= 1.5:
            return 720
        if 0.5 < length / width <= 0.7:
            return 960
        if 0.3 < length / width <= 0.5:
            return 960