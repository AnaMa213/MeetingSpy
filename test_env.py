import torch
import torchaudio
from asteroid.models import ConvTasNet

try:
    model = ConvTasNet.from_pretrained("JorisCos/ConvTasNet_Libri2Mix_sepnoisy_16k")
    print("Conv-TasNet chargé avec succès !")
except Exception as e:
    print(f"Erreur lors du chargement de Conv-TasNet : {e}")