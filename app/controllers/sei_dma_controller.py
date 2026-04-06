from models.sei_dma_model import Sei_dmaModel

class SeiDmaController:
    """
    Controller for sei_dma page
    """

    def __init__(self, model=None):
        self.model = model or Sei_dmaModel

    def get_title(self):
        return "Automação: SEI DMA"
