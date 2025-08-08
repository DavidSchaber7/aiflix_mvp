from pathlib import Path
import sys
from unittest.mock import Mock

sys.path.append(str(Path(__file__).resolve().parents[1]))
import utils.image_gen as image_gen


def test_generate_images_placeholder(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    dummy_client = Mock()
    dummy_client.images.generate.side_effect = Exception("failure")
    monkeypatch.setattr(image_gen.config, "get_openai_client", lambda: dummy_client)

    paths = image_gen.generate_images("Szene: Test")

    assert paths, "Es sollte mindestens einen Platzhalter geben"
    assert paths[0].endswith("_placeholder.png")


