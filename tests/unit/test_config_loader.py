import unittest
from webappbase.lib.Config import Config

JSON_PATH = "../../config/config.json"
YAML_PATH = "../../config/config.yaml"


class TestConfig(unittest.TestCase):

    def test_load_json(self):
        config = Config(JSON_PATH)
        print config.get_all()
        self.assertTrue(isinstance(config, Config))

    def test_load_yaml(self):
        config = Config(YAML_PATH)
        print config.get_all()
        self.assertTrue(isinstance(config, Config))


if __name__ == '__main__':
    unittest.main()
