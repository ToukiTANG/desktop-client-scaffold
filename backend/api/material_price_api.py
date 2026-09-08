from services.material_price_service import MaterialPriceService


class MaterialPriceApi:
    def __init__(self):
        self._window = None
        self._service = MaterialPriceService()

    def _bind_window(self, window):
        self._window = window

    def get_material_prices(self):
        return self._service.get_material_prices()